"""Gemini-only transport with typed outputs, redacted failures, budgets and hashed caching.

Generation uses documented REST endpoints; Embedding 2 uses Google's official SDK.
Credentials are never placed in URLs or logs. Provider failures use redacted error codes.
"""
import hashlib
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone

from skintellect.config import DB_PATH, llm_enabled, load_environment
from skintellect.database import database

API_ROOT = 'https://generativelanguage.googleapis.com/v1beta/'
_ACTIVE_RUN = ContextVar('gemini_run', default=None)


class GeminiUnavailable(RuntimeError):
    """Safe error codes only; message never contains request credentials or provider bodies."""


def ensure_tables(db_path):
    with database(db_path) as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS gemini_cache(
            cache_key TEXT PRIMARY KEY, task TEXT NOT NULL, model TEXT NOT NULL,
            output_json TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS gemini_runs(
            id INTEGER PRIMARY KEY, task TEXT, model TEXT, status TEXT,
            cache_hit INTEGER, attempts INTEGER, input_tokens INTEGER,
            output_tokens INTEGER, elapsed_ms REAL, error_code TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS research_vectors(
            evidence_id TEXT NOT NULL, model TEXT NOT NULL, content_hash TEXT NOT NULL,
            dimensions INTEGER NOT NULL, vector_json TEXT NOT NULL,
            PRIMARY KEY(evidence_id,model));
        CREATE TABLE IF NOT EXISTS embedding_query_cache(
            cache_key TEXT PRIMARY KEY, vector_json TEXT NOT NULL, created_at TEXT NOT NULL);
        ''')
        columns={row[1] for row in c.execute('PRAGMA table_info(gemini_runs)')}
        for name,kind in (('thinking_tokens','INTEGER'),('total_tokens','INTEGER'),
                          ('backend','TEXT'),('model_version','TEXT')):
            if name not in columns:
                c.execute('ALTER TABLE gemini_runs ADD COLUMN '+name+' '+kind)


@contextmanager
def run_budget(max_calls=6, max_seconds=120):
    run = {'calls': 0, 'max_calls': max_calls, 'deadline': time.monotonic()+max_seconds, 'events': []}
    token = _ACTIVE_RUN.set(run)
    try:
        yield run
    finally:
        _ACTIVE_RUN.reset(token)


def safe_model(value):
    value = value.removeprefix('models/')
    if not re.fullmatch(r'[a-zA-Z0-9._-]{1,100}', value):
        raise GeminiUnavailable('invalid_model_name')
    return value


def vertex_schema(schema):
    """Convert Pydantic JSON Schema to the supported Cloud responseSchema subset."""
    definitions=schema.get('$defs',{})
    # Keep Cloud's generation schema minimal; bounds remain enforced by local Pydantic.
    allowed={'description','enum','required','format','nullable'}
    def convert(node):
        if '$ref' in node:
            node=definitions[node['$ref'].rsplit('/',1)[-1]]
        if 'anyOf' in node:
            options=[x for x in node['anyOf'] if x.get('type')!='null']
            if len(options)==1:
                return convert(options[0]) | {'nullable':True}
        result={key:value for key,value in node.items() if key in allowed}
        if 'type' in node:
            result['type']=node['type'].upper()
        if 'properties' in node:
            result['properties']={key:convert(value) for key,value in node['properties'].items()}
        if 'items' in node:
            result['items']=convert(node['items'])
        return result
    return convert(schema)


class GeminiClient:
    def __init__(self, db_path=None, transport=None, model=None):
        load_environment()
        self.api_key = (os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or '').strip()
        self.backend = os.environ.get('GEMINI_BACKEND',
            'vertex' if os.environ.get('GOOGLE_CLOUD_PROJECT') else 'developer').lower()
        if self.backend not in {'vertex','developer'}:
            raise GeminiUnavailable('invalid_backend')
        self.model = safe_model(model or os.environ.get('GEMINI_MODEL') or os.environ.get('MODEL_ID') or
                                ('gemini-4-argon' if self.backend=='vertex' else 'gemini-flash-latest'))
        self.project = os.environ.get('GOOGLE_CLOUD_PROJECT','')
        self.location = os.environ.get('GOOGLE_CLOUD_LOCATION','global')
        self.embedding_location = os.environ.get('GEMINI_EMBEDDING_LOCATION',self.location)
        if self.backend=='vertex':
            for value in (self.project,self.location,self.embedding_location):
                if not re.fullmatch(r'[a-zA-Z0-9_-]{1,100}',value):
                    raise GeminiUnavailable('invalid_vertex_configuration')
            if self.model=='gemini-4-argon' and self.location!='global':
                raise GeminiUnavailable('argon_requires_global_location')
            if os.environ.get('API_ENDPOINT','https://aiplatform.googleapis.com').rstrip('/')!='https://aiplatform.googleapis.com':
                raise GeminiUnavailable('untrusted_api_endpoint')
        self.embedding_model = safe_model(os.environ.get('GEMINI_EMBEDDING_MODEL', 'gemini-embedding-2'))
        self.embedding_access_token = os.environ.get('GEMINI_EMBEDDING_ACCESS_TOKEN','').strip()
        self.embedding_dimensions = int(os.environ.get('GEMINI_EMBEDDING_DIMENSIONS','768'))
        if not 1 <= self.embedding_dimensions <= 3072:
            raise GeminiUnavailable('invalid_embedding_dimensions')
        self.db_path = str(db_path) if db_path else str(DB_PATH)
        self.transport = transport or urllib.request.urlopen
        default_transport='rest' if transport is not None or self.embedding_model!='gemini-embedding-2' else 'sdk'
        self.embedding_transport=os.environ.get('GEMINI_EMBEDDING_TRANSPORT',default_transport)
        if self.embedding_transport not in {'sdk','rest'}:raise GeminiUnavailable('invalid_embedding_transport')
        self.last_telemetry = {}
        self.timeout = min(60, max(1, float(os.environ.get('GEMINI_TIMEOUT_SECONDS', '30'))))
        self.max_attempts = min(3, max(1, int(os.environ.get('GEMINI_MAX_ATTEMPTS', '2'))))

    @property
    def available(self):
        return bool(self.api_key) and llm_enabled()

    def status(self):
        return {'provider': 'Gemini', 'configured': bool(self.api_key), 'enabled': self.available,
                'backend':self.backend, 'location':self.location if self.backend=='vertex' else None,
                'model': self.model, 'absa_model':safe_model(os.environ.get('GEMINI_ABSA_MODEL') or self.model),
                'embedding_model': self.embedding_model,
                'embedding_dimensions':self.embedding_dimensions,'embedding_transport':self.embedding_transport,
                'connection_check': 'not_performed_by_status'}

    def endpoint(self, model, method):
        model=safe_model(model)
        if self.backend=='developer':
            return API_ROOT+'models/'+model+':'+method
        location=self.embedding_location if model==self.embedding_model and method in {'predict','embedContent'} else self.location
        return ('https://aiplatform.googleapis.com/v1/projects/'+self.project+'/locations/'+location+
                '/publishers/google/models/'+model+':'+method)

    def _sdk_embedding_request(self,payload,timeout):
        """Use Google's supported client and its environment-based Cloud authentication."""
        try:
            import httpx
            from google import genai
            from google.genai import errors, types
        except ImportError:
            raise GeminiUnavailable('google_genai_sdk_not_installed') from None
        http=types.HttpOptions(timeout=max(1,int(timeout*1000)),
            retry_options=types.HttpRetryOptions(attempts=1))
        kwargs={'vertexai':self.backend=='vertex','http_options':http}
        if self.backend=='vertex':
            kwargs.update(project=self.project,location=self.embedding_location)
            if self.embedding_access_token:
                from google.oauth2.credentials import Credentials
                kwargs['credentials']=Credentials(token=self.embedding_access_token)
        else:
            kwargs['api_key']=self.api_key
        dimensions=(payload.get('embedContentConfig') or payload).get('outputDimensionality',self.embedding_dimensions)
        text=payload['content']['parts'][0]['text']
        try:
            with genai.Client(**kwargs) as sdk:
                result=sdk.models.embed_content(model=self.embedding_model,contents=text,
                    config=types.EmbedContentConfig(output_dimensionality=dimensions))
            embeddings=result.embeddings or []
            if len(embeddings)!=1:raise GeminiUnavailable('invalid_embedding_response')
            usage=getattr(result,'usage_metadata',None)
            return {'embedding':{'values':embeddings[0].values},
                'truncated':bool(getattr(result,'truncated',False)),
                'usageMetadata':{'promptTokenCount':getattr(usage,'prompt_token_count',0) or 0,
                    'totalTokenCount':getattr(usage,'total_token_count',0) or 0}}
        except errors.APIError as exc:
            code=exc.code if isinstance(exc.code,int) else 502
            raise urllib.error.HTTPError(self.endpoint(self.embedding_model,'embedContent'),code,
                'provider_failure',None,None) from None
        except httpx.TransportError:
            raise OSError('sdk_transport_unavailable') from None
        except ImportError:
            raise GeminiUnavailable('google_genai_sdk_dependency_missing') from None
        except Exception as exc:
            if type(exc).__name__ in {'DefaultCredentialsError','RefreshError'}:
                raise GeminiUnavailable('sdk_credentials_unavailable') from None
            raise

    def _request(self, model, method, payload, event):
        if not self.available:
            raise GeminiUnavailable('disabled_or_missing_key')
        for attempt in range(self.max_attempts):
            run = _ACTIVE_RUN.get()
            if run and (run['calls'] >= run['max_calls'] or time.monotonic() >= run['deadline']):
                raise GeminiUnavailable('run_budget_exhausted')
            if run:
                run['calls'] += 1
            event['attempts'] += 1
            headers={'Content-Type':'application/json'}
            if self.backend=='vertex' and model==self.embedding_model and method=='embedContent' and self.embedding_access_token:
                headers['Authorization']='Bearer '+self.embedding_access_token
            else:
                headers['x-goog-api-key']=self.api_key
            request=urllib.request.Request(self.endpoint(model,method),data=json.dumps(payload).encode(),headers=headers)
            timeout = min(self.timeout, max(.1, run['deadline']-time.monotonic())) if run else self.timeout
            try:
                if model==self.embedding_model and method=='embedContent' and self.embedding_transport=='sdk':
                    result=self._sdk_embedding_request(payload,timeout)
                else:
                    with self.transport(request, timeout=timeout) as response:
                        result = json.loads(response.read().decode())
                if not isinstance(result, dict):
                    raise GeminiUnavailable('invalid_provider_response')
                usage = result.get('usageMetadata', {})
                event['input_tokens'] += usage.get('promptTokenCount', 0)
                event['output_tokens'] += usage.get('candidatesTokenCount', 0)
                event['thinking_tokens'] = event.get('thinking_tokens',0)+usage.get('thoughtsTokenCount',0)
                event['total_tokens'] = event.get('total_tokens',0)+usage.get('totalTokenCount',0)
                event['model_version'] = result.get('modelVersion', model)
                return result
            except urllib.error.HTTPError as exc:
                retryable = exc.code in {429, 500, 502, 503, 504}
                code = 'provider_http_'+str(exc.code)
                exc.close()
                if not retryable or attempt+1 == self.max_attempts:
                    raise GeminiUnavailable(code) from None
            except GeminiUnavailable:
                raise
            except (OSError, ValueError):
                if attempt+1 == self.max_attempts:
                    raise GeminiUnavailable('provider_network_or_json_error') from None
            delay = min(2**attempt, 4)
            if run and time.monotonic()+delay >= run['deadline']:
                raise GeminiUnavailable('run_budget_exhausted')
            time.sleep(delay)
        raise GeminiUnavailable('provider_unavailable')

    def _record(self, event, start):
        event['backend']=self.backend
        event['elapsed_ms'] = round((time.perf_counter()-start)*1000, 2)
        self.last_telemetry = event.copy()
        run = _ACTIVE_RUN.get()
        if run is not None:
            run['events'].append(event.copy())
        with database(self.db_path) as c:
            c.execute('''INSERT INTO gemini_runs(task,model,status,cache_hit,attempts,input_tokens,
                output_tokens,elapsed_ms,error_code,thinking_tokens,total_tokens,backend,model_version,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                tuple(event.get(k) for k in ('task','model','status','cache_hit','attempts',
                    'input_tokens','output_tokens','elapsed_ms','error_code','thinking_tokens','total_tokens',
                    'backend','model_version'))+(datetime.now(timezone.utc).isoformat(),))

    def structured(self, task, system, data, response_model, version='1', max_tokens=3000, image=None):
        ensure_tables(self.db_path)
        started = time.perf_counter()
        event = {'task': task, 'model': self.model, 'status': 'failed', 'cache_hit': False,
                 'attempts': 0, 'input_tokens': 0, 'output_tokens': 0, 'error_code': None}
        schema = response_model.model_json_schema()
        cache_parts=[self.backend,self.project,self.location,self.model,task,version,system,data,schema]
        if image is not None:
            cache_parts.append(image)
        key = hashlib.sha256(json.dumps(cache_parts,
                                        sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        try:
            if not self.available:
                raise GeminiUnavailable('disabled_or_missing_key')
            with database(self.db_path) as c:
                cached = c.execute('SELECT output_json FROM gemini_cache WHERE cache_key=?', (key,)).fetchone()
            if cached:
                try:
                    value = response_model.model_validate_json(cached[0])
                    event.update(status='ok', cache_hit=True)
                    return value
                except ValueError:
                    pass
            payload = {'systemInstruction': {'parts': [{'text': system}]},
                       'contents': [{'role': 'user', 'parts': [{'text': json.dumps(data,ensure_ascii=False)}]}],
                       'generationConfig': {'temperature': 0, 'maxOutputTokens': max_tokens,
                                            'responseMimeType': 'application/json', 'responseJsonSchema': schema}}
            if image is not None:
                payload['contents'][0]['parts'].append({'inlineData':image})
            if self.backend=='vertex':
                del payload['generationConfig']['responseJsonSchema']
                payload['generationConfig']['responseSchema']=vertex_schema(schema)
            if self.model=='gemini-4-argon':
                level=os.environ.get('GEMINI_THINKING_LEVEL','LOW').upper()
                if level not in {'LOW','MEDIUM','HIGH'}:
                    raise GeminiUnavailable('invalid_thinking_level')
                payload['generationConfig']['thinkingConfig']={'thinkingLevel':level}
                payload['generationConfig'].pop('temperature',None)
            result = self._request(self.model, 'generateContent', payload, event)
            candidates = result.get('candidates') or []
            if not candidates or candidates[0].get('finishReason') not in {None,'STOP'}:
                raise GeminiUnavailable('blocked_or_incomplete_output')
            text = ''.join(p.get('text','') for p in candidates[0].get('content',{}).get('parts',[]) if not p.get('thought'))
            try:
                value = response_model.model_validate_json(text)
            except ValueError:
                raise GeminiUnavailable('schema_validation_failed') from None
            with database(self.db_path) as c:
                c.execute('INSERT OR REPLACE INTO gemini_cache VALUES(?,?,?,?,?)',
                          (key,task,self.model,value.model_dump_json(),datetime.now(timezone.utc).isoformat()))
            event['status'] = 'ok'
            return value
        except GeminiUnavailable as exc:
            event['error_code'] = str(exc)
            raise
        finally:
            self._record(event, started)

    def embed(self, texts, task_type='RETRIEVAL_DOCUMENT', dimensions=None):
        if not texts:
            return []
        dimensions=self.embedding_dimensions if dimensions is None else dimensions
        if len(texts)>32 or dimensions<1 or dimensions>3072:
            raise ValueError('Invalid embedding batch or dimensions')
        if self.embedding_model=='gemini-embedding-2' and dimensions<128:
            raise ValueError('Embedding 2 requires at least 128 dimensions')
        ensure_tables(self.db_path)
        started = time.perf_counter()
        event = {'task':'embedding','model':self.embedding_model,'status':'failed','cache_hit':False,
                 'attempts':0,'input_tokens':0,'output_tokens':0,'error_code':None}
        cache_parts=[self.backend,self.project,self.embedding_location,
            self.embedding_model,task_type,dimensions,texts]
        if self.embedding_model=='gemini-embedding-2':
            cache_parts.insert(-1,'retrieval-format-v1')
        cache_key=hashlib.sha256(json.dumps(cache_parts,ensure_ascii=False).encode()).hexdigest()
        try:
            if not self.available:
                raise GeminiUnavailable('disabled_or_missing_key')
            # Query vectors are independent of corpus state. Ranked results are never cached.
            if task_type=='RETRIEVAL_QUERY':
                with database(self.db_path) as c:
                    cached=c.execute('SELECT vector_json FROM embedding_query_cache WHERE cache_key=?',(cache_key,)).fetchone()
                if cached:
                    try:
                        vectors=json.loads(cached[0])
                        if len(vectors)==len(texts) and all(len(v)==dimensions and
                            all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in v)
                            and abs(sum(x*x for x in v)-1)<.001 for v in vectors):
                            event.update(status='ok',cache_hit=True)
                            return vectors
                    except (ValueError,TypeError):
                        pass
            if self.embedding_model=='gemini-embedding-2':
                # One content per call: multiple parts would aggregate separate documents.
                prefixes={'RETRIEVAL_QUERY':'task: search result | query: ',
                          'RETRIEVAL_DOCUMENT':'title: none | text: '}
                if task_type not in prefixes:
                    raise ValueError('Unsupported Embedding 2 retrieval task')
                vectors=[]
                for text in texts:
                    payload={'content':{'parts':[{'text':prefixes[task_type]+text}]}}
                    if self.backend=='vertex':
                        payload['embedContentConfig']={'outputDimensionality':dimensions}
                    else:
                        payload['outputDimensionality']=dimensions
                    result=self._request(self.embedding_model,'embedContent',payload,event)
                    if result.get('truncated'):
                        raise GeminiUnavailable('truncated_embedding_input')
                    vectors.append(result.get('embedding',{}).get('values',[]))
            elif self.backend=='vertex':
                # Preserve the legacy text-embedding predict contract for rollback.
                vectors=[]
                for text in texts:
                    result=self._request(self.embedding_model,'predict',
                        {'instances':[{'content':text,'task_type':task_type}],
                         'parameters':{'outputDimensionality':dimensions,'autoTruncate':False}},event)
                    predictions=result.get('predictions',[])
                    statistics=[p.get('embeddings',{}).get('statistics',{}) for p in predictions]
                    if any(s.get('truncated') for s in statistics):
                        raise GeminiUnavailable('truncated_embedding_input')
                    tokens=sum(int(s.get('token_count',0)) for s in statistics)
                    event['input_tokens']+=tokens
                    event['total_tokens']=event.get('total_tokens',0)+tokens
                    vectors.extend(p.get('embeddings',{}).get('values',[]) for p in predictions)
            else:
                requests=[{'model':'models/'+self.embedding_model,
                    'content':{'parts':[{'text':t}]},'outputDimensionality':dimensions} for t in texts]
                for request in requests:
                    if self.embedding_model=='gemini-embedding-001':
                        request['taskType']=task_type
                result=self._request(self.embedding_model,'batchEmbedContents',{'requests':requests},event)
                vectors=[e.get('values',[]) for e in result.get('embeddings',[])]
            if len(vectors)!=len(texts) or any(len(v)!=dimensions or not all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in v) for v in vectors):
                raise GeminiUnavailable('invalid_embedding_response')
            normalized = []
            for vector in vectors:
                norm = math.sqrt(sum(x*x for x in vector))
                if not norm:
                    raise GeminiUnavailable('zero_embedding')
                normalized.append([x/norm for x in vector])
            event['status']='ok'
            if task_type=='RETRIEVAL_QUERY':
                with database(self.db_path) as c:
                    c.execute('INSERT OR REPLACE INTO embedding_query_cache VALUES(?,?,?)',
                        (cache_key,json.dumps(normalized),datetime.now(timezone.utc).isoformat()))
            return normalized
        except GeminiUnavailable as exc:
            event['error_code']=str(exc)
            raise
        finally:
            self._record(event,started)
