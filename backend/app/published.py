"""Validated immutable publication package and safe public projections."""

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from app.contracts import (
    EvaluationSummary,
    ProfileInfo,
    ProfilesResponse,
    ProfileSummary,
    PublicConcept,
    PublicEdge,
    PublicLesson,
    PublicQuestion,
    ReleaseSummary,
    SeedResponse,
    canonical_json,
)
from app.release import Release, load_release


def payload_hash(payload: dict) -> str:
    return hashlib.sha256(canonical_json(payload)).hexdigest()


@dataclass(frozen=True)
class PublishedRelease:
    release: Release
    concepts: tuple[PublicConcept, ...]
    edges: tuple[PublicEdge, ...]
    evaluation: EvaluationSummary | None

    def summary(self) -> ReleaseSummary:
        identity = self.release.manifest["identity"]
        return ReleaseSummary(
            contract_version=1,
            release_hash=self.release.manifest["release_hash"],
            **{
                k: identity[k]
                for k in ReleaseSummary.model_fields
                if k not in {"contract_version", "release_hash"}
            },
        )

    def profiles(self) -> ProfilesResponse:
        return ProfilesResponse(
            contract_version=1,
            profiles=[
                ProfileSummary(
                    **self.info(p.profile_id).model_dump(),
                    versions=self.release.versions(p.profile_id),
                )
                for p in sorted(self.release.profiles.values(), key=lambda p: p.profile_id)
            ],
        )

    def info(self, profile_id: str) -> ProfileInfo:
        p = self.release.profiles[profile_id]
        return ProfileInfo(
            id=p.profile_id, **{k: getattr(p, k) for k in ProfileInfo.model_fields if k != "id"}
        )

    def seed(self, profile_id: str) -> SeedResponse:
        activities = []
        for a in sorted(self.release.activities.values(), key=lambda a: a["id"]):
            model = PublicQuestion if a["kind"] == "question" else PublicLesson
            activities.append(model.model_validate({k: a[k] for k in model.model_fields}))
        return SeedResponse(
            contract_version=1,
            versions=self.release.versions(profile_id),
            profile=self.info(profile_id),
            seed_events=self.release.profiles[profile_id].events,
            concepts=list(self.concepts),
            edges=list(self.edges),
            activities=activities,
        )


def unpack(payload: dict, stored_hash: str) -> PublishedRelease:
    if payload_hash(payload) != stored_hash or len(canonical_json(payload)) > 524288:
        raise ValueError("Published package integrity/size failure")
    if set(payload) != {"package_version", "manifest", "artifacts", "evaluation"} or (
        type(payload["package_version"]) is not int or payload["package_version"] != 1
    ):
        raise ValueError("Unsupported publication package")
    artifacts = {
        path: base64.b64decode(data, validate=True) for path, data in payload["artifacts"].items()
    }
    release = Release(payload["manifest"], artifacts)
    graph = json.loads(artifacts["curriculum/graph.v1.json"])
    evaluation = (
        EvaluationSummary.model_validate(payload["evaluation"])
        if payload["evaluation"] is not None
        else None
    )
    if evaluation and any(
        getattr(evaluation, key) != release.manifest["identity"][key]
        for key in ("graph_version", "catalog_version", "model_version")
    ):
        raise ValueError("Evaluation is incompatible with publication")
    return PublishedRelease(
        release=release,
        concepts=tuple(
            PublicConcept.model_validate({k: c[k] for k in PublicConcept.model_fields})
            for c in sorted(graph["concepts"], key=lambda c: c["id"])
        ),
        edges=tuple(
            PublicEdge.model_validate({k: e[k] for k in PublicEdge.model_fields})
            for e in sorted(graph["edges"], key=lambda e: (e["prerequisite"], e["dependent"]))
        ),
        evaluation=evaluation,
    )


def publication_input(
    root: Path, evaluation_path: Path | None = None, release_id: str = "learngraph-review-v1"
) -> dict:
    release = load_release(root, release_id)
    payload = {
        "package_version": 1,
        "manifest": release.manifest,
        "artifacts": {
            a["path"]: base64.b64encode((root / a["path"]).read_bytes()).decode("ascii")
            for a in release.manifest["identity"]["artifacts"]
        },
        "evaluation": json.loads(evaluation_path.read_bytes())["summary"]
        if evaluation_path
        else None,
    }
    unpack(payload, payload_hash(payload))
    return payload
