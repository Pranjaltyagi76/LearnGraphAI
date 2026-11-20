import { checkEventReferences, digest, normalized, parse, same, snapshot, storageKey } from "./protocol";
import type { AnalysisBundle, AnalyzeRequest, Event, SandboxRecord, SeedResponse } from "./protocol";

const MAX = Number.MAX_SAFE_INTEGER;
function sameStored(a: unknown, b: unknown, seen = new WeakMap<object, object>()): boolean {
  if (Object.is(a, b)) return true;
  if (!a || !b || typeof a !== "object" || typeof b !== "object") return false;
  if (seen.has(a)) return seen.get(a) === b;
  seen.set(a, b);
  if (a instanceof Date || b instanceof Date) return a instanceof Date && b instanceof Date && +a === +b;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  if (Array.isArray(a) && Array.isArray(b) && a.length !== b.length) return false;
  const plain = (v: object) => Array.isArray(v) || Object.getPrototypeOf(v) === Object.prototype || Object.getPrototypeOf(v) === null;
  if (!plain(a) || !plain(b)) return false;
  const left = Object.keys(a).sort(), right = Object.keys(b).sort();
  return left.length === right.length && left.every((key, i) => key === right[i] &&
    sameStored((a as Record<string, unknown>)[key], (b as Record<string, unknown>)[key], seen));
}
function fit(record: SandboxRecord): SandboxRecord {
  const next = structuredClone(record);
  if (new TextEncoder().encode(JSON.stringify(next)).length > 1048576) {
    next.last_analysis = null; next.analysis_input_revision = null; next.analysis_history_digest = null;
  }
  if (new TextEncoder().encode(JSON.stringify(next)).length > 1048576) throw new SandboxError("event_limit");
  return next;
}
export class SandboxError extends Error {
  constructor(public code: "storage_unavailable" | "storage_blocked" | "corrupt_record" | "tab_conflict" | "event_limit" | "revision_limit") {
    super(code);
  }
}
export function initial(seed: SeedResponse, persistence: "indexeddb" | "session"): SandboxRecord {
  return { schema_version: 1, key: storageKey(seed.profile.id, seed.versions), versions: seed.versions,
    profile_id: seed.profile.id, sandbox_id: crypto.randomUUID(), revision: 0, persistence,
    acknowledged_events: [], pending: null, last_analysis: null,
    analysis_input_revision: null, analysis_history_digest: null };
}

export async function verifyBundle(value: unknown, request: AnalyzeRequest, seed: SeedResponse): Promise<AnalysisBundle> {
  const b = parse<AnalysisBundle>("AnalysisBundle", value);
  if (!same(b.versions, request.versions) || b.profile_id !== request.profile_id ||
      b.sandbox_id !== request.sandbox_id || b.local_revision !== request.local_revision ||
      b.focus_concept_id !== request.focus_concept_id ||
      b.requested_trigger_event_id !== (request.trigger_event_id ?? null) ||
      b.accepted_visitor_events !== normalized(request.events).length || b.history_digest !== await digest(request)) {
    throw new Error("response_mismatch");
  }
  const events = [...seed.seed_events, ...normalized(request.events)];
  if (b.graded_events.length !== events.length || b.graded_events.some((g, i) =>
      g.event_id !== events[i].event_id || g.activity_id !== events[i].activity_id ||
      g.activity_version !== events[i].activity_version || g.kind !== events[i].kind ||
      g.concept_id !== seed.activities.find((a) => a.id === g.activity_id)?.primary_concept_id ||
      g.provenance !== (i < seed.seed_events.length ? "canonical_seed" : "visitor_demo"))) {
    throw new Error("response_mismatch");
  }
  if (new Set(b.estimates.map((e) => e.concept_id)).size !== 12 ||
      b.estimates.some((e) => !seed.concepts.some((c) => c.id === e.concept_id))) throw new Error("response_mismatch");
  for (const item of b.plan.items) {
    const a = seed.activities.find((a) => a.id === item.activity_id);
    if (!a || a.version !== item.activity_version || a.primary_concept_id !== item.concept_id ||
        a.role !== item.role) throw new Error("response_mismatch");
  }
  return b;
}

