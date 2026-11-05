/* Start page: findings first; diagnostics stay behind explicit disclosures. */
const {text,button,badge,api,safeLink,details,raw,table,stat,reviewSummary,evidence,observation,quoteExplorer,aspect,status}=Studio;
const byId=id=>document.getElementById(id);
let detailRequest=0;
let detailTrigger=null;
const reviewCache=new Map();
function savedReviews(id) {
  if(!reviewCache.has(id)) reviewCache.set(id,api('/products/'+id+'/review-insights').catch(error=>{reviewCache.delete(id);throw error;}));
  return reviewCache.get(id);
}
async function previewReviews(product,parent) {
  try {
    const r=await savedReviews(product.id); parent.replaceChildren();
    const ranked=[...r.aspects].sort((a,b)=>b.mentioning_reviews-a.mentioning_reviews);
    if(!ranked.length) {text('p','Review themes have not been extracted yet.',parent,'hint'); return;}
    text('p','FROM THE COLLECTED REVIEWS',parent,'eyebrow');
    text('strong',aspect(ranked[0].aspect),parent);
    text('p','Mentioned in '+ranked[0].mentioning_reviews+' of '+r.unique_reviews+' collected reviews.',parent,'hint');
    const topics=text('div',undefined,parent,'chips');
    ranked.slice(1,3).forEach(a=>badge(aspect(a.aspect),topics,'info'));
  } catch { parent.replaceChildren(); text('p','Snapshot unavailable. Open the product to retry.',parent,'hint'); }
}

async function inspectProduct(product,trigger) {
  const request=++detailRequest;
  detailTrigger=trigger;
  const panel=byId('product-detail');
  panel.hidden=false;
  byId('detail-title').textContent=product.name;
  const body=byId('detail-body'); body.replaceChildren();
  text('p','Loading review themes and recorded ingredients…',body,'skeleton');
  panel.focus(); panel.scrollIntoView?.({block:'start',behavior:'auto'});
  trigger.disabled=true;
  try {
    const [reviewResult,graphResult]=await Promise.allSettled([savedReviews(product.id),api('/products/'+product.id+'/connections')]);
    if(reviewResult.status==='rejected') throw reviewResult.reason;
    const reviews=reviewResult.value;
    const graph=graphResult.status==='fulfilled'?graphResult.value:null;
    if(request!==detailRequest) return;
    body.replaceChildren();
    badge('Collected review evidence',body,'info');
    const summary=text('section',undefined,body,'section-divider');
    text('h3','What reviewers mention',summary); reviewSummary(reviews,summary);
    text('h3','Read their own words',body);
    quoteExplorer(reviews.observations,body);
    const formula=details('Recorded ingredient list',body);
    evidence('product:'+product.id,formula,'Read the catalog source and ingredient list');
    const related=details('Which formulas share these ingredients?',body);
    text('p','Shared ingredient names show an overlap, not equal concentration, performance, or suitability.',related,'note');
    for(const p of graph?.paths||[]) {
      const row=text('article',undefined,related,'source-card'); text('h3',p.name,row);
      const chips=text('div',undefined,row,'chips'); p.shared_ingredients.forEach(n=>badge(n,chips));
      evidence('product:'+p.product_id,row,'View this product’s recorded ingredients');
    }
    if(!graph) text('p','Related ingredient lists could not load. Close this product and open it again to retry.',related,'notice');
    else {
      if(!graph.paths.length) text('p','No connected formulas are available.',related);
      raw('Technical graph data',graph,related);
    }
  } catch(e) {
    if(request===detailRequest) { body.replaceChildren(); text('p',e.message,body,'notice'); }
  } finally { trigger.disabled=false; }
}

