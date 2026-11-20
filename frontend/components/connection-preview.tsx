"use client";

import { useEffect, useRef, useState } from "react";

type Question = {
  id: string;
  concept_id: string;
  role: string;
  prompt: string;
  code: string;
  options: { id: string; text: string }[];
};
type Feedback = { is_correct: boolean; explanation: string };
type Seed = {
  release_id: string;
  profile: { name: string; focus_concept_id: string };
  activities: Question[];
  seed_events: { activity_id: string }[];
};
const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
const recorded: Question = {
  id: "recorded_base_case",
  concept_id: "base_cases",
  role: "practice",
  prompt: "Which return value handles both Fibonacci boundary inputs?",
  code: "def fib(n):\n    if n <= 1:\n        return RESULT\n    return fib(n - 1) + fib(n - 2)",
  options: [
    { id: "a", text: "0" },
    { id: "b", text: "1" },
    { id: "c", text: "n" },
    { id: "d", text: "n + 1" },
  ],
};

export function ConnectionPreview() {
  const [seed, setSeed] = useState<Seed | null>(null);
  const [state, setState] = useState<
    "recorded" | "loading" | "ready" | "sending" | "unavailable"
  >("recorded");
  const [selected, setSelected] = useState("");
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [notice, setNotice] = useState("");
  const controller = useRef<AbortController | null>(null);
  const revision = useRef(0);
  const pendingEvent = useRef<string | null>(null);
  useEffect(() => () => controller.current?.abort(), []);

  const question =
    seed?.activities.find(
      (q) =>
        q.role === "practice" &&
        q.concept_id === seed.profile.focus_concept_id &&
        !seed.seed_events.some((e) => e.activity_id === q.id),
    ) ?? recorded;
  const live = seed !== null && (state === "ready" || state === "sending");

  async function request<T>(
    path: string,
    signal: AbortSignal,
    init?: RequestInit,
  ): Promise<T> {
    if (!apiBase) throw new Error("unavailable");
    const response = await fetch(`${apiBase}${path}`, {
      ...init,
      signal: AbortSignal.any([signal, AbortSignal.timeout(10_000)]),
    });
    if (!response.ok) {
      if (response.status === 429)
        throw new Error(
          "Please pause a moment: the free demo request limit has been reached.",
        );
      if (response.status === 409)
        throw new Error(
          "The question set changed. Check the live connection again.",
        );
      throw new Error("unavailable");
    }
    return response.json() as Promise<T>;
  }

  async function loadLive() {
    controller.current?.abort();
    const current = ++revision.current;
    const active = new AbortController();
    controller.current = active;
    setState("loading");
    setNotice("");
    setFeedback(null);
    setSelected("");
    setSeed(null);
    pendingEvent.current = null;
    try {
      await request("/ready", active.signal);
      const profiles = await request<{ profiles: { id: string }[] }>(
        "/api/v1/demo/profiles",
        active.signal,
      );
      if (!profiles.profiles.length) throw new Error("unavailable");
      const data = await request<Seed>(
        `/api/v1/demo/profiles/${encodeURIComponent(profiles.profiles[0].id)}/seed`,
        active.signal,
      );
      if (current !== revision.current || active.signal.aborted) return;
      if (
        !data.activities.some(
          (q) =>
            q.role === "practice" &&
            !data.seed_events.some((e) => e.activity_id === q.id),
        )
      )
        throw new Error("unavailable");
      setSeed(data);
      setState("ready");
    } catch {
      if (current !== revision.current || active.signal.aborted) return;
      setState("unavailable");
      setNotice(
        "The live demo is temporarily unavailable. This recorded example remains available; no response has been accepted.",
      );
    }
  }

  async function submit() {
    if (!seed || !selected || state !== "ready") return;
    const current = revision.current;
    const active = new AbortController();
    controller.current = active;
    pendingEvent.current ??= crypto.randomUUID();
    setState("sending");
    setNotice("");
    try {
      const result = await request<Feedback>(
        "/api/v1/bootstrap/answer",
        active.signal,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            event_id: pendingEvent.current,
            release_id: seed.release_id,
            activity_id: question.id,
            option_id: selected,
          }),
        },
      );
      if (current !== revision.current || active.signal.aborted) return;
      setFeedback(result);
      setState("ready");
      pendingEvent.current = null;
    } catch (error) {
      if (current !== revision.current || active.signal.aborted) return;
      setState("ready");
      const message =
        error instanceof Error &&
        error.message !== "unavailable" &&
        error.name !== "TimeoutError"
          ? error.message
          : "Your response was not confirmed. Please retry when the live service is available.";
      setNotice(message);
    }
  }

  return (
    <section
      className="preview-card"
      id="preview"
      aria-labelledby="preview-title"
    >
      <div className="preview-top">
        <span className="eyebrow">LEARNER PREVIEW</span>
        <span className="phase-badge">Phase 1</span>
      </div>
      <div className="profile-row">
        <span className="avatar" aria-hidden="true">
          M
        </span>
        <div>
          <h2 id="preview-title">A clearer next step</h2>
          <p>{seed?.profile.name ?? "Mira"} · Synthetic learner</p>
        </div>
        <span className="profile-tag">DSA</span>
      </div>
      <div
        className={`connection-label ${live ? "connected" : ""}`}
        role="status"
      >
        <span className="status-dot" />
        {live
          ? "Live question · server-graded"
          : state === "loading"
            ? "Checking live availability…"
            : "Prerecorded example · synthetic"}
      </div>
      <p className="concept-label">
        {question.concept_id.replaceAll("_", " ").toUpperCase()} <span>/</span>{" "}
        RECURSION
      </p>
      <h3 className="question-prompt">{question.prompt}</h3>
      <pre className="code-panel">
        <code>{question.code}</code>
      </pre>
      {live ? (
        <fieldset disabled={state === "sending" || feedback !== null}>
          <legend className="sr-only">Choose a return value</legend>
          <div className="options">
            {question.options.map((option) => (
              <label
                key={option.id}
                className={`answer-option ${selected === option.id ? "selected" : ""}`}
              >
                <input
                  type="radio"
                  name="answer"
                  value={option.id}
                  checked={selected === option.id}
                  onChange={() => {
                    setSelected(option.id);
                    pendingEvent.current = null;
                  }}
                />
                <span className="option-letter">{option.id.toUpperCase()}</span>
                <span>{option.text}</span>
              </label>
            ))}
          </div>
        </fieldset>
      ) : (
        <div
          className="options recorded-options"
          aria-label="Recorded answer choices"
        >
          {question.options.map((option) => (
            <div className="answer-option" key={option.id}>
              <span className="option-letter">{option.id.toUpperCase()}</span>
              <span>{option.text}</span>
            </div>
          ))}
        </div>
      )}
      {feedback ? (
        <div className="feedback" role="status">
          <strong>
            {!live
              ? "Recorded explanation"
              : feedback.is_correct
                ? "That’s right."
                : "A useful point to revisit."}
          </strong>
          <p>{feedback.explanation}</p>
        </div>
      ) : null}
      {notice ? (
        <p className="notice" role="alert">
          {notice}
        </p>
      ) : null}
      {live ? (
        <button
          className="submit-button"
          onClick={submit}
          disabled={!selected || state === "sending" || feedback !== null}
        >
          {state === "sending"
            ? "Checking response…"
            : feedback
              ? "Response checked"
              : "Check my response"}
          <span aria-hidden="true">→</span>
        </button>
      ) : (
        <button
          className="submit-button"
          onClick={() =>
            setFeedback({
              is_correct: true,
              explanation:
                "Recorded feedback: returning n gives fib(0) = 0 and fib(1) = 1. This example was not submitted to a live service.",
            })
          }
          disabled={feedback !== null}
        >
          View recorded feedback<span aria-hidden="true">→</span>
        </button>
      )}
      <button
        className="connection-button"
        onClick={loadLive}
        disabled={state === "loading" || state === "sending"}
      >
        {state === "loading" ? "Connecting…" : "Check live connection"}
      </button>
      <p className="preview-note">
        Infrastructure preview: question delivery and grading only. Diagnosis,
        saved progress, and reassessment arrive in later phases.
      </p>
    </section>
  );
}
