#!/usr/bin/env node
/**
 * Content-preservation ledger for the hallmark retheme (local-only check).
 *
 * The redesign must preserve the count of every structural interactive marker. This script scans the
 * Vue sources for structural markers (links, form fields, interactive
 * primitives, event bindings) and compares them against the baseline recorded
 * in .redesign/before/ledger.json before any redesign edit landed.
 *
 * It complements two other preservation checks:
 *   - hallmark's native `--kept` source ledger (.hallmark/before.json)
 *   - the manual DOM pass captured in ledger.json's `dom` section (via IAB)
 *
 * Usage:
 *   node tests/check_ui_ledger.js --record   # write baseline (before editing)
 *   node tests/check_ui_ledger.js            # compare current sources to baseline
 *
 * Local-only like tests/ui_smoke.py: needs no dev server, but is not part of
 * CI because the DOM section of the ledger is captured from a live browser.
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readdirSync, statSync } from 'node:fs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'frontend', 'src');
const LEDGER = join(ROOT, '.redesign', 'before', 'ledger.json');

const METRICS = {
  routerLinks: /<RouterLink\b/g,
  anchorLinks: /<a\s[^>]*href=/g,
  inputTags: /<Input\b|<input\b/g,
  textareaTags: /<Textarea\b|<textarea\b/g,
  selectTriggers: /<SelectTrigger\b/g,
  switchTags: /<Switch\b/g,
  checkboxTags: /<Checkbox\b/g,
  sliderTags: /<Slider\b/g,
  toggleGroupTags: /<ToggleGroup\b/g,
  buttonTags: /<Button\b|<button\b/g,
  clickHandlers: /@click/g,
  updateHandlers: /@update:/g,
  submitHandlers: /@submit/g,
};

function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    const st = statSync(p);
    if (st.isDirectory()) yield* walk(p);
    else if (entry.endsWith('.vue')) yield p;
  }
}

function scanSources() {
  const totals = Object.fromEntries(Object.keys(METRICS).map((k) => [k, 0]));
  const perFile = {};
  for (const file of walk(SRC)) {
    const text = readFileSync(file, 'utf8');
    const counts = {};
    for (const [name, re] of Object.entries(METRICS)) {
      const n = (text.match(re) ?? []).length;
      counts[name] = n;
      totals[name] += n;
    }
    perFile[file.replace(SRC + '\\', '').replace(SRC + '/', '')] = counts;
  }
  return { totals, perFile };
}

const mode = process.argv.includes('--record') ? 'record' : 'check';

if (!existsSync(LEDGER)) {
  console.error(`ledger baseline missing: ${LEDGER}`);
  console.error('Run with --record on the pristine sources first.');
  process.exit(2);
}
const baseline = JSON.parse(readFileSync(LEDGER, 'utf8'));

if (mode === 'record') {
  baseline.static = scanSources();
  writeFileSync(LEDGER, JSON.stringify(baseline, null, 2));
  console.log('recorded static baseline into', LEDGER);
  console.log(JSON.stringify(baseline.static.totals, null, 2));
  process.exit(0);
}

if (!baseline.static) {
  console.error('ledger has no static section — run --record first.');
  process.exit(2);
}

const current = scanSources();
let failures = 0;
console.log('metric            baseline  current  delta');
for (const [name, re] of Object.entries(METRICS)) {
  void re;
  const b = baseline.static.totals[name] ?? 0;
  const c = current.totals[name] ?? 0;
  const delta = c - b;
  const mark = delta === 0 ? 'ok' : 'FAIL';
  if (delta !== 0) failures += 1;
  console.log(
    `${name.padEnd(18)}${String(b).padStart(8)}${String(c).padStart(9)}${String(delta).padStart(7)}  ${mark}`,
  );
}

if (failures > 0) {
  console.error(`\n${failures} metric(s) drifted from the baseline.`);
  console.error('The redesign must preserve every interactive element.');
  console.error('Per-metric diffs by file (baseline -> current):');
  for (const [name] of Object.entries(METRICS)) {
    const files = new Set([...Object.keys(baseline.static.perFile), ...Object.keys(current.perFile)]);
    for (const f of files) {
      const b = baseline.static.perFile[f]?.[name] ?? 0;
      const c = current.perFile[f]?.[name] ?? 0;
      if (b !== c) console.error(`  ${name}  ${f}: ${b} -> ${c}`);
    }
  }
  process.exit(1);
}
console.log('\nkept-ledger: all static metrics preserved.');
