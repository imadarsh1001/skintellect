/* Unit checks for the SPA evidence semantics, the v-html sanitizer contract,
 * and color contrast of the theme tokens. Does not test browser layout.
 *
 * The legacy workspace.js unit checks were retired with the legacy pages
 * (Stage 5): the same evidence-summary behaviors now live in
 * frontend/src/lib/evidence-summary.ts and are imported here directly (Node >= 26
 * strips TypeScript types natively). */
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const assert = require('node:assert/strict');

const FRONTEND = path.join(__dirname, '../frontend');

let assertions = 0;
function check(condition, message) { assert.ok(condition, message); assertions++; }

(async () => {
  // --- Evidence summary semantics (shared by StudyView/ResearchView) ---
  const evidence = await import(pathToFileURL(path.join(FRONTEND, 'src/lib/evidence-summary.ts')).href);
  const insights = (aspects, unique = 10, gemini = 6) => ({ unique_reviews: unique, gemini_reviews: gemini, aspects });

  const model = evidence.buildSummaryModel(
    insights([
      { aspect: 'texture', mentioning_reviews: 5, positive_reviews: 3, negative_reviews: 2, mixed_reviews: 0, neutral_reviews: 0 },
      { aspect: 'scent', mentioning_reviews: 2, positive_reviews: 2, negative_reviews: 0, mixed_reviews: 0, neutral_reviews: 0 },
    ]),
  );
  check(model.cards[0].label === 'Texture & feel', 'Most-mentioned theme comes from counts, not array order');
  check(model.cards[0].mentioning === 5 && model.cards[0].denominator === 10, 'Counts retain the collected-review denominator');
  check(model.cards[0].tone === 'mixed', 'Opposing sentiments are identified as differing experiences');
  check(model.cards[1].label === 'Scent', 'Known aspect ids receive readable display labels');
  check(!model.showsDifferingExperiences || model.cards.some(c => c.tone === 'mixed'), 'Mixed flag tracks card tones');

  const mixedOnly = evidence.buildSummaryModel(
    insights([{ aspect: 'hydration', mentioning_reviews: 2, positive_reviews: 0, negative_reviews: 0, mixed_reviews: 2, neutral_reviews: 0 }], 4, 4),
  );
  check(mixedOnly.showsDifferingExperiences, 'Mixed observations are identified even without separate positive/negative counts');

  const oneSided = evidence.buildSummaryModel(
    insights([{ aspect: 'hydration', mentioning_reviews: 2, positive_reviews: 2, negative_reviews: 0, mixed_reviews: 0, neutral_reviews: 0 }], 4, 2),
  );
  check(oneSided.oneSidedSample, 'One-sided extracted sample does not imply consensus');

  const empty = evidence.buildSummaryModel({ unique_reviews: 4, gemini_reviews: 0, aspects: [] });
  check(empty.cards.length === 0 && !empty.showsDifferingExperiences, 'Empty extraction produces no invented highlights');

  check(evidence.aspectLabel('white_cast') === 'White Cast', 'New aspect IDs receive readable display labels');
  check(evidence.aspectLabel('constructor') === 'Constructor', 'New aspect IDs do not resolve inherited object properties');

  const observations = [
    { aspect: 'texture', sentiment: 'negative', span: 'Sticky', evidence_id: 'review:1' },
    { aspect: 'texture', sentiment: 'positive', span: 'Smooth', evidence_id: 'review:2' },
    { aspect: 'hydration', sentiment: 'negative', span: 'Dry', evidence_id: 'review:3' },
    { topic: 'scent', span: 'No sentiment label' },
  ];
  check(evidence.filterObservations(observations, 'texture', 'negative').length === 1, 'Theme and experience filters are combined');
  check(evidence.filterObservations(observations, 'texture', 'negative')[0].span === 'Sticky', 'Filtered result keeps its exact source excerpt');
  check(evidence.filterObservations(observations, '', 'negative').length === 2, 'All-theme filter includes negative observations across themes');
  check(evidence.filterObservations(observations, 'hydration', 'positive').length === 0, 'No-match combination returns empty results');
  check(evidence.filterObservations(observations, 'scent', 'unspecified').length === 1, 'Unlabeled sentiment remains discoverable');
  check(evidence.filterObservations(observations).length === 4 && observations.length === 4, 'Clearing filters restores all observations without mutating input');

  // --- v-html sanitizer contract: every v-html binding must be sanitized ---
  const vueFiles = [];
  (function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name.endsWith('.vue')) vueFiles.push(full);
    }
  })(path.join(FRONTEND, 'src'));
  const vhtmlLines = vueFiles.flatMap(f =>
    fs.readFileSync(f, 'utf8').split('\n')
      .map((line, idx) => ({ file: path.relative(FRONTEND, f), line: idx + 1, text: line }))
      .filter(l => l.text.includes('v-html')),
  );
  check(vhtmlLines.length >= 1, 'SPA markdown rendering uses v-html (sanitized)');
  for (const line of vhtmlLines) {
    check(line.text.includes('renderMarkdown('), `v-html is bound to renderMarkdown (sanitized): ${line.file}:${line.line}`);
  }
  const markdownModule = fs.readFileSync(path.join(FRONTEND, 'src/lib/markdown.ts'), 'utf8');
  check(markdownModule.includes('DOMPurify.sanitize'), 'Copilot markdown is sanitized with DOMPurify before v-html');

  // --- Contrast: theme tokens from the Tailwind v4 CSS entry ---
  function luminance(hex) {
    const c = hex.match(/[a-f0-9]{2}/gi).map(x => parseInt(x, 16) / 255).map(x => x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4);
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2];
  }
  function hslToHex(h, s, l) {
    s /= 100; l /= 100;
    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
    const to255 = x => Math.round(255 * x).toString(16).padStart(2, '0');
    return `#${to255(f(0))}${to255(f(8))}${to255(f(4))}`;
  }
  const css = fs.readFileSync(path.join(FRONTEND, 'src/assets/index.css'), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');
  function token(name) {
    const m = css.match(new RegExp(`--color-${name}\\s*:\\s*([^;]+);`));
    assert.ok(m, `CSS token exists: --color-${name}`);
    return m[1].trim();
  }
  function rootHsl(name) {
    const m = css.match(new RegExp(`--${name}\\s*:\\s*([\\d.]+)\\s+([\\d.]+)%\\s+([\\d.]+)%`));
    assert.ok(m, `HSL variable exists: --${name}`);
    return hslToHex(Number(m[1]), Number(m[2]), Number(m[3]));
  }
  const pairs = [
    ['verified', token('evidence-verified'), token('evidence-verified-bg')],
    ['source', token('evidence-source'), token('evidence-source-bg')],
    ['unknown', token('evidence-unknown'), token('evidence-unknown-bg')],
    ['negative', token('evidence-negative'), token('evidence-negative-bg')],
    ['mixed', token('evidence-mixed'), token('evidence-mixed-bg')],
    ['body', rootHsl('foreground'), rootHsl('background')],
    ['muted', rootHsl('muted-foreground'), rootHsl('background')],
  ];
  const contrast = pairs.map(([name, foreground, background]) => {
    const a = luminance(foreground), b = luminance(background);
    const ratio = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    check(ratio >= 4.5, name + ' text contrast is at least 4.5:1');
    return { name, foreground, background, ratio: Number(ratio.toFixed(2)) };
  });

  const report = { kind: 'ui_semantic_unit_checks', passed: true, assertions, contrast_pairs: contrast, browser_layout_tested: false, provider_calls: 0 };
  fs.mkdirSync(path.join(__dirname, '../reports/latest'), { recursive: true });
  fs.writeFileSync(path.join(__dirname, '../reports/latest/ui-semantics.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
