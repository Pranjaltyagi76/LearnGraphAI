import { parse } from "./protocol";
import type { AnalyzeRequest, AnalysisBundle, ErrorEnvelope, ProfilesResponse, ReleaseSummary, SeedResponse } from "./protocol";

const base = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
export class APIError extends Error {
  constructor(public code: string, public retryAfter = 1) { super(code); }
}
async function request<T>(path: string, schema: string, signal: AbortSignal, body?: AnalyzeRequest): Promise<T> {
  if (!base) throw new APIError("not_configured");
  const data = body ? JSON.stringify(body) : undefined;
  if (data && new TextEncoder().encode(data).length > 262144) throw new APIError("payload_too_large");
  const response = await fetch(`${base}${path}`, {
    method: body ? "POST" : "GET", cache: "no-store",
    headers: body ? { "Content-Type": "application/json" } : undefined, body: data,
    signal: AbortSignal.any([signal, AbortSignal.timeout(15_000)]),
  });
  const value: unknown = await response.json();
  if (!response.ok) {
    let code = "dependency_unavailable";
    try { code = parse<ErrorEnvelope>("ErrorEnvelope", value).code; } catch { /* safe generic failure */ }
    const retry = Number(response.headers.get("Retry-After"));
    throw new APIError(code, Number.isInteger(retry) && retry > 0 ? Math.min(retry, 86400) : 1);
  }
  return parse<T>(schema, value);
}
export const api = {
  release: (signal: AbortSignal) => request<ReleaseSummary>("/api/v1/demo/release", "ReleaseSummary", signal),
  profiles: (id: string, signal: AbortSignal) => request<ProfilesResponse>(`/api/v1/releases/${encodeURIComponent(id)}/profiles`, "ProfilesResponse", signal),
  seed: (id: string, profile: string, signal: AbortSignal) => request<SeedResponse>(`/api/v1/releases/${encodeURIComponent(id)}/profiles/${encodeURIComponent(profile)}/seed`, "SeedResponse", signal),
  analyze: (body: AnalyzeRequest, signal: AbortSignal) => request<AnalysisBundle>("/api/v1/demo/analyze", "AnalysisBundle", signal, body),
};
