

import json
import sqlite3
from datetime import datetime, timezone

from skintellect.config import DB_PATH

BENCHMARK_PRODUCTS = [
    # ==========================================
    # 💇 HAIR & SCALP (Trichology & Strands)
    # ==========================================
    {
        "id": 200001,
        "brand": "Olaplex",
        "name": "No. 4 Bond Maintenance Shampoo",
        "slug": "olaplex-no-4-bond-maintenance-shampoo",
        "domain": "hair",
        "target_area": "scalp",
        "category": "Shampoos",
        "category_slug": "shampoos",
        "brand_country": "United States",
        "price_tier": "$$$",
        "price_tier_num": 3,
        "price_range": "Premium ($30-$60)",
        "rating": 4.6,
        "review_count": 840,
        "match_score": 96,
        "size": "250 ml / 8.5 fl oz",
        "routine_step": "Step 1: Cleanse (Scalp Wash)",
        "fungal_acne_safe": 0,
        "fragrance_free": 0,
        "alcohol_free": 1,
        "silicone_free": 0,
        "oil_free": 1,
        "sulfate_free": 1,
        "pore_clogger_free": 1,
        "vegan": 1,
        "cruelty_free": 1,
        "short_desc": "Patented bis-aminopropyl diglycol dimaleate restores broken disulfide bonds while gently cleansing without stripping moisture.",
        "description": "Formulated with Olaplex Bond Building chemistry. Restores internal strength and moisture levels to add incredible shine and manageability.",
        "skin_goals": ["Bond Repair", "Color Protection", "Scalp Health"],
        "ingredients": [
            {"name": "Water", "key": False, "note": "Solvent"},
            {"name": "Sodium Lauroyl Methyl Isethionate", "key": True, "note": "Gentle sulfate-free surfactant"},
            {"name": "Cocamidopropyl Hydroxysultaine", "key": False, "note": "Conditioning foam booster"},
            {"name": "Potassium Cocoyl Glycinate", "key": False, "note": "Mild amino-acid surfactant"},
            {"name": "Bis-Aminopropyl Diglycol Dimaleate", "key": True, "note": "Patented disulfide bond builder"},
            {"name": "Glycerin", "key": False, "note": "Humectant"},
            {"name": "Panthenol", "key": True, "note": "Pro-vitamin B5 strand strengthener"},
            {"name": "Tocopherol", "key": False, "note": "Antioxidant Vitamin E"}
        ]
    },
    {
        "id": 200002,
        "brand": "K18",
        "name": "Leave-In Molecular Repair Hair Mask",
        "slug": "k18-leave-in-molecular-repair-hair-mask",
        "domain": "hair",
        "target_area": "hair_strands",
        "category": "Hair Masks",
        "category_slug": "hair-masks",
        "brand_country": "United States",
        "price_tier": "$$$$",
        "price_tier_num": 4,
        "price_range": "Luxury ($60+)",
        "rating": 4.8,
        "review_count": 920,
        "match_score": 98,
        "size": "50 ml / 1.7 fl oz",
        "routine_step": "Step 3: Treat & Target (Bond Mask)",
        "fungal_acne_safe": 1,
        "fragrance_free": 0,
        "alcohol_free": 0,
        "silicone_free": 1,
        "oil_free": 1,
        "sulfate_free": 1,
        "pore_clogger_free": 1,
        "vegan": 1,
        "cruelty_free": 1,
        "short_desc": "Biomimetic peptide treatment reconnects polypeptide keratin chains broken by bleach, chemical treatments, and heat.",
        "description": "K18Peptide travels deep into the core inner layers of hair to reconnect broken keratin chains, renewing core strength and elasticity in 4 minutes.",
        "skin_goals": ["Keratin Repair", "Porosity Control", "Curl Definition (CGM)"],
        "ingredients": [
            {"name": "Water", "key": False, "note": "Solvent"},
            {"name": "Alcohol Denat.", "key": False, "note": "Penetration enhancer"},
            {"name": "Propylene Glycol", "key": False, "note": "Humectant"},
            {"name": "Cetearyl Alcohol", "key": False, "note": "Fatty alcohol conditioner"},
            {"name": "Dicaprylyl Ether", "key": False, "note": "Fast-spreading emollient"},
            {"name": "sh-Oligopeptide-78", "key": True, "note": "Patented K18 biomimetic peptide"},
            {"name": "Hydrolyzed Wheat Protein", "key": True, "note": "Tensile strength booster"},
            {"name": "Hydrolyzed Wheat Starch", "key": False, "note": "Film former"}
        ]
    },
    {
        "id": 200003,
        "brand": "Nizoral",
        "name": "Anti-Dandruff 1% Ketoconazole Shampoo",
        "slug": "nizoral-anti-dandruff-shampoo",
        "domain": "hair",
        "target_area": "scalp",
        "category": "Clarifying Treatments",
        "category_slug": "clarifying-treatments",
        "brand_country": "United States",
        "price_tier": "$",
        "price_tier_num": 1,
        "price_range": "Budget (<$15)",
        "rating": 4.7,
        "review_count": 1420,
        "match_score": 95,
        "size": "200 ml / 7 fl oz",
        "routine_step": "Step 1: Cleanse (Therapeutic Wash)",
        "fungal_acne_safe": 1,
        "fragrance_free": 0,
        "alcohol_free": 1,
        "silicone_free": 1,
        "oil_free": 1,
        "sulfate_free": 0,
        "pore_clogger_free": 1,
        "vegan": 0,
        "cruelty_free": 0,
        "short_desc": "Clinical strength ketoconazole antifungal shampoo targets Malassezia yeast overgrowth causing flaking and itching.",
        "description": "Proven clinically to control dandruff, itching, and flaking. Targets the root fungal cause of seborrheic dermatitis on scalp.",
        "skin_goals": ["Scalp Barrier & Flakes (Dandruff)", "Oil Control", "Microbiome Balance"],
        "ingredients": [
            {"name": "Ketoconazole", "key": True, "note": "Antifungal active 1%"},
            {"name": "Water", "key": False, "note": "Solvent"},
            {"name": "Sodium Laureth Sulfate", "key": False, "note": "Surfactant"},
            {"name": "Cocamide MEA", "key": False, "note": "Foam stabilizer"},
            {"name": "Sodium Chloride", "key": False, "note": "Viscosity controller"},
            {"name": "Hydrolyzed Collagen", "key": False, "note": "Conditioning protein"}
        ]
    },
    {
        "id": 200004,
        "brand": "The Ordinary",
        "name": "Multi-Peptide Serum for Hair Density",
        "slug": "the-ordinary-multi-peptide-serum-hair-density",
        "domain": "hair",
        "target_area": "scalp",
        "category": "Scalp Serums",
        "category_slug": "scalp-serums",
        "brand_country": "Canada",
        "price_tier": "$$",
        "price_tier_num": 2,
        "price_range": "Moderate ($15-$30)",
        "rating": 4.4,
        "review_count": 510,
        "match_score": 94,
        "size": "60 ml / 2 fl oz",
        "routine_step": "Step 3: Treat & Target (Scalp Drops)",
        "fungal_acne_safe": 1,
        "fragrance_free": 1,
        "alcohol_free": 1,
        "silicone_free": 1,
        "oil_free": 1,
        "sulfate_free": 1,
        "pore_clogger_free": 1,
        "vegan": 1,
        "cruelty_free": 1,
        "short_desc": "Concentrated leave-in scalp serum with REDENSYL, Procapil, and CAPIXYL complexes to support hair follicle health and density.",
        "description": "Lightweight, water-based serum designed to support the scalp and give hair a thicker, denser, and fuller appearance.",
        "skin_goals": ["Hair Thinning & Density", "Scalp Health", "Follicle Stimulation"],
        "ingredients": [
            {"name": "Water", "key": False, "note": "Solvent"},
            {"name": "Propanediol", "key": False, "note": "Humectant"},
            {"name": "Butylene Glycol", "key": False, "note": "Carrier"},
            {"name": "Glycerin", "key": False, "note": "Humectant"},
            {"name": "Caffeine", "key": True, "note": "Microcirculation stimulant"},
            {"name": "Biotinoyl Tripeptide-1", "key": True, "note": "Follicle anchorage peptide"},
            {"name": "Acetyl Tetrapeptide-3", "key": True, "note": "Extracellular matrix peptide"},
            {"name": "Trifolium Pratense (Clover) Flower Extract", "key": False, "note": "Botanical active"},
            {"name": "Glycine", "key": False, "note": "Amino acid"}
        ]
    },

    # ==========================================
    # 🧼 BATH & BODY (Keratosis Pilaris & Bacne)
    # ==========================================
    {
        "id": 200005,
        "brand": "CeraVe",
        "name": "SA Cream for Rough & Bumpy Skin",
        "slug": "cerave-sa-cream-rough-and-bumpy-skin",
        "domain": "body",
        "target_area": "arms_legs",
        "category": "Body Lotions",
        "category_slug": "body-lotions",
        "brand_country": "United States",
        "price_tier": "$$",
        "price_tier_num": 2,
        "price_range": "Moderate ($15-$30)",
        "rating": 4.6,
        "review_count": 1150,
        "match_score": 97,
        "size": "340 g / 12 oz",
        "routine_step": "Step 4: Moisturize (Body Barrier)",
        "fungal_acne_safe": 0,
        "fragrance_free": 1,
        "alcohol_free": 1,
        "silicone_free": 0,
        "oil_free": 0,
        "sulfate_free": 1,
        "pore_clogger_free": 0,
        "vegan": 0,
        "cruelty_free": 0,
        "short_desc": "Keratolytic salicylic acid, lactic acid, 10% urea, and 3 essential ceramides exfoliate bumpy Keratosis Pilaris while restoring body barrier.",
        "description": "Formulated with MVE technology to release moisturizing ingredients over 24 hours. Exfoliates rough skin patches without disrupting protective barrier.",
        "skin_goals": ["Keratosis Pilaris (Strawberry Skin)", "Barrier Repair", "Rough Texture"],
        "ingredients": [
            {"name": "Water", "key": False, "note": "Solvent"},
            {"name": "Glycerin", "key": False, "note": "Humectant"},
            {"name": "Salicylic Acid", "key": True, "note": "Beta-hydroxy acid keratolytic"},
            {"name": "Lactic Acid", "key": True, "note": "Alpha-hydroxy acid exfoliant"},
            {"name": "Urea", "key": True, "note": "Natural moisturizing factor & keratolytic"},
            {"name": "Ceramide NP", "key": True, "note": "Essential barrier lipid"},
            {"name": "Ceramide AP", "key": True, "note": "Essential barrier lipid"},
            {"name": "Ceramide EOP", "key": True, "note": "Essential barrier lipid"},
            {"name": "Cholesterol", "key": True, "note": "Lipid bilayer stabilizer"},
            {"name": "Niacinamide", "key": True, "note": "Vitamin B3 soothing"}
        ]
    },
    {
        "id": 200006,
        "brand": "PanOxyl",
        "name": "10% Benzoyl Peroxide Acne Foaming Wash",
        "slug": "panoxyl-10-benzoyl-peroxide-acne-foaming-wash",
        "domain": "body",
        "target_area": "back_chest",
        "category": "Body Washes",
        "category_slug": "body-washes",
        "brand_country": "United States",
        "price_tier": "$",
        "price_tier_num": 1,
        "price_range": "Budget (<$15)",
        "rating": 4.7,
        "review_count": 980,
        "match_score": 96,
        "size": "156 g / 5.5 oz",
        "routine_step": "Step 1: Cleanse (Body Wash)",
        "fungal_acne_safe": 1,
        "fragrance_free": 1,
        "alcohol_free": 1,
        "silicone_free": 1,
        "oil_free": 1,
        "sulfate_free": 1,
        "pore_clogger_free": 1,
        "vegan": 1,
        "cruelty_free": 0,
        "short_desc": "Maximum strength 10% Benzoyl Peroxide antibacterial cleanser clears active chest and back acne (bacne) and unclogs body pores.",
        "description": "Fast-acting foaming wash penetrates pores to kill acne-causing bacteria on contact. Recommended by dermatologists for chest, back, and body breakouts.",
        "skin_goals": ["Body Acne (Bacne)", "Pore Clearing", "Antibacterial"],
        "ingredients": [
            {"name": "Benzoyl Peroxide", "key": True, "note": "Antibacterial acne active 10%"},
            {"name": "Water", "key": False, "note": "Solvent"},
            {"name": "Glycerin", "key": False, "note": "Humectant"},
            {"name": "Carbomer", "key": False, "note": "Gel former"},
            {"name": "Potassium Hydroxide", "key": False, "note": "pH adjuster"},
            {"name": "Sodium Cocoyl Glycinate", "key": False, "note": "Gentle cleanser"}
        ]
    },
    {
        "id": 200007,
        "brand": "AmLactin",
        "name": "Daily 12% Lactic Acid Body Lotion",
        "slug": "amlactin-daily-12-lactic-acid-body-lotion",
        "domain": "body",
        "target_area": "arms_legs",
        "category": "Body Lotions",
        "category_slug": "body-lotions",
        "brand_country": "United States",
        "price_tier": "$$",
        "price_tier_num": 2,
        "price_range": "Moderate ($15-$30)",
        "rating": 4.5,
        "review_count": 760,
        "match_score": 95,
        "size": "225 g / 7.9 oz",
        "routine_step": "Step 4: Moisturize (Body Hydration)",
        "fungal_acne_safe": 1,
        "fragrance_free": 1,
        "alcohol_free": 1,
        "silicone_free": 1,
        "oil_free": 0,
        "sulfate_free": 1,
        "pore_clogger_free": 0,
        "vegan": 0,
        "cruelty_free": 0,
        "short_desc": "12% ammonium lactate formulation boosts skin's natural renewal through gentle exfoliation for dry, rough, strawberry skin.",
        "description": "Clinically proven formula with 12% lactic acid neutralized with ammonium hydroxide for effective exfoliation and deep hydration.",
        "skin_goals": ["Keratosis Pilaris (Strawberry Skin)", "Extreme Dryness (Xerosis)", "Rough Calluses"],
        "ingredients": [
            {"name": "Water", "key": False, "note": "Solvent"},
            {"name": "Ammonium Lactate", "key": True, "note": "12% Lactic acid keratolytic"},
            {"name": "Mineral Oil", "key": False, "note": "Occlusive emollient"},
            {"name": "Propylene Glycol", "key": False, "note": "Humectant"},
            {"name": "Glycerin", "key": False, "note": "Humectant"},
            {"name": "Magnesium Aluminum Silicate", "key": False, "note": "Stabilizer"}
        ]
    },

    # ==========================================
    # 💄 MAKEUP & COMPLEXION (Non-Acnegenic Base)
    # ==========================================
    {
        "id": 200008,
        "brand": "NARS",
        "name": "Radiant Creamy Concealer",
        "slug": "nars-radiant-creamy-concealer",
        "domain": "makeup",
        "target_area": "complexion",
        "category": "Concealers",
        "category_slug": "concealers",
        "brand_country": "France",
        "price_tier": "$$$",
        "price_tier_num": 3,
        "price_range": "Premium ($30-$60)",
        "rating": 4.8,
        "review_count": 1850,
        "match_score": 97,
        "size": "6 ml / 0.22 fl oz",
        "routine_step": "Step 6: Base Coverage",
        "fungal_acne_safe": 1,
        "fragrance_free": 1,
        "alcohol_free": 1,
        "silicone_free": 0,
        "oil_free": 1,
        "sulfate_free": 1,
        "pore_clogger_free": 1,
        "vegan": 0,
        "cruelty_free": 0,
        "short_desc": "Multi-award winning non-comedogenic liquid concealer with light-diffusing mineral pigments and Vitamin E.",
        "description": "Delivers all-purpose, 16-hour perfection with a natural, radiant finish. Enriched with hydrating, multi-action skincare benefits.",
        "skin_goals": ["Non-Acnegenic Coverage", "Dark Spots & Melanin", "Long-Wear Transfer Resistance"],
        "ingredients": [
            {"name": "Water", "key": False, "note": "Solvent"},
            {"name": "Dimethicone", "key": False, "note": "Silicone smooth base"},
            {"name": "Hydrogenated Polydecene", "key": False, "note": "Emollient"},
            {"name": "Titanium Dioxide", "key": True, "note": "Mineral pigment & UV blocker"},
            {"name": "Iron Oxides", "key": True, "note": "Mineral colorant pigments"},
            {"name": "Tocopheryl Acetate", "key": True, "note": "Vitamin E antioxidant"},
            {"name": "Glycerin", "key": False, "note": "Humectant"}
        ]
    },
    {
        "id": 200009,
        "brand": "Rare Beauty",
        "name": "Positive Light Tinted Moisturizer SPF 20",
        "slug": "rare-beauty-positive-light-tinted-moisturizer",
        "domain": "makeup",
        "target_area": "complexion",
        "category": "Tinted Moisturizers",
        "category_slug": "tinted-moisturizers",
        "brand_country": "United States",
        "price_tier": "$$$",
        "price_tier_num": 3,
        "price_range": "Premium ($30-$60)",
        "rating": 4.6,
        "review_count": 620,
        "match_score": 96,
        "size": "30 ml / 1.0 fl oz",
        "routine_step": "Step 6: Base Coverage & SPF",
        "fungal_acne_safe": 1,
        "fragrance_free": 1,
        "alcohol_free": 1,
        "silicone_free": 0,
        "oil_free": 1,
        "sulfate_free": 1,
        "pore_clogger_free": 1,
        "vegan": 1,
        "cruelty_free": 1,
        "short_desc": "Weightless, non-comedogenic skin tint with Vitamin E and botanical extracts providing breathable light-to-medium coverage.",
        "description": "Feels like nothing on skin while blurring imperfections. Blends effortlessly with SPF 20 broad spectrum protection.",
        "skin_goals": ["Non-Acnegenic Coverage", "Hydrating Finish", "SPF Protection in Makeup"],
        "ingredients": [
            {"name": "Zinc Oxide", "key": True, "note": "Mineral broad-spectrum SPF"},
            {"name": "Titanium Dioxide", "key": True, "note": "Mineral UV & pigment"},
            {"name": "Water", "key": False, "note": "Solvent"},
            {"name": "Dimethicone", "key": False, "note": "Skin protectant"},
            {"name": "Glycerin", "key": False, "note": "Hydrator"},
            {"name": "Tocopherol", "key": True, "note": "Vitamin E"}
        ]
    },
    {
        "id": 200010,
        "brand": "Tower 28",
        "name": "SOS Daily Rescue Lip Softener",
        "slug": "tower-28-sos-lip-softener",
        "domain": "makeup",
        "target_area": "lips",
        "category": "Lip Balms & Tints",
        "category_slug": "lip-balms",
        "brand_country": "United States",
        "price_tier": "$",
        "price_tier_num": 1,
        "price_range": "Budget (<$15)",
        "rating": 4.7,
        "review_count": 480,
        "match_score": 98,
        "size": "15 ml / 0.5 fl oz",
        "routine_step": "Step 6: Lip Care",
        "fungal_acne_safe": 1,
        "fragrance_free": 1,
        "alcohol_free": 1,
        "silicone_free": 1,
        "oil_free": 0,
        "sulfate_free": 1,
        "pore_clogger_free": 1,
        "vegan": 1,
        "cruelty_free": 1,
        "short_desc": "National Eczema Association approved barrier lip treatment with soothing shea butter and squalane.",
        "description": "Specially formulated for sensitive, dry lips prone to eczema, cracking, and dermatitis. Completely fragrance-free.",
        "skin_goals": ["Barrier Repair", "Lip Care", "Hypoallergenic"],
        "ingredients": [
            {"name": "Squalane", "key": True, "note": "Biomimetic barrier lipid"},
            {"name": "Butyrospermum Parkii (Shea) Butter", "key": True, "note": "Rich plant emollient"},
            {"name": "Euphorbia Cerifera (Candelilla) Wax", "key": False, "note": "Natural wax base"},
            {"name": "Tocopherol", "key": True, "note": "Antioxidant Vitamin E"}
        ]
    }
]

