"""Attributed reference notes, kept separate from product and reviewer evidence."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from skintellect.database import database

SOURCE_FILE=Path(__file__).with_name('reference_sources.json')


def ingest_references(db_path, path=SOURCE_FILE):
    records=json.loads(Path(path).read_text(encoding='utf-8'))
    allowed={'www.fda.gov','www.aad.org','pubmed.ncbi.nlm.nih.gov'}
    with database(db_path) as c:
        for record in records:
            parsed=urlparse(record['url'])
            if parsed.scheme!='https' or parsed.hostname not in allowed or not re.fullmatch(r'[a-z0-9-]{1,100}',record['id']):
                raise ValueError('invalid_reference_metadata')
            content=json.dumps(record,ensure_ascii=False,sort_keys=True)
            c.execute('INSERT OR REPLACE INTO source_documents VALUES(?,?,?,?,?,?)',
                (record['id'],record['url'],record['retrieved_at'],content,
                 hashlib.sha256(content.encode()).hexdigest(),'attributed_reference_note'))
    return {'ingested':len(records),'kind':'attributed_reference_notes','human_reviewed':False}


def references(db_path, query=None):
    with database(db_path) as c:
        rows=c.execute("SELECT id,content,content_hash FROM source_documents WHERE status='attributed_reference_note' ORDER BY id").fetchall()
    result=[]
    def terms(text):
        return {t.removesuffix('s') if len(t)>3 else t for t in re.findall(r'\w+',text.casefold())}
    tokens=terms(query) if query else None
    for sid,content,h in rows:
        record=json.loads(content)
        if hashlib.sha256(content.encode()).hexdigest()!=h:
            continue
        if tokens is not None:
            topic_tokens=terms(' '.join(record['topics']))
            if not tokens & topic_tokens:
                continue
        result.append(record|{'evidence_id':'source:'+sid,'content_hash':h,
            'kind':'reference_note','human_reviewed':False})
    return result


def source_passages(db_path):
    return [{'evidence_id':r['evidence_id'],'product_id':None,'kind':'reference_note',
             'text':r['title']+'\n'+r['summary']+'\nSource excerpt: '+r['quote']+'\nLimitations: '+r['limitations'],
             'content_hash':r['content_hash'],'url':r['url']}
            for r in references(db_path)]
