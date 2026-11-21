// Small declared workload, not a capacity or load-test claim. Invoke in a fresh quota minute.
import { chromium, expect } from "@playwright/test";
import { writeFile } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import { parseArgs } from "node:util";
const { values }=parseArgs({options:{output:{type:"string"}}});
if(!values.output)throw Error("Choose a new --output path");
const base="https://learngraph-ai-web.vercel.app",api="https://learngraph-ai-api.vercel.app";
const report={observed_at:new Date().toISOString(),method:"Eight full-analysis calls, concurrency two; eight fresh browser contexts, unthrottled desktop hardware with desktop/mobile viewports. No automatic POST retry.",samples:[],pages:[]};
const seed=await(await fetch(api+"/api/v1/releases/learngraph-full-v1/profiles/demo_base_cases/seed")).json();
const body={contract_version:1,versions:seed.versions,profile_id:seed.profile.id,sandbox_id:randomUUID(),local_revision:0,focus_concept_id:"base_cases",events:[]};
async function call(input){const start=performance.now();const response=await fetch(api+"/api/v1/demo/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(input)});const text=await response.text();const value=JSON.parse(text);return {status:response.status,ms:performance.now()-start,server_timing:response.headers.get("server-timing"),bytes:Buffer.byteLength(text),value};}
try{
  let digest;
  for(let i=0;i<4;i++){
    const batch=await Promise.all([call(body),call(body)]);
    for(const row of batch){expect(row.status).toBe(200);expect(row.value.persisted).toBe(false);expect(row.value.accepted_visitor_events).toBe(0);digest??=row.value.history_digest;expect(row.value.history_digest).toBe(digest);delete row.value;report.samples.push(row);}
  }
  const bad=await call({...body,versions:{...body.versions,release_hash:"0".repeat(64)}});expect(bad.status).toBe(409);expect(bad.value.code).toBe("version_mismatch");report.version_conflict_status=bad.status;
  const oversized=await fetch(api+"/api/v1/demo/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:"x".repeat(262145)});expect(oversized.status).toBe(413);report.oversized_status=oversized.status;
  const browser=await chromium.launch({headless:true});
  try{for(const width of [1365,360]){for(let i=0;i<4;i++){
    const ctx=await browser.newContext({viewport:{width,height:900}});const page=await ctx.newPage();const start=performance.now();
    await page.goto(base+"/learn");await expect(page.getByRole("button",{name:"Analyze this learner",exact:true})).toBeVisible();
    const visible_ms=performance.now()-start;
    const timing=await page.evaluate(()=>{const n=performance.getEntriesByType("navigation")[0];return {dom_content_loaded_ms:n.domContentLoadedEventEnd,load_event_end_ms:n.loadEventEnd,first_contentful_paint_ms:performance.getEntriesByName("first-contentful-paint")[0]?.startTime??null,overflow:document.documentElement.scrollWidth>innerWidth};});
    expect(timing.overflow).toBe(false);report.pages.push({viewport_width:width,usable_analysis_control_ms:visible_ms,...timing});await ctx.close();
  }}}finally{await browser.close();}
  const ordered=report.samples.map(r=>r.ms).sort((a,b)=>a-b);report.p95_ms=ordered[Math.ceil(ordered.length*.95)-1];report.passed=true;
}catch(error){report.passed=false;report.failure=String(error);}
await writeFile(values.output,JSON.stringify(report,null,2)+"\n",{flag:"wx"});
console.log(JSON.stringify({passed:report.passed,output:values.output,p95_ms:report.p95_ms}));if(!report.passed)process.exitCode=1;
