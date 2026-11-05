"""Own saved passage-vector acceptance, repair eligibility and persistence."""
import hashlib
import json
import math
from dataclasses import dataclass

from skintellect.database import database
from skintellect.gemini import ensure_tables


@dataclass
class PassageState:
    vectors: dict
    fingerprints: list
    pending: list
    stored_count: int


class PassageIndex:
    def __init__(self, db_path, model, dimensions):
        self.db_path = db_path
        self.model = model
        self.dimensions = dimensions

    def _decode(self, raw, dimensions):
        try:
            vector = json.loads(raw)
            if (dimensions != self.dimensions or not isinstance(vector, list)
                    or len(vector) != dimensions or not vector
                    or not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                               and math.isfinite(v) for v in vector)
                    or abs(sum(v * v for v in vector) - 1) > .001):
                return None
            return vector
        except (ValueError, TypeError, OverflowError):
            return None

    def read(self, documents):
        ensure_tables(self.db_path)
        expected = {d['evidence_id']: d['content_hash'] for d in documents}
        with database(self.db_path) as connection:
            rows = connection.execute(
                'SELECT evidence_id,content_hash,dimensions,vector_json FROM research_vectors WHERE model=?',
                (self.model,)).fetchall()
        vectors, fingerprints = {}, []
        for eid, content_hash, dimensions, raw in rows:
            if eid not in expected or expected[eid] != content_hash:
                continue
            vector = self._decode(raw, dimensions)
            if vector is not None:
                vectors[eid] = vector
                fingerprints.append((eid, content_hash, hashlib.sha256(raw.encode()).hexdigest()))
        return PassageState(vectors, sorted(fingerprints),
                            [d for d in documents if d['evidence_id'] not in vectors], len(rows))

    def save(self, documents, vectors):
        if len(documents) != len(vectors):
            raise ValueError('embedding_batch_size_mismatch')
        rows = []
        for doc, vector in zip(documents, vectors):
            raw = json.dumps(vector)
            if self._decode(raw, self.dimensions) is None:
                raise ValueError('invalid_passage_vector')
            rows.append((doc['evidence_id'], self.model, doc['content_hash'], self.dimensions, raw))
        ensure_tables(self.db_path)
        with database(self.db_path) as connection:
            connection.executemany('INSERT OR REPLACE INTO research_vectors VALUES(?,?,?,?,?)', rows)
