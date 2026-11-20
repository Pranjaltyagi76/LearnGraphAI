import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import ts from "typescript";
import { expect, type Page } from "@playwright/test";
import type * as protocol from "../lib/protocol";
import type { SandboxStore as Store, Loaded } from "../lib/sandbox";

declare global {
  interface Window {
    sandboxTest: { SandboxStore: typeof Store; digest: typeof protocol.digest;
      parse: typeof protocol.parse; snapshot: typeof protocol.snapshot;
      storageKey: typeof protocol.storageKey; validateRecord: (raw: unknown, seed: protocol.SeedResponse) => Promise<protocol.SandboxRecord> };
  }
}
export type { Loaded };

export async function injectStore(page: Page) {
  const compile = (name: string) => ts.transpileModule(readFileSync(resolve(process.cwd(), `lib/${name}.ts`), "utf8"), {
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext },
  }).outputText.replace(/^export /gm, "");
  const schema = readFileSync(resolve(process.cwd(), "lib/generated/protocol.json"), "utf8");
  const source = compile("protocol").replace(/import rawSchema from [^;]+;/, `const rawSchema = ${schema};`)
    + compile("sandbox").replace(/import \{[^}]+\} from [^;]+;/g, "")
    + "\nwindow.sandboxTest = { SandboxStore, digest, parse, snapshot, storageKey, validateRecord };";
  await page.addScriptTag({ type: "module", content: source });
  await expect.poll(() => page.evaluate(() => !!window.sandboxTest)).toBe(true);
}

export async function seedFixture(request: import("@playwright/test").APIRequestContext) {
  const result = await request.get("http://127.0.0.1:8000/api/v1/releases/learngraph-review-v1/profiles/demo_base_cases/seed");
  expect(result.ok()).toBe(true);
  return await result.json() as protocol.SeedResponse;
}
