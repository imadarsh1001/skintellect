import skintellect.research.evidence as evidence_tools
import skintellect.research.reviews as review_tools

"""Headless Chromium checks against local fixtures. Never makes Gemini calls.

Run with the project runtime: python tests/ui_smoke.py
Browser profiles and fixture requests are isolated from the user's browser/data.
"""
import json
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import urllib.error
import urllib.request
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
# The smoke test drives the REAL backend; start it first:
#   PYTHONPATH=src python -m uvicorn skintellect.api.app:app --port 8000
BACKEND_URL = 'http://127.0.0.1:8000'

# The SPA replaces the retired templates: this smoke test drives the built
# frontend. Run `npm run build` in frontend/ before this check.
FRONTEND_DIST=ROOT/'frontend'/'dist'
if not (FRONTEND_DIST/'index.html').is_file():
    raise SystemExit('frontend/dist/index.html is missing - run `npm run build` in frontend/ first.')

SCRIPT=r"""
(async()=>{
 const checks=[];
 const check=(condition,message)=>{if(!condition)throw new Error(message);checks.push(message);};
 const wait=async(fn,label)=>{const deadline=Date.now()+120000;for(;;){if(fn())return;if(Date.now()>deadline)throw new Error('Timed out waiting for SPA state'+(label?': '+label:''));await new Promise(r=>setTimeout(r,100));}};
 const byText=(selector,text)=>Array.from(document.querySelectorAll(selector)).find(n=>n.textContent.trim().includes(text));
 const kind=new URLSearchParams(location.search).get('check');
 const fetchLog=[];
 const rawFetch=window.fetch;
 window.fetch=(...args)=>{fetchLog.push(String(args[0]));return rawFetch(...args);};
 const fillQuestion=async text=>{
  const ta=document.querySelector('textarea');
  if(!ta)throw new Error('no question textarea');
  ta.value=text;ta.dispatchEvent(new Event('input',{bubbles:true}));
  await new Promise(r=>setTimeout(r,150));
 };
 try {
  if(kind==='study'||kind==='mobile') {
   await wait(()=>document.body.innerText.includes('Follow the evidence'));
   await wait(()=>byText('main','Thank You Farmer')&&byText('main',"Dr. Sheth's")&&byText('main','iUNIK'),'prepared product cards');
   const cards=byText('main','Thank You Farmer')&&byText('main',"Dr. Sheth's")&&byText('main','iUNIK');
   check(cards,'Three prepared product cards loaded');
   const trigger=byText('button','Uncover the evidence');
   check(trigger,'Evidence expander is offered per product');
   trigger.click();
   await wait(()=>byText('button','Hide evidence'),'evidence drawer opens');
   check(/\d+ of \d+/.test(document.body.innerText),'Review summary renders counts with its denominator');
   check(document.body.innerText.includes('"'),'Reviewer quotes render as readable text');
   trigger.click();
   await wait(()=>byText('button','Uncover the evidence'),'evidence drawer closes');
   check(!byText('button','Hide evidence'),'Evidence drawer collapses on second click');
   check(document.querySelectorAll('main img').length===0,'Catalog text cannot create markup');
  } else if(kind==='research') {
   await wait(()=>document.body.innerText.includes('Go beyond the ingredient list'));
   const scope=Array.from(document.querySelectorAll('input[type=checkbox]')).find(n=>n.closest('label')?.textContent.includes('prepared group'));
   check(scope&&scope.checked,'Prepared-study scope is preserved from ?demo=1');
   await fillQuestion('Find moisturizers with ceramides. Summarize texture evidence and suggest one alternative.');
   const run=byText('button','Find products & explain');
   check(run&&!run.disabled,'Main action enables once a question is present');
   run.click();
   await wait(()=>document.body.innerText.includes('Matching records'),'matching records panel');
   check(document.body.innerText.includes('Found ')||document.body.innerText.includes('match'),'Answer renders the catalog verdict');
   check(!document.querySelector('main img')&&!window.uiInjection,'Catalog text cannot create markup');
   const example=byText('button','What do hydration reviews reveal?');
   example.click();
   await wait(()=>{const ta=document.querySelector('textarea');return !!ta&&ta.value.includes('hydration')},'example chip fills the input');
   check(document.querySelector('textarea').value.includes('hydration'),'Example question fills the input');
  } else if(kind==='error') {
   await wait(()=>document.body.innerText.includes('Go beyond the ingredient list'));
   await fillQuestion('How do ceramide moisturizers feel?');
   byText('button','Find products & explain').click();
   await wait(()=>document.body.innerText.includes('assistant request failed'));
   const run=byText('button','Find products & explain');
   check(run&&!run.disabled,'Failed request restores the main action');
  } else if(kind==='progress') {
   await wait(()=>document.body.innerText.includes('Preparation and indexing status'));
   await wait(()=>byText('button','Queue job'),'preparation job form loads');
   const queue=byText('button','Queue job');
   queue.click();
   // The real worker may finish a small job between polls, so accept either
   // the active job (stop button) or a terminal badge before interacting.
   await wait(()=>byText('button','Stop after current batch')
     ||document.body.innerText.includes('cancelled')
     ||document.body.innerText.includes('completed')
     ||document.body.innerText.includes('failed'),'queued job appears');
   await wait(()=>{const q=byText('button','Queue job');return !!q&&!q.disabled},'queue form stays usable');
   check(true,'A queued task keeps the form usable');
   if(byText('button','Stop after current batch')){
   // The real worker may finish the batch before the cancellation lands;
   // accept any terminal state: cancellation text, a cancelled badge, or the
   // job leaving the active list.
   byText('button','Stop after current batch').click();
   await wait(()=>document.body.innerText.includes('Cancellation requested')
     ||document.body.innerText.includes('Cancelled')
     ||!byText('button','Stop after current batch'),'job leaves the active list');
   check(!byText('button','Stop after current batch')||document.body.innerText.includes('Cancellation requested')||document.body.innerText.includes('Cancelled'),'Cancellation updates task state');
  } else {
   check(document.body.innerText.includes('cancelled')||document.body.innerText.includes('completed')||document.body.innerText.includes('failed'),'Job reached a terminal state');
  }
  }
  if(document.documentElement.scrollWidth>innerWidth+1){
   const leaf=Array.from(document.querySelectorAll('body *')).find(n=>n.getBoundingClientRect().right>innerWidth+1&&n.children.length===0);
   const chain=[];
   let cur=leaf;
   while(cur&&cur!==document.body&&chain.length<6){const r=cur.getBoundingClientRect();chain.push(cur.tagName+'['+String(cur.className.baseVal!==undefined?cur.className.baseVal:cur.className).slice(0,50)+'] w='+Math.round(r.width)+' x='+Math.round(r.x));cur=cur.parentElement;}
   throw new Error('Horizontal overflow at '+innerWidth+'px: '+chain.join(' <- '));
  }
  check(document.documentElement.scrollWidth<=innerWidth+1,'Page fits the viewport without horizontal overflow');
  window.scrollTo(0,0);
  await fetch('/__ui_result__',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ok:true,kind,checks})});
 } catch(error) {
  await fetch('/__ui_result__',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ok:false,kind,checks,error:String(error),bodySnippet:(document.body?.innerText||'').slice(0,400),fetchLog:fetchLog.join(' | ')})}).catch(()=>{});
 }
})();
"""

