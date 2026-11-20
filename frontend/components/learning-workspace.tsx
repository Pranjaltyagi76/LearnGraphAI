"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, APIError } from "@/lib/api";
import { same, snapshot } from "@/lib/protocol";
import type { Event, ProfileSummary, SandboxRecord, SeedResponse } from "@/lib/protocol";
import { SandboxError, SandboxStore } from "@/lib/sandbox";
import { label, LearningEvidence } from "./learning-evidence";

const messages: Record<string, string> = {
  storage_unavailable: "Browser storage could not commit this change. No unstored response was sent. You can continue in this tab only.",
  storage_blocked: "Storage is blocked by another open tab. Close older LearnGraph tabs and reload, or continue in this tab only.",
  corrupt_record: "This saved record is invalid. It has been preserved. Export or explicitly reset it before continuing.",
  tab_conflict: "Progress was updated in another tab. Reload the local state before taking another action.",
  event_limit: "This sandbox has reached its history limit. Export or reset local progress to continue.",
  revision_limit: "The revision limit was reached. An explicit reset creates a new sandbox generation.",
  quota_exhausted: "The free demo request limit was reached. Your pending response is preserved. Retry after the displayed wait.",
  version_mismatch: "The pinned release is no longer supported. Your local record is preserved. Start a new supported release from the demo entry.",
  event_conflict: "A response identity conflicts with this history. Keep/export it or discard the pending response and submit a new one.",
  invalid_timestamp: "The device clock is outside the allowed window. Correct the device clock; discard and recreate the pending response if needed.",
  invalid_order: "History order is invalid. Export or reset this sandbox; the service did not accept a partial history.",
  response_mismatch: "The returned analysis did not match this request. Your pending response remains unaccepted.",
};

