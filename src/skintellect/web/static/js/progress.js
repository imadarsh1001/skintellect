/* Processing status in plain language; request metadata stays expandable. */
const {text,button,badge,api,details,raw,stat,status}=Studio;
const el=id=>document.getElementById(id);
const names={reviews:'Review analysis',embed:'Meaning-based search indexing'};
const states={queued:'Waiting to start',running:'Running',completed:'Finished',paused:'Usage or time limit reached',interrupted:'Server stopped',failed:'Could not finish',cancelled:'Cancelled'};
let loading=false;
let submitting=false;
let jobSignature='';

function coverage(title,done,total,meaning) {
  const card=text('article',undefined,el('coverage'),'card'); text('h3',title,card);
  text('div',done.toLocaleString()+' / '+total.toLocaleString(),card,'metric');
  text('p',meaning,card,'hint');
  const p=text('progress',undefined,card); p.max=total||1; p.value=done; p.setAttribute('aria-label',title+' coverage');
  text('p',(total?100*done/total:0).toFixed(1)+'% prepared · '+(total-done).toLocaleString()+' remaining',card,'hint');
}
function fillSettings(job) {
  el('kind').value=job.kind; el('limit').value=job.limit_count; el('product').value=job.product_id||'';
  el('calls').value=job.max_calls; el('seconds').value=job.max_seconds;
  if(job.product_id) el('product').closest('details').open=true;
  el('kind').focus(); el('job-form').scrollIntoView?.({block:'start',behavior:'auto'});
  status(el('status'),'The previous settings are filled. Start preparation to continue; completed records will be skipped.');
}
function renderJobs(jobs) {
  const signature=JSON.stringify(jobs);
  if(signature===jobSignature) return;
  jobSignature=signature;
  const focused=document.activeElement?.dataset.jobId;
  el('jobs').replaceChildren();
  if(!jobs.length) {text('p','No preparation tasks have been started yet.',el('jobs'),'hint'); return;}
  for(const j of jobs) {
    const row=text('article',undefined,el('jobs'),'job'); row.dataset.state=j.status; const head=text('div',undefined,row,'job-heading');
    text('h3',names[j.kind]||'Preparation',head);
    badge(j.cancel_requested&&['running','queued'].includes(j.status)?'Stopping after current batch':states[j.status]||j.status,head,j.status==='completed'?'good':j.status==='failed'?'negative':['paused','interrupted'].includes(j.status)?'warning':['running','queued'].includes(j.status)?'info':'');
    text('p',j.completed+' of '+(j.selected??'the selected')+' records saved',row);
    if(j.selected) {const p=text('progress',undefined,row);p.max=j.selected;p.value=j.completed;p.setAttribute('aria-label','Records saved');}
    const created=new Date(j.created_at);
    text('p',(j.product_id?'Selected product':'Eligible catalog records')+' · Started '+(Number.isNaN(created.getTime())?'recently':created.toLocaleString()),row,'hint');
    if(j.error_code) text('p',j.status==='paused'?'This task reached its configured limit. Saved work will be reused by the next task.':'The task stopped before all selected records were saved. You can try another batch with the same settings.',row,'note');
    if(['queued','running'].includes(j.status)&&!j.cancel_requested) {
      let cancel;
      cancel=button('Stop after current batch',async()=>{
        cancel.disabled=true;
        try {await api('/research/jobs/'+j.id+'/cancel',{}); await refresh();}
        catch(e){status(el('status'),e.message,'error');cancel.disabled=false;}
      },row);
      cancel.dataset.jobId=j.id;
    } else if(['paused','interrupted','failed','cancelled'].includes(j.status)) {
      const resume=button('Use these settings again',()=>fillSettings(j),row); resume.dataset.jobId=j.id;
    }
    const meta=details('Usage and task details',row);
    text('p',j.calls+' of '+j.max_calls+' API attempts used · '+j.tokens.toLocaleString()+' reported tokens · '+j.max_seconds+'s time limit',meta,'hint');
    raw('Raw task record',j,meta);
  }
  if(focused) el('jobs').querySelector('[data-job-id="'+focused+'"]')?.focus();
}
async function refresh() {
  if(loading) return; loading=true;
  try {
    const [progress,study]=await Promise.allSettled([api('/research/progress'),api('/research/demo')]);
    if(progress.status==='rejected') throw progress.reason;
    const d=progress.value;
    if(study.status==='fulfilled') {
      const s=study.value;
      el('cohort').textContent=s.configured?(s.ready?'Ready to explore. ':'Some evidence is still processing. ')+s.products.length+' products; '+s.products.reduce((n,p)=>n+p.reviews.processed,0)+' reviews analyzed.':'No prepared demo is available yet.';
    } else el('cohort').textContent='Prepared-demo information could not load. Full-catalog progress is shown below.';
    el('coverage').replaceChildren();
    coverage('Reviews analyzed',d.reviews.processed,d.reviews.eligible,'Collected reviews with current Gemini analysis.');
    coverage('Passages searchable by meaning',d.embeddings.indexed,d.embeddings.eligible,'Product and review passages with current search vectors.');
    const active=d.jobs.find(j=>['queued','running'].includes(j.status));
    el('start').disabled=!!active||!d.model.enabled||submitting;
    const message=active?(names[active.kind]||'Preparation')+' is '+(active.status==='queued'?'waiting to start.':'running. '+active.completed+' records saved.'):'No preparation task is running.';
    if(el('status').textContent!==message&&!submitting) status(el('status'),message,active?'loading':'');
    el('model').textContent='Gemini: '+(d.model.enabled?'available':'disabled or not configured')+' · '+d.model.model;
    renderJobs(d.jobs);
    el('usage').replaceChildren();const stats=text('div',undefined,el('usage'),'stat-grid');
    stat(d.usage.provider_attempts.toLocaleString(),'API attempts',stats);stat(d.usage.reported_tokens.toLocaleString(),'reported tokens',stats);stat(d.usage.cache_hits.toLocaleString(),'cached operations',stats);
    el('notice').textContent='Tokens are usage metadata, not a billing amount. Check your Cloud billing console for charges. Processing continues only while this server stays open.';
    el('operations').replaceChildren();for(const op of d.recent_operations)raw(op.task+' · '+(op.status==='ok'?'Completed':'Stopped'),op,el('operations'));
  } catch(e) {status(el('status'),'Could not load progress. '+e.message,'error');}
  finally {loading=false;}
}
el('job-form').onsubmit=async e=>{
  e.preventDefault();if(submitting)return;submitting=true;el('start').disabled=true;el('start').textContent='Starting…';
  try {
    await api('/research/jobs',{kind:el('kind').value,limit:Number(el('limit').value),product_id:el('product').value?Number(el('product').value):null,max_calls:Number(el('calls').value),max_seconds:Number(el('seconds').value)});
    status(el('status'),'Preparation queued. Completed batches will appear below.');
  } catch(error) {status(el('status'),error.message,'error');submitting=false;el('start').disabled=false;el('start').textContent='Start preparation';return;}
  submitting=false;el('start').textContent='Start preparation';await refresh();
};
el('refresh').onclick=refresh;
setInterval(()=>{if(!document.hidden&&!submitting)refresh();},5000);
refresh();
