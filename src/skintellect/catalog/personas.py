from skintellect.catalog.store import get_catalog

"""
Skintellect Personas Management Module
====================================
Canonical stage home: skintellect.catalog.personas
Manages dynamic user personas and skin profiles.
Stores personas in SQLite (`skintellect_moisturizers.db`) and exports to `skintellect_personas.json`.
Primary default persona: 'uap'.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List

# Robust DB Path Resolution (supports root execution or execution from subfolders)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
from skintellect.config import DB_PATH, EXPORTS_DIR

BASE_DIR = os.path.dirname(DB_PATH)
JSON_PATH = os.path.join(EXPORTS_DIR, "skintellect_personas.json")

DEFAULT_PERSONAS: List[Dict[str, Any]] = [
    {
        "id": "uap",
        "username": "uap",
        "label": "uap (Combination · Barrier & Dark Spots)",
        "description": "Combination skin with oily T-zone, dry cheeks, post-inflammatory hyperpigmentation, rough texture, and strict fungal acne avoidance.",
        "skin_type": "combination",
        "sensitivity": "slightly_sensitive",
        "target_concerns": ["dark_spots", "dryness", "dullness", "rough_texture"],
        "safety_exclusions": {
            "fungal_acne_safe": True,
            "fragrance_free": True,
            "alcohol_free": True,
            "oil_free": False,
            "pore_clogger_free": True
        },
        "is_default": 1
    },
    {
        "id": "oily_acne",
        "username": "clearskin",
        "label": "ClearSkin (Oily & Acne-Prone)",
        "description": "Excess sebum production, active breakouts, clogged pores; prioritizes Salicylic Acid (BHA), Zinc PCA, Niacinamide, and oil-free gel textures.",
        "skin_type": "oily",
        "sensitivity": "resilient",
        "target_concerns": ["acne", "large_pores", "oil_control", "rough_texture"],
        "safety_exclusions": {
            "fungal_acne_safe": False,
            "fragrance_free": False,
            "alcohol_free": False,
            "oil_free": True,
            "pore_clogger_free": True
        },
        "is_default": 0
    },
    {
        "id": "dry_barrier",
        "username": "hydrashield",
        "label": "HydraShield (Dry & Barrier-Damaged)",
        "description": "Tightness, flaking, depleted lipid barrier; prioritizes Ceramides (NP/AP/EOP), Cholesterol, Squalane, Hyaluronic Acid, and rich emollients.",
        "skin_type": "dry",
        "sensitivity": "sensitive",
        "target_concerns": ["dryness", "barrier_repair", "flaking", "redness"],
        "safety_exclusions": {
            "fungal_acne_safe": False,
            "fragrance_free": True,
            "alcohol_free": True,
            "oil_free": False,
            "pore_clogger_free": False
        },
        "is_default": 0
    },
    {
        "id": "sensitive_rosacea",
        "username": "calmflora",
        "label": "CalmFlora (Sensitive & Rosacea-Prone)",
        "description": "Easily flushed, reactive, burning sensation; requires strict hypoallergenic, anti-inflammatory, fragrance-free care with Centella & Panthenol.",
        "skin_type": "sensitive",
        "sensitivity": "very_sensitive",
        "target_concerns": ["redness", "sensitivity", "barrier_repair"],
        "safety_exclusions": {
            "fungal_acne_safe": False,
            "fragrance_free": True,
            "alcohol_free": True,
            "oil_free": False,
            "pore_clogger_free": False
        },
        "is_default": 0
    },
    {
        "id": "mature_antiaging",
        "username": "youthrenewal",
        "label": "YouthRenewal (Mature & Anti-Aging)",
        "description": "Fine lines, wrinkles, loss of elasticity, uneven tone; prioritizes Retinoids, Peptides, Vitamin C, and collagen-boosting antioxidants.",
        "skin_type": "normal",
        "sensitivity": "normal",
        "target_concerns": ["anti_aging", "fine_lines", "elasticity", "dullness"],
        "safety_exclusions": {
            "fungal_acne_safe": False,
            "fragrance_free": False,
            "alcohol_free": False,
            "oil_free": False,
            "pore_clogger_free": False
        },
        "is_default": 0
    },
    {
        "id": "fungal_strict",
        "username": "malasseziazero",
        "label": "MalasseziaZero (Strict Fungal Acne Safe)",
        "description": "100% Malassezia yeast safe; strictly zero fatty acid esters, plant oils, or polysorbates that feed folliculitis.",
        "skin_type": "combination",
        "sensitivity": "moderate",
        "target_concerns": ["fungal_acne", "congestion", "oil_control"],
        "safety_exclusions": {
            "fungal_acne_safe": True,
            "fragrance_free": False,
            "alcohol_free": False,
            "oil_free": True,
            "pore_clogger_free": True
        },
        "is_default": 0
    }
]


def init_personas_db() -> None:
    """Initializes the personas table in SQLite and seeds default personas if empty."""
    conn = sqlite3.connect(get_catalog().path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            label TEXT NOT NULL,
            description TEXT,
            skin_type TEXT NOT NULL,
            sensitivity TEXT NOT NULL,
            target_concerns TEXT NOT NULL,
            safety_exclusions TEXT NOT NULL,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed defaults if empty
    cur.execute("SELECT COUNT(*) FROM personas")
    count = cur.fetchone()[0]
    if count == 0:
        for p in DEFAULT_PERSONAS:
            cur.execute("""
                INSERT OR REPLACE INTO personas (
                    id, username, label, description, skin_type, sensitivity,
                    target_concerns, safety_exclusions, is_default, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["id"],
                p["username"],
                p["label"],
                p["description"],
                p["skin_type"],
                p["sensitivity"],
                json.dumps(p["target_concerns"]),
                json.dumps(p["safety_exclusions"]),
                p["is_default"],
                datetime.now(timezone.utc).isoformat()
            ))
        conn.commit()
    conn.close()


