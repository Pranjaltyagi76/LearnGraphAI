import rawSchema from "./generated/protocol.json";
import type { AnalyzeRequest, Event, SandboxRecord, SeedResponse, Versions } from "./generated/types";
export type * from "./generated/types";

type Schema = {
  $ref?: string; anyOf?: Schema[]; oneOf?: Schema[]; const?: unknown; enum?: unknown[];
  type?: string; properties?: Record<string, Schema>; required?: string[];
  additionalProperties?: boolean; items?: Schema; minItems?: number; maxItems?: number;
  minLength?: number; maxLength?: number; pattern?: string; minimum?: number; maximum?: number;
  format?: string;
};
const definitions: Record<string, Schema> = rawSchema.$defs;

function matches(value: unknown, schema: Schema): boolean {
  if (schema.$ref) return matches(value, definitions[schema.$ref.split("/").at(-1)!]);
  if (schema.anyOf) return schema.anyOf.some((s) => matches(value, s));
  if (schema.oneOf) return schema.oneOf.filter((s) => matches(value, s)).length === 1;
  if (Object.hasOwn(schema, "const") && value !== schema.const) return false;
  if (schema.enum && !schema.enum.includes(value)) return false;
  if (schema.type === "null") return value === null;
  if (schema.type === "object") {
    if (!value || typeof value !== "object" || Array.isArray(value)) return false;
    const record = value as Record<string, unknown>;
    return (schema.required ?? []).every((k) => Object.hasOwn(record, k)) &&
      Object.keys(record).every((k) => schema.properties && Object.hasOwn(schema.properties, k)
        ? matches(record[k], schema.properties[k]) : schema.additionalProperties !== false);
  }
  if (schema.type === "array") return Array.isArray(value) &&
    value.length >= (schema.minItems ?? 0) && value.length <= (schema.maxItems ?? Infinity) &&
    value.every((item) => matches(item, schema.items!));
  if (schema.type === "string") return typeof value === "string" &&
    [...value].length >= (schema.minLength ?? 0) && [...value].length <= (schema.maxLength ?? Infinity) &&
    (!schema.pattern || new RegExp(schema.pattern).test(value)) &&
    (schema.format !== "date-time" || validTimestamp(value));
  if (schema.type === "number" || schema.type === "integer") return typeof value === "number" &&
    Number.isFinite(value) && (schema.type !== "integer" || Number.isSafeInteger(value)) &&
    value >= (schema.minimum ?? -Infinity) && value <= (schema.maximum ?? Infinity);
  if (schema.type === "boolean") return typeof value === "boolean";
  return true;
}

function validTimestamp(value: string): boolean {
  const parts = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,3})?(Z|[+-](\d{2}):(\d{2}))$/.exec(value);
  if (!parts || !Number.isFinite(Date.parse(value))) return false;
  const [, y, m, d, h, minute, second, , zoneH, zoneM] = parts;
  const days = [31, (+y % 4 === 0 && (+y % 100 !== 0 || +y % 400 === 0)) ? 29 : 28,
    31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  return +y >= 1 && +m >= 1 && +m <= 12 && +d >= 1 && +d <= days[+m-1] &&
    +h < 24 && +minute < 60 && +second < 60 && +(zoneH ?? 0) < 24 && +(zoneM ?? 0) < 60;
}

export function parse<T>(name: string, value: unknown): T {
  if (!Object.hasOwn(definitions, name) || !matches(value, definitions[name])) throw new Error("invalid_contract");
  return value as T;
}
export function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map((k) =>
    `${JSON.stringify(k)}:${canonical((value as Record<string, unknown>)[k])}`).join(",")}}`;
  return JSON.stringify(value);
}
export function same(a: unknown, b: unknown): boolean { return canonical(a) === canonical(b); }
export function storageKey(profile: string, v: Versions): string {
  return "learngraph:v1:" + JSON.stringify([profile, v.release_id, v.release_hash, v.seed_id,
    v.seed_version, v.graph_version, v.catalog_version, v.model_version]);
}
export function normalized(events: Event[]): Event[] {
  const unique = new Map<string, Event>();
  for (const raw of events) {
    const e: Event = { ...raw, event_id: raw.event_id.toLowerCase(),
      assessment_run_id: raw.assessment_run_id.toLowerCase(),
      occurred_at: new Date(raw.occurred_at).toISOString(), time_spent_seconds: raw.time_spent_seconds ?? null,
      ...(raw.kind === "response" ? { hints_used: raw.hints_used ?? null } : {}) };
    if (unique.has(e.event_id) && !same(unique.get(e.event_id), e)) throw new Error("event_conflict");
    unique.set(e.event_id, e);
  }
  const result = [...unique.values()];
  if (result.some((e, i) => e.sequence_number !== i + 1 ||
      (i > 0 && e.occurred_at < result[i-1].occurred_at))) throw new Error("invalid_order");
  return result;
}
export async function digest(request: AnalyzeRequest): Promise<string> {
  const value = { contract_version: request.contract_version, versions: request.versions,
    profile_id: request.profile_id, focus_concept_id: request.focus_concept_id,
    trigger_event_id: request.trigger_event_id ?? null, events: normalized(request.events) };
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonical(value)));
  return [...new Uint8Array(bytes)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
export function snapshot(record: SandboxRecord, focus: string, trigger: string | null = null): AnalyzeRequest {
  return { contract_version: 1, versions: record.versions, profile_id: record.profile_id,
    sandbox_id: record.sandbox_id, local_revision: record.revision,
    focus_concept_id: record.pending?.focus_concept_id ?? focus,
    trigger_event_id: record.pending ? record.pending.trigger_event_id : trigger,
    events: [...record.acknowledged_events, ...(record.pending ? [record.pending.event] : [])] };
}
export function checkEventReferences(events: Event[], seed: SeedResponse): void {
  const seedIds = new Set(seed.seed_events.map((e) => e.event_id));
  for (const e of events) {
    const a = seed.activities.find((a) => a.id === e.activity_id);
    if (seedIds.has(e.event_id) || !a || a.version !== e.activity_version ||
        (a.kind === "question") !== (e.kind === "response") ||
        (a.kind === "question" && e.kind === "response" && !a.options.some((o) => o.id === e.response.option_id))) {
      throw new Error("invalid_reference");
    }
  }
}
