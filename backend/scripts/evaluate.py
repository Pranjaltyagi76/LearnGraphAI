"""Run or verify the frozen offline benchmark; never connects to a provider."""

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from app.release import load_release
from evaluation.runner import evaluate, load_packet

ROOT = Path(__file__).resolve().parents[2]


def encoded(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def source_hashes():
    paths = [
        *sorted((ROOT / "backend/app").glob("*.py")),
        *sorted((ROOT / "backend/evaluation").glob("*.py")),
        ROOT / "backend/scripts/analyze.py",
        ROOT / "backend/scripts/evaluate.py",
        ROOT / "backend/scripts/check_phase0.py",
    ]
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(
            p.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        for p in paths
    }


def render_report(results: dict) -> bytes:
    lines = [
        "# Phase 2 measured synthetic audit",
        "",
        "Public exposed cases; no blind, generalization, causal or learning-gain claim.",
        "",
    ]
    for split, result in results.items():
        summary = result["summary"]
        lines += [
            f"## {split}",
            "",
            f"Cases: {len(result['cases'])}; failures: {len(result['failures'])}.",
            "",
            "| Prediction | N | Positive/negative | Log loss | Brier | ROC AUC | "
            "Average precision |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
        ]
        for row in summary["prediction"]:
            lines.append(
                f"| {row['baseline']} | {row['eligible_predictions']} | "
                f"{row['positive_outcomes']}/{row['negative_outcomes']} | "
                f"{row['log_loss']:.6f} | {row['brier']:.6f} | "
                f"{row['roc_auc']} | {row['pr_auc']} |"
            )
        lines += [
            "",
            "| Diagnosis | Labeled/all | Precision@1 | Recall@3 | MRR | Coverage | "
            "No-gap false rate |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in summary["diagnosis"]:
            lines.append(
                f"| {row['baseline']} | {row['labeled_gap_cases']}/{row['all_cases']} | "
                f"{row['precision_at_1']} | {row['recall_at_3']} | {row['mrr']} | "
                f"{row['coverage']} | {row['false_diagnosis_rate']} |"
            )
        lines += [
            "",
            "Recommendation counts, all metrics/denominators, excluded events, "
            "per-case outputs and observed workflow predicates are in the matching JSON file.",
            "",
        ]
        if result["failures"]:
            lines += [
                "Failures (retained):",
                "",
                "```json",
                json.dumps(result["failures"], indent=2),
                "```",
                "",
            ]
    lines += [
        "## Interpretation",
        "",
        "The global rate is fit on eligible training events only. Concept predictions use "
        "the preceding learner prefix, including an internal 1/2 prior for no observations. "
        "That prior is never displayed as assessed mastery.",
        "",
        "Precision@K divides by returned candidates (zero on labeled-case abstention). "
        "Coverage uses all cases; false diagnoses use only no-gap controls. PR AUC means "
        "tie-grouped stepwise average precision. Undefined ratios have explicit reasons in JSON.",
        "",
        "All plan comparators share targets, catalog, stages and hard readiness/freshness "
        "constraints. Lowest-estimate prioritizes available DAG concepts, then the frozen "
        "activity score. Random uses fixed per-learner seeds within available concepts/stages. "
        "The two-concept chain provides little ranking discrimination.",
        "",
        "Prerequisite validity counts returned plans with correct ordering/readiness/locks; "
        "this is not a count of currently executable questions. "
        "Item counts and gap coverage are separate. "
        "Reassessment distinctness does not assert that a learner completed the workflow.",
        "",
        "The frozen manifest retains results=not_run as historical definition metadata. "
        "This run's manifest and outputs are the measurement record. Production activation, "
        "browser storage and the full 72-item curriculum remain later work.",
        "",
    ]
    return ("\n".join(lines)).encode()


def compute(release, packet, split_manifest, manifest_hash, source_commit, measured_at, splits):
    return {
        split: evaluate(
            release,
            packet,
            split_manifest,
            split,
            source_commit=source_commit,
            measured_at=measured_at,
            manifest_hash=manifest_hash,
        )
        for split in splits
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New immutable output directory")
    parser.add_argument("--check", type=Path, help="Recompute and verify a saved run")
    parser.add_argument("--split", choices=("development", "test", "all"), default="all")
    args = parser.parse_args()
    if args.output and args.check:
        parser.error("Choose output or check")
    release = load_release(ROOT)
    packet, split_manifest, manifest_hash = load_packet(ROOT, release)
    if args.check:
        manifest = json.loads((args.check / "manifest.json").read_bytes())
        if source_hashes() != manifest["source_hashes_lf"]:
            raise ValueError("Measured implementation differs; create a new versioned run")
        if release.manifest["release_hash"] != manifest["release_hash"]:
            raise ValueError("Measured release differs")
        for path, digest in manifest["input_hashes"].items():
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
                raise ValueError(f"Measured input differs: {path}")
        results = compute(
            release,
            packet,
            split_manifest,
            manifest_hash,
            manifest["source_commit"],
            manifest["measured_at"],
            manifest["splits"],
        )
        outputs = {f"{split}.json": encoded(result) for split, result in results.items()}
        outputs["report.md"] = render_report(results)
        for name, data in outputs.items():
            if (args.check / name).read_bytes() != data or hashlib.sha256(data).hexdigest() != (
                manifest["output_hashes"][name]
            ):
                raise ValueError(f"Benchmark output mismatch: {name}")
        print("Saved benchmark inputs, source hashes and exact outputs reproduced.")
    else:
        source_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
        measured_at = datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        splits = ["development", "test"] if args.split == "all" else [args.split]
        results = compute(
            release, packet, split_manifest, manifest_hash, source_commit, measured_at, splits
        )
        outputs = {f"{split}.json": encoded(result) for split, result in results.items()}
        outputs["report.md"] = render_report(results)
        if args.output:
            if args.output.exists():
                raise ValueError("Output already exists; use --check or a new run version")
            manifest = {
                "run_id": args.output.name,
                "source_commit": source_commit,
                "source_dirty": dirty,
                "measured_at": measured_at,
                "split_manifest_hash": manifest_hash,
                "splits": splits,
                "release_hash": release.manifest["release_hash"],
                "input_hashes": {
                    path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                    for path in (
                        "evaluation/scenarios.v1.json",
                        "evaluation/manifest.v1.json",
                        "evaluation/variants.v1.json",
                        "backend/uv.lock",
                    )
                },
                "source_hashes_lf": source_hashes(),
                "random_baseline_seed": split_manifest["random_baseline_seed"],
                "command": (
                    f"python -m scripts.evaluate --output {args.output.as_posix()} "
                    f"--split {args.split}"
                ),
                "environment": {
                    "python": sys.version,
                    "platform": platform.platform(),
                    "pydantic": version("pydantic"),
                    "dependencies_added": [],
                },
                "output_hashes": {
                    name: hashlib.sha256(data).hexdigest() for name, data in outputs.items()
                },
                "metric_definitions": "evaluation/readme.md and context/benchmark.md",
                "test_exposure": split_manifest["test_exposure"],
                "fitting": "Training-only global rate; no policy tuned on audit output.",
            }
            args.output.mkdir(parents=True)
            for name, data in outputs.items():
                (args.output / name).write_bytes(data)
            (args.output / "manifest.json").write_bytes(encoded(manifest))
        print(outputs["report.md"].decode())
    if any(result["failures"] for result in results.values()):
        raise SystemExit("Benchmark retained failures; inspect artifacts")


if __name__ == "__main__":
    main()
