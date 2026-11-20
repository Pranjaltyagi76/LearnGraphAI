import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, test } from "@playwright/test";
import type { AnalyzeRequest, Event } from "../lib/protocol";
import { injectStore, seedFixture } from "./sandbox-helper";

test("browser canonicalization matches all independent frozen hash vectors", async ({ page }) => {
  const vectors = JSON.parse(readFileSync(resolve(process.cwd(), "../contracts/fixtures/hash-vectors.json"), "utf8")).vectors as {request: AnalyzeRequest; sha256: string; storage_key: string}[];
  await page.goto("/"); await injectStore(page);
  const results = await page.evaluate(async (items) => Promise.all(items.map(async (v) => ({
    hash: await window.sandboxTest.digest(v.request),
    key: window.sandboxTest.storageKey(v.request.profile_id, v.request.versions),
  }))), vectors);
  results.forEach((r, i) => { expect(r.hash).toBe(vectors[i].sha256); expect(r.key).toBe(vectors[i].storage_key); });
});

test("two actual tabs cannot stage from the same observed revision, without BroadcastChannel", async ({ page, context, request }) => {
  const seed = await seedFixture(request);
  await context.addInitScript(() => { Object.defineProperty(window, "BroadcastChannel", { value: undefined }); });
  const other = await context.newPage();
  await Promise.all([page.goto("/"), other.goto("/")]);
  await Promise.all([injectStore(page), injectStore(other)]);
  const original = await page.evaluate(async (seed) => (await new window.sandboxTest.SandboxStore().load(seed)).record!, seed);
  const make = (id: string): Event => ({ schema_version: 1, kind: "response", event_id: id, sequence_number: 1,
    activity_id: "base_cases_practice_03", activity_version: 2,
    assessment_run_id: "45db2dd4-73e8-5c97-8cc5-59ed346c941e", occurred_at: "2026-11-20T12:00:00.000Z",
    time_spent_seconds: null, response: { option_id: "c" }, hints_used: 0 });
  const outcomes = await Promise.all([page, other].map((tab, i) => tab.evaluate(async ({ seed, original, event }) => {
    try { await new window.sandboxTest.SandboxStore().stage(original, event, "base_cases", seed); return "staged"; }
    catch (e) { return (e as Error).message; }
  }, { seed, original, event: make(i ? "08a99c55-d3c9-47d6-94ef-e263ab6185c9" : "014454e7-c64d-46ed-bc03-8df06ff426ee") })));
  expect(outcomes.sort()).toEqual(["staged", "tab_conflict"]);
});

test("corrupt cache is preserved and requires explicit compare-and-swap reset", async ({ page, request }) => {
  const seed = await seedFixture(request);
  await page.goto("/"); await injectStore(page);
  const results = await page.evaluate(async (seed) => {
    const store = new window.sandboxTest.SandboxStore();
    const initial = (await store.load(seed)).record!;
    const raw = { ...initial, revision: "corrupt" };
    const db = await new Promise<IDBDatabase>((resolve) => { const req = indexedDB.open("learngraph-ai-v1", 1); req.onsuccess = () => resolve(req.result); });
    await new Promise<void>((resolve) => { const tx = db.transaction("sandboxes", "readwrite"); tx.objectStore("sandboxes").put(raw); tx.oncomplete = () => resolve(); });
    const loaded = await store.load(seed);
    const persisted = await new Promise<unknown>((resolve) => { const req = db.transaction("sandboxes").objectStore("sandboxes").get(initial.key); req.onsuccess = () => resolve(req.result); });
    const reset = await store.resetCorrupt(loaded.raw, seed);
    db.close(); store.close();
    return { corrupt: loaded.record === null, preserved: (persisted as {revision: unknown}).revision,
      newGeneration: reset.sandbox_id !== initial.sandbox_id, events: reset.acknowledged_events.length };
  }, seed);
  expect(results).toEqual({ corrupt: true, preserved: "corrupt", newGeneration: true, events: 0 });
});

test("aborted write never commits a pending response", async ({ page, request }) => {
  const seed = await seedFixture(request);
  await page.goto("/"); await injectStore(page);
  const result = await page.evaluate(async (seed) => {
    const store = new window.sandboxTest.SandboxStore();
    const initial = (await store.load(seed)).record!;
    const original = IDBObjectStore.prototype.put;
    IDBObjectStore.prototype.put = function () { this.transaction.abort(); throw new DOMException("Test failure", "QuotaExceededError"); };
    let failure = "";
    try {
      await store.stage(initial, { schema_version: 1, kind: "response", event_id: crypto.randomUUID(), sequence_number: 1,
        activity_id: "base_cases_practice_03", activity_version: 2, assessment_run_id: crypto.randomUUID(),
        occurred_at: "2026-11-20T12:00:00.000Z", time_spent_seconds: null, hints_used: 0, response: { option_id: "c" } }, "base_cases", seed);
    } catch (e) { failure = (e as Error).message; }
    finally { IDBObjectStore.prototype.put = original; }
    const loaded = (await store.load(seed)).record!;
    store.close(); return { failure, revision: loaded.revision, pending: loaded.pending };
  }, seed);
  expect(result).toEqual({ failure: "storage_unavailable", revision: 0, pending: null });
});

test("versionchange releases the connection for an actual database upgrade", async ({ page, request }) => {
  const seed = await seedFixture(request);
  await page.goto("/"); await injectStore(page);
  const closed = await page.evaluate(async (seed) => {
    const store = new window.sandboxTest.SandboxStore(); await store.load(seed);
    await new Promise<void>((resolve, reject) => {
      const req = indexedDB.open("learngraph-ai-v1", 2);
      req.onsuccess = () => { req.result.close(); resolve(); }; req.onerror = () => reject(req.error);
      req.onblocked = () => reject(new Error("Connection did not close"));
    });
    store.close(); return true;
  }, seed);
  expect(closed).toBe(true);
});

