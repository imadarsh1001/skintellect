import skintellect.research.evidence as evidence_tools
import skintellect.research.reviews as review_tools

"""Headless Chromium checks against local fixtures. Never makes Gemini calls.

Run with the project runtime: python tests/ui_smoke.py
Browser profiles and fixture requests are isolated from the user's browser/data.
"""
import copy
import json
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from skintellect.config import DB_PATH, STATIC_DIR, TEMPLATES_DIR
from skintellect.research.connections import connections
from skintellect.research.references import references
from skintellect.research.study import readiness

SCRIPT=r"""
(async()=>{
 const checks=[];
 const check=(condition,message)=>{if(!condition)throw new Error(message);checks.push(message);};
 const wait=async fn=>{for(let i=0;i<160;i++){if(fn())return;await new Promise(r=>setTimeout(r,50));}throw new Error('Timed out waiting for UI');};
 const visible=n=>n&&n.getClientRects().length>0;
 const id=n=>document.getElementById(n);
 const kind=new URLSearchParams(location.search).get('check');
 try {
  if(kind==='study'||kind==='mobile') {
   await wait(()=>id('products').children.length===3);
   check(id('products').querySelectorAll('.product-card').length===3,'Three product cards loaded');
   check(id('panel-quality').hidden,'Quality metrics are hidden initially');
   check([...document.querySelectorAll('pre')].every(p=>!visible(p)),'Raw JSON is not visible by default');
   id('tab-quality').click();check(!id('panel-quality').hidden&&id('panel-products').hidden,'Study tabs switch panels');
   id('tab-quality').dispatchEvent(new KeyboardEvent('keydown',{key:'Home',bubbles:true}));
   check(!id('panel-products').hidden&&document.activeElement===id('tab-products'),'Tabs support keyboard navigation');
   const trigger=id('products').querySelector('button');trigger.click();
   await wait(()=>id('detail-body').querySelector('table'));
   check(!id('product-detail').hidden,'Product evidence opens in a dedicated panel');
   const source=id('detail-body').querySelector('.quote-card details');source.open=true;
   await wait(()=>source.querySelector('.source-details blockquote'));
   check(source.querySelector('.source-details').textContent.includes('reviewer'),'Review source uses readable text');
   id('close-detail').click();check(id('product-detail').hidden&&document.activeElement===trigger,'Closing evidence restores focus');
   id('tab-label').click();
   const file=new File([new Uint8Array(6000001)],'too-large.png',{type:'image/png'});const transfer=new DataTransfer();transfer.items.add(file);id('label-file').files=transfer.files;
   id('label-form').requestSubmit();
   check(id('label-output').textContent.includes('smaller than 6 MB'),'Oversized label is rejected before upload');
   id('tab-products').click();
  } else if(kind==='research') {
   await wait(()=>id('demo-status').textContent.includes('ready'));
   check(!id('filter-details').open,'Advanced filters are collapsed initially');
   id('assistant').click();await wait(()=>id('results').children.length===2&&!id('assistant').disabled);
   check(id('demo-scope').checked,'Prepared-study scope is preserved');
   check(id('answer').querySelectorAll('blockquote').length===2,'Answer displays supported source quotes');
   check(!id('results').querySelector('img')&&!window.uiInjection,'Catalog text cannot create markup');
   check([...document.querySelectorAll('pre')].every(p=>!visible(p)),'Research diagnostics remain collapsed');
   const source=id('results').querySelector('details');source.open=true;
   await wait(()=>source.querySelector('.source-details h3'));
   check(source.textContent.includes('Recorded ingredients'),'Catalog source shows a readable ingredient list');
   document.querySelectorAll('[data-query]')[1].click();check(id('query').value.includes('niacinamide'),'Example question fills the input');
   id('query').value=' ';id('assistant').click();await wait(()=>id('status').classList.contains('error'));
   check(!id('assistant').disabled,'Empty-question error restores the main action');
  } else if(kind==='error') {
   await wait(()=>id('demo-status').textContent.includes('ready'));id('assistant').click();
   await wait(()=>id('status').classList.contains('error'));
   check(id('status').textContent.includes('Gemini could not respond'),'Provider failures use a helpful message');
   check(!id('assistant').disabled,'Failed request restores the main action');
  } else if(kind==='progress') {
   await wait(()=>id('jobs').querySelector('button'));
   check(id('model').closest('details').open===false,'Service metadata is hidden initially');
   id('jobs').querySelector('button').click();
   check(id('product').value==='10256'&&id('limit').value==='20','Resume fills the previous task settings');
   id('job-form').requestSubmit();
   await wait(()=>id('jobs').querySelector('button')?.textContent==='Stop after current batch');
   check(id('start').disabled,'A running task prevents duplicate starts');
   id('jobs').querySelector('button').click();
   await wait(()=>!id('start').disabled&&id('jobs').textContent.includes('Cancelled'));
   check(id('jobs').textContent.includes('Cancelled'),'Cancellation updates task state');
  }
  check(document.documentElement.scrollWidth<=innerWidth+1,'Page fits the viewport without horizontal overflow');
  window.scrollTo(0,0);
  const result=document.createElement('script');result.type='application/json';result.id='ui-check-result';result.textContent=JSON.stringify({ok:true,kind,checks});document.body.append(result);
 } catch(error) {
  const result=document.createElement('script');result.type='application/json';result.id='ui-check-result';result.textContent=JSON.stringify({ok:false,kind,checks,error:String(error)});document.body.append(result);
 }
})();
"""

