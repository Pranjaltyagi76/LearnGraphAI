"""Bounded local maximum-history profile; no database or network access."""

import argparse
import copy
import hashlib
import json
import math
import platform
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from app.analysis import analyze
from app.contracts import AnalyzeRequest, canonical_json
from app.release import load_release
from scripts.freeze_full_audit import ROOT


def fixture():
    release = copy.deepcopy(load_release(ROOT, "learngraph-full-v1"))
    questions = [a for a in release.activities.values() if a["kind"] == "question"]

    def events(count, day):
        result = []
        for i in range(count):
            a = questions[i % len(questions)]
            wrong = next(o["id"] for o in a["options"] if o["id"] != a["correct_option"])
            result.append(
                {
                    "schema_version": 1,
                    "kind": "response",
                    "event_id": str(uuid5(NAMESPACE_URL, f"profile-max:{day}:{i}")),
                    "sequence_number": i + 1,
                    "activity_id": a["id"],
                    "activity_version": a["version"],
                    "assessment_run_id": str(uuid5(NAMESPACE_URL, f"profile-max:{day}")),
                    "occurred_at": f"2026-11-{day}T01:{i // 60:02}:{i % 60:02}.000Z",
                    "response": {"option_id": wrong},
                    "hints_used": 0,
                    "time_spent_seconds": None,
                }
            )
        return result

    p = release.profiles["demo_base_cases"]
    release.profiles[p.profile_id] = type(p).model_validate(
        {**p.model_dump(), "events": events(100, 19)}
    )
    request = AnalyzeRequest(
        contract_version=1,
        versions=release.versions(p.profile_id),
        profile_id=p.profile_id,
        sandbox_id=str(uuid5(NAMESPACE_URL, "max-sandbox")),
        local_revision=200,
        focus_concept_id="memoization",
        events=events(200, 20),
    )
    return release, request


def run(release, request):
    started = time.perf_counter()
    result = analyze(release, request, received_at=datetime(2026, 11, 21, tzinfo=UTC))
    assert result.accepted_visitor_events == 200 and len(result.graded_events) == 300
    return (time.perf_counter() - started) * 1000, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    release, request = fixture()
    load_ms = (time.perf_counter() - started) * 1000
    if args.worker:
        ms, result = run(release, request)
        print(
            json.dumps(
                {
                    "fixture_load_ms": load_ms,
                    "analysis_ms": ms,
                    "bundle_bytes": len(canonical_json(result.model_dump(mode="json"))),
                }
            )
        )
        return
    for _ in range(5):
        run(release, request)
    samples = [run(release, request)[0] for _ in range(100)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        concurrent = list(pool.map(lambda _: run(release, request)[0], range(20)))
    cold = []
    for _ in range(3):
        start = time.perf_counter()
        row = json.loads(
            subprocess.check_output(
                [sys.executable, "-m", "scripts.profile_release", "--worker"],
                cwd=ROOT / "backend",
                text=True,
            )
        )
        row["process_start_to_exit_ms"] = (time.perf_counter() - start) * 1000
        cold.append(row)
    report = {
        "observed_at": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python": sys.version,
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_dirty": bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
        ),
        "profile_script_sha256_lf": hashlib.sha256(
            Path(__file__).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest(),
        "fixture": (
            "Fixture-only 100 seed + 200 visitor responses, twelve-concept catalog; "
            "all failed, many retries. Canonical seeds unchanged."
        ),
        "request_bytes": len(canonical_json(request.model_dump(mode="json"))),
        "bundle_bytes": cold[0]["bundle_bytes"],
        "warmup": 5,
        "sequential_samples_ms": samples,
        "sequential_p50_ms": statistics.median(samples),
        "sequential_p95_ms": sorted(samples)[math.ceil(0.95 * len(samples)) - 1],
        "concurrent_workers": 4,
        "concurrent_samples_ms": concurrent,
        "fresh_processes": cold,
        "limits": {"api_seconds": 10, "request_bytes": 262144},
        "limitations": (
            "Local compute and process-start samples, not platform cold starts, "
            "network latency or production capacity."
        ),
    }
    if not args.output:
        parser.error("--output is required for the parent measurement")
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(
        json.dumps(
            {
                k: report[k]
                for k in ("request_bytes", "bundle_bytes", "sequential_p50_ms", "sequential_p95_ms")
            }
        )
    )


if __name__ == "__main__":
    main()
