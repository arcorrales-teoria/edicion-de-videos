// Renderiza video.html cuadro a cuadro con Chrome (WebGPU) y arma el MP4 con ffmpeg.
// Uso: node render.mjs [desde] [hasta] [carpeta]   (por defecto 0..599 en frames/)
import { spawn, execFileSync } from "child_process";
import { mkdirSync, writeFileSync } from "fs";
const [from = "0", to = "599", dir = "frames", page = "video.html", W = "1920", H = "1080"] = process.argv.slice(2);
mkdirSync(dir, { recursive: true });
const chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const port = 9600 + Math.floor(Math.random() * 300);
const p = spawn(chrome, ["--headless=new", "--enable-unsafe-webgpu", "--use-angle=metal", "--hide-scrollbars", "--force-device-scale-factor=1", `--remote-debugging-port=${port}`, `--user-data-dir=/tmp/render-${port}-${Date.now()}`, "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws;
for (let i = 0; i < 60; i++) { try { const l = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); const pg = l.find((t) => t.type === "page"); if (pg) { ws = new WebSocket(pg.webSocketDebuggerUrl); break; } } catch {} await sleep(200); }
await new Promise((r) => (ws.onopen = r));
let id = 0; const pend = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d.result ?? d); pend.delete(d.id); } else if (d.method === "Runtime.exceptionThrown") console.error("EXC", d.params.exceptionDetails.exception?.description); };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send("Runtime.enable");
await send("Network.enable");
await send("Network.setCacheDisabled", { cacheDisabled: true });
await send("Emulation.setDeviceMetricsOverride", { width: +W, height: +H, deviceScaleFactor: 1, mobile: false });
await send("Page.enable");
await send("Page.navigate", { url: `http://localhost:8765/${page}` });
for (let i = 0; i < 100; i++) { const r = await send("Runtime.evaluate", { expression: "!!window.__ready", returnByValue: true }); if (r.result?.value) break; await sleep(200); }
// Calienta el shader unos cuadros antes de grabar.
for (let n = 0; n < 5; n++) await send("Runtime.evaluate", { expression: `window.__frame(${n})`, awaitPromise: true });
const t0 = Date.now();
for (let n = +from; n <= +to; n++) {
  await send("Runtime.evaluate", { expression: `window.__frame(${n})`, awaitPromise: true });
  await sleep(25);
  const shot = await send("Page.captureScreenshot", { format: "jpeg", quality: 95, captureBeyondViewport: false });
  writeFileSync(`${dir}/f${String(n).padStart(4, "0")}.jpg`, Buffer.from(shot.data, "base64"));
  if (n % 60 === 0) console.log(`cuadro ${n} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
}
ws.close(); p.kill();
console.log("listo");
