// Resolve axe's SVG-background uncertainty from actual rendered text/rect colors.
import { chromium, expect } from "@playwright/test";
import axe from "axe-core";
import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { parseArgs } from "node:util";

const { values } = parseArgs({ options: {
  base: { type: "string", default: "https://learngraph-ai-web.vercel.app" },
  output: { type: "string", default: "../context/evidence/phase4_graph_accessibility.json" },
} });
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1365, height: 1000 } });
  const path = "/examples/demo_upstream";
  await page.goto(`${values.base}${path}`, { waitUntil: "networkidle" });
  await expect(page.getByRole("group", { name: "Curriculum view", exact: true })).toBeVisible();
  await page.addScriptTag({ content: axe.source });
  const review = await page.evaluate(async () => {
    const luminance = (color) => {
      const channels = color.match(/[\d.]+/g).slice(0, 3).map(Number).map((v) => v / 255)
        .map((v) => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
      return channels[0] * .2126 + channels[1] * .7152 + channels[2] * .0722;
    };
    const ratio = (a, b) => {
      const [light, dark] = [luminance(a), luminance(b)].sort((a, b) => b - a);
      return (light + .05) / (dark + .05);
    };
    const texts = [...document.querySelectorAll(".concept-map svg text")].map((node) => {
      const rect = node.parentElement.querySelector("rect");
      const foreground = getComputedStyle(node).fill;
      const background = getComputedStyle(rect).fill;
      return { text: node.textContent, foreground, background, contrast_ratio: ratio(foreground, background) };
    });
    const graphBackground = getComputedStyle(document.querySelector(".graph-scroll")).backgroundColor;
    const arrowStroke = getComputedStyle(document.querySelector(".graph-edge")).stroke;
    const scan = await window.axe.run(document, { runOnly: {
      type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa", "best-practice"],
    } });
    return { texts, arrow: { foreground: arrowStroke, background: graphBackground, contrast_ratio: ratio(arrowStroke, graphBackground) },
      violations: scan.violations.map((v) => v.id), incomplete: scan.incomplete.map((r) => ({ id: r.id,
        targets: r.nodes.flatMap((n) => n.target), messages: [...new Set(r.nodes.flatMap((n) => [...n.any, ...n.all, ...n.none].map((c) => c.message)))] })) };
  });
  expect(review.texts.length).toBeGreaterThanOrEqual(24);
  expect(review.texts.every((n) => n.contrast_ratio >= 4.5)).toBe(true);
  expect(review.arrow.contrast_ratio).toBeGreaterThanOrEqual(3);
  expect(review.violations).toEqual([]);
  expect(review.incomplete.every((r) => r.id === "color-contrast" && r.targets.every((t) => t.includes(".graph-")))).toBe(true);
  await page.getByRole("button", { name: "List view", exact: true }).focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(".graph-scroll")).toHaveCount(0);
  await expect(page.getByRole("list", { name: "Concept evidence and prerequisites" }).locator(":scope > li")).toHaveCount(12);
  const report = { observed_at: new Date().toISOString(), url: `${values.base}${path}`, axe_core: axe.version,
    ...review, named_control_group: true, keyboard_list_alternative: true,
    manual_render_review: "Actual desktop/mobile production captures inspected; text is inside opaque rect fills. HTML list repeats every named state/prerequisite.",
    limitation: "Targeted contrast/semantics review; not complete assistive-technology conformance" };
  await writeFile(resolve(values.output), JSON.stringify(report, null, 2) + "\n", { flag: "wx" });
  console.log(JSON.stringify({ passed: true, output: values.output,
    minimum_text_contrast: Math.min(...review.texts.map((n) => n.contrast_ratio)), arrow_contrast: review.arrow.contrast_ratio }));
} finally { await browser.close(); }