test("blocked database queue is bounded and offers recovery", async ({ page, request }) => {
  const seed = await seedFixture(request);
  await page.goto("/"); await injectStore(page);
  const result = await page.evaluate(async (seed) => {
    const held = await new Promise<IDBDatabase>((resolve) => {
      const req = indexedDB.open("learngraph-ai-v1", 1);
      req.onupgradeneeded = () => req.result.createObjectStore("sandboxes", { keyPath: "key" });
      req.onsuccess = () => resolve(req.result);
    });
    const deletion = indexedDB.deleteDatabase("learngraph-ai-v1");
    await new Promise<void>((resolve) => { deletion.onblocked = () => resolve(); });
    const store = new window.sandboxTest.SandboxStore();
    let result = "";
    try { await store.load(seed); } catch (e) { result = (e as Error).message; }
    held.close(); store.close(); return result;
  }, seed);
  expect(result).toBe("storage_blocked");
});

test("duplicate acknowledgements append once and a tampered cache digest is rejected", async ({ page, request }) => {
  const seed = await seedFixture(request);
  await page.goto("/"); await injectStore(page);
  const staged = await page.evaluate(async (seed) => {
    const store = new window.sandboxTest.SandboxStore();
    const old = (await store.load(seed)).record!;
    const result = await store.stage(old, { schema_version: 1, kind: "response", event_id: crypto.randomUUID(),
      sequence_number: 1, activity_id: "base_cases_practice_03", activity_version: 2,
      assessment_run_id: crypto.randomUUID(), occurred_at: new Date().toISOString(),
      time_spent_seconds: null, hints_used: 0, response: { option_id: "c" } }, "base_cases", seed);
    store.close(); return { record: result, request: window.sandboxTest.snapshot(result, "base_cases") };
  }, seed);
  const response = await request.post("http://127.0.0.1:8000/api/v1/demo/analyze", { data: staged.request });
  expect(response.ok()).toBe(true);
  const result = await page.evaluate(async ({ seed, staged, bundle }) => {
    const store = new window.sandboxTest.SandboxStore();
    const accepted = await store.acknowledge(staged.record, staged.request, bundle, seed);
    let duplicate = "", corrupt = "";
    try { await store.acknowledge(staged.record, staged.request, bundle, seed); }
    catch (e) { duplicate = (e as Error).message; }
    const tampered = structuredClone(accepted);
    tampered.analysis_history_digest = "0".repeat(64);
    tampered.last_analysis!.history_digest = "0".repeat(64);
    try { await window.sandboxTest.validateRecord(tampered, seed); }
    catch (e) { corrupt = (e as Error).message; }
    store.close(); return { duplicate, corrupt, events: accepted.acknowledged_events.length };
  }, { seed, staged, bundle: await response.json() });
  expect(result).toEqual({ duplicate: "tab_conflict", corrupt: "corrupt_record", events: 1 });
});

test("revisions never wrap and reset changes generation at the safe-integer limit", async ({ page, request }) => {
  const seed = await seedFixture(request);
  await page.goto("/"); await injectStore(page);
  const result = await page.evaluate(async (seed) => {
    const store = new window.sandboxTest.SandboxStore();
    const old = (await store.load(seed)).record!;
    old.revision = Number.MAX_SAFE_INTEGER;
    const db = await new Promise<IDBDatabase>((resolve) => { const req = indexedDB.open("learngraph-ai-v1", 1); req.onsuccess = () => resolve(req.result); });
    await new Promise<void>((resolve) => { const tx = db.transaction("sandboxes", "readwrite"); tx.objectStore("sandboxes").put(old); tx.oncomplete = () => resolve(); });
    let failure = "";
    try { await store.discard(old); } catch (e) { failure = (e as Error).message; }
    const reset = await store.reset(old, seed);
    store.close(); db.close(); return { failure, revision: reset.revision, changed: reset.sandbox_id !== old.sandbox_id };
  }, seed);
  expect(result).toEqual({ failure: "revision_limit", revision: 0, changed: true });
});

test("versioned keys preserve incompatible history instead of migrating it", async ({ page, request }) => {
  const seed = await seedFixture(request);
  await page.goto("/"); await injectStore(page);
  const result = await page.evaluate(async (seed) => {
    const store = new window.sandboxTest.SandboxStore();
    const current = (await store.load(seed)).record!;
    const oldSeed = structuredClone(seed);
    oldSeed.versions.release_id = "fixture-old-release";
    oldSeed.versions.release_hash = "0".repeat(64);
    const old = (await store.load(oldSeed)).record!;
    await store.stage(current, { schema_version: 1, kind: "response", event_id: crypto.randomUUID(), sequence_number: 1,
      activity_id: "base_cases_practice_03", activity_version: 2, assessment_run_id: crypto.randomUUID(),
      occurred_at: "2026-11-20T12:00:00.000Z", hints_used: 0, time_spent_seconds: null, response: { option_id: "c" } }, "base_cases", seed);
    const preserved = (await store.load(oldSeed)).record!;
    store.close(); return { keysDiffer: current.key !== old.key, oldUnchanged: preserved.sandbox_id === old.sandbox_id,
      oldPending: preserved.pending, oldEvents: preserved.acknowledged_events.length };
  }, seed);
  expect(result).toEqual({ keysDiffer: true, oldUnchanged: true, oldPending: null, oldEvents: 0 });
});