class FixtureServer(BaseHTTPRequestHandler):
    demo=readiness(DB_PATH)
    answer=json.loads((ROOT/'reports/latest/prepared_assistant_demo.json').read_text(encoding='utf-8'))
    review=review_tools.review_insights(10256)
    graph=connections(10256,DB_PATH)
    jobs=[{'id':1,'kind':'reviews','status':'paused','limit_count':20,'product_id':10256,'max_calls':8,'max_seconds':120,'completed':5,'selected':20,'calls':2,'tokens':1234,'cancel_requested':0,'error_code':'run_budget_exhausted','created_at':'2026-10-23T05:00:00+00:00'}]
    def log_message(self,*args):pass
    def send(self,value,status=200,mime='application/json'):
        body=json.dumps(value).encode() if mime=='application/json' else value.encode()
        self.send_response(status);self.send_header('Content-Type',mime+'; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        path=unquote(urlsplit(self.path).path)
        if path in ['/study','/research','/progress']:
            body=(Path(TEMPLATES_DIR)/(path[1:]+'.html')).read_text(encoding='utf-8')
            self.send(body.replace('</body>','<script>'+SCRIPT+'</script></body>'),mime='text/html');return
        if path.startswith('/static/'):
            file=(Path(STATIC_DIR)/path.removeprefix('/static/')).resolve()
            if file.is_relative_to(Path(STATIC_DIR)) and file.is_file():
                self.send(file.read_text(encoding='utf-8'),mime='text/css' if file.suffix=='.css' else 'application/javascript');return
        data={'/api/research/demo':self.demo,'/api/research/references':{'references':references(DB_PATH)},
              '/api/research/status':{'enabled':True,'model':'fixture-service','indexed_vectors':35},
              '/api/quality':{'products':2502,'formulas_present':576,'verified_complete':0,'truncated_reviews':1226},
              '/api/products/10256/review-insights':self.review,'/api/products/10256/connections':self.graph}
        if path=='/api/research/progress':
            self.send({'model':{'enabled':True,'model':'fixture-service'},'reviews':{'processed':58,'eligible':4062},'embeddings':{'indexed':35,'eligible':6554},'usage':{'provider_attempts':76,'reported_tokens':28988,'cache_hits':44},'jobs':self.jobs,'recent_operations':[]});return
        if path in data:self.send(data[path]);return
        if path.startswith('/api/evidence/'):
            result=evidence_tools.evidence(path.removeprefix('/api/evidence/'));self.send(result,200 if result else 404);return
        self.send({'detail':'Not found'},404)
    def do_POST(self):
        data=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
        if self.path=='/api/assistant/query':
            if 'check=error' in self.headers.get('Referer',''):self.send({'detail':'provider_network_or_json_error'},503);return
            answer=copy.deepcopy(self.answer);answer['search']['products'][0]['brand']='<img src=x onerror="window.uiInjection=1">'
            self.send(answer);return
        if self.path=='/api/research/jobs':
            self.__class__.jobs=[dict(self.jobs[0],id=2,status='running',completed=0,error_code=None),self.jobs[0]]
            self.send({'job_id':2,'status':'queued'},202);return
        if self.path=='/api/research/jobs/2/cancel':
            self.__class__.jobs[0]['status']='cancelled';self.__class__.jobs[0]['cancel_requested']=1
            self.send({'status':'cancellation_requested'});return
        self.send({'detail':'Unknown fixture request'},400)


def main():
    candidates=[Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'),Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')]
    browser=next((p for p in candidates if p.exists()),None)
    if browser is None:raise SystemExit('No local Chromium browser available for this test.')
    server=ThreadingHTTPServer(('127.0.0.1',0),FixtureServer)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    cases=[('study','study',1440,1200),('research','research',1440,1200),('error','research',1440,1000),('progress','progress',1440,1200),('mobile','study',412,915)]
    results=[]
    test_root=ROOT/'.test-work';test_root.mkdir(exist_ok=True)
    preview=ROOT/'reports/previews';preview.mkdir(parents=True,exist_ok=True)
    for kind,page,width,height in cases:
        with tempfile.TemporaryDirectory(dir=test_root,prefix='browser-',ignore_cleanup_errors=True) as profile:
            url=f'http://127.0.0.1:{server.server_port}/{page}?check={kind}&demo=1'
            args=[str(browser),'--headless=new','--disable-gpu','--disable-background-networking','--no-first-run','--no-default-browser-check',
                  '--user-data-dir='+profile,f'--window-size={width},{height}','--virtual-time-budget=15000','--dump-dom']
            if kind in ['study','mobile']:args.append('--screenshot='+str(preview/('ux-'+kind+'.png')))
            process=subprocess.run(args+[url],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
            import re
            match=re.search(r'<script type="application/json" id="ui-check-result">(.*?)</script>',process.stdout,re.S)
            result=json.loads(match.group(1)) if match else {'ok':False,'kind':kind,'error':'Browser did not produce the UI check result','browser_exit_code':process.returncode,'browser_error':process.stderr[-800:]}
            results.append(result);print(json.dumps(result),flush=True)
            if match is None:
                report={'kind':'headless_local_fixture_ui_checks','status':'browser_unavailable','provider_calls':0,
                    'browser':browser.name,'results':results,'all_passed':None,
                    'limitation':'The installed browser could not run this fixture page in the current execution environment. Run this check in a desktop session; no UI checks are claimed as passed.'}
                (ROOT/'reports/latest/ui-smoke.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
                server.shutdown();server.server_close()
                return 2
    server.shutdown();server.server_close()
    report={'kind':'headless_local_fixture_ui_checks','provider_calls':0,'browser':browser.name,'results':results,'all_passed':all(r['ok'] for r in results)}
    (ROOT/'reports/latest/ui-smoke.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return 0 if report['all_passed'] else 1

if __name__=='__main__':raise SystemExit(main())