def get_all_personas() -> List[Dict[str, Any]]:
    """Returns all stored personas from the database."""
    init_personas_db()
    conn = sqlite3.connect(get_catalog().path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM personas ORDER BY is_default DESC, id ASC")
    rows = cur.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        d["target_concerns"] = json.loads(d["target_concerns"]) if isinstance(d["target_concerns"], str) else d["target_concerns"]
        d["safety_exclusions"] = json.loads(d["safety_exclusions"]) if isinstance(d["safety_exclusions"], str) else d["safety_exclusions"]
        result.append(d)
    return result


def export_personas_json() -> str:
    """Exports all personas to skintellect_personas.json and returns file path."""
    personas = get_all_personas()
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(personas, f, indent=2, ensure_ascii=False)
    print(f"[OK] Exported {len(personas)} personas to {JSON_PATH}")
    return JSON_PATH


def save_persona(payload):
    """Creates and persists a custom skin persona in SQLite and JSON."""
    username = payload.username.strip().lower()
    pid = f"custom_{username}"

    conn = sqlite3.connect(get_catalog().path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO personas (
            id, username, label, description, skin_type, sensitivity,
            target_concerns, safety_exclusions, is_default, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (
        pid,
        username,
        payload.label,
        payload.description,
        payload.skin_type,
        payload.sensitivity,
        json.dumps(payload.target_concerns),
        json.dumps(payload.safety_exclusions.dict()),
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()

    export_personas_json()
    personas = get_all_personas()
    saved = next((p for p in personas if p["id"] == pid), None)
    if not saved:
        raise RuntimeError("Failed to create persona")
    return saved


if __name__ == "__main__":
    init_personas_db()
    path = export_personas_json()
    print("Default Personas Loaded:")
    for p in get_all_personas():
        default_tag = " (DEFAULT)" if p.get("is_default") else ""
        print(f" - [{p['username']}]{default_tag} {p['label']}")