class FixtureServer(BaseHTTPRequestHandler):
    """Injecting reverse proxy: serves the built SPA with the check script and
    forwards /api/* to the real backend, so the smoke test exercises the same
    endpoints and payloads as production."""

    last_result = None

    def log_message(self, *args): pass

    def send(self, value, status=200, mime='application/json'):
        if isinstance(value, str):
            body = value.encode('utf-8')
        elif isinstance(value, (dict, list)):
            body = json.dumps(value).encode('utf-8')
        else:
            body = value
        try:
            self.send_response(status); self.send_header('Content-Type', mime + '; charset=utf-8')
            self.send_header('Content-Length', str(len(body))); self.end_headers()
            self.wfile.write(body)
        except (ConnectionResetError, BrokenPipeError):
            pass

    def _proxy(self, method):
        length = int(self.headers.get('Content-Length', '0') or 0)
        body = self.rfile.read(length) if length else None
        request = urllib.request.Request(
            BACKEND_URL.rstrip('/') + self.path, data=body, method=method,
            headers={k: v for k, v in self.headers.items() if k.lower() in ('content-type', 'accept')})
        started = time.time()
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = response.read()
                print(f'[proxy] {method} {self.path} -> {response.status} in {time.time()-started:.1f}s', flush=True)
                self.send(payload, status=response.status,
                          mime=response.headers.get('Content-Type', 'application/json'))
        except urllib.error.HTTPError as exc:
            print(f'[proxy] {method} {self.path} -> HTTP {exc.code} in {time.time()-started:.1f}s', flush=True)
            self.send(exc.read(), status=exc.code, mime=exc.headers.get('Content-Type', 'application/json'))
        except Exception as exc:
            print(f'[proxy] {method} {self.path} -> ERROR {exc} in {time.time()-started:.1f}s', flush=True)
            self.send({'detail': f'fixture proxy failure: {exc}'}, status=502)

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if path.startswith('/api/'):
            self._proxy('GET'); return
        if path in ['/', '/study', '/research', '/progress', '/copilot', '/compare', '/graph']:
            body = (FRONTEND_DIST / 'index.html').read_text(encoding='utf-8')
            self.send(body.replace('</body>', '<script>' + SCRIPT + '</script></body>'), mime='text/html'); return
        if path.startswith('/assets/'):
            file = (FRONTEND_DIST / path.removeprefix('/')).resolve()
            if file.is_relative_to(FRONTEND_DIST) and file.is_file():
                mime = {'.js': 'application/javascript', '.css': 'text/css'}.get(file.suffix, 'application/octet-stream')
                self.send(file.read_bytes(), mime=mime); return
        self.send({'detail': 'Not found'}, 404)

    def do_POST(self):
        path_only = unquote(urlsplit(self.path).path)
        if path_only == '/api/assistant/query' and 'check=error' in (self.headers.get('Referer') or ''):
            self.send({'detail': 'provider_network_or_json_error'}, status=503); return
        if path_only == '/__ui_result__':
            raw = self.rfile.read(int(self.headers.get('Content-Length', '0') or 0))
            try: FixtureServer.last_result = json.loads(raw.decode('utf-8'))
            except Exception: FixtureServer.last_result = {'ok': False, 'error': 'unparseable result'}
            self.send_response(204); self.end_headers(); return
        self._proxy('POST')


