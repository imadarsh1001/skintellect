"""Small evidence graph projected from recorded facts; no invented causal edges."""
from collections import Counter

from skintellect.formulation.ingredient_facts import normalize


def connections(product_id,db_path,limit=5):
    from skintellect.catalog.products import load_records
    from skintellect.research.references import references
    records=[p for p in load_records(db_path) if p.get('is_seed')==0]
    target=next((p for p in records if p['id']==product_id),None)
    if not target:return None
    frequency=Counter(n for p in records for n in set(p['names']))
    a=set(target['names']);related=[]
    for p in records:
        if p['id']==product_id or p.get('domain')!=target.get('domain') or p.get('category')!=target.get('category'):continue
        shared=a & set(p['names'])
        if not shared:continue
        score=sum(1/frequency[n] for n in shared)
        related.append((score,p,sorted(shared,key=lambda n:(frequency[n],n))[:3]))
    related.sort(key=lambda row:(-row[0],row[1]['id']))
    nodes={'product:'+str(product_id):{'id':'product:'+str(product_id),'type':'product','label':target['name']}}
    edges=[];paths=[]
    for score,p,shared in related[:limit]:
        eid='product:'+str(p['id'])
        nodes[eid]={'id':eid,'type':'product','label':p['name']}
        paths.append({'product_id':p['id'],'name':p['name'],'shared_ingredients':shared,'evidence_ids':['product:'+str(product_id),eid]})
        for name in shared:
            iid='ingredient:'+name
            nodes[iid]={'id':iid,'type':'ingredient','label':name}
            for pid in (product_id,p['id']):
                edge={'from':'product:'+str(pid),'to':iid,'relation':'recorded_contains','evidence_id':'product:'+str(pid)}
                if edge not in edges:edges.append(edge)
    for source in references(db_path):
        for topic in source['topics']:
            n=normalize(topic)
            if n not in a:continue
            iid='ingredient:'+n;sid=source['evidence_id']
            nodes[iid]={'id':iid,'type':'ingredient','label':n}
            nodes[sid]={'id':sid,'type':'reference','label':source['title']}
            edge={'from':'product:'+str(product_id),'to':iid,'relation':'recorded_contains','evidence_id':'product:'+str(product_id)}
            if edge not in edges:edges.append(edge)
            edges.append({'from':sid,'to':iid,'relation':'discusses','evidence_id':sid})
    return {'product_id':product_id,'nodes':list(nodes.values()),'edges':edges,'paths':paths,
        'notice':'Edges describe recorded ingredients and reference topics. Shared ingredients do not prove equal efficacy, concentration, compatibility or safety.'}
