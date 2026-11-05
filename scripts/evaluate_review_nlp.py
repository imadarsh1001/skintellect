"""Compare rule/Gemini extraction on authored smoke fixtures or an annotated JSONL set.

These defaults are synthetic developer examples, not a held-out real-review benchmark.
Custom lines: {"id": 1, "text": "...", "expected": [["aspect","sentiment",false]]}
"""
import argparse
import json
from pathlib import Path

from skintellect.config import DB_PATH
from skintellect.gemini import GeminiClient, GeminiUnavailable, run_budget
from skintellect.research.model_steps import analyze_review_batch
from skintellect.research.review_store import extract_review

CASES=[
    {'id':1,'text':'It is lightweight.','expected':[['texture','positive',False]]},
    {'id':2,'text':'Very sticky.','expected':[['stickiness','negative',False]]},
    {'id':3,'text':'Not sticky.','expected':[['stickiness','positive',True]]},
    {'id':4,'text':"Didn't sting.",'expected':[['stinging','positive',True]]},
    {'id':5,'text':'It burned.','expected':[['stinging','negative',False]]},
    {'id':6,'text':'Hydrating, but sticky.','expected':[['hydration','positive',False],['stickiness','negative',False]]},
    {'id':7,'text':'Absorbs quickly.','expected':[['absorption','positive',False]]},
    {'id':8,'text':'The scent is strong.','expected':[['scent','neutral',False]]},
    {'id':9,'text':'Too expensive.','expected':[['value','negative',False]]},
    {'id':10,'text':'Not hydrating.','expected':[['hydration','negative',True]]},
    {'id':11,'text':'No pilling.','expected':[['pilling','positive',True]]},
    {'id':12,'text':'It arrived yesterday.','expected':[]},
]


def metrics(cases, predictions):
    expected={(c['id'],*label) for c in cases for label in c['expected']}
    actual={(rid,p['aspect'],p['sentiment'],p['negated']) for rid,items in predictions.items() for p in items}
    tp,fp,fn=len(expected&actual),len(actual-expected),len(expected-actual)
    precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0
    return {'precision':precision,'recall':recall,'f1':2*precision*recall/(precision+recall) if precision+recall else 0,
            'true_positive':tp,'false_positive':fp,'false_negative':fn,
            'missing':[list(x) for x in sorted(expected-actual)],
            'extra':[list(x) for x in sorted(actual-expected)]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['rules','gemini','both'],default='rules')
    parser.add_argument('--dataset',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--model',action='append',help='Compare this hosted model; repeat for multiple models.')
    parser.add_argument('--max-calls',type=int,default=8)
    parser.add_argument('--max-seconds',type=int,default=120)
    args=parser.parse_args()
    if not 1<=args.max_calls<=1000 or not 1<=args.max_seconds<=3600:parser.error('invalid budget')
    cases=[json.loads(line) for line in args.dataset.read_text(encoding='utf-8').splitlines() if line.strip()] if args.dataset else CASES
    report={'dataset_kind':'user_supplied_annotations' if args.dataset else 'authored_synthetic_smoke_fixtures',
            'reviews':len(cases),'results':{},'limitation':'No real-world model accuracy claim follows from the synthetic examples.'}
    cleaned={c['id']:extract_review(c['text'])[0] for c in cases}
    if args.mode in {'rules','both'}:
        predicted={c['id']:extract_review(c['text'])[1] for c in cases}
        report['results']['rules']=metrics(cases,predicted)
    status=0
    if args.mode in {'gemini','both'}:
        from skintellect.research.model_steps import review_client
        models=args.model or [None]
        for model in models:
            client=GeminiClient(DB_PATH,model=model) if model else review_client(DB_PATH)
            label=client.model if args.model else 'gemini'
            try:
                with run_budget(args.max_calls,args.max_seconds) as run:
                    predicted={}
                    for offset in range(0,len(cases),5):
                        batch=[{'id':c['id'],'cleaned_text':cleaned[c['id']]} for c in cases[offset:offset+5]]
                        predicted.update(analyze_review_batch(batch,DB_PATH,client))
                    report['results'][label]=metrics(cases,predicted)|{
                        'model':client.model,'metric_kind':'joint_aspect_sentiment_negation_tuple_micro',
                        'source_quotes_validated':True,'observations':sum(map(len,predicted.values())),
                        'provider_attempts':run['calls'],'events':run['events']}
            except GeminiUnavailable as exc:
                report['results'][label]={'model':client.model,'status':'unavailable','error_code':str(exc)}
                status=2
    text=json.dumps(report,indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text,encoding='utf-8')
    print(text)
    return status


if __name__=='__main__':
    raise SystemExit(main())