function renderEvaluation(d) {
  const target=byId('evaluation'); target.replaceChildren();
  const e=d.evaluation;
  if(!e) { text('p','A quality-check report is not available yet.',target); return; }
  badge(d.evaluation_current?'Report matches current study data':'Report needs to be rerun',target,d.evaluation_current?'good':'warning');
  const a=e.review_agreement;
  const warm=e.latency.measurements.at(-1);
  table(['Check','Result','How to read it'],[
    ['Source quotes',a.reviews+' reviews checked; '+a.invalid_model_source_spans+' invalid quote spans','Checks that displayed text exists in its source.'],
    ['Rules vs. Gemini',a.exact_set_agreement===null?'Not available':(a.exact_set_agreement*100).toFixed(1)+'% exact agreement','The methods disagree often. Agreement alone does not establish correctness.'],
    ['Search comparison',e.retrieval.cases.length+' generated test queries','A small engineering benchmark, not a human relevance assessment.'],
    ['Repeated-query speed',warm?(warm.elapsed_ms/1000).toFixed(2)+' seconds':'Not measured','These requests reused caches. New questions can take much longer.']
  ],target);
  text('p','Product suitability, formula completeness, and clinical performance have not been validated.',target,'disclaimer');
  const metrics=byId('evaluation-metrics'); metrics.replaceChildren();
  text('p','MRR measures how early a generated relevant result appears. Recall@3 measures how many generated relevant results are in the first three. Literal-match labels favor keyword search.',metrics,'note');
  table(['Search method','MRR (top 10)','Recall@3'],Object.entries(e.retrieval.summary).map(([mode,v])=>[mode==='lexical'?'Keyword':mode==='semantic'?'Meaning-based':'Combined',v.mrr.toFixed(3),v.recall_at_3.toFixed(3)]),metrics);
  text('p',e.latency.limitation,metrics,'note');
  byId('evaluation-json').textContent=JSON.stringify(e,null,2);
}

async function loadStudy() {
  try {
    const d=await api('/research/demo');
    status(byId('status'),d.configured?(d.ready?'The prepared products are ready to explore.':'Some evidence is still being prepared. You can browse the available records.'):'No prepared group is available yet.',d.ready?'ready':'loading');
    byId('query').textContent=d.example_query||'Find products and explore their collected reviews.';
    byId('try-query').href=d.configured?'/research?demo=1&query='+encodeURIComponent(d.example_query||''):'/research';
    byId('limits').textContent='This small group is a demonstration, not a market-wide comparison. Recorded ingredient lists have not been verified complete.';
    byId('products').replaceChildren();
    const overview=byId('study-overview'); overview.replaceChildren();
    const totalReviews=d.products.reduce((n,p)=>n+p.reviews.processed,0);
    const totalPassages=d.products.reduce((n,p)=>n+p.passages.indexed,0);
    for(const item of [
      {label:'PREPARED STUDY',value:d.products.filter(p=>p.ready).length+' / '+d.products.length,description:'Products with selected evidence prepared.',tone:'ready'},
      {label:'FOLLOW THE SOURCES',value:totalReviews+' reviews',description:totalPassages+' passages indexed for search.',tone:'info'},
      {label:'KEEP THE LIMITS VISIBLE',value:'Lists unverified',description:'Missing text does not establish absence.',tone:'unknown'}
    ]) {
      const card=text('article',undefined,overview,'overview-card'); card.dataset.tone=item.tone;
      text('p',item.label,card,'eyebrow'); text('strong',item.value,card); text('p',item.description,card);
    }
    for(const p of d.products) {
      const card=text('article',undefined,byId('products'),'product-card');
      card.dataset.state=p.ready?'ready':'pending';
      text('span',p.brand,card,'brand'); text('h2',p.name,card);
      badge(p.ready?'Review evidence ready':'Preparation in progress',card,p.ready?'good':'warning');
      const stats=text('div',undefined,card,'stat-grid');
      stat(p.reviews.processed+'/'+p.reviews.eligible,'reviews analyzed',stats);
      stat(p.passages.indexed+'/'+p.passages.eligible,'passages searchable',stats);
      const preview=text('div','Loading review snapshot.',card,'review-preview');
      previewReviews(p,preview);
      const preparation=details('Preparation counts',card);
      preparation.append(stats);
      const action=text('div',undefined,card,'card-action');
      let b; b=button('Uncover the evidence',()=>inspectProduct(p,b),action,'');
      const option=text('option',p.brand+' — '+p.name,byId('label-product')); option.value=p.id;
    }
    if(!d.products.length) text('p','No prepared products are available. You can still search the catalog.',byId('products'),'empty-state');
    renderEvaluation(d);
  } catch(e) { status(byId('status'),e.message,'error'); }
}

