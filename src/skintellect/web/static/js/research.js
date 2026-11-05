/* Research UI: natural question first; editable filters and diagnostics on demand. */
const {text,button,badge,api,details,raw,aspect,reviewSummary,evidence,observation,quoteExplorer,status}=Studio;
const $=id=>document.getElementById(id);
const split=value=>value.split(',').map(x=>x.trim()).filter(Boolean);
const params=new URLSearchParams(location.search);
let preparedIds=[];
let unresolved=[];
let busy=false;
if(params.get('query')) $('query').value=params.get('query').slice(0,2000);
$('demo-scope').checked=params.get('demo')==='1';
$('query').maxLength=2000;

function filters() {
  return {category:$('category').value,domain:$('domain').value,required_ingredients:split($('required').value),excluded_ingredients:split($('excluded').value),preferred_price_tiers:$('price').value?[$('price').value]:[],limit:10};
}
function scope() {
  if($('demo-scope').checked&&!preparedIds.length) throw new Error('The prepared group is still loading or unavailable. Try again shortly, or switch to the full catalog.');
  return $('demo-scope').checked?[...preparedIds]:null;
}
function question() {
  const value=$('query').value.trim();
  if(!value) throw new Error('Enter a question or choose an example first.');
  return value;
}
function showIntent(intent) {
  $('category').value=intent.category; $('domain').value=intent.domain;
  $('required').value=intent.required_ingredients.join(', '); $('excluded').value=intent.excluded_ingredients.join(', ');
  $('price').value=intent.preferred_price_tiers[0]||'';
  unresolved=intent.unresolved_terms||[];
  $('clarification').hidden=!unresolved.length;
  $('clarification').textContent=unresolved.join('\n')+'\nPlease review the filters before searching.';
  if(unresolved.length) $('filter-details').open=true;
}
async function run(action,label='Working…') {
  if(busy) return;
  busy=true;
  const old=$('assistant').textContent;
  for(const id of ['assistant','interpret','search']) $(id).disabled=true;
  $('assistant').textContent=label;
  try { await action(); }
  catch(e) { status($('status'),e.message,'error'); }
  finally { busy=false; $('assistant').textContent=old; for(const id of ['assistant','interpret','search']) $(id).disabled=false; }
}
async function reviewPanel(id,parent) {
  parent.replaceChildren();
  text('p','Loading review themes…',parent,'skeleton');
  const r=await api('/products/'+id+'/review-insights'); parent.replaceChildren();
  reviewSummary(r,parent);
  quoteExplorer(r.observations,parent);
  if(r.gemini_reviews<r.unique_reviews) {
    const prep=details('Analyze additional reviews with Gemini',parent);
    text('p','This action sends up to 10 unprocessed reviews to Gemini and may incur API charges. Existing observations remain available.',prep,'note');
    let b;
    b=button('Analyze up to 10 more reviews',async()=>{
      b.disabled=true; b.textContent='Analyzing…';
      try { await api('/research/reviews/prepare',{product_id:id,limit:10}); await reviewPanel(id,parent); }
      catch(e) { text('p',e.message,prep,'notice'); b.disabled=false; b.textContent='Try analyzing again'; }
    },prep);
  }
}
function renderResults(result,selectedScope) {
  $('answer').hidden=true; $('answer').replaceChildren(); $('results').replaceChildren();
  $('empty-state').hidden=!!result.products.length;
  $('result-heading').hidden=!result.products.length;
  $('result-count').textContent=result.total+' match'+(result.total===1?'':'es')+' in '+(selectedScope?'the prepared group':'the catalog')+'. Showing '+result.products.length+'.';
  if(!result.products.length) {
    $('empty-state').replaceChildren(); text('h2',result.needs_clarification?.length?'Please clarify the question':'No products match these filters',$('empty-state'));
    text('p',result.needs_clarification?.length?'Open the filters above and resolve the highlighted request.':result.unknown_count?'Some products could not be evaluated because ingredient-list completeness is unknown. An exclusion is not treated as safe just because it is missing from an unverified list.':'Try a different ingredient or category. You can also turn off prepared-group scope to search the wider catalog.',$('empty-state'));
  }
  const notes=[];
  if(result.unknown_count) notes.push(result.unknown_count+' products withheld because the ingredient constraints could not be verified.');
  if(result.failed_count) notes.push(result.failed_count+' products did not meet the ingredient constraints.');
  if(result.needs_clarification?.length) notes.push('Please review the filters above.');
  status($('status'),notes.join(' ')||('Search complete. '+result.total+' matching product'+(result.total===1?'':'s')+'.'));
  const constraints=JSON.parse(JSON.stringify(result.intent||filters()));
  for(const p of result.products) {
    const card=text('article',undefined,$('results'),'product-card');
    text('span',p.brand,card,'brand'); text('h2',p.name,card);
    const tags=text('div',undefined,card,'chips');
    if(p.price_tier) badge('Price tier '+p.price_tier,tags,'info');
    badge(p.formula_status==='verified_complete'?'Complete list verified':'Ingredient list unverified',tags,p.formula_status==='verified_complete'?'good':'warning');
    for(const c of p.checks) {
      const [kind,...name]=c.constraint.split(':');
      text('p',(kind==='require'?'Contains ':'Excludes ')+name.join(':')+(c.status==='pass'?' — supported by the recorded list':''),card,'hint');
    }
    evidence(p.evidence_id,card,'View ingredient list & source');
    const reviews=details('What stands out in the reviews?',card);
    let reviewsLoaded=false;
    reviews.addEventListener('toggle',async()=>{
      if(!reviews.open||reviewsLoaded) return;
      reviewsLoaded=true; reviews.querySelector('.notice')?.remove(); const body=text('div',undefined,reviews);
      try { await reviewPanel(p.id,body); }
      catch(e) { reviewsLoaded=false; body.remove(); text('p',e.message,reviews,'notice'); }
    });
    const alternatives=details('What changes in a similar formula?',card);
    let alternativesLoaded=false;
    alternatives.addEventListener('toggle',async()=>{
      if(!alternatives.open||alternativesLoaded) return;
      alternativesLoaded=true; const body=text('div','Loading comparable formulas…',alternatives);
      try {
        const r=await api('/alternatives',{product_id:p.id,constraints,product_ids:selectedScope}); body.replaceChildren();
        if(!r.alternatives.length) text('p','No alternative meets these constraints in the selected group.',body);
        for(const a of r.alternatives.slice(0,5)) {
          const row=text('div',undefined,body,'selection'); text('h3',a.name,row); text('p',a.brand,row,'hint');
          text('p','Shared ingredients: '+a.shared_ingredients.join(', '),row,'ingredients');
          evidence(a.evidence_id,row,'Read this ingredient list');
          const comparison=details('Ingredient differences',row);
          text('p','Only in the original: '+(a.removed_ingredients.join(', ')||'None'),comparison,'ingredients');
          text('p','Only in the alternative: '+(a.added_ingredients.join(', ')||'None'),comparison,'ingredients');
        }
        text('p','Ingredient overlap does not establish equal concentrations, performance, or suitability.',body,'disclaimer');
      } catch(e) { alternativesLoaded=false; body.textContent=e.message; }
    });
  }
}
function renderAnswer(r) {
  const panel=$('answer'); panel.hidden=false;
  text('p','WHAT THE EVIDENCE SAYS',panel,'eyebrow'); text('h2','Here is what the sources reveal',panel);
  text('p',r.search.total+' product'+(r.search.total===1?'':'s')+' met the ingredient filters. The quotes below come directly from the collected sources.',panel);
  for(const s of r.synthesis?.selections||[]) {
    const q=observation(s,panel); badge(s.kind==='reported_experience'?'Reviewer experience':'Catalog wording',q.querySelector('.quote-meta'));
  }
  if(!r.synthesis?.selections?.length) text('p','No supported excerpts could be selected. You can still read product sources and available review themes below.',panel,'notice');
  for(const group of r.alternatives||[]) {
    text('h3','An ingredient-based alternative',panel);
    if(!group.alternatives.length) text('p','No alternative meets these constraints in the selected group.',panel);
    for(const a of group.alternatives.slice(0,1)) {
      const row=text('div',undefined,panel,'selection'); text('h3',a.brand+' — '+a.name,row);
      text('p','Shared ingredients: '+a.shared_ingredients.join(', '),row,'ingredients'); evidence(a.evidence_id,row,'Inspect this alternative’s ingredient list');
    }
    text('p','Shared ingredients indicate overlap. Concentrations and results may differ.',panel,'note');
  }
  if(r.synthesis?.unanswered_topics?.length) text('p','Still unclear: '+r.synthesis.unanswered_topics.join('; '),panel,'notice');
  if(r.references?.length) {
    const refs=details('Background references for this question',panel);
    for(const ref of r.references) { text('h3',ref.title,refs); text('p',ref.summary,refs); evidence(ref.evidence_id,refs,'Read this reference and its limits'); }
  }
  text('p','These are collected experiences and catalog records. Individual suitability and clinical performance are not established.',panel,'disclaimer');
}