export async function validateRecord(value: unknown, seed: SeedResponse): Promise<SandboxRecord> {
  try {
    const record = parse<SandboxRecord>("SandboxRecord", value);
    if (new TextEncoder().encode(JSON.stringify(record)).length > 1048576 ||
        !same(record.versions, seed.versions) || record.profile_id !== seed.profile.id ||
        record.key !== storageKey(seed.profile.id, seed.versions) ||
        record.acknowledged_events.length + Number(record.pending !== null) > 200) throw new Error();
    const acknowledged = normalized(record.acknowledged_events);
    if (acknowledged.length !== record.acknowledged_events.length ||
        !same(acknowledged, record.acknowledged_events)) throw new Error();
    checkEventReferences(acknowledged, seed);
    if (record.pending) {
      const p = record.pending;
      checkEventReferences([p.event], seed);
      if (p.request_revision !== record.revision || p.event.sequence_number !== acknowledged.length + 1 ||
          acknowledged.some((e) => e.event_id === p.event.event_id) ||
          (acknowledged.length > 0 && p.event.occurred_at < acknowledged.at(-1)!.occurred_at) ||
          !seed.concepts.some((c) => c.id === p.focus_concept_id)) throw new Error();
    }
    const events = [...acknowledged, ...(record.pending ? [record.pending.event] : [])];
    if (!same(normalized(events), events)) throw new Error();
    const lower = seed.seed_events.at(-1)?.occurred_at ?? "0001-01-01T00:00:00.000Z";
    if (events.some((e) => e.occurred_at <= lower || e.occurred_at !== new Date(e.occurred_at).toISOString())) throw new Error();
    if (record.last_analysis) {
      const bundle = record.last_analysis;
      if (bundle.local_revision !== record.analysis_input_revision || bundle.local_revision > record.revision ||
          record.analysis_history_digest !== bundle.history_digest) throw new Error();
      const request: AnalyzeRequest = { ...snapshot(record, bundle.focus_concept_id),
        events: acknowledged, local_revision: bundle.local_revision,
        trigger_event_id: bundle.requested_trigger_event_id, focus_concept_id: bundle.focus_concept_id };
      await verifyBundle(bundle, request, seed);
    } else if (record.analysis_input_revision !== null || record.analysis_history_digest !== null) throw new Error();
    return record;
  } catch { throw new SandboxError("corrupt_record"); }
}

