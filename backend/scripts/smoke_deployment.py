"""Bounded public Phase 1 smoke check: eleven HTTP requests, three quota reservations.

No retries, quota bypass, credential input, or load generation. Run only after
checking free allowances. Timings are descriptive and do not prove cold starts.
"""

import argparse
import json
import math
import platform
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def origin(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise argparse.ArgumentTypeError(
            "Provide a public HTTPS origin without credentials or paths."
        )
    return value.rstrip("/")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", required=True, type=origin)
    parser.add_argument("--frontend", required=True, type=origin)
    parser.add_argument("--deployment-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = {
        "observed_at": datetime.now(UTC).isoformat(),
        "api": args.api,
        "frontend": args.frontend,
        "deployment_id": args.deployment_id,
        "client": {"os": platform.system(), "python": platform.python_version()},
        "method": "Sequential, no retries; cold state unclassified; three grading reservations.",
        "requests": [],
        "passed": False,
    }

    def require(condition: bool, message: str) -> None:
        if not condition:
            raise ValueError(message)

    def request(path: str, body: dict | None = None, expected_status: int = 200):
        headers = {"Origin": args.frontend, "User-Agent": "LearnGraph-Phase1-Smoke/1"}
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()
        started = time.perf_counter()
        req = Request(args.api + path, data=data, headers=headers)
        try:
            response = urlopen(req, timeout=15)
        except HTTPError as exc:
            response = exc
        with response:
            raw = response.read(512 * 1024 + 1)
            elapsed = round((time.perf_counter() - started) * 1000, 2)
            report["requests"].append(
                {
                    "method": "POST" if body is not None else "GET",
                    "path": path,
                    "status": response.status,
                    "elapsed_ms": elapsed,
                    "response_bytes": len(raw),
                    "server_timing": response.headers.get("Server-Timing"),
                    "request_id": response.headers.get("X-Request-ID"),
                }
            )
            require(len(raw) <= 512 * 1024, "Response exceeded smoke-check size bound.")
            require(
                response.status == expected_status, "Unexpected HTTP status; stopped without retry."
            )
            require(
                response.headers.get("Access-Control-Allow-Origin") == args.frontend,
                "Production CORS did not match the frontend origin.",
            )
            require(
                response.headers.get("Cache-Control") == "no-store", "API response was cacheable."
            )
            return json.loads(raw)

    try:
        require(request("/health")["status"] == "ok", "Liveness failed.")
        for _ in range(5):
            require(request("/ready")["status"] == "ready", "Database readiness failed.")
        profiles = request("/api/v1/demo/profiles")
        profile = profiles["profiles"][0]
        seed = request(f"/api/v1/demo/profiles/{profile['id']}/seed")
        source = json.loads((ROOT / "data/phase1.json").read_text(encoding="utf-8"))
        require(seed["release_id"] == source["release_id"], "Unexpected published release.")
        require(
            all("correct_option" not in q and "explanation" not in q for q in seed["activities"]),
            "Seed projection exposed future grading feedback.",
        )
        seen = {e["activity_id"] for e in seed["seed_events"]}
        question = next(
            q
            for q in source["questions"]
            if q["concept_id"] == profile["focus_concept_id"]
            and q["role"] == "practice"
            and q["id"] not in seen
        )
        answer = {
            "event_id": str(uuid4()),
            "release_id": seed["release_id"],
            "activity_id": question["id"],
            "option_id": question["correct_option"],
        }
        correct = request("/api/v1/bootstrap/answer", answer)
        require(
            correct["is_correct"] is True and correct["persisted"] is False, "Correct grade failed."
        )
        wrong_option = next(
            o["id"] for o in question["options"] if o["id"] != question["correct_option"]
        )
        wrong = request(
            "/api/v1/bootstrap/answer",
            {**answer, "event_id": str(uuid4()), "option_id": wrong_option},
        )
        require(
            wrong["is_correct"] is False and wrong["persisted"] is False, "Incorrect grade failed."
        )
        conflict = request(
            "/api/v1/bootstrap/answer", {**answer, "release_id": "unpublished-smoke-version"}, 409
        )
        require(conflict["code"] == "version_mismatch", "Version conflict contract failed.")
        values = sorted(r["elapsed_ms"] for r in report["requests"] if r["path"] == "/ready")
        report["readiness_ms"] = {
            "n": len(values),
            "p50": statistics.median(values),
            "p95_nearest_rank": values[math.ceil(0.95 * len(values)) - 1],
            "max": max(values),
            "interpretation": "Small network/TLS sample; no latency SLO claim.",
        }
        report["passed"] = True
    except (OSError, ValueError, KeyError, StopIteration):
        report["failure"] = (
            "Smoke check failed; inspect statuses/connection privately before another run."
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"Smoke check {'passed' if report['passed'] else 'failed'}; report saved to {args.output}."
    )
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