$('assistant').onclick=()=>run(async()=>{
  const selectedScope=scope(); const q=question();
  status($('status'),'Finding matching products and checking source excerpts. A new question can take up to two minutes.','loading');
  const r=await api('/assistant/query',{query:q,product_ids:selectedScope});
  showIntent(r.search.intent); renderResults(r.search,selectedScope);
  $('trace').textContent=JSON.stringify(r.trace,null,2);
  if(!r.search.needs_clarification?.length&&r.search.products.length) renderAnswer(r);
},'Finding evidence…');
$('interpret').onclick=()=>run(async()=>{
  status($('status'),'Reading the ingredient filters in your question…','loading');
  const r=await api('/search/interpret',{query:question()}); showIntent(r.intent);
  status($('status'),unresolved.length?'Please resolve the highlighted filters.':'Filters are filled. You can edit them and search.');
},'Reading question…');
$('search').onclick=()=>run(async()=>{
  const selectedScope=scope(); $('clarification').hidden=true;
  status($('status'),'Checking the selected ingredient filters…','loading');
  const r=await api('/search',{...filters(),product_ids:selectedScope});
  renderResults(r,selectedScope); $('trace').textContent='This search used the editable filters directly, without model planning.';
},'Searching…');
document.querySelectorAll('[data-query]').forEach(b=>b.onclick=()=>{$('query').value=b.dataset.query; $('query').focus();});
Promise.allSettled([
  api('/research/demo').then(d=>{preparedIds=d.product_ids; $('demo-status').textContent=d.configured?(d.ready?'Prepared group ready: ':'Prepared group still processing: ')+d.products.length+' products with review evidence.':'The prepared group is unavailable. The full catalog is still searchable.';}),
  api('/research/status').then(s=>{$('model-status').textContent=s.enabled?'AI service available: '+s.model+'. '+s.indexed_vectors+' passages have a search vector.':'AI is unavailable. Direct filters and saved evidence are still usable.';}),
  api('/quality').then(q=>{$('quality').textContent=q.products.toLocaleString()+' catalog products; '+q.formulas_present+' recorded ingredient lists; '+q.verified_complete+' verified complete lists. '+q.truncated_reviews+' reviews contain truncated text.';})
]).then(results=>{
  if(results[0].status==='rejected') $('demo-status').textContent='Prepared-group information could not load. Try the full catalog.';
  if(results[1].status==='rejected') $('model-status').textContent='AI service status could not load.';
  if(results[2].status==='rejected') $('quality').textContent='Catalog coverage could not load.';
});
