"""Additive metadata migration and reproducible data quality audit. Never infer completeness."""
import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from skintellect.config import DB_PATH, EXPORTS_DIR


@contextmanager
def database(path):
    """Commit/rollback a transaction and always release the Windows file handle."""
    connection = sqlite3.connect(path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def migrate(db_path=DB_PATH):
    with database(db_path) as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS foundation_migrations(version INTEGER PRIMARY KEY, applied_at TEXT);
        CREATE TABLE IF NOT EXISTS record_quality(
            product_id INTEGER PRIMARY KEY REFERENCES products(id),
            is_seed INTEGER NOT NULL DEFAULT 0,
            formula_status TEXT NOT NULL DEFAULT 'unverified'
                CHECK(formula_status IN ('missing','unverified','verified_complete')),
            verified_hash TEXT, verified_at TEXT, verified_source TEXT);
        CREATE TABLE IF NOT EXISTS ingredient_aliases(alias TEXT PRIMARY KEY, canonical_name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS source_documents(
            id TEXT PRIMARY KEY, url TEXT, retrieved_at TEXT, content TEXT NOT NULL,
            content_hash TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'retrieved');
        CREATE TABLE IF NOT EXISTS review_aspects(
            review_id INTEGER NOT NULL, input_hash TEXT NOT NULL, extraction_version TEXT NOT NULL,
            observations_json TEXT NOT NULL, PRIMARY KEY(review_id, input_hash, extraction_version));
        CREATE TABLE IF NOT EXISTS rule_registry(
            id TEXT PRIMARY KEY, version TEXT NOT NULL, evidence_status TEXT NOT NULL,
            rationale TEXT NOT NULL, limitations TEXT NOT NULL);
        """)
        # Exact IDs taken from the bundled seed script, not a guessed domain or ID range.
        from skintellect.ingestion.maintenance import BENCHMARK_PRODUCTS
        seed_ids = {p['id'] for p in BENCHMARK_PRODUCTS}
        for pid, raw in c.execute('SELECT id, ingredients_json FROM products').fetchall():
            try:
                present = bool(json.loads(raw or '[]'))
            except (ValueError, TypeError):
                present = False
            c.execute('INSERT OR IGNORE INTO record_quality(product_id,is_seed,formula_status) VALUES(?,?,?)',
                      (pid, int(pid in seed_ids), 'unverified' if present else 'missing'))
        from skintellect.formulation.ingredient_facts import ALIASES
        from skintellect.research.evidence import RULE_VERSION
        c.executemany('INSERT OR IGNORE INTO ingredient_aliases VALUES(?,?)', ALIASES.items())
        c.execute('INSERT OR REPLACE INTO rule_registry VALUES(?,?,?,?,?)',
                  ('routine-cooccurrence', RULE_VERSION, 'unverified_heuristic',
                   'Report recorded ingredient co-occurrence only.',
                   'Concentration, pH, use frequency, tolerance and formulation version are unavailable.'))
        c.execute('INSERT OR IGNORE INTO foundation_migrations VALUES(1,?)',
                  (datetime.now(timezone.utc).isoformat(),))


def formula_hash(items):
    return hashlib.sha256(json.dumps(items, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def audit(db_path=DB_PATH):
    migrate(db_path)
    with database(db_path) as c:
        counts = {t: c.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]
                  for t in ('products', 'ingredients', 'reviews', 'source_documents')}
        counts['seed_products'] = c.execute('SELECT COUNT(*) FROM record_quality WHERE is_seed=1').fetchone()[0]
        counts['formulas_present'] = 0
        counts['verified_complete'] = 0
        counts['formula_link_mismatches'] = 0
        counts['invalid_formula_json'] = 0
        counts['stale_verifications'] = 0
        for pid, raw, status, verified_hash in c.execute('''SELECT p.id,p.ingredients_json,q.formula_status,q.verified_hash
                FROM products p JOIN record_quality q ON p.id=q.product_id''').fetchall():
            try:
                items = json.loads(raw or '[]')
            except (ValueError, TypeError):
                counts['invalid_formula_json'] += 1
                continue
            counts['formulas_present'] += bool(items)
            counts['verified_complete'] += bool(items and status == 'verified_complete' and verified_hash == formula_hash(items))
            counts['stale_verifications'] += status == 'verified_complete' and verified_hash != formula_hash(items)
            links = c.execute('SELECT COUNT(*) FROM product_ingredients WHERE product_id=?', (pid,)).fetchone()[0]
            counts['formula_link_mismatches'] += links != len(items)
        texts = c.execute('SELECT product_id,review_text FROM reviews').fetchall()
        counts['truncated_reviews'] = sum('show more' in (t or '').casefold() for _, t in texts)
        keys = [(pid, ' '.join((t or '').casefold().split())) for pid, t in texts if t]
        counts['duplicate_reviews'] = len(keys) - len(set(keys))
        counts['retrieval_note'] = 'Configured source labels and generated URLs are not retrieved evidence.'
        counts['created_at'] = datetime.now(timezone.utc).isoformat()
        return counts

def run_migrations():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Upgrade products table
    p_cols = [r[1] for r in c.execute("PRAGMA table_info(products)").fetchall()]
    if "domain" not in p_cols:
        c.execute("ALTER TABLE products ADD COLUMN domain TEXT DEFAULT 'skin'")
        print("  [+] Added 'domain' column to products")
    if "target_area" not in p_cols:
        c.execute("ALTER TABLE products ADD COLUMN target_area TEXT DEFAULT 'face'")
        print("  [+] Added 'target_area' column to products")

    # 2. Upgrade ingredients table
    i_cols = [r[1] for r in c.execute("PRAGMA table_info(ingredients)").fetchall()]
    if "domains_json" not in i_cols:
        c.execute("ALTER TABLE ingredients ADD COLUMN domains_json TEXT DEFAULT '[\"skin\"]'")
        print("  [+] Added 'domains_json' column to ingredients")
    if "sources_json" not in i_cols:
        c.execute("ALTER TABLE ingredients ADD COLUMN sources_json TEXT DEFAULT '[\"skinsort\", \"incidecoder\"]'")
        print("  [+] Added 'sources_json' column to ingredients")
    if "target_areas_json" not in i_cols:
        c.execute("ALTER TABLE ingredients ADD COLUMN target_areas_json TEXT DEFAULT '[\"face\"]'")
        print("  [+] Added 'target_areas_json' column to ingredients")

    # 3. Create indexes for high-speed Ingredient Explorer queries
    c.execute("CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_ingredients_function ON ingredients(function)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_product_ingredients_pid ON product_ingredients(product_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_product_ingredients_iid ON product_ingredients(ingredient_id)")

    conn.commit()
    conn.close()
    print("  [OK] Migrations completed successfully.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Schema migration and catalog quality audit.')
    parser.add_argument('command', choices=['audit', 'schema', 'metadata'], nargs='?', default='audit')
    args = parser.parse_args()
    if args.command == 'schema':
        run_migrations()
    elif args.command == 'metadata':
        migrate()
    else:
        print(json.dumps(audit(), indent=2))


if __name__ == '__main__':
    main()


def init_db(db_path: str = DB_PATH) -> None:
    """Initializes and migrates the SQLite schema with category, brand_country, skin_goals, and pricing."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        brand TEXT,
        name TEXT,
        slug TEXT,
        url TEXT,
        image_url TEXT,
        short_desc TEXT,
        match_score INTEGER,
        rating REAL,
        review_count INTEGER,
        category TEXT,
        category_slug TEXT DEFAULT 'moisturizers',
        brand_country TEXT DEFAULT 'International',
        skin_goals TEXT,
        price_tier TEXT DEFAULT '$$',
        price_tier_num INTEGER DEFAULT 2,
        price_range TEXT DEFAULT 'Moderate ($15-$30)',
        size TEXT DEFAULT '50 ml / 1.7 fl oz',
        routine_step TEXT DEFAULT 'Step 4: Moisturize & Barrier (AM/PM)',
        description TEXT,
        badges TEXT,
        has_detail INTEGER DEFAULT 0,
        fungal_acne_safe INTEGER DEFAULT -1,
        fragrance_free INTEGER DEFAULT -1,
        alcohol_free INTEGER DEFAULT -1,
        silicone_free INTEGER DEFAULT -1,
        oil_free INTEGER DEFAULT -1,
        paraben_free INTEGER DEFAULT -1,
        sulfate_free INTEGER DEFAULT -1,
        pore_clogger_free INTEGER DEFAULT -1,
        vegan INTEGER DEFAULT -1,
        cruelty_free INTEGER DEFAULT -1,
        comedogenic_max INTEGER DEFAULT 0,
        irritancy_max INTEGER DEFAULT 0,
        ingredients_json TEXT,
        community_survey TEXT,
        rating_breakdown TEXT,
        key_actives_json TEXT,
        key_benefits_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Normalized Master Ingredients Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skinsort_id INTEGER,
        name TEXT UNIQUE NOT NULL,
        slug TEXT,
        function TEXT,
        description TEXT,
        comedogenic INTEGER DEFAULT 0,
        irritancy INTEGER DEFAULT 0,
        is_pore_clogging INTEGER DEFAULT 0,
        fungal_trigger TEXT DEFAULT '',
        icons_json TEXT,
        benefits_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Many-to-Many Product Ingredients Junction Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS product_ingredients (
        product_id INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        ingredient_order INTEGER DEFAULT 0,
        is_key_ingredient INTEGER DEFAULT 0,
        key_note TEXT DEFAULT '',
        PRIMARY KEY (product_id, ingredient_id),
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
    )
    """)

    # User Reviews Table for NLP / Sentiment Analysis / Chatbot
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skinsort_post_id INTEGER UNIQUE,
        product_id INTEGER NOT NULL,
        author TEXT,
        reviewer_skin_type TEXT,
        rating INTEGER DEFAULT 5,
        date_posted TEXT,
        formulation_version TEXT DEFAULT 'Current Formulation',
        review_text TEXT,
        tags_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reviews_skin_type ON reviews(reviewer_skin_type)")

    # Migrate reviews table columns if needed
    cur.execute("PRAGMA table_info(reviews)")
    existing_rev_cols = [c[1] for c in cur.fetchall()]
    if 'formulation_version' not in existing_rev_cols:
        cur.execute("ALTER TABLE reviews ADD COLUMN formulation_version TEXT DEFAULT 'Current Formulation'")
    conn.commit()

    cur.execute("CREATE INDEX IF NOT EXISTS idx_reviews_version ON reviews(formulation_version)")
    conn.commit()

    # Migrate columns if existing database lacked them
    cur.execute("PRAGMA table_info(products)")
    existing_cols = [c[1] for c in cur.fetchall()]

    if 'category_slug' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN category_slug TEXT DEFAULT 'moisturizers'")
    if 'brand_country' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN brand_country TEXT DEFAULT 'International'")
    if 'skin_goals' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN skin_goals TEXT")
    if 'price_tier' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN price_tier TEXT DEFAULT '$$'")
    if 'price_tier_num' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN price_tier_num INTEGER DEFAULT 2")
    if 'price_range' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN price_range TEXT DEFAULT 'Moderate ($15-$30)'")
    if 'size' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN size TEXT DEFAULT '50 ml / 1.7 fl oz'")
    if 'routine_step' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN routine_step TEXT DEFAULT 'Step 4: Moisturize & Barrier (AM/PM)'")
    if 'community_survey' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN community_survey TEXT")
    if 'rating_breakdown' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN rating_breakdown TEXT")
    if 'key_actives_json' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN key_actives_json TEXT")
    if 'key_benefits_summary' not in existing_cols:
        cur.execute("ALTER TABLE products ADD COLUMN key_benefits_summary TEXT")

    conn.commit()
    conn.close()


def export_reviews_json(db_path: str = DB_PATH, json_path: str = None) -> int:
    """Exports all parsed reviews with product name and brand metadata to JSON for NLP/Chatbot/RAG pipelines."""
    if not json_path:
        json_path = os.path.join(EXPORTS_DIR, "skintellect_reviews.json")
    os.makedirs(os.path.dirname(os.path.abspath(json_path)), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            r.id,
            r.skinsort_post_id,
            r.product_id,
            p.brand,
            p.name as product_name,
            p.category,
            r.author,
            r.reviewer_skin_type,
            r.rating,
            r.date_posted,
            r.formulation_version,
            r.review_text,
            r.tags_json,
            r.created_at
        FROM reviews r
        JOIN products p ON r.product_id = p.id
        ORDER BY r.product_id ASC, r.rating DESC, r.id ASC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    for r in rows:
        if r.get('tags_json'):
            try:
                r['tags'] = json.loads(r['tags_json'])
            except Exception:
                r['tags'] = []
        else:
            r['tags'] = []

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    return len(rows)


def export_json(db_path: str = DB_PATH, json_path: str = None) -> int:
    """Exports SQLite products table to a clean, indented JSON file with parsed lists."""
    if not json_path:
        json_path = os.path.join(EXPORTS_DIR, "skintellect_moisturizers.json")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY match_score DESC, rating DESC")
    rows = [dict(r) for r in cur.fetchall()]

    # Fetch all reviews to embed directly into product records for UI rendering
    reviews_by_pid = {}
    try:
        cur.execute("SELECT skinsort_post_id, product_id, author, reviewer_skin_type, rating, date_posted, formulation_version, review_text, tags_json FROM reviews ORDER BY id ASC")
        for rev_row in cur.fetchall():
            rev_d = dict(rev_row)
            if rev_d.get('tags_json'):
                try:
                    rev_d['tags'] = json.loads(rev_d['tags_json'])
                except Exception:
                    rev_d['tags'] = []
            else:
                rev_d['tags'] = []
            reviews_by_pid.setdefault(rev_d['product_id'], []).append(rev_d)
    except Exception:
        pass
    conn.close()

    for r in rows:
        r['reviews'] = reviews_by_pid.get(r['id'], [])
        if r.get('badges'):
            try:
                r['badges'] = json.loads(r['badges'])
            except Exception:
                pass
        if r.get('skin_goals'):
            try:
                r['skin_goals'] = json.loads(r['skin_goals'])
            except Exception:
                pass
        else:
            r['skin_goals'] = []
        if r.get('ingredients_json'):
            try:
                r['ingredients_json'] = json.loads(r['ingredients_json'])
            except Exception:
                pass
        if r.get('community_survey'):
            try:
                r['community_survey'] = json.loads(r['community_survey'])
            except Exception:
                pass
        else:
            r['community_survey'] = []
        if r.get('rating_breakdown'):
            try:
                r['rating_breakdown'] = json.loads(r['rating_breakdown'])
            except Exception:
                pass
        else:
            r['rating_breakdown'] = {}
        if r.get('key_actives_json'):
            try:
                r['key_actives'] = json.loads(r['key_actives_json'])
            except Exception:
                pass
        else:
            r['key_actives'] = []
        if r.get('key_benefits_summary'):
            try:
                r['key_benefits'] = json.loads(r['key_benefits_summary'])
            except Exception:
                pass
        else:
            r['key_benefits'] = []

    os.makedirs(os.path.dirname(os.path.abspath(json_path)), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    # Also export dedicated master ingredients database to JSON
    ing_json_path = os.path.join(os.path.dirname(json_path), "skintellect_ingredients.json")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM ingredients ORDER BY name ASC")
        ing_rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        for ir in ing_rows:
            if ir.get('icons_json'):
                try:
                    ir['icons'] = json.loads(ir['icons_json'])
                except Exception:
                    pass
            if ir.get('benefits_json'):
                try:
                    ir['benefits'] = json.loads(ir['benefits_json'])
                except Exception:
                    pass
        with open(ing_json_path, "w", encoding="utf-8") as f:
            json.dump(ing_rows, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    try:
        export_reviews_json(db_path=db_path, json_path=os.path.join(os.path.dirname(json_path), "skintellect_reviews.json"))
    except Exception:
        pass

    return len(rows)
