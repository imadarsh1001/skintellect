"""Own saved passage-vector acceptance, repair eligibility and persistence."""
import hashlib
import json
import math
from dataclasses import dataclass

from skintellect.config import IS_REMOTE_DB
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
        # Remote (Turso) stores native F16_BLOB vectors: membership and
        # fingerprints come from metadata, similarity runs server-side.
        self.native = IS_REMOTE_DB

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
        vector_col = 'vector' if self.native else 'vector_json'
        with database(self.db_path) as connection:
            rows = connection.execute(
                f'SELECT evidence_id,content_hash,dimensions,{vector_col} FROM research_vectors WHERE model=?',
                (self.model,)).fetchall()
        vectors, fingerprints = {}, []
        for eid, content_hash, dimensions, raw in rows:
            if eid not in expected or expected[eid] != content_hash:
                continue
            if self.native:
                # Vector payloads stay server-side; only membership and a
                # stable change fingerprint are tracked locally.
                vectors[eid] = None
                fingerprints.append((eid, content_hash,
                                     hashlib.sha256((self.model + ':' + content_hash).encode()).hexdigest()))
            else:
                vector = self._decode(raw, dimensions)
                if vector is not None:
                    vectors[eid] = vector
                    fingerprints.append((eid, content_hash, hashlib.sha256(raw.encode()).hexdigest()))
        return PassageState(vectors, sorted(fingerprints),
                            [d for d in documents if d['evidence_id'] not in vectors], len(rows))

    def rank(self, query_vector, documents, limit=5000):
        """Server-side cosine ranking over stored F16_BLOB vectors (remote only).

        Returns [(evidence_id, similarity)] for current, hash-matched passages.
        Stale rows are filtered in Python after the fetch so the ranking never
        injects evidence that no longer matches the corpus.
        """
        if not self.native:
            raise ValueError('native_ranking_requires_remote_db')
        expected = {d['evidence_id']: d['content_hash'] for d in documents}
        query_json = json.dumps([float(v) for v in query_vector])
        with database(self.db_path) as connection:
            rows = connection.execute(
                'SELECT evidence_id,content_hash,1 - vector_distance_cos(vector, vector16(?)) AS sim '
                'FROM research_vectors WHERE model=? ORDER BY sim DESC LIMIT ?',
                (query_json, self.model, limit)).fetchall()
        return [(eid, sim) for eid, content_hash, sim in rows
                if expected.get(eid) == content_hash]

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
            if self.native:
                # vector16() parses the JSON text into a half-precision blob server-side.
                connection.executemany(
                    'INSERT OR REPLACE INTO research_vectors VALUES(?,?,?,?,vector16(?))', rows)
            else:
                connection.executemany('INSERT OR REPLACE INTO research_vectors VALUES(?,?,?,?,?)', rows)