def seed_multidomain(db_path: str = DB_PATH):
    print(f"[*] Seeding Multi-Domain Benchmark Formulations into {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Ensure schema columns exist
    try:
        cur.execute("ALTER TABLE products ADD COLUMN domain TEXT DEFAULT 'skin'")
        cur.execute("ALTER TABLE products ADD COLUMN target_area TEXT DEFAULT 'face'")
    except Exception:
        pass

    inserted_prods = 0
    inserted_ings = 0
    linked_ings = 0

    for p in BENCHMARK_PRODUCTS:
        # Check if product exists
        cur.execute("SELECT id FROM products WHERE id = ?", (p["id"],))
        existing = cur.fetchone()

        ing_json = json.dumps([i["name"] for i in p["ingredients"]])
        goals_json = json.dumps(p["skin_goals"])
        now_str = datetime.now(timezone.utc).isoformat()

        if existing:
            cur.execute("""
                UPDATE products SET
                    brand = ?, name = ?, slug = ?, category = ?, category_slug = ?,
                    brand_country = ?, price_tier = ?, price_tier_num = ?, price_range = ?,
                    rating = ?, review_count = ?, match_score = ?, size = ?, routine_step = ?,
                    fungal_acne_safe = ?, fragrance_free = ?, alcohol_free = ?, silicone_free = ?,
                    oil_free = ?, sulfate_free = ?, pore_clogger_free = ?, vegan = ?, cruelty_free = ?,
                    short_desc = ?, description = ?, skin_goals = ?, ingredients_json = ?,
                    domain = ?, target_area = ?, has_detail = 1
                WHERE id = ?
            """, (
                p["brand"], p["name"], p["slug"], p["category"], p["category_slug"],
                p["brand_country"], p["price_tier"], p["price_tier_num"], p["price_range"],
                p["rating"], p["review_count"], p["match_score"], p["size"], p["routine_step"],
                p["fungal_acne_safe"], p["fragrance_free"], p["alcohol_free"], p["silicone_free"],
                p["oil_free"], p["sulfate_free"], p["pore_clogger_free"], p["vegan"], p["cruelty_free"],
                p["short_desc"], p["description"], goals_json, ing_json,
                p["domain"], p["target_area"], p["id"]
            ))
        else:
            cur.execute("""
                INSERT INTO products (
                    id, brand, name, slug, url, image_url, short_desc, match_score, rating,
                    review_count, category, description, badges, has_detail, fungal_acne_safe,
                    fragrance_free, alcohol_free, silicone_free, oil_free, paraben_free,
                    sulfate_free, pore_clogger_free, vegan, cruelty_free, comedogenic_max,
                    irritancy_max, ingredients_json, created_at, category_slug, brand_country,
                    skin_goals, price_tier, price_tier_num, price_range, size, routine_step,
                    domain, target_area
                ) VALUES (
                    ?, ?, ?, ?, ?, '', ?, ?, ?,
                    ?, ?, ?, '[]', 1, ?,
                    ?, ?, ?, ?, 1,
                    ?, ?, ?, ?, 0,
                    0, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?
                )
            """, (
                p["id"], p["brand"], p["name"], p["slug"], f"https://skintellect.com/products/{p['slug']}",
                p["short_desc"], p["match_score"], p["rating"], p["review_count"], p["category"],
                p["description"], p["fungal_acne_safe"], p["fragrance_free"], p["alcohol_free"],
                p["silicone_free"], p["oil_free"], p["sulfate_free"], p["pore_clogger_free"],
                p["vegan"], p["cruelty_free"], ing_json, now_str, p["category_slug"],
                p["brand_country"], goals_json, p["price_tier"], p["price_tier_num"],
                p["price_range"], p["size"], p["routine_step"], p["domain"], p["target_area"]
            ))
            inserted_prods += 1

        # Link ingredients
        for order_idx, ing_info in enumerate(p["ingredients"]):
            ing_name = ing_info["name"].strip()
            cur.execute("SELECT id FROM ingredients WHERE LOWER(name) = LOWER(?)", (ing_name,))
            row = cur.fetchone()
            if row:
                i_id = row[0]
            else:
                # Insert ingredient
                slug = ing_name.lower().replace(" ", "-")
                domains_json = json.dumps([p["domain"]])
                sources_json = json.dumps(["skinsort", "incidecoder", "pubchem"])
                targets_json = json.dumps([p["target_area"]])
                cur.execute("""
                    INSERT INTO ingredients (
                        name, slug, function, description, comedogenic, irritancy,
                        is_pore_clogging, fungal_trigger, domains_json, sources_json, target_areas_json
                    ) VALUES (?, ?, ?, ?, 0, 0, 0, '', ?, ?, ?)
                """, (
                    ing_name, slug, ing_info.get("note", "Formulation active"),
                    f"Biochemical ingredient utilized in {p['brand']} {p['name']}.",
                    domains_json, sources_json, targets_json
                ))
                i_id = cur.lastrowid
                inserted_ings += 1

            # Link in product_ingredients
            cur.execute("DELETE FROM product_ingredients WHERE product_id = ? AND ingredient_id = ?", (p["id"], i_id))
            cur.execute("""
                INSERT INTO product_ingredients (
                    product_id, ingredient_id, ingredient_order, is_key_ingredient, key_note
                ) VALUES (?, ?, ?, ?, ?)
            """, (p["id"], i_id, order_idx + 1, 1 if ing_info.get("key") else 0, ing_info.get("note", "")))
            linked_ings += 1

    conn.commit()

    # Print summary counts
    print(f"\n[✓] Successfully processed {len(BENCHMARK_PRODUCTS)} Multi-Domain formulations:")
    for r in cur.execute("SELECT domain, COUNT(*) FROM products GROUP BY domain").fetchall():
        print(f"    • Domain '{r[0]}': {r[1]} products")

    conn.close()

def clean_database(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print(f"=== STARTING DATABASE CLEANING & CANONICALIZATION ({db_path}) ===")

    # 1. Inspect and fix null/empty categories
    c.execute("SELECT id, brand, name, category_slug FROM products WHERE category IS NULL OR category = ''")
    null_cat_products = c.fetchall()
    print(f"Found {len(null_cat_products)} products with NULL or empty category.")

    c.execute("""
        UPDATE products 
        SET category = 'Moisturizers' 
        WHERE (category IS NULL OR category = '') 
          AND (category_slug = 'moisturizers' OR category_slug IS NULL)
    """)
    print(f"Updated {c.rowcount} products to 'Moisturizers'.")

    # 2. Canonicalize fragmented categories
    c.execute("UPDATE products SET category = 'Cleansers' WHERE category = 'Face Cleansers'")
    print(f"Merged {c.rowcount} 'Face Cleansers' into 'Cleansers'.")

    c.execute("""
        UPDATE products 
        SET category = 'Moisturizers' 
        WHERE category IN ('General Moisturizers', 'Day Moisturizers', 'Oils')
    """)
    print(f"Merged {c.rowcount} variants into 'Moisturizers'.")

    # 3. Standardize routine_step according to canonical category
    routine_step_map = {
        'Cleansers': 'Step 1: Cleanse (AM/PM)',
        'Toners': 'Step 2: Tone & Prep (AM/PM)',
        'Serums': 'Step 3: Target & Treat (AM/PM)',
        'Moisturizers': 'Step 4: Moisturize & Barrier (AM/PM)',
        'Sunscreens': 'Step 5: Protect & Defend (AM)'
    }
    for cat, step in routine_step_map.items():
        c.execute("UPDATE products SET routine_step = ? WHERE category = ?", (step, cat))

    # 4. Fix missing match_scores (default to 45 neutral score)
    c.execute("UPDATE products SET match_score = 45 WHERE match_score IS NULL")
    print(f"Updated {c.rowcount} NULL match_scores to default 45%.")

    # 5. Fix missing ratings (default to 0.0)
    c.execute("UPDATE products SET rating = 0.0 WHERE rating IS NULL")
    print(f"Updated {c.rowcount} NULL ratings to 0.0.")

    # 6. Fix missing review_counts (default to 0)
    c.execute("UPDATE products SET review_count = 0 WHERE review_count IS NULL")
    print(f"Updated {c.rowcount} NULL review_counts to 0.")

    conn.commit()

    print("\n=== POST-CLEANING CATEGORY COUNTS ===")
    c.execute("SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY count(*) DESC")
    for r in c.fetchall():
        print(f"  {r[0]}: {r[1]}")

    c.execute("SELECT COUNT(*) FROM products")
    print(f"Total Products in Catalog: {c.fetchone()[0]}")

    conn.close()

def run_audit(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print(f"=== 1. CATEGORIES BREAKDOWN ({db_path}) ===")
    for row in c.execute('SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY count(*) DESC'):
        print(f"  {row[0]}: {row[1]}")

    print("\n=== 2. FIELD COMPLETENESS ===")
    total = c.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    no_brand = c.execute("SELECT COUNT(*) FROM products WHERE brand IS NULL OR brand = ''").fetchone()[0]
    no_match = c.execute("SELECT COUNT(*) FROM products WHERE match_score IS NULL").fetchone()[0]
    no_rating = c.execute("SELECT COUNT(*) FROM products WHERE rating IS NULL").fetchone()[0]
    no_price = c.execute("SELECT COUNT(*) FROM products WHERE price_tier IS NULL OR price_tier = ''").fetchone()[0]
    no_country = c.execute("SELECT COUNT(*) FROM products WHERE brand_country IS NULL OR brand_country = ''").fetchone()[0]
    enriched = c.execute("SELECT COUNT(*) FROM products WHERE has_detail = 1").fetchone()[0]
    no_category = c.execute("SELECT COUNT(*) FROM products WHERE category IS NULL OR category = ''").fetchone()[0]

    print(f"Total products: {total}")
    print(f"Missing category: {no_category}")
    print(f"Missing brand: {no_brand}")
    print(f"Missing match_score: {no_match}")
    print(f"Missing rating: {no_rating}")
    print(f"Missing price_tier: {no_price}")
    print(f"Missing country: {no_country}")
    print(f"Deeply enriched: {enriched} (Unenriched: {total - enriched})")

    print("\n=== 3. CATEGORY CANONICALIZATION GAPS ===")
    c.execute("SELECT category, COUNT(*) FROM products GROUP BY category")
    cats = dict(c.fetchall())
    print("Categories present:", cats)

    print("\n=== 4. DUPLICATES ===")
    dupe_slugs = c.execute("SELECT slug, count(*) FROM products GROUP BY slug HAVING count(*) > 1").fetchall()
    print(f"Products sharing same slug name across brands: {len(dupe_slugs)}")

    print("\n=== 5. INGREDIENTS AUDIT ===")
    print("Total master ingredients:", c.execute("SELECT count(*) FROM ingredients").fetchone()[0])
    print("Ingredients with comedogenic rating:", c.execute("SELECT count(*) FROM ingredients WHERE comedogenic IS NOT NULL AND comedogenic > 0").fetchone()[0])
    print("Ingredients with benefits/functions:", c.execute("SELECT count(*) FROM ingredients WHERE function IS NOT NULL AND function != ''").fetchone()[0])
    print("Total product_ingredients links:", c.execute("SELECT count(*) FROM product_ingredients").fetchone()[0])

    print("\n=== 6. REVIEWS AUDIT ===")
    total_reviews = c.execute("SELECT count(*) FROM reviews").fetchone()[0]
    with_skin = c.execute("SELECT count(*) FROM reviews WHERE reviewer_skin_type IS NOT NULL AND reviewer_skin_type != ''").fetchone()[0]
    with_ver = c.execute("SELECT count(*) FROM reviews WHERE formulation_version IS NOT NULL AND formulation_version != ''").fetchone()[0]
    print(f"Total reviews: {total_reviews}")
    print(f"With reviewer skin type: {with_skin}")
    print(f"With formulation version: {with_ver}")

    conn.close()

from skintellect.database import database, formula_hash, migrate


def verify_formula(product_id, source, reviewer):
    migrate()
    with database(DB_PATH) as c:
        row = c.execute('SELECT p.ingredients_json,q.is_seed FROM products p JOIN record_quality q ON p.id=q.product_id WHERE p.id=?', (product_id,)).fetchone()
        if not row or row[1]:
            raise ValueError('Select an existing non-seed catalog product.')
        items = json.loads(row[0] or '[]')
        if not items:
            raise ValueError('Cannot verify an empty ingredient list.')
        c.execute("UPDATE record_quality SET formula_status='verified_complete',verified_hash=?,verified_at=?,verified_source=? WHERE product_id=?",
                  (formula_hash(items), datetime.now(timezone.utc).isoformat(),
                   source + ' | reviewed by ' + reviewer, product_id))
    print('Recorded human completeness verification for product', product_id)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Catalog maintenance commands.')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('audit', 'clean', 'seed'):
        commands.add_parser(name)
    verify = commands.add_parser('verify')
    verify.add_argument('product_id', type=int)
    verify.add_argument('--source', required=True)
    verify.add_argument('--reviewer', required=True)
    args = parser.parse_args()
    if args.command == 'verify':
        verify_formula(args.product_id, args.source, args.reviewer)
    elif args.command == 'seed':
        seed_multidomain()
    elif args.command == 'clean':
        clean_database()
    else:
        run_audit()


if __name__ == '__main__':
    main()
