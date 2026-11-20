"""Write missing Phase 0 schemas/manifest, or verify them without mutation.

Existing differing artifacts are never overwritten. Change frozen versions
deliberately when editing contracts after this review.
"""

import argparse
import hashlib
import json
from pathlib import Path

from app.contracts import (
    AnalysisBundle,
    AnalyzeRequest,
    ErrorEnvelope,
    EvaluationSummary,
    HealthResponse,
    ProfileSeed,
    ProfilesResponse,
    ReadyResponse,
    ReleaseSummary,
    SandboxRecord,
    SeedResponse,
    canonical_json,
)

ROOT = Path(__file__).resolve().parents[2]
MODELS = (
    ReleaseSummary,
    AnalyzeRequest,
    AnalysisBundle,
    ProfilesResponse,
    SeedResponse,
    ErrorEnvelope,
    SandboxRecord,
    ProfileSeed,
    HealthResponse,
    ReadyResponse,
    EvaluationSummary,
)
ARTIFACTS = (
    "curriculum/graph.v1.json",
    "curriculum/catalog-slice.v1.json",
    "curriculum/model-config.v1.json",
    "curriculum/profiles.v1.json",
    "contracts/protocol-v1.schema.json",
)


def encoded(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def protocol_schema() -> dict:
    definitions = {}
    for model in MODELS:
        generated = model.model_json_schema(ref_template="#/$defs/{model}")
        for name, definition in generated.pop("$defs", {}).items():
            if name in definitions and definitions[name] != definition:
                raise ValueError(f"Conflicting definition: {name}")
            definitions[name] = definition
        definitions[model.__name__] = generated
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:learngraph:protocol:v1",
        "title": "LearnGraph offline reviewed protocol v1",
        "oneOf": [{"$ref": f"#/$defs/{model.__name__}"} for model in MODELS],
        "$defs": definitions,
    }


def manifest() -> dict:
    identity = {
        "contract_version": 1,
        "release_id": "learngraph-review-v1",
        "graph_version": "graph-v1",
        "catalog_version": "catalog-slice-v1",
        "model_version": "baseline-v1",
        "profiles_version": "demo-profiles-v1",
        "scope": "two_concept_review_slice",
        "artifacts": [
            {"path": path, "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}
            for path in ARTIFACTS
        ],
    }
    return {
        "status": "reviewed_draft_not_published",
        "identity": identity,
        "release_hash": hashlib.sha256(canonical_json(identity)).hexdigest(),
    }


def check_or_create(path: str, value: dict, write: bool) -> None:
    target = ROOT / path
    expected = encoded(value)
    if target.exists():
        if target.read_bytes() != expected:
            raise ValueError(
                f"Frozen artifact changed: {path}; review/bump its version deliberately"
            )
    elif write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(expected)
    else:
        raise ValueError(f"Missing frozen artifact: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create missing artifacts only")
    args = parser.parse_args()
    check_or_create("contracts/protocol-v1.schema.json", protocol_schema(), args.write)
    check_or_create("contracts/release-manifest.json", manifest(), args.write)
    print("Frozen protocol schema and compatible release manifest verified.")


if __name__ == "__main__":
    main()