export type Loaded = { record: SandboxRecord; raw?: never } | { record: null; raw: unknown };
export class SandboxStore {
  private db: IDBDatabase | null = null;
  private memory = new Map<string, SandboxRecord>();
  private channel: BroadcastChannel | null = null;
  constructor(public mode: "indexeddb" | "session" = "indexeddb") {
    try { if (mode === "indexeddb" && typeof BroadcastChannel !== "undefined") this.channel = new BroadcastChannel("learngraph-v1"); }
    catch { /* Notifications are advisory; storage transactions remain authoritative. */ }
  }
  subscribe(callback: (key: string) => void): () => void {
    const handler = (e: MessageEvent) => {
      if (e.data && typeof e.data.key === "string") callback(e.data.key);
    };
    this.channel?.addEventListener("message", handler);
    return () => this.channel?.removeEventListener("message", handler);
  }
  close() { this.db?.close(); this.db = null; this.channel?.close(); }
  private open(): Promise<IDBDatabase> {
    if (this.db) return Promise.resolve(this.db);
    return new Promise((resolve, reject) => {
      let settled = false;
      const timer = setTimeout(() => fail("storage_blocked"), 3000);
      const fail = (code: "storage_unavailable" | "storage_blocked") => { clearTimeout(timer); settled = true; reject(new SandboxError(code)); };
      try {
        const request = indexedDB.open("learngraph-ai-v1", 1);
        request.onupgradeneeded = () => request.result.createObjectStore("sandboxes", { keyPath: "key" });
        request.onerror = () => fail("storage_unavailable");
        request.onblocked = () => fail("storage_blocked");
        request.onsuccess = () => {
          clearTimeout(timer);
          if (settled) { request.result.close(); return; }
          this.db = request.result;
          this.db.onversionchange = () => { this.db?.close(); this.db = null; };
          resolve(this.db);
        };
      } catch { fail("storage_unavailable"); }
    });
  }
  private async raw(key: string): Promise<unknown> {
    if (this.mode === "session") return structuredClone(this.memory.get(key));
    const db = await this.open();
    return new Promise((resolve, reject) => {
      try {
        const tx = db.transaction("sandboxes", "readonly");
        const req = tx.objectStore("sandboxes").get(key);
        tx.oncomplete = () => resolve(req.result);
        tx.onerror = tx.onabort = () => reject(new SandboxError("storage_unavailable"));
      } catch { reject(new SandboxError("storage_unavailable")); }
    });
  }
  async load(seed: SeedResponse): Promise<Loaded> {
    const key = storageKey(seed.profile.id, seed.versions);
    let raw = await this.raw(key);
    if (raw === undefined) {
      const fresh = initial(seed, this.mode);
      try { await this.replace(undefined, fresh); raw = fresh; }
      catch (e) { if (!(e instanceof SandboxError) || e.code !== "tab_conflict") throw e; raw = await this.raw(key); }
    }
    try {
      const record = await validateRecord(raw, seed);
      if (record.persistence !== this.mode) throw new Error("Persistence mismatch");
      return { record };
    }
    catch { return { record: null, raw }; }
  }
  private async replace(expected: unknown, next: SandboxRecord): Promise<SandboxRecord> {
    const safe = fit(next);
    // Every async preparation finishes BEFORE opening the transaction.
    if (this.mode === "session") {
      if (!sameStored(this.memory.get(safe.key), expected)) throw new SandboxError("tab_conflict");
      this.memory.set(safe.key, safe); return structuredClone(safe);
    }
    const db = await this.open();
    await new Promise<void>((resolve, reject) => {
      let conflict = false;
      try {
        const tx = db.transaction("sandboxes", "readwrite");
        const store = tx.objectStore("sandboxes");
        const req = store.get(safe.key);
        req.onsuccess = () => {
          // Compare the observed record as well as UUID/revision/pending to reject stale caches.
          if (!sameStored(req.result, expected)) { conflict = true; tx.abort(); return; }
          try { store.put(safe); }
          catch { try { tx.abort(); } catch { /* Already aborted. */ } }
        };
        tx.oncomplete = () => resolve();
        tx.onerror = tx.onabort = () => reject(new SandboxError(conflict ? "tab_conflict" : "storage_unavailable"));
      } catch { reject(new SandboxError("storage_unavailable")); }
    });
    this.channel?.postMessage({ key: safe.key, sandbox_id: safe.sandbox_id, revision: safe.revision });
    return safe;
  }
  async stage(record: SandboxRecord, event: Event, focus: string, seed: SeedResponse): Promise<SandboxRecord> {
    if (record.pending) throw new SandboxError("tab_conflict");
    if (record.acknowledged_events.length >= 200) throw new SandboxError("event_limit");
    if (record.revision === MAX) throw new SandboxError("revision_limit");
    const revision = record.revision + 1;
    const next = fit({ ...record, revision, pending: { event, focus_concept_id: focus,
      trigger_event_id: null, request_revision: revision } });
    await validateRecord(next, seed);
    return this.replace(record, next);
  }
  async acknowledge(record: SandboxRecord, request: AnalyzeRequest, value: unknown, seed: SeedResponse): Promise<SandboxRecord> {
    const bundle = await verifyBundle(value, request, seed);
    if (request.local_revision !== record.revision || request.sandbox_id !== record.sandbox_id ||
        !same(request, snapshot(record, request.focus_concept_id, request.trigger_event_id ?? null))) throw new SandboxError("tab_conflict");
    if (record.pending && record.revision === MAX) throw new SandboxError("revision_limit");
    const next: SandboxRecord = fit({ ...record,
      acknowledged_events: request.events, pending: null,
      revision: record.revision + Number(record.pending !== null),
      last_analysis: bundle, analysis_input_revision: request.local_revision,
      analysis_history_digest: bundle.history_digest });
    await validateRecord(next, seed);
    return this.replace(record, next);
  }
  async reset(record: SandboxRecord, seed: SeedResponse): Promise<SandboxRecord> {
    const next = initial(seed, this.mode);
    next.revision = record.revision === MAX ? 0 : record.revision + 1;
    return this.replace(record, next);
  }
  async resetCorrupt(raw: unknown, seed: SeedResponse): Promise<SandboxRecord> {
    return this.replace(raw, initial(seed, this.mode));
  }
  async discard(record: SandboxRecord): Promise<SandboxRecord> {
    if (record.revision === MAX) throw new SandboxError("revision_limit");
    return this.replace(record, { ...record, pending: null, revision: record.revision + 1 });
  }
}
