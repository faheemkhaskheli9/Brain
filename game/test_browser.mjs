// Browser smoke tests for the interactive demos (issue #109), in headless Chromium.
//   Brain World      starts, trains, pauses and resumes, fast-forwards, saves and loads (the save it
//                    made and the legacy v3 fixture of #98), uses a skill with learning off, teach
//                    mode, a mobile layout with no sideways scroll, and ten new brains in a row
//                    without adding canvases or errors.
//   Brain Ecosystem  starts, steps, toggles learning, new world, mobile layout.
// Every page must log no console error and throw no uncaught exception.
// Needs playwright (npm i -g playwright; npx playwright install chromium) and three@0.160.0: the
// pages import it from jsDelivr, and the test serves it from a local copy instead (THREE_DIR, else
// node_modules/three found locally or globally), so it runs offline; without one it uses the CDN.
// Run: node game/test_browser.mjs [--extended]
//   --extended also loads Brain Lab (game/web), which downloads Pyodide from its CDN (slow).
import assert from "node:assert/strict";
import { execSync } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const EXTENDED = process.argv.includes("--extended");

async function load(name) {
  try { return await import(name); } catch { /* try the global install */ }
  const dir = path.join(execSync("npm root -g").toString().trim(), name);
  const pkg = JSON.parse(fs.readFileSync(path.join(dir, "package.json"), "utf8"));
  const entry = pkg.exports?.["."]?.import?.default ?? pkg.exports?.["."]?.import ?? pkg.module ?? pkg.main ?? "index.js";
  return import(path.join(dir, typeof entry === "string" ? entry : "index.mjs"));
}
function threeDir() {
  const tries = [process.env.THREE_DIR, path.join(ROOT, "node_modules/three")];
  try { tries.push(path.join(execSync("npm root -g").toString().trim(), "three")); } catch { /* no npm */ }
  return tries.find(d => d && fs.existsSync(path.join(d, "build/three.module.js")));
}

const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json", ".css": "text/css" };
function serve() {
  const srv = http.createServer((req, res) => {
    const file = path.join(ROOT, decodeURIComponent(new URL(req.url, "http://x").pathname));
    if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404).end(); return; }
    res.writeHead(200, { "content-type": TYPES[path.extname(file)] || "application/octet-stream" });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(ok => srv.listen(0, "127.0.0.1", () => ok(srv)));
}

const { chromium } = await load("playwright");
const srv = await serve(), base = `http://127.0.0.1:${srv.address().port}/`, three = threeDir();
const browser = await chromium.launch();
let failures = 0;

async function page(url, viewport = { width: 1280, height: 900 }) {
  const ctx = await browser.newContext({ viewport, acceptDownloads: true });
  if (three) await ctx.route("https://cdn.jsdelivr.net/npm/three@0.160.0/**", route => {
    const file = path.join(three, new URL(route.request().url()).pathname.replace(/^\/npm\/three@0\.160\.0\//, ""));
    return fs.existsSync(file) ? route.fulfill({ path: file, contentType: "text/javascript" }) : route.abort();
  });
  const p = await ctx.newPage(), errors = [];
  p.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
  p.on("pageerror", e => errors.push(String(e)));
  await p.goto(base + url);
  return { p, errors, ctx };
}
async function test(name, fn) {
  try { await fn(); console.log(`ok   ${name}`); } catch (e) { failures++; console.log(`FAIL ${name}\n     ${e.message.split("\n").join("\n     ")}`); }
}
const noSideScroll = p => p.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1);

await test("Brain World: start, train, pause, save, load, perform, teach, restart", async () => {
  const { p, errors, ctx } = await page("game/world/index.html");
  await p.locator("#intro form button").click();           // the first-visit dialog
  await p.locator("#fast").click();
  await p.waitForTimeout(1500);
  assert.ok((await p.locator("#banner").textContent()).length > 0, "no banner text");
  await p.locator("#pause").click();
  assert.equal(await p.locator("#pause").textContent(), "Resume");
  const a = await p.locator("#doing").textContent(); await p.waitForTimeout(300);
  assert.equal(await p.locator("#doing").textContent(), a, "paused but still acting");
  await p.locator("#pause").click();

  const [dl] = await Promise.all([p.waitForEvent("download"), p.locator("#save").click()]);
  const saved = JSON.parse(fs.readFileSync(await dl.path(), "utf8"));
  assert.equal(saved.version, 5, "save version");
  for (const [file, what] of [[await dl.path(), "its own save"], [path.join(ROOT, "game/world/fixtures/v3-seed1.json"), "the v3 fixture (#98)"]]) {
    await p.locator("#loadFile").setInputFiles(file);
    await p.waitForFunction(() => /Loaded a brain|Could not load/.test(document.getElementById("banner").textContent));
    assert.match(await p.locator("#banner").textContent(), /Loaded a brain/, `loading ${what}`);
  }
  await p.locator("#skill").selectOption("listen");
  assert.match(await p.locator("#banner").textContent(), /learning off/);
  await p.locator("#skill").selectOption("teach");
  assert.equal(await p.locator("#teach").isHidden(), false);
  await p.locator('#teach [data-tone="0"]').click();
  await p.locator("#clearRoom").click();
  await p.locator("#skill").selectOption("");
  const canvases = await p.locator("canvas").count();
  for (let i = 0; i < 10; i++) await p.locator("#restart").click();
  await p.waitForTimeout(500);
  assert.equal(await p.locator("canvas").count(), canvases, "new brains added canvases");
  assert.deepEqual(errors, []);
  await ctx.close();
});

await test("Brain World: mobile layout", async () => {
  const { p, errors, ctx } = await page("game/world/index.html", { width: 390, height: 844 });
  await p.locator("#intro form button").click();
  await p.waitForTimeout(500);
  assert.ok(await noSideScroll(p), "the page scrolls sideways at 390 px");
  assert.deepEqual(errors, []);
  await ctx.close();
});

await test("Brain Ecosystem: start, step, learning off, new world, mobile layout", async () => {
  for (const viewport of [{ width: 1280, height: 900 }, { width: 390, height: 844 }]) {
    const { p, errors, ctx } = await page("game/ecosystem/index.html", viewport);
    if (await p.locator("#intro").evaluate(d => d.open)) await p.locator("#intro form button").click();
    await p.locator("#fast").click();
    await p.waitForFunction(() => +document.getElementById("t").textContent > 50, null, { timeout: 15000 });
    await p.locator("#learn").click();
    assert.equal(await p.locator("#learn").getAttribute("aria-pressed"), "false");
    await p.locator("#new").click();
    await p.waitForTimeout(300);
    if (viewport.width < 500) assert.ok(await noSideScroll(p), "the page scrolls sideways at 390 px");
    assert.deepEqual(errors, []);
    await ctx.close();
  }
});

if (EXTENDED) await test("Brain Lab (Pyodide from its CDN): starts", async () => {
  const { p, errors, ctx } = await page("game/web/index.html");
  await p.waitForTimeout(20000);
  assert.deepEqual(errors, []);
  await ctx.close();
});

await browser.close(); srv.close();
if (!three) console.log("note: three.js came from the CDN (set THREE_DIR to test offline)");
console.log(failures ? `${failures} failed` : "ok");
process.exit(failures ? 1 : 0);
