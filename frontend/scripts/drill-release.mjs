// Bounded real-production drills. No request mocks or automatic POST retries.
import { chromium, expect } from "@playwright/test";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { parseArgs } from "node:util";
const { values } = parseArgs({ options: {
  mode: { type: "string" }, output: { type: "string" },
} });
if (!["outage", "quota"].includes(values.mode) || !values.output) throw Error("Use --mode outage|quota --output new-file.json");
const base="https://learngraph-ai-web.vercel.app", api="https://learngraph-ai-api.vercel.app";
// Playwright's test runner clears test-results on startup; coordination must
// survive independent local/CI checks running at the same time.
const marker=resolve(".vercel/phase5-control.json");
const report={observed_at:new Date().toISOString(),mode:values.mode,synthetic_only:true,checks:{},requests:[]};
const browser=await chromium.launch({headless:true});
try {
  const context=await browser.newContext({viewport:{width:1365,height:1000}});
  const page=await context.newPage();
  await page.goto(base+"/learn");
  const initialPromise=page.waitForResponse(r=>r.url()===api+"/api/v1/demo/analyze" && r.request().method()==="POST");
  await page.getByRole("button",{name:"Analyze this learner",exact:true}).click();
  const initial=await initialPromise;expect(initial.status()).toBe(200);
  await expect(page.getByText("Live analysis · server-graded",{exact:true})).toBeVisible();
  const original=await initial.json(); const request=initial.request().postDataJSON();
  if(values.mode==="outage") {
    await writeFile(marker,JSON.stringify({state:"ready_to_pause"}));
    async function wait(state) {
      const deadline=Date.now()+900000;
      while(Date.now()<deadline) {
        const current=JSON.parse(await readFile(marker,"utf8"));
        if(current.state===state)return;
        await new Promise(r=>setTimeout(r,500));
      }
      throw Error("Drill coordination timed out: "+state);
    }
    await wait("paused");
    const ready=await context.request.get(api+"/ready");expect(ready.status()).toBe(503);
    report.checks.real_paused_database_readiness_503=true;
    report.pause_readiness_code=(await ready.json()).code;
    await page.locator("input[type=radio][value=c]").check();
    const failed=page.waitForResponse(r=>r.url()===api+"/api/v1/demo/analyze" && r.request().method()==="POST");
    await page.getByRole("button",{name:"Submit response",exact:true}).click();
    const response=await failed;expect(response.status()).toBe(503);
    report.pending_request=response.request().postDataJSON();
    await expect(page.getByRole("heading",{name:"Response pending — not accepted"})).toBeVisible();
    await page.reload();
    // A cold API may also make seed metadata unavailable on refresh. Inspect the
    // actual local pending record rather than pretending the API is available.
    const preserved=await page.evaluate(async()=>{
      const db=await new Promise((resolve,reject)=>{const r=indexedDB.open("learngraph-ai-v1",1);r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
      const rows=await new Promise((resolve,reject)=>{const r=db.transaction("sandboxes").objectStore("sandboxes").getAll();r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
      db.close();return rows.find(r=>r.pending)?.pending?.event?.event_id;
    });
    expect(preserved).toBe(report.pending_request.events.at(-1).event_id);
    const examples=await context.newPage();await examples.goto(base+"/examples/demo_upstream");
    await expect(examples.getByText("No live submission in this example.",{exact:true})).toBeVisible();
    await expect(examples.locator("form, input[type=radio]")).toHaveCount(0);await examples.close();
    report.checks.paused_database_pending_refresh_and_readonly_example=true;
    await writeFile(marker,JSON.stringify({state:"outage_observed"}));
    await wait("restored");
    await page.reload();await expect(page.getByRole("heading",{name:"Response pending — not accepted"})).toBeVisible();
  } else {
    let denied=false;
    for(let i=0;i<11;i++) {
      const start=performance.now();const r=await context.request.post(api+"/api/v1/demo/analyze",{data:request});
      const body=await r.json();report.requests.push({status:r.status(),ms:performance.now()-start,retry_after:r.headers()["retry-after"]??null});
      if(r.status()===429){expect(body.code).toBe("quota_exhausted");denied=true;break;}
      expect(r.status()).toBe(200);expect(body.history_digest).toBe(original.history_digest);
      expect(body.accepted_visitor_events).toBe(0);
    }
    expect(denied).toBe(true);report.checks.same_request_retries_add_no_evidence=true;
    await page.locator("input[type=radio][value=c]").check();
    const failure=page.waitForResponse(r=>r.url()===api+"/api/v1/demo/analyze" && r.request().method()==="POST");
    await page.getByRole("button",{name:"Submit response",exact:true}).click();
    const response=await failure;expect(response.status()).toBe(429);report.pending_request=response.request().postDataJSON();
    await expect(page.getByRole("heading",{name:"Response pending — not accepted"})).toBeVisible();
    await page.reload();await expect(page.getByRole("heading",{name:"Response pending — not accepted"})).toBeVisible();
    const seconds=Number(response.headers()["retry-after"]);expect(seconds).toBeGreaterThan(0);
    // Wait for the explicit operator-style retry below; no timer sends a POST.
    await new Promise(r=>setTimeout(r,(seconds+1)*1000));
    report.checks.real_quota_denial_preserved_exact_pending=true;
  }
  const retryPromise=page.waitForResponse(r=>r.url()===api+"/api/v1/demo/analyze" && r.request().method()==="POST");
  await page.getByRole("button",{name:"Retry pending response",exact:true}).click();
  const retry=await retryPromise;expect(retry.status()).toBe(200);
  expect(retry.request().postDataJSON()).toEqual(report.pending_request);
  const accepted=await retry.json();expect(accepted.accepted_visitor_events).toBe(1);
  await expect(page.getByText("1 accepted local events",{exact:false})).toBeVisible();
  report.checks.exact_manual_retry_accepted_once=true;report.final_history_digest=accepted.history_digest;
  delete report.pending_request;report.passed=true;
}catch(error){report.passed=false;report.failure=String(error);}
finally{await browser.close();await writeFile(resolve(values.output),JSON.stringify(report,null,2)+"\n",{flag:"wx"});}
console.log(JSON.stringify({passed:report.passed,mode:values.mode,output:values.output}));
if(!report.passed)process.exitCode=1;
