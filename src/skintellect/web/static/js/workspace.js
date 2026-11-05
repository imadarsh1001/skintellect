/* Shared text-only rendering. Source content never becomes trusted HTML. */
window.Studio = (() => {
  const labels = {texture:'Texture & feel',hydration:'Hydration',stickiness:'Stickiness',pilling:'Pilling',stinging:'Stinging & irritation',scent:'Scent',absorption:'Absorption',value:'Price & value'};
  function text(tag,value,parent,cls) {
    const n=document.createElement(tag);
    if(value!==undefined) n.textContent=value;
    if(cls) n.className=cls;
    if(parent) parent.append(n);
    return n;
  }
  function button(label,action,parent,cls='secondary') {
    const b=text('button',label,parent,cls); b.type='button'; b.addEventListener('click',action); return b;
  }
  const badge=(label,parent,tone='')=>text('span',label,parent,'badge '+tone);
  function errorMessage(detail,status) {
    const known={preparation_already_active:'A preparation task is already running. Wait for it or cancel it from Data progress.',disabled_or_missing_key:'Gemini is unavailable. You can still browse existing product evidence.',provider_network_or_json_error:'Gemini could not respond. Please try again; saved evidence is still available.',invalid_image_signature:'This file could not be read as an image. Choose a PNG or JPEG photograph.',invalid_image_encoding:'Choose a valid PNG or JPEG image.',unsupported_or_oversized_image:'Choose a PNG or JPEG image smaller than 6 MB.'};
    return known[detail]||(typeof detail==='string'&&!detail.includes('_')?detail:status===404?'That record is no longer available.':status===422?'Please check the fields or file format.':'We could not complete this request. Please try again.');
  }
  async function api(path,data) {
    const r=await fetch('/api'+path,data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
    let value;
    try { value=await r.json(); } catch { throw new Error('The server returned an unreadable response. Please try again.'); }
    if(!r.ok) throw new Error(errorMessage(value.detail,r.status));
    return value;
  }
  function safeLink(url,label,parent) {
    try {
      const u=new URL(url,location.origin);
      if(!['https:','http:'].includes(u.protocol)) return null;
      const a=text('a',label,parent); a.href=u.href; a.target='_blank'; a.rel='noopener noreferrer'; return a;
    } catch { return null; }
  }
  function details(label,parent,technical=false) {
    const d=text('details',undefined,parent,technical?'technical':''); text('summary',label,d); return d;
  }
  function raw(label,value,parent) { const d=details(label,parent,true); text('pre',JSON.stringify(value,null,2),d); return d; }
  const aspect=k=>Object.hasOwn(labels,k)?labels[k]:String(k||'Unlabeled').replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
  function table(headers,rows,parent) {
    const wrap=text('div',undefined,parent,'table-wrap'); const t=text('table',undefined,wrap);
    const head=text('tr',undefined,text('thead',undefined,t));
    headers.forEach(h=>{const th=text('th',h,head); th.scope='col';});
    const body=text('tbody',undefined,t);
    rows.forEach(row=>{const tr=text('tr',undefined,body); row.forEach(v=>text('td',String(v),tr));}); return t;
  }
  function stat(value,label,parent) { const s=text('div',undefined,parent,'stat'); text('strong',value,s); text('p',label,s,'hint'); return s; }
  function insight(title,description,parent,tone='info',label='AT A GLANCE') {
    const card=text('article',undefined,parent,'insight'); card.dataset.tone=tone;
    text('p',label,card,'eyebrow'); text('h3',title,card); text('p',description,card); return card;
  }
  function reviewSummary(result,parent) {
    text('p',result.unique_reviews+' collected reviews. '+(result.gemini_reviews||0)+' have been analyzed with Gemini.',parent,'hint');
    if(!result.aspects.length) {text('p','No supported review themes have been extracted yet.',parent); return;}
    const highlights=text('div',undefined,parent,'insight-grid');
    const ranked=[...result.aspects].sort((a,b)=>b.mentioning_reviews-a.mentioning_reviews);
    const top=ranked[0];
    insight(aspect(top.aspect),top.mentioning_reviews+' of '+result.unique_reviews+' collected reviews mention this theme. This is the most-mentioned theme in the extracted observations.',highlights,'info','MOST DISCUSSED');
    const differing=ranked.filter(a=>(a.positive_reviews>0&&a.negative_reviews>0)||a.mixed_reviews>0);
    if(differing.length) insight(differing.map(a=>aspect(a.aspect)).join(', '),'These themes include both positive and negative observations or mixed experiences. Read the quotes to understand the differences.',highlights,'mixed','EXPERIENCES DIFFER');
    else insight('Read beyond the counts','No theme has opposing or mixed observations in this extracted sample. This does not establish that reviewers agree or that all experiences were captured.',highlights,'unknown','SAMPLE LIMIT');
    const t=table(['Review theme','Mentioned in','Positive','Negative','Mixed / neutral'],result.aspects.map(a=>[aspect(a.aspect),a.mentioning_reviews+' reviews',a.positive_reviews,a.negative_reviews,(a.mixed_reviews||0)+' / '+(a.neutral_reviews||0)]),parent);
    t.className='review-table';
    text('p','Colors describe review sentiment, not product suitability. One review can discuss multiple themes or express mixed opinions.',parent,'note');
  }
  function evidence(id,parent,label='View source') {
    const d=details(label,parent); let loaded=false;
    d.addEventListener('toggle',async()=>{
      if(!d.open||loaded) return;
      loaded=true; d.querySelector('.source-details')?.remove(); const body=text('div','Loading source…',d,'source-details');
      try {
        const s=await api('/evidence/'+encodeURIComponent(id)); body.replaceChildren();
        if(s.kind==='reported_experience') {
          badge('Collected review',body,'info'); text('blockquote',s.cleaned_text||s.review_text,body);
          if(s.date_posted) text('p','Review date: '+s.date_posted,body,'hint');
          text('p','This is a reviewer’s experience. The formula version is unknown.',body,'note');
        } else if(s.kind==='reference_note') {
          text('h3',s.title,body); text('p',s.publisher,body,'hint'); text('p',s.summary,body);
          text('blockquote',s.quote,body); text('p',s.limitations,body,'note'); safeLink(s.url,'Read original reference',body);
        } else {
          badge('Catalog record',body,'info'); if(s.description) text('p',s.description,body);
          let items=[]; try { items=JSON.parse(s.ingredients_json||'[]'); } catch {}
          if(!Array.isArray(items)) items=[];
          text('h3','Recorded ingredients',body);
          text('p',items.length?items.map(i=>typeof i==='string'?i:i?.name).filter(Boolean).join(', '):'No ingredient list is recorded.',body,'ingredients');
          text('p','The completeness and formula version of this list have not been verified.',body,'note');
          if(s.url) safeLink(s.url,'Open catalog source',body);
        }
        raw('Technical source details',s,body);
      } catch(e) { loaded=false; body.textContent=e.message; }
    }); return d;
  }
  function observation(o,parent) {
    const q=text('article',undefined,parent,'quote-card'); const meta=text('div',undefined,q,'quote-meta');
    badge(aspect(o.aspect||o.topic),meta,'info');
    if(o.is_discovered_aspect) badge('Discovered theme',meta);
    if(o.sentiment) q.dataset.sentiment=o.sentiment;
    if(o.sentiment) badge(o.sentiment,meta,o.sentiment==='positive'?'good':o.sentiment==='negative'?'negative':o.sentiment==='mixed'?'mixed':'');
    if(o.truncated) text('span','Partial review',meta);
    text('blockquote',o.span||o.quote,q);
    if(o.evidence_id) evidence(o.evidence_id,q,'Read the collected source'); return q;
  }
  function filterObservations(items,topic='',sentiment='') {
    return items.filter(o=>(!topic||(o.aspect||o.topic||'unspecified')===topic)&&(!sentiment||(o.sentiment||'unspecified')===sentiment));
  }
  function quoteExplorer(items,parent,pageSize=6) {
    const shell=text('section',undefined,parent,'quote-explorer');
    if(!items.length) { text('p','No supported quotes are available for this product yet.',shell,'hint'); return shell; }
    const controls=text('div',undefined,shell,'quote-controls');
    const topicLabel=text('label','Review theme',controls);
    const topic=text('select',undefined,topicLabel); text('option','All themes',topic).value='';
    [...new Set(items.map(o=>o.aspect||o.topic||'unspecified'))].sort().forEach(key=>text('option',key==='unspecified'?'Unlabeled theme':aspect(key),topic).value=key);
    const sentimentLabel=text('label','Experience',controls);
    const sentiment=text('select',undefined,sentimentLabel); text('option','All experiences',sentiment).value='';
    for(const key of ['positive','negative','mixed','neutral','unspecified']) {
      if(items.some(o=>(o.sentiment||'unspecified')===key)) text('option',key==='unspecified'?'Unlabeled':key[0].toUpperCase()+key.slice(1),sentiment).value=key;
    }
    const reset=button('Clear filters',()=>{topic.value='';sentiment.value='';limit=pageSize;render();},controls,'secondary');
    const count=text('p',undefined,shell,'hint'); count.setAttribute('role','status'); count.setAttribute('aria-live','polite');
    const list=text('div',undefined,shell);
    let limit=pageSize;
    let rendered=0;
    const more=button('Show more quotes',()=>{limit+=pageSize;render(false);},shell,'secondary');
    function render(replace=true) {
      const matching=filterObservations(items,topic.value,sentiment.value);
      if(replace) {list.replaceChildren();rendered=0;}
      count.textContent='Showing '+Math.min(limit,matching.length)+' of '+matching.length+' matching observations ('+items.length+' total).';
      matching.slice(rendered,limit).forEach(o=>observation(o,list));
      rendered=Math.min(limit,matching.length);
      if(!matching.length) text('p','No observations match both filters. Clear filters to see all collected excerpts.',list,'empty-state');
      more.hidden=limit>=matching.length; reset.disabled=!topic.value&&!sentiment.value;
    }
    topic.addEventListener('change',()=>{limit=pageSize;render();});
    sentiment.addEventListener('change',()=>{limit=pageSize;render();});
    render(); return shell;
  }
  function initTabs() {
    document.querySelectorAll('[role=tablist]').forEach(list=>{
      const buttons=[...list.querySelectorAll('[role=tab]')];
      const select=b=>buttons.forEach(x=>{const on=x===b; x.setAttribute('aria-selected',String(on)); x.tabIndex=on?0:-1; document.getElementById(x.getAttribute('aria-controls')).hidden=!on;});
      buttons.forEach((b,i)=>{
        b.addEventListener('click',()=>select(b));
        b.addEventListener('keydown',e=>{
          let next;
          if(e.key==='ArrowRight') next=(i+1)%buttons.length;
          if(e.key==='ArrowLeft') next=(i-1+buttons.length)%buttons.length;
          if(e.key==='Home') next=0;
          if(e.key==='End') next=buttons.length-1;
          if(next!==undefined) { e.preventDefault(); select(buttons[next]); buttons[next].focus(); }
        });
      });
    });
  }
  function status(el,message,tone='') { el.textContent=message; el.className='status '+tone; }
  initTabs();
  return {text,button,badge,api,safeLink,details,raw,aspect,table,stat,insight,reviewSummary,evidence,observation,filterObservations,quoteExplorer,status};
})();