async function loadReferences() {
  const parent=byId('references');
  try {
    const r=await api('/research/references'); parent.replaceChildren();
    for(const ref of r.references) {
      const card=text('article',undefined,parent,'source-card');
      badge(ref.source_type==='regulatory_guidance'?'Labeling guidance':ref.source_type==='primary_study_abstract'?'Study abstract':'Professional guidance',card);
      text('h3',ref.title,card); text('p',ref.publisher+' · Checked '+ref.retrieved_at,card,'hint');
      text('p',ref.summary,card); safeLink(ref.url,'Read the original reference',card);
      const context=details('Source excerpt and limits',card); text('blockquote',ref.quote,context); text('p',ref.limitations,context,'note');
    }
    if(!r.references.length) text('p','No reference notes are available yet.',parent);
  } catch(e) { text('p',e.message,parent,'notice'); }
}

byId('close-detail').onclick=()=>{detailRequest++; byId('product-detail').hidden=true; detailTrigger?.focus();};
byId('label-form').onsubmit=async e=>{
  e.preventDefault(); const file=byId('label-file').files[0]; if(!file) return;
  const output=byId('label-output'); output.replaceChildren();
  if(file.size>6000000||!['image/png','image/jpeg'].includes(file.type)) {text('p','Choose a PNG or JPEG smaller than 6 MB.',output,'notice'); return;}
  byId('transcribe').disabled=true; byId('transcribe').textContent='Reading label…';
  text('p','Reading the visible ingredient names. This may take a minute.',output,'skeleton');
  try {
    const data=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]);reader.onerror=()=>reject(new Error('This image could not be opened.'));reader.readAsDataURL(file);});
    const r=await api('/research/label',{data_b64:data,mime_type:file.type,product_id:byId('label-product').value?Number(byId('label-product').value):null});
    output.replaceChildren(); text('h3','Visible ingredients',output);
    const chips=text('div',undefined,output,'chips'); r.extraction.ingredients.forEach(n=>badge(n,chips));
    if(!r.extraction.ingredients.length) text('p','No readable ingredient names were found. Try a clearer photo.',output);
    text('p','Uncertain text: '+(r.extraction.uncertain_text.join('; ')||'None flagged by the model. This still needs checking.'),output,'note');
    if(r.comparison) {
      text('h3','Comparison with the recorded list',output);
      table(['Group','Ingredient names'],[['Found in both',r.comparison.shared.join(', ')||'None'],['Visible in photo only',r.comparison.image_only.join(', ')||'None'],['Catalog only',r.comparison.catalog_only.join(', ')||'None']],output);
    }
    text('p','This is an experimental transcription. Packaging, markets, and formula versions may differ. The catalog has not been changed.',output,'disclaimer');
  } catch(error) { output.replaceChildren(); text('p',error.message,output,'notice'); }
  finally { byId('transcribe').disabled=false; byId('transcribe').textContent='Read label'; }
};
Promise.allSettled([loadStudy(),loadReferences()]);

document.querySelectorAll('[data-explore]').forEach(b=>b.addEventListener('click',()=>{const tab=byId(b.dataset.explore); tab.click(); tab.focus(); tab.scrollIntoView?.({block:'center',behavior:'auto'});}));