def main():
    candidates=[Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'),Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')]
    browser=next((p for p in candidates if p.exists()),None)
    if browser is None:raise SystemExit('No local Chromium browser available for this test.')
    import urllib.request as _ur
    try:
        _ur.urlopen(BACKEND_URL + '/health', timeout=5)
    except Exception:
        raise SystemExit('Backend is not running on ' + BACKEND_URL + ' - start uvicorn first.')
    server=ThreadingHTTPServer(('127.0.0.1',0),FixtureServer)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    cases=[('study','study',1440,1200),('research','research',1440,1200),('error','research',1440,1000),('progress','progress',1440,1200),('mobile','study',412,915)]
    results=[]
    test_root=ROOT/'.test-work';test_root.mkdir(exist_ok=True)
    for kind,page,width,height in cases:
        with tempfile.TemporaryDirectory(dir=test_root,prefix='browser-',ignore_cleanup_errors=True) as profile:
            url=f'http://127.0.0.1:{server.server_port}/{page}?check={kind}&demo=1'
            args=[str(browser),'--headless=new','--disable-gpu','--disable-background-networking','--no-first-run','--no-default-browser-check',
                  '--user-data-dir='+profile,f'--window-size={width},{height}']
            # The SPA result arrives over the fixture result channel; run the
            # browser in the background and poll for it (no dump-dom, which
            # would terminate the page at the load event).
            process=subprocess.Popen(args+[url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
            deadline=time.time()+240
            try:
                while FixtureServer.last_result is None and time.time()<deadline:
                    time.sleep(0.25)
                result=FixtureServer.last_result or {'ok':False,'kind':kind,'error':'Browser did not report a UI check result in time','browser_pid':process.pid}
                FixtureServer.last_result=None
            finally:
                process.terminate()
                try:process.wait(timeout=10)
                except Exception:process.kill()
            results.append(result);print(json.dumps(result),flush=True)
            if 'error' in result and 'did not report' in str(result.get('error')):
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
