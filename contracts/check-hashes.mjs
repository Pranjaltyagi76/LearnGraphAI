// Independent Node conformance check, not a browser validator or diagnosis engine.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

const fixture = JSON.parse(readFileSync(new URL("./fixtures/hash-vectors.json", import.meta.url), "utf8"));
function canonical(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    assert(Number.isSafeInteger(value), "Semantic numbers must be safe integers");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(",")}}`;
}
function normalize(raw) {
  const seen = new Map();
  for (const e of raw.events) {
    const value = {
      schema_version: e.schema_version,
      kind: e.kind,
      event_id: e.event_id.toLowerCase(),
      sequence_number: e.sequence_number,
      activity_id: e.activity_id,
      activity_version: e.activity_version,
      assessment_run_id: e.assessment_run_id.toLowerCase(),
      occurred_at: new Date(e.occurred_at).toISOString(),
      time_spent_seconds: e.time_spent_seconds ?? null,
    };
    if (e.kind === "response") {
      value.response = { option_id: e.response.option_id };
      value.hints_used = e.hints_used ?? null;
    } else assert.equal(e.kind, "lesson_completed");
    if (seen.has(value.event_id)) assert.equal(canonical(seen.get(value.event_id)), canonical(value));
    else seen.set(value.event_id, value);
  }
  const events = [...seen.values()];
  events.forEach((e, i) => {
    assert.equal(e.sequence_number, i + 1);
    if (i) assert(events[i - 1].occurred_at <= e.occurred_at);
  });
  return {
    contract_version: raw.contract_version,
    versions: raw.versions,
    profile_id: raw.profile_id,
    focus_concept_id: raw.focus_concept_id,
    trigger_event_id: raw.trigger_event_id?.toLowerCase() ?? null,
    events,
  };
}
for (const vector of fixture.vectors) {
  const text = canonical(normalize(vector.request));
  assert.equal(text, vector.canonical_utf8, `${vector.id}: canonical bytes`);
  assert.equal(createHash("sha256").update(text, "utf8").digest("hex"), vector.sha256, `${vector.id}: SHA-256`);
  const r = vector.request;
  const v = r.versions;
  const key = "learngraph:v1:" + JSON.stringify([r.profile_id, v.release_id, v.release_hash,
    v.seed_id, v.seed_version, v.graph_version, v.catalog_version, v.model_version]);
  assert.equal(key, vector.storage_key, `${vector.id}: storage key`);
}
const manifest = JSON.parse(readFileSync(new URL("./release-manifest.json", import.meta.url), "utf8"));
assert.equal(createHash("sha256").update(canonical(manifest.identity)).digest("hex"), manifest.release_hash);
for (const artifact of manifest.identity.artifacts) {
  const bytes = readFileSync(new URL(`../${artifact.path}`, import.meta.url));
  assert.equal(createHash("sha256").update(bytes).digest("hex"), artifact.sha256, artifact.path);
}
console.log(`Node verified ${fixture.vectors.length} canonical/hash/storage vectors and ${manifest.identity.artifacts.length} release artifacts.`);
