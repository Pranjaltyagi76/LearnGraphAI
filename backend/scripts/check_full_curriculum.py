"""Review full coverage and trusted authored traces; generate reproducible read-only examples."""

import argparse
import ast
import json
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from app.analysis import analyze
from app.contracts import AnalyzeRequest, canonical_json
from app.published import payload_hash, publication_input, unpack
from app.release import load_release
from scripts.build_full_curriculum import FULL_ID, outputs
from scripts.full_content import CONTENT

ROOT = Path(__file__).resolve().parents[2]
RECORDED_AT = datetime(2026, 11, 21, tzinfo=UTC)


def review():
    for path, data in outputs().items():
        assert (ROOT / path).read_bytes() == data, f"Generated artifact differs: {path}"
    release = load_release(ROOT, FULL_ID)
    old = load_release(ROOT)
    assert all(release.activities[key] == value for key, value in old.activities.items())
    assert len(release.activities) == 84
    questions = [a for a in release.activities.values() if a["kind"] == "question"]
    assert len(questions) == 72
    assert len({(q["prompt"], q["code"]) for q in questions}) == 72
    coverage = []
    for concept in release.graph.order:
        items = [a for a in release.activities.values() if a["primary_concept_id"] == concept]
        assert Counter(a["role"] for a in items) == {
            "diagnostic": 1,
            "practice": 4,
            "reassessment": 1,
            "lesson": 1,
        }
        for item in items:
            assert item["active"] and item["provenance"]["origin"] == "original"
            if item["kind"] == "question":
                assert len({o["text"] for o in item["options"]}) == 4
                assert item["explanation"] and len(item["prompt"]) > 20
        consumed = {
            f"{concept}_{suffix}" for suffix in ("diagnostic_01", "practice_01", "practice_02")
        }
        fresh = [a for a in items if a["id"] not in consumed]
        assert sum(a["role"] == "practice" for a in fresh) == 2
        assert sum(a["role"] == "reassessment" for a in fresh) == 1
        coverage.append(
            {
                "concept": concept,
                "questions": 6,
                "lessons": 1,
                "remaining_practice_after_three": 2,
                "fresh_reassessment": True,
            }
        )
    traces = []
    # Only these original, explicitly marked source literals are executed offline.
    # Never load code from HTTP, local visitor histories, or a publication package.
    for concept, content in CONTENT.items():
        for i, item in enumerate(content["questions"]):
            if not item["verify_stdout"]:
                continue
            tree = ast.parse(item["code"])
            assert not any(
                isinstance(n, (ast.Import, ast.ImportFrom, ast.With, ast.AsyncWith))
                for n in ast.walk(tree)
            )
            names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
            assert not names & {"open", "eval", "exec", "compile", "input", "__import__"}
            assert all(
                not n.attr.startswith("_") for n in ast.walk(tree) if isinstance(n, ast.Attribute)
            )
            run = subprocess.run(
                [sys.executable, "-I", "-S", "-c", item["code"]],
                capture_output=True,
                text=True,
                timeout=3,
                check=True,
            )
            assert run.stdout.strip() == item["options"][item["correct"]], (concept, i)
            assert not run.stderr
            traces.append(
                {"concept": concept, "question_ordinal": i + 1, "actual_stdout": run.stdout.strip()}
            )
    payload = publication_input(ROOT, release_id=FULL_ID)
    published = unpack(payload, payload_hash(payload))
    expected = {
        "demo_base_cases": (6, "supported_gap", "base_cases"),
        "demo_upstream": (27, "supported_gap", "overlapping_subproblems"),
        "demo_sparse": (1, "no_failed_trigger", None),
        "demo_ambiguous": (15, "ambiguous", None),
    }
    examples = []
    for profile in release.profiles.values():
        request = AnalyzeRequest(
            contract_version=1,
            versions=release.versions(profile.profile_id),
            profile_id=profile.profile_id,
            sandbox_id=str(uuid5(NAMESPACE_URL, f"{FULL_ID}:example:{profile.profile_id}")),
            local_revision=0,
            focus_concept_id=profile.focus_concept_id,
            events=[],
        )
        bundle = analyze(release, request, received_at=RECORDED_AT)
        count, status, candidate = expected[profile.profile_id]
        assert len(profile.events) == count
        assert bundle.diagnosis.status == status, (profile.profile_id, bundle.diagnosis.status)
        assert (
            bundle.diagnosis.candidates[0].concept_id if bundle.diagnosis.candidates else None
        ) == candidate
        assert bundle.plan.items
        examples.append(
            {
                "seed": published.seed(profile.profile_id).model_dump(mode="json"),
                "analysis": bundle.model_dump(mode="json"),
            }
        )
    return {
        "recorded_at": "2026-11-21T00:00:00.000Z",
        "release_id": FULL_ID,
        "release_hash": release.manifest["release_hash"],
        "scope": (
            "Engineering content review; not educator validation or an "
            "independent quality benchmark"
        ),
        "coverage": coverage,
        "checked_new_output_traces": traces,
        "preserved_slice_activities": len(old.activities),
        "package_bytes": len(canonical_json(payload)),
        "profile_event_counts": {p.profile_id: len(p.events) for p in release.profiles.values()},
    }, {"recorded_at": "2026-11-21T00:00:00.000Z", "examples": examples}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report, examples = review()
    for path, value in (
        (ROOT / "context/evidence/phase4_content.json", report),
        (ROOT / "frontend/lib/generated/examples-full-v1.json", examples),
    ):
        data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
        if args.write:
            path.write_bytes(data)
        else:
            assert path.read_bytes() == data, f"Review/example output differs: {path.name}"
    count = len(report["checked_new_output_traces"])
    print(f"72 questions / 12 lessons / 4 profiles; {count} trusted output traces passed.")


if __name__ == "__main__":
    main()
