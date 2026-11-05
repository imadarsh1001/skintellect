/* Unit checks for evidence summaries and color contrast. Does not test browser layout. */
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.dataset={}; this.className=''; this.value=''; this._text=''; this.events={}; this.attributes={}; }
  append(child) { if(child.parent)child.parent.children=child.parent.children.filter(c=>c!==child);child.parent=this;this.children.push(child); }
  replaceChildren(...children) {this.children=[];this._text='';children.forEach(c=>this.append(c));}
  setAttribute(key,value) {this.attributes[key]=value;}
  addEventListener(name,handler) {this.events[name]=handler;}
  set textContent(value) { this._text=String(value); this.children=[]; }
  get textContent() { return this._text+this.children.map(c=>c.textContent).join(' '); }
}
const context={window:{},document:{createElement:tag=>new Element(tag),querySelectorAll:()=>[]}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../src/skintellect/web/static/js/workspace.js'),'utf8'),context);
const ui=context.window.Studio;
let assertions=0;
function check(condition,message) { assert.ok(condition,message); assertions++; }
const root=()=>new Element('div');
const theme=(aspect,count,positive,negative,mixed=0)=>({aspect,mentioning_reviews:count,positive_reviews:positive,negative_reviews:negative,mixed_reviews:mixed,neutral_reviews:0});
let view=root();
ui.reviewSummary({unique_reviews:10,gemini_reviews:6,aspects:[theme('scent',2,2,0),theme('texture',5,3,2)]},view);
let cards=view.children.find(n=>n.className==='insight-grid').children;
check(cards[0].textContent.includes('Texture & feel'),'Most-mentioned theme comes from counts, not array order');
check(cards[0].textContent.includes('5 of 10'),'Counts retain the collected-review denominator');
check(cards[1].dataset.tone==='mixed'&&cards[1].textContent.includes('Texture & feel'),'Opposing sentiments are identified as differing experiences');
check(view.children.some(n=>n.className==='table-wrap'&&n.children[0].className==='review-table'),'Sentiment table has its semantic color hook');
view=root();ui.reviewSummary({unique_reviews:4,gemini_reviews:4,aspects:[theme('hydration',2,0,0,2)]},view);
check(view.textContent.includes('EXPERIENCES DIFFER'),'Mixed observations are identified even without separate positive/negative counts');
view=root();ui.reviewSummary({unique_reviews:4,gemini_reviews:2,aspects:[theme('hydration',2,2,0)]},view);
check(view.textContent.includes('does not establish that reviewers agree'),'One-sided extracted sample does not imply consensus');
view=root();ui.reviewSummary({unique_reviews:4,gemini_reviews:0,aspects:[]},view);
check(!view.children.some(n=>n.className==='insight-grid'),'Empty extraction produces no invented highlights');
view=root();ui.insight('<img src=x>','<script>bad()</script>',view);
check(view.children[0].children[1].textContent==='<img src=x>','Highlight titles are literal text');
check(view.children[0].children[2].textContent==='<script>bad()</script>','Highlight descriptions are literal text');
const observations=[{aspect:'texture',sentiment:'negative',span:'Sticky',evidence_id:'review:1'},{aspect:'texture',sentiment:'positive',span:'Smooth',evidence_id:'review:2'},{aspect:'hydration',sentiment:'negative',span:'Dry',evidence_id:'review:3'},{topic:'scent',span:'No sentiment label'}];
check(ui.filterObservations(observations,'texture','negative').length===1,'Theme and experience filters are combined');
check(ui.filterObservations(observations,'texture','negative')[0].span==='Sticky','Filtered result keeps its exact source excerpt');
check(ui.filterObservations(observations,'','negative').length===2,'All-theme filter includes negative observations across themes');
check(ui.filterObservations(observations,'hydration','positive').length===0,'No-match combination returns empty results');
check(ui.filterObservations(observations,'scent','unspecified').length===1,'Unlabeled sentiment remains discoverable');
check(ui.filterObservations(observations).length===4&&observations.length===4,'Clearing filters restores all observations without mutating input');
view=root();const explorer=ui.quoteExplorer(observations,view,1);
const controls=explorer.children[0],count=explorer.children[1],list=explorer.children[2],more=explorer.children[3];
const topic=controls.children[0].children[0],experience=controls.children[1].children[0],reset=controls.children[2];
check(count.textContent.includes('1 of 4')&&list.children.length===1,'Quote explorer paginates the initial observation set');
const firstQuote=list.children[0];more.events.click();
check(list.children.length===2&&list.children[0]===firstQuote,'Loading more keeps existing source disclosure elements');
topic.value='texture';topic.events.change();
check(count.textContent.includes('1 of 2'),'Changing theme resets pagination and updates the matching count');
experience.value='negative';experience.events.change();
check(count.textContent.includes('1 of 1')&&list.children[0].textContent.includes('Sticky'),'Experience filter renders only its exact matching excerpt');
topic.value='hydration';experience.value='positive';experience.events.change();
check(list.textContent.includes('No observations match both filters')&&more.hidden,'Empty filter combination has recovery guidance and hides pagination');
reset.events.click();
check(count.textContent.includes('1 of 4')&&reset.disabled&&!topic.value&&!experience.value,'Clear filters restores the initial set and clears both controls');
check(ui.aspect('white_cast')==='White Cast','New aspect IDs receive readable display labels');
check(ui.aspect('constructor')==='Constructor','New aspect IDs do not resolve inherited object properties');
function luminance(hex) {const c=hex.match(/[a-f0-9]{2}/gi).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2];}
const css=fs.readFileSync(path.join(__dirname,'../src/skintellect/web/static/css/workspace.css'),'utf8').replace(/\/\*[\s\S]*?\*\//g,'');
const rules=[...css.matchAll(/([^{}]+)\{([^{}]*)\}/g)];
function declaration(selector,property) {
  const matched=rules.filter(r=>r[1].split(',').some(s=>s.trim()===selector));
  let value;
  for(const r of matched) {
    const d=r[2].split(';').map(x=>x.split(':')).find(x=>x[0].trim()===property);
    if(d)value=d.slice(1).join(':').trim();
  }
  assert.ok(value,'CSS declaration exists: '+selector+' '+property);
  if(value.startsWith('var('))return declaration(':root',value.slice(4,-1));
  if(/^#[a-f0-9]{3}$/i.test(value))return '#'+value.slice(1).split('').map(x=>x+x).join('');
  return value;
}
const pairs=[['ready','.badge.good'],['source','.badge.info'],['unknown','.badge.warning'],['negative','.badge.negative'],['mixed','.badge.mixed'],['button','button']].map(([name,selector])=>[name,declaration(selector,'color'),declaration(selector,'background')]);
pairs.push(['body',declaration(':root','color'),declaration(':root','background')],['muted',declaration('p','color'),declaration('.panel','background')]);
const contrast=pairs.map(([name,foreground,background])=>{const a=luminance(foreground),b=luminance(background);const ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);check(ratio>=4.5,name+' text contrast is at least 4.5:1');return {name,foreground,background,ratio:Number(ratio.toFixed(2))};});
const report={kind:'ui_semantic_unit_checks',passed:true,assertions,contrast_pairs:contrast,browser_layout_tested:false,provider_calls:0};
fs.writeFileSync(path.join(__dirname,'../reports/latest/ui-semantics.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
