"""Hash-verified compatible release input. File loading belongs to offline tools.

The byte-mapping constructor can later consume canonical database package bytes;
domain services neither open files nor connect to a provider.
"""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from pydantic import Field

from app.contracts import (
    ProfileSeed,
    PublicConcept,
    PublicLesson,
    PublicQuestion,
    Versions,
    canonical_json,
    normalized_events,
)
from app.graph import Graph
from app.replay import replay

SUPPORTED_POLICY_HASH = "068b6fc04154f53d48948ad295edd8dd031890e57059cdeb1ecedb5b7127a6fd"
SUPPORTED_SCHEMA_HASH = "4aacf8a0eaa2b2aa2bf73d17bf7fd5224f8002ecb449b670ba42393b88a56aef"


class Question(PublicQuestion):
    correct_option: str = Field(pattern=r"^[a-z0-9_-]{1,8}$")
    explanation: str = Field(min_length=1, max_length=2000)


class Release:
    def __init__(self, manifest: dict, artifacts: dict[str, bytes]):
        manifest = deepcopy(manifest)
        identity = manifest["identity"]
        if hashlib.sha256(canonical_json(identity)).hexdigest() != manifest["release_hash"]:
            raise ValueError("Release identity hash mismatch")
        expected = {entry["path"]: entry["sha256"] for entry in identity["artifacts"]}
        paths = {
            "curriculum/graph.v1.json",
            "curriculum/catalog-slice.v1.json",
            "curriculum/model-config.v1.json",
            "curriculum/profiles.v1.json",
            "contracts/protocol-v1.schema.json",
        }
        if set(expected) != paths or set(artifacts) != paths or len(identity["artifacts"]) != 5:
            raise ValueError("Incomplete compatible release")
        for path, digest in expected.items():
            if hashlib.sha256(artifacts[path]).hexdigest() != digest:
                raise ValueError("Release artifact hash mismatch")
        values = {path: json.loads(data) for path, data in artifacts.items()}
        graph = values["curriculum/graph.v1.json"]
        catalog = values["curriculum/catalog-slice.v1.json"]
        profiles = values["curriculum/profiles.v1.json"]
        self.config = values["curriculum/model-config.v1.json"]
        for field, source in (
            ("graph_version", graph),
            ("catalog_version", catalog),
            ("profiles_version", profiles),
            ("model_version", self.config),
        ):
            if identity[field] != source[field]:
                raise ValueError("Incompatible artifact version")
        if identity["contract_version"] != 1 or identity["model_version"] != "baseline-v1":
            raise ValueError("Unsupported analysis policy")
        if (
            expected["curriculum/model-config.v1.json"] != SUPPORTED_POLICY_HASH
            or expected["contracts/protocol-v1.schema.json"] != SUPPORTED_SCHEMA_HASH
        ):
            raise ValueError("Unsupported policy/schema bytes under frozen version")
        self.graph = Graph(graph)
        if len(self.graph.order) != 12:
            raise ValueError("Protocol v1 requires twelve concepts")
        for concept in graph["concepts"]:
            PublicConcept.model_validate({k: concept[k] for k in PublicConcept.model_fields})
        self.activities = {}
        for activity in catalog["activities"]:
            model = Question if activity["kind"] == "question" else PublicLesson
            model.model_validate(activity)
            concept = activity["primary_concept_id"]
            secondary = activity["secondary_concept_ids"]
            if (
                activity["id"] in self.activities
                or concept not in self.graph.parents
                or len(secondary) != len(set(secondary))
                or not set(secondary) <= set(self.graph.order) - {concept}
            ):
                raise ValueError("Invalid activity identity/tags")
            if activity["kind"] == "question":
                options = {o["id"] for o in activity["options"]}
                if len(options) != 4 or activity["correct_option"] not in options:
                    raise ValueError("Invalid question key/options")
            self.activities[activity["id"]] = activity
        if len(self.activities) > 128:
            raise ValueError("Catalog exceeds protocol bound")
        self.profiles = {}
        for raw in profiles["profiles"]:
            profile = ProfileSeed.model_validate(raw)
            if (
                profile.profile_id in self.profiles
                or profile.focus_concept_id not in self.graph.parents
            ):
                raise ValueError("Invalid profile identity/focus")
            if len(normalized_events(profile.events)) != len(profile.events):
                raise ValueError("Duplicate seed event")
            self.profiles[profile.profile_id] = profile
        if not 1 <= len(self.profiles) <= 4:
            raise ValueError("Profile count exceeds protocol bound")
        seen_seed_ids, seen_event_ids = set(), set()
        for profile in self.profiles.values():
            seed_key = (profile.seed_id, profile.seed_version)
            events = normalized_events(profile.events)
            ids = {e["event_id"] for e in events}
            if seed_key in seen_seed_ids or ids & seen_event_ids:
                raise ValueError("Duplicate seed/event identity across profiles")
            seen_seed_ids.add(seed_key)
            seen_event_ids.update(ids)
            replay(self.graph.order, self.activities, events, [], self.config)
        self.manifest = manifest

    def versions(self, profile_id: str) -> Versions:
        profile = self.profiles[profile_id]
        identity = self.manifest["identity"]
        return Versions(
            release_id=identity["release_id"],
            release_hash=self.manifest["release_hash"],
            graph_version=identity["graph_version"],
            catalog_version=identity["catalog_version"],
            model_version=identity["model_version"],
            seed_id=profile.seed_id,
            seed_version=profile.seed_version,
        )


def load_release(root: Path) -> Release:
    manifest = json.loads((root / "contracts/release-manifest.json").read_bytes())
    # Use fixed paths; never follow file paths from an unverified external manifest.
    paths = (
        "curriculum/graph.v1.json",
        "curriculum/catalog-slice.v1.json",
        "curriculum/model-config.v1.json",
        "curriculum/profiles.v1.json",
        "contracts/protocol-v1.schema.json",
    )
    return Release(manifest, {path: (root / path).read_bytes() for path in paths})
