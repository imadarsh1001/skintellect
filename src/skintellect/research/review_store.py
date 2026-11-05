"""Own review source identity, duplicate policy and accepted prepared observations."""
import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass

from skintellect.database import database


@dataclass
class PreparedReviews:
    observations: dict
    fingerprints: list


class ReviewCorpus:
    def __init__(self, db_path):
        self.db_path = db_path

    def read(self, product_ids=None, review_ids=None, unique=True, include_seeds=False):
        if product_ids is not None and not product_ids:
            return []
        if review_ids is not None and not review_ids:
            return []
        sql = 'SELECT r.* FROM reviews r'
        conditions, params = [], []
        if not include_seeds:
            sql += ' JOIN record_quality q ON q.product_id=r.product_id'
            conditions.append('q.is_seed=0')
        for column, selected in [('r.product_id', product_ids), ('r.id', review_ids)]:
            if selected is not None:
                conditions.append(column + ' IN (' + ','.join('?' for _ in selected) + ')')
                params.extend(selected)
        if conditions:
            sql += ' WHERE ' + ' AND '.join(conditions)
        with database(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = [dict(row) for row in connection.execute(sql + ' ORDER BY r.id', params)]
        seen, sources = set(), []
        for row in rows:
            raw = row.get('review_text') or ''
            cleaned, baseline = extract_review(raw)
            identity = (row['product_id'], ' '.join(cleaned.casefold().split()))
            duplicate = identity in seen
            if cleaned:
                seen.add(identity)
            if unique and (not cleaned or duplicate):
                continue
            sources.append(row | {'raw_text': raw, 'cleaned_text': cleaned,
                'input_hash': hashlib.sha256(raw.encode()).hexdigest(),
                'duplicate': duplicate, 'baseline': baseline})
        return sources

    @staticmethod
    def version(model):
        from skintellect.research.model_steps import REVIEW_VERSION
        return EXTRACTION_VERSION if model is None else REVIEW_VERSION + ':' + model

    @staticmethod
    def _valid(observations, source):
        if not source['cleaned_text'] or not isinstance(observations, list):
            return False
        for item in observations:
            if not isinstance(item, dict):
                return False
            start, end, span = item.get('start'), item.get('end'), item.get('span')
            if (type(start) is not int or type(end) is not int or not isinstance(span, str)
                    or not 0 <= start < end <= len(source['cleaned_text'])
                    or source['cleaned_text'][start:end] != span
                    or not isinstance(item.get('aspect'), str) or not item['aspect']
                    or not isinstance(item.get('sentiment'), str)
                    or item['sentiment'] not in {'positive', 'negative', 'neutral', 'mixed'}
                    or not isinstance(item.get('negated'), bool)):
                return False
        return True

    def cached(self, model, sources):
        expected = {s['id']: s for s in sources}
        with database(self.db_path) as connection:
            rows = connection.execute(
                'SELECT review_id,input_hash,observations_json FROM review_aspects WHERE extraction_version=?',
                (self.version(model),)).fetchall()
        accepted, fingerprints = {}, []
        for rid, input_hash, raw in rows:
            source = expected.get(rid)
            if source is None or source['input_hash'] != input_hash:
                continue
            try:
                observations = json.loads(raw)
            except (ValueError, TypeError):
                continue
            if self._valid(observations, source):
                accepted[rid] = observations
                fingerprints.append((rid, input_hash, hashlib.sha256(raw.encode()).hexdigest()))
        return PreparedReviews(accepted, sorted(fingerprints))

    def save(self, model, sources, observations):
        rows = []
        for source in sources:
            extracted = observations.get(source['id'])
            if not self._valid(extracted, source):
                raise ValueError('invalid_prepared_review')
            rows.append((source['id'], source['input_hash'], self.version(model), json.dumps(extracted)))
        with database(self.db_path) as connection:
            connection.executemany('INSERT OR REPLACE INTO review_aspects VALUES(?,?,?,?)', rows)


EXTRACTION_VERSION = 'review-rules-1'


ASPECTS = {
    'texture': r'\b(lightweight|light weight|heavy|thick|thin|greasy|oily|silky)\b',
    'hydration': r'\b(hydrat\w*|moisturiz\w*|drying|dryness)\b',
    'stickiness': r'\b(sticky|tacky)\b',
    'pilling': r'\b(pill(?:ing|s|ed)?)\b',
    'stinging': r'\b(sting\w*|burn\w*|irritat\w*)\b',
    'scent': r'\b(scent\w*|smell\w*|fragrance|perfume)\b',
    'absorption': r'\b(absorb\w*)\b',
    'value': r'\b(expensive|cheap|pricey|affordable|worth)\b',
}


def extract_review(text):
    cleaned = re.sub(r'\bshow more\b', '', text or '', flags=re.I).strip()
    observations = []
    # Clause splitting preserves mixed sentiment and local negation.
    for clause in re.finditer(r'[^.!?;,]+', cleaned):
        value = clause.group()
        for aspect, pattern in ASPECTS.items():
            for match in re.finditer(pattern, value, re.I):
                prefix = value[max(0, match.start()-35):match.start()].casefold()
                negated = bool(re.search(r"\b(?:no|not|never|didn't|doesn't|did not|does not|isn't|wasn't|without)\s+(?:\w+\s+){0,2}$", prefix))
                token = match.group().casefold()
                negative = aspect in {'stickiness', 'pilling', 'stinging'} or token in {'heavy','greasy','oily','drying','dryness','expensive','pricey'}
                neutral = aspect == 'scent' or token in {'thick', 'thin', 'worth'}
                sentiment = 'neutral' if neutral else ('negative' if negative else 'positive')
                if negated and not neutral:
                    sentiment = 'positive' if negative else 'negative'
                start, end = clause.start(), clause.end()
                observations.append({'aspect': aspect, 'sentiment': sentiment, 'negated': negated,
                                     'span': cleaned[start:end], 'start': start, 'end': end})
    return cleaned, observations

