"""Analyze a frozen demo or an explicit protocol request, entirely offline."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from app.analysis import analyze
from app.contracts import AnalyzeRequest
from app.explanation import explain
from app.release import load_release

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="demo_base_cases")
    parser.add_argument("--release", default="learngraph-review-v1")
    parser.add_argument("--request", type=Path, help="Complete AnalyzeRequest JSON")
    parser.add_argument("--received-at", default="2026-11-20T00:00:00+00:00")
    parser.add_argument("--explain", action="store_true", help="Include fixed evidence templates")
    args = parser.parse_args()
    release = load_release(ROOT, args.release)
    if args.request:
        with args.request.open("rb") as stream:
            raw = stream.read(release.config["limits"]["request_bytes"] + 1)
        if len(raw) > release.config["limits"]["request_bytes"]:
            parser.error("Request exceeds 262144 UTF-8 bytes")
        request = AnalyzeRequest.model_validate_json(raw)
    else:
        profile = release.profiles[args.profile]
        request = AnalyzeRequest(
            contract_version=1,
            versions=release.versions(args.profile),
            profile_id=args.profile,
            sandbox_id=str(uuid5(NAMESPACE_URL, "learngraph:offline:" + args.profile)),
            local_revision=0,
            focus_concept_id=profile.focus_concept_id,
            events=[],
        )
    bundle = analyze(release, request, received_at=datetime.fromisoformat(args.received_at))
    output = bundle.model_dump(mode="json")
    if args.explain:
        output = {"analysis": output, "explanation": explain(bundle)}
    # ASCII JSON escapes preserve Unicode text on Windows cp1252 pipes as well as UTF-8.
    print(json.dumps(output, ensure_ascii=True, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
