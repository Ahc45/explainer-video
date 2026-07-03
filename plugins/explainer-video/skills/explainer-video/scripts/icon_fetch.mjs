#!/usr/bin/env node
/**
 * Icon fetcher — renders `tech-stack-icons` (690+ brand SVGs) to transparent PNGs
 * that Manim loads with ImageMobject. This is the "image icon" visual vocabulary
 * that complements the line/box shapes (great for tech-stack & system-design videos).
 *
 * Which icons to fetch: gathered from the timing contract —
 *   - a top-level  "icons": ["nextjs","redis",...]  array, and/or
 *   - any per-scene "icons": [...] arrays
 *   - plus any names passed as extra CLI args.
 *
 * Usage:
 *   node scripts/icon_fetch.mjs                          # read timing_contract.json, variant=dark
 *   node scripts/icon_fetch.mjs --variant light          # light variant (for light backgrounds)
 *   node scripts/icon_fetch.mjs nextjs redis docker      # also fetch these explicit names
 *   node scripts/icon_fetch.mjs --list | grep kafka      # print the full catalog of 690+ names
 *
 * Requires (install in the project once):
 *   npm i tech-stack-icons react react-dom @resvg/resvg-js
 *
 * Output: assets/icons/<name>.png  (512px wide, transparent background).
 * The neon-dark theme (#0A0A0A bg) wants variant "dark" — those icons carry light
 * outlines so they pop on black. Use "light" only if you switch to a light theme.
 */
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import StackIcon, * as TSI from "tech-stack-icons";
import { Resvg } from "@resvg/resvg-js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { createRequire } from "module";

const require = createRequire(import.meta.url);

// Run from project root (parent of scripts/).
const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.basename(HERE) === "scripts" ? path.dirname(HERE) : HERE;
process.chdir(ROOT);

const RES = 512;
const OUT = path.join("assets", "icons");
const CONTRACT = "timing_contract.json";

// ---- args ----------------------------------------------------------------
const argv = process.argv.slice(2);
let variant = "dark";
const cliNames = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === "--variant") { variant = argv[++i] || "dark"; }
  else if (argv[i] === "--list") { listCatalog(); process.exit(0); }
  else { cliNames.push(argv[i]); }
}

// ---- gather names --------------------------------------------------------
const names = new Set(cliNames);
if (fs.existsSync(CONTRACT)) {
  const c = JSON.parse(fs.readFileSync(CONTRACT, "utf8"));
  for (const n of c.icons || []) names.add(n);
  for (const sc of c.scenes || []) for (const n of sc.icons || []) names.add(n);
}
if (names.size === 0) {
  console.error("No icons requested. Add an \"icons\" array to timing_contract.json or pass names as args.");
  console.error("Tip: node scripts/icon_fetch.mjs --list  (prints all available names)");
  process.exit(1);
}

fs.mkdirSync(OUT, { recursive: true });
let ok = 0, fail = 0;
for (const name of names) {
  try {
    let html = renderToStaticMarkup(React.createElement(StackIcon, { name, variant }));
    // StackIcon wraps the <svg> in a <span>; strip everything but the svg.
    const svg = html.replace(/^.*?(<svg)/s, "$1").replace(/<\/svg>.*$/s, "</svg>");
    if (!svg.startsWith("<svg")) throw new Error("no svg produced (unknown name?)");
    const resvg = new Resvg(svg, { fitTo: { mode: "width", value: RES }, background: "rgba(0,0,0,0)" });
    fs.writeFileSync(path.join(OUT, `${name}.png`), resvg.render().asPng());
    console.log("ok  ", name);
    ok++;
  } catch (e) {
    console.log("FAIL", name, "-", e.message.slice(0, 80));
    fail++;
  }
}
console.log(`\n${ok} icons -> ${OUT}/  (${fail} failed)`);

// ---- helpers -------------------------------------------------------------
function listCatalog() {
  // Best-effort: pull the embedded icon map out of the bundle to print names.
  try {
    const bundle = require.resolve("tech-stack-icons");
    const src = fs.readFileSync(bundle, "utf8");
    const found = new Set();
    const re = /([A-Za-z0-9+#._-]+):\{svg:\{/g;
    let m;
    while ((m = re.exec(src))) found.add(m[1]);
    [...found].sort().forEach((n) => console.log(n));
    console.error(`\n${found.size} icons available`);
  } catch (e) {
    console.error("Could not enumerate catalog:", e.message);
  }
}