export function LearningWorkspace() {
  const [profiles, setProfiles] = useState<ProfileSummary[]>([]);
  const [seed, setSeed] = useState<SeedResponse | null>(null);
  const [record, setRecord] = useState<SandboxRecord | null>(null);
  const [corrupt, setCorrupt] = useState<{ raw: unknown } | null>(null);
  const [focus, setFocus] = useState("base_cases");
  const [selected, setSelected] = useState("");
  const [opened, setOpened] = useState("");
  const [notice, setNotice] = useState("");
  const [storageProblem, setStorageProblem] = useState(false);
  const [busy, setBusy] = useState(true);
  const [live, setLive] = useState(false);
  const [confirmReset, setConfirmReset] = useState(false);
  const [retryAt, setRetryAt] = useState(0);
  const [retryBlocked, setRetryBlocked] = useState(false);
  const store = useRef<SandboxStore | null>(null);
  const epoch = useRef(0);
  const flight = useRef(false);
  const controller = useRef<AbortController | null>(null);
  const bundle = record?.last_analysis ?? null;
  const cancel = useCallback(() => {
    ++epoch.current; controller.current?.abort(); flight.current = false;
  }, []);

  function errorMessage(error: unknown) {
    const code = error instanceof SandboxError || error instanceof APIError ? error.code :
      error instanceof Error ? error.message : "dependency_unavailable";
    setNotice(messages[code] ?? "The live service is unavailable or returned invalid data. No new response has been accepted. Saved/pending progress is preserved; retry manually.");
    if (["storage_unavailable", "storage_blocked"].includes(code)) setStorageProblem(true);
    if (error instanceof APIError) setRetryAt(Date.now() + error.retryAfter * 1000);
    else setRetryAt(Date.now() + 1000);
    setRetryBlocked(true);
  }
  useEffect(() => {
    if (!retryBlocked) return;
    const timer = setTimeout(() => setRetryBlocked(false), Math.max(0, retryAt - Date.now()));
    return () => clearTimeout(timer);
  }, [retryAt, retryBlocked]);

  const chooseProfile = useCallback(async (profile: ProfileSummary) => {
    const current = ++epoch.current;
    controller.current?.abort(); flight.current = false;
    const active = new AbortController(); controller.current = active;
    setBusy(true); setLive(false); setRecord(null); setSeed(null); setCorrupt(null);
    setNotice(""); setOpened(""); setSelected(""); setStorageProblem(false); setConfirmReset(false);
    try {
      const data = await api.seed(profile.versions.release_id, profile.id, active.signal);
      if (current !== epoch.current) return;
      if (!same(data.versions, profile.versions) || data.profile.id !== profile.id) throw new Error("response_mismatch");
      setSeed(data); setFocus(data.profile.focus_concept_id);
      const loaded = await store.current!.load(data);
      if (current !== epoch.current) return;
      if (loaded.record) setRecord(loaded.record); else { setCorrupt({ raw: loaded.raw }); setNotice(messages.corrupt_record); }
      const url = new URL(window.location.href); url.searchParams.set("profile", profile.id);
      window.history.replaceState(null, "", url);
    } catch (e) { if (current === epoch.current) errorMessage(e); }
    finally { if (current === epoch.current) setBusy(false); }
  }, []);

  const connect = useCallback(async () => {
    const current = ++epoch.current;
    controller.current?.abort();
    const active = new AbortController(); controller.current = active;
    try {
      const release = await api.release(active.signal);
      const list = await api.profiles(release.release_id, active.signal);
      if (current !== epoch.current) return;
      if (list.profiles.some((p) => p.versions.release_id !== release.release_id ||
          p.versions.release_hash !== release.release_hash || p.versions.graph_version !== release.graph_version ||
          p.versions.catalog_version !== release.catalog_version || p.versions.model_version !== release.model_version)) throw new Error("response_mismatch");
      setProfiles(list.profiles);
      const wanted = new URL(window.location.href).searchParams.get("profile");
      await chooseProfile(list.profiles.find((p) => p.id === wanted) ?? list.profiles.find((p) => p.id === "demo_base_cases") ?? list.profiles[0]);
    } catch (e) { if (current === epoch.current) { errorMessage(e); setBusy(false); } }
  }, [chooseProfile]);

  useEffect(() => {
    const activeStore = new SandboxStore();
    store.current = activeStore;
    let disposed = false;
    // The discarded Strict Mode setup must not initiate a network request.
    queueMicrotask(() => { if (!disposed) void connect(); });
    return () => { disposed = true; cancel(); activeStore.close(); };
  }, [connect, cancel]);

  const reloadLocal = useCallback(async () => {
    if (!seed || !record || !store.current) return;
    const current = epoch.current;
    try {
      const loaded = await store.current.load(seed);
      if (current !== epoch.current) return;
      if (!loaded.record) { setCorrupt({ raw: loaded.raw }); setRecord(null); setNotice(messages.corrupt_record); return; }
      if (!same(loaded.record, record)) {
        ++epoch.current; controller.current?.abort(); flight.current = false;
        setRecord(loaded.record); setLive(false); setBusy(false); setSelected(""); setOpened("");
        setNotice("Progress was updated in another tab. The current local state is loaded; recheck live analysis or retry its pending response.");
      }
    } catch (e) { if (current === epoch.current) errorMessage(e); }
  }, [record, seed]);
  useEffect(() => {
    const unsubscribe = store.current?.subscribe((key) => { if (key === record?.key) void reloadLocal(); });
    const visibility = () => { if (document.visibilityState === "visible") void reloadLocal(); };
    window.addEventListener("focus", reloadLocal); document.addEventListener("visibilitychange", visibility);
    return () => { unsubscribe?.(); window.removeEventListener("focus", reloadLocal); document.removeEventListener("visibilitychange", visibility); };
  }, [record?.key, reloadLocal]);

  async function send(observed: SandboxRecord) {
    if (!seed || flight.current || !store.current) return;
    flight.current = true; setBusy(true); setLive(false); setNotice("");
    const current = epoch.current;
    const active = new AbortController(); controller.current = active;
    try {
      const request = snapshot(observed, focus);
      const value = await api.analyze(request, active.signal);
      if (current !== epoch.current) return;
      const accepted = await store.current.acknowledge(observed, request, value, seed);
      if (current !== epoch.current) return;
      setRecord(accepted); setLive(true); setSelected(""); setOpened(""); setRetryBlocked(false);
    } catch (e) { if (current === epoch.current) errorMessage(e); }
    finally { if (current === epoch.current) { flight.current = false; setBusy(false); } }
  }

  async function submit(activityId: string, option?: string) {
    if (!seed || !record || !live || busy || flight.current || record.pending || !store.current) return;
    const activity = seed.activities.find((a) => a.id === activityId);
    const item = bundle?.plan.items.find((i) => i.activity_id === activityId && i.readiness === "ready");
    if (!activity || !item) return;
    const now = new Date().toISOString();
    if (now <= (seed.seed_events.at(-1)?.occurred_at ?? "") || now < (record.acknowledged_events.at(-1)?.occurred_at ?? "")) {
      errorMessage(new APIError("invalid_timestamp")); return;
    }
    const previous = record.acknowledged_events.at(-1);
    const previousActivity = seed.activities.find((a) => a.id === previous?.activity_id);
    const run = previous && previousActivity?.role !== "reassessment" ? previous.assessment_run_id : crypto.randomUUID();
    const common = { schema_version: 1 as const, event_id: crypto.randomUUID(),
      sequence_number: record.acknowledged_events.length + 1, activity_id: activity.id,
      activity_version: activity.version, assessment_run_id: run, occurred_at: now, time_spent_seconds: null };
    const event: Event = activity.kind === "lesson" ? { ...common, kind: "lesson_completed" } :
      { ...common, kind: "response", response: { option_id: option! }, hints_used: 0 };
    const current = epoch.current;
    flight.current = true; setBusy(true); setLive(false);
    try {
      const staged = await store.current.stage(record, event, focus, seed);
      if (current !== epoch.current) return;
      setRecord(staged); flight.current = false;
      await send(staged);
    } catch (e) { if (current === epoch.current) { errorMessage(e); flight.current = false; setBusy(false); } }
  }

  async function reset() {
    if (!seed || !store.current) return;
    const current = ++epoch.current; controller.current?.abort(); flight.current = false;
    setBusy(true); setConfirmReset(false); setLive(false);
    try {
      const next = record ? await store.current.reset(record, seed) : await store.current.resetCorrupt(corrupt?.raw, seed);
      if (current !== epoch.current) return;
      setRecord(next); setCorrupt(null); setSelected(""); setOpened(""); setNotice("Local progress reset. The canonical synthetic seed is unchanged. Analyze this learner to begin again.");
    } catch (e) { if (current === epoch.current) errorMessage(e); }
    finally { if (current === epoch.current) setBusy(false); }
  }
  async function discard() {
    if (!record || !store.current) return;
    const current = ++epoch.current; controller.current?.abort(); flight.current = false;
    try {
      const next = await store.current.discard(record);
      if (current !== epoch.current) return;
      setRecord(next); setLive(false); setBusy(false); setNotice("Only the pending response was discarded. Recheck the acknowledged history before continuing.");
    } catch (e) { if (current === epoch.current) errorMessage(e); }
  }
  async function sessionOnly() {
    if (!seed) return;
    const current = ++epoch.current; controller.current?.abort(); flight.current = false;
    store.current?.close(); store.current = new SandboxStore("session");
    const loaded = await store.current.load(seed);
    if (current !== epoch.current) return;
    setRecord(loaded.record); setCorrupt(null); setStorageProblem(false); setLive(false); setBusy(false);
    setNotice("Session-only mode: this separate sandbox lasts only in this tab. The stored record was not overwritten.");
  }
  function download() {
    try {
      const blob = new Blob([JSON.stringify(corrupt ? corrupt.raw : record, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url;
      a.download = "learngraph-synthetic-progress.json"; a.click(); URL.revokeObjectURL(url);
    } catch { setNotice("This corrupt record cannot be exported as JSON. It is preserved until you explicitly reset it."); }
  }

  const available = bundle?.plan.items.filter((i) => i.readiness === "ready") ?? [];
  const item = available.find((i) => i.activity_id === opened) ?? available.find((i) => i.role !== "lesson") ?? available[0];
  const activity = seed?.activities.find((a) => a.id === item?.activity_id);
  const last = record?.acknowledged_events.at(-1);
  const feedback = bundle?.graded_events.find((g) => g.event_id === last?.event_id);
  const acceptedReassessment = feedback?.catalog_role === "reassessment" && feedback.attempt_number === 1;
  return <main className="learn-shell">
    <header className="learn-header"><Link href="/" className="brand">LearnGraph <span className="brand-ai">AI</span></Link>
      <span className="state-pill">Synthetic learners · no account</span></header>
    <div className="learn-intro"><p className="eyebrow">FOLLOW THE EVIDENCE</p><h1>A clearer next step.</h1>
      <p>Explore a learner, inspect a hypothesis, and try fresh practice. Progress stays in this browser.</p></div>
    {notice && <div className="learn-notice" role="alert">{notice}{retryBlocked && <p>Retry available after {new Date(retryAt).toLocaleTimeString()}.</p>}</div>}
    {profiles.length === 0 && !busy && <section className="learn-panel"><p className="state-pill">Prerecorded example · synthetic</p>
      <h2>Base cases: a starting hypothesis</h2><p>Recorded 20 November 2026. Mira has 0/3 eligible base-case responses correct and 3/3 function-call responses correct. This example was not submitted to a live service.</p>
      <button className="learn-primary" onClick={() => { setBusy(true); setNotice(""); void connect(); }}>Reconnect live demo</button></section>}
    {profiles.length > 0 && <section className="profile-picker" aria-label="Synthetic learners">
      {profiles.map((p) => <button key={p.id} aria-pressed={seed?.profile.id === p.id} onClick={() => void chooseProfile(p)}>
        <span className="profile-avatar">{p.name[0]}</span><strong>{p.name}</strong><span>{label(p.archetype)}</span>
      </button>)}
    </section>}
    {seed && <>
      <div className="workspace-toolbar"><div><strong>{seed.profile.name}&apos;s sandbox</strong><p className="learn-muted">{seed.profile.summary}</p></div>
        <div className="toolbar-actions"><label>Focus concept <select aria-label="Focus concept" value={focus} disabled={busy || !!record?.pending}
          onChange={(e) => { setFocus(e.target.value); setLive(false); setOpened(""); }}>
          {seed.concepts.map((c) => <option key={c.id} value={c.id}>{label(c.id)}</option>)}</select></label>
          {(record || corrupt) && <button onClick={() => setConfirmReset(true)}>Reset local progress</button>}
          {(record || corrupt) && <button onClick={download}>Export local record</button>}
        </div></div>
      {confirmReset && <div className="learn-notice" role="region" aria-label="Confirm local reset"><strong>Reset this sandbox?</strong><p>This removes only your local changes. Other browsers and canonical seeds are unaffected.</p><button onClick={() => void reset()}>Confirm reset</button><button onClick={() => setConfirmReset(false)}>Cancel</button></div>}
      {storageProblem && <button className="learn-primary" onClick={() => void sessionOnly()}>Continue in this tab only</button>}
      {record && <>
        <div className="sandbox-status"><span>{record.persistence === "session" ? "Session-only · no refresh recovery" : "Browser-local · IndexedDB"}</span>
          <span>{record.acknowledged_events.length} accepted local events · revision {record.revision}</span>
          <span>{live ? "Live analysis · server-graded" : bundle ? "Saved analysis · recheck before continuing" : "Ready to analyze"}</span></div>
        {record.pending ? <section className="pending-panel" aria-labelledby="pending-title"><h2 id="pending-title">Response pending — not accepted</h2>
          <p>{label(record.pending.event.activity_id)}. The exact saved submission will be retried, including its original focus and event ID.</p>
          <button className="learn-primary" disabled={busy || retryBlocked} onClick={() => void send(record)}>Retry pending response</button>
          <button disabled={busy} onClick={() => void discard()}>Discard pending response</button>
        </section> : !live && <button className="learn-primary" disabled={busy || retryBlocked} onClick={() => void send(record)}>
          {busy ? "Analyzing…" : bundle ? "Recheck live analysis" : "Analyze this learner"}</button>}
        {bundle && <div className="learning-grid"><div className="learning-main">
          <section className="learn-panel question-panel" aria-labelledby="practice-title">
            <div className="panel-kicker">03 / A FRESH RESPONSE</div>
            <h2 id="practice-title">{item ? label(item.role) : label(bundle.plan.status)}</h2>
            {activity?.kind === "question" && <form onSubmit={(e) => { e.preventDefault(); if (selected) void submit(activity.id, selected); }}>
              <p className="question-prompt">{activity.prompt}</p>{activity.code && <pre className="question-code"><code>{activity.code}</code></pre>}
              <fieldset disabled={busy || !live || !!record.pending}><legend>Choose one answer</legend><div className="options">
                {activity.options.map((o) => <label className={selected === o.id ? "option selected" : "option"} key={activity.id + o.id}>
                  <input type="radio" name={activity.id} value={o.id} checked={selected === o.id} onChange={() => setSelected(o.id)} />
                  <span className="option-letter">{o.id.toUpperCase()}</span><span>{o.text}</span></label>)}
              </div></fieldset><button className="learn-primary" disabled={busy || !live || !selected || !!record.pending} type="submit">{busy ? "Checking response…" : "Submit response"}</button>
              <p className="learn-muted">No hints are provided in this slice. The server derives grades and evidence eligibility.</p>
            </form>}
            {activity?.kind === "lesson" && <><h3>{activity.title}</h3><p className="lesson-body">{activity.body}</p><button className="learn-primary" disabled={!live || busy || !!record.pending} onClick={() => void submit(activity.id)}>Mark lesson read</button><p className="learn-muted">Reading a lesson adds no correctness evidence or prerequisite readiness.</p></>}
            {!activity && <p>No currently permitted fresh question is available. {bundle.plan.status === "catalog_exhausted" ? "The needed question pool is exhausted. Review your evidence or reset the sandbox; we will not relabel a retry as new evidence." : "Inspect prerequisite locks or choose a different focus. Some concepts still lack authored activities."}</p>}
            {feedback && <div className="response-feedback" role="status"><strong>{feedback.kind === "lesson_completed" ? "Lesson recorded · zero new observations" : feedback.is_correct ? "Correct response" : "Incorrect response"}</strong>
              <p>{feedback.explanation}</p><p className="learn-muted">{label(feedback.eligibility_reason)} · {label(feedback.catalog_role)}</p>
              {acceptedReassessment && <p><strong>Distinct reassessment received.</strong> Compare the seed/current counts below. An unchanged, lower, or developing estimate is an honest outcome.</p>}
            </div>}
          </section>
          <LearningEvidence bundle={bundle} seed={seed} />
        </div><aside className="learning-side"><section className="learn-panel" aria-labelledby="plan-title"><div className="panel-kicker">THE PATH AHEAD</div><h2 id="plan-title">Your next steps</h2>
          <p className="state-pill">{label(bundle.plan.mode)} · {label(bundle.plan.status)}</p>
          <ol className="plan-list">{bundle.plan.items.map((i) => <li key={i.activity_id}>
            <button disabled={i.readiness === "locked" || busy || !!record.pending} aria-pressed={activity?.id === i.activity_id}
              onClick={() => { setOpened(i.activity_id); setSelected(""); }}>
              <strong>{label(i.role)}</strong><span>{label(i.concept_id)}</span><small>{i.readiness === "locked" ? "Locked" : "Available"} · {label(i.reason)}</small>
            </button>{i.blocked_by_concept_ids.length > 0 && <p className="learn-muted">Needs ready prerequisites: {i.blocked_by_concept_ids.map(label).join(", ")}.</p>}
            {i.depends_on_activity_ids.length > 0 && <p className="learn-muted">Requires a fresh same-run practice response first.</p>}
          </li>)}</ol><p className="learn-muted">Steps unlock only when observed evidence permits it. Recompute after every response.</p></section>
          <section className="learn-panel"><h2>Local response timeline</h2><ol className="timeline">{bundle.graded_events.filter((g) => g.provenance === "visitor_demo").map((g) => <li key={g.event_id}><strong>{label(g.catalog_role)}</strong><span>{label(g.concept_id)} · {g.is_correct === null ? "read" : g.is_correct ? "correct" : "incorrect"}</span><small>{label(g.eligibility_reason)}</small></li>)}</ol>
            {record.acknowledged_events.length === 0 && <p className="learn-muted">Your new responses will appear here. Canonical seed observations are kept separately.</p>}</section>
        </aside></div>}
      </>}
    </>}
    {busy && !seed && <p role="status">Loading the pinned synthetic release…</p>}
    <footer className="learn-footer"><p>Observed correctness is not mastery, causal proof, or a learning-gain claim. Only two concepts currently have authored activities.</p><Link href="/">Back to the project</Link><a href="https://github.com/Pranjaltyagi76/LearnGraphAI/blob/main/evaluation/model_card.md">Methods & measured limits ↗</a></footer>
  </main>;
}
