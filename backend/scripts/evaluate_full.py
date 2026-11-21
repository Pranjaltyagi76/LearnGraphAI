"""Measure/reproduce the separately frozen full-track audit without policy fitting."""

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from app.contracts import EvaluationSummary
from app.release import load_release
from evaluation.runner import EVENTS, evaluate
from scripts.freeze_full_audit import ROOT, encoded


def hashes():
    paths = [
        *sorted((ROOT / "backend/app").glob("*.py")),
        *sorted((ROOT / "backend/evaluation").glob("*.py")),
        ROOT / "backend/scripts/evaluate_full.py",
    ]
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(
            p.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        for p in paths
    }


def packet():
    raw = (ROOT / "evaluation/full-scenarios.v1.json").read_bytes()
    manifest_raw = (ROOT / "evaluation/full-manifest.v1.json").read_bytes()
    data, manifest = json.loads(raw), json.loads(manifest_raw)
    assert hashlib.sha256(raw).hexdigest() == manifest["source_sha256"]
    assert (
        hashlib.sha256((ROOT / "contracts/releases/full-v1.json").read_bytes()).hexdigest()
        == manifest["release_manifest_sha256"]
    )
    assert Counter(c["split"] for c in data["cases"]) == manifest["split_counts"]
    for field in ("id", "learner_id", "scenario_group"):
        assert len({c[field] for c in data["cases"]}) == len(data["cases"])
    ids = []
    for c in data["cases"]:
        events = EVENTS.validate_python(c["events"])
        ids.extend(e.event_id for e in events)
    assert len(set(ids)) == len(ids)
    return data, manifest, hashlib.sha256(manifest_raw).hexdigest()


def compute(source, measured):
    release = load_release(ROOT, "learngraph-full-v1")
    data, manifest, digest = packet()
    outputs = {}
    for split in ("development", "test"):
        result = evaluate(
            release,
            data,
            manifest,
            split,
            source_commit=source,
            measured_at=measured,
            manifest_hash=digest,
        )
        summary = result["summary"]
        summary.update(
            evaluation_version="full-evaluation-v1",
            scenario_version="full-scenarios-v1",
            limitations=[
                data["exposure"],
                data["item_reuse"],
                data["label_provenance"],
                "Synthetic assumption checks, not student validation, causality or learning gains.",
                "Small authored sample; no calibrated mastery or uncertainty interval claim.",
            ],
        )
        EvaluationSummary.model_validate(summary)
        outputs[split] = result
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if bool(args.output) == bool(args.check):
        parser.error("Choose exactly one output/check")
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    measured = datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    if args.check:
        manifest = json.loads((args.check / "manifest.json").read_bytes())
        assert manifest["source_hashes_lf"] == hashes(), "Measured source differs"
        source, measured = manifest["source_commit"], manifest["measured_at"]
    results = compute(source, measured)
    files = {f"{split}.json": encoded(r) for split, r in results.items()}
    if args.check:
        for name, data in files.items():
            assert (args.check / name).read_bytes() == data
            assert hashlib.sha256(data).hexdigest() == manifest["output_hashes"][name]
        assert manifest["input_manifest_sha256"] == packet()[2]
    else:
        if args.output.exists():
            raise ValueError("Never overwrite an existing run")
        manifest = {
            "source_commit": source,
            "source_dirty": bool(
                subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
            ),
            "measured_at": measured,
            "source_hashes_lf": hashes(),
            "input_manifest_sha256": packet()[2],
            "release_hash": load_release(ROOT, "learngraph-full-v1").manifest["release_hash"],
            "environment": {"python": sys.version, "platform": platform.platform()},
            "output_hashes": {
                name: hashlib.sha256(data).hexdigest() for name, data in files.items()
            },
            "exposure": "Frozen before first evaluation; existing implementation known; no tuning",
        }
        args.output.mkdir(parents=True)
        for name, data in files.items():
            (args.output / name).write_bytes(data)
        (args.output / "manifest.json").write_bytes(encoded(manifest))
    print(
        json.dumps(
            {
                s: {
                    "cases": len(r["cases"]),
                    "failures": r["failures"],
                    "prediction": r["summary"]["prediction"],
                    "diagnosis": r["summary"]["diagnosis"],
                }
                for s, r in results.items()
            }
        )
    )
    if any(r["failures"] for r in results.values()):
        raise SystemExit("Failures retained; investigate without relabeling the frozen audit")


if __name__ == "__main__":
    main()
