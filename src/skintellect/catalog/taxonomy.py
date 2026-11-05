"""
Formulation Studio - Multi-Domain Taxonomy & Body Architecture
=============================================================
Canonical stage home: skintellect.catalog.taxonomy
Defines the primary body domains (Skin, Hair, Body, Makeup),
target anatomical areas, formulation categories, and clinical guardrails.
"""

from typing import Any, Dict, List

DOMAINS: Dict[str, Dict[str, Any]] = {
    "skin": {
        "id": "skin",
        "name": "Skin & Facial Dermatology",
        "icon": "🧴",
        "description": "Facial skincare, barrier repair, acne control, and UV protection.",
        "target_areas": [
            {"id": "face", "name": "Full Face", "icon": "😊"},
            {"id": "tzone", "name": "T-Zone (Forehead & Nose)", "icon": "🎯"},
            {"id": "cheeks", "name": "Cheeks & Jawline", "icon": "🌸"},
            {"id": "eye_area", "name": "Periorbital (Eye Area)", "icon": "👁️"},
            {"id": "neck", "name": "Neck & Décolleté", "icon": "🧣"}
        ],
        "categories": [
            "Cleansers", "Toners", "Serums", "Moisturizers", "Sunscreens", "Exfoliators", "Face Masks"
        ],
        "key_concerns": [
            "Barrier Repair", "Dark Spots & Melanin", "Acne & Blemishes", 
            "Anti-Aging & Fine Lines", "Hydration", "Redness & Rosacea", "Texture & Pores"
        ],
        "safety_guardrails": [
            {"id": "fungal_acne_safe", "label": "Malassezia / Fungal Safe", "desc": "Free from C11-C24 fatty acids & esters"},
            {"id": "fragrance_free", "label": "Fragrance Free", "desc": "0 synthetic perfumes or EU allergens"},
            {"id": "alcohol_free", "label": "Alcohol Free", "desc": "0 drying simple alcohols (Alcohol Denat)"},
            {"id": "pore_clogger_free", "label": "Non-Comedogenic", "desc": "0 high-comedogenic pore-clogging lipids"}
        ]
    },
    "hair": {
        "id": "hair",
        "name": "Hair & Scalp Care",
        "icon": "💇",
        "description": "Trichology, scalp microbiome balance, strand tensile strength, and follicle health.",
        "target_areas": [
            {"id": "scalp", "name": "Scalp & Follicles", "icon": "💆"},
            {"id": "hair_strands", "name": "Mid-Lengths & Strands", "icon": "✨"},
            {"id": "hair_ends", "name": "Split Ends & Tips", "icon": "✂️"}
        ],
        "categories": [
            "Shampoos", "Conditioners", "Scalp Serums", "Hair Masks", "Leave-In Conditioners", "Hair Oils", "Clarifying Treatments"
        ],
        "key_concerns": [
            "Scalp Barrier & Flakes (Dandruff)", "Hair Thinning & Density", 
            "Bond & Keratin Repair", "Frizz & Porosity Control", "Curl Definition (CGM)", "Color Protection"
        ],
        "safety_guardrails": [
            {"id": "sulfate_free", "label": "Sulfate Free (SLS/SLES)", "desc": "Non-stripping amphoteric/anionic surfactants"},
            {"id": "silicone_free", "label": "Silicone Free", "desc": "Curly Girl Method (CGM) approved without buildup"},
            {"id": "scalp_fungal_safe", "label": "Dandruff / Malassezia Safe", "desc": "Prevents feeding seborrheic dermatitis yeast"},
            {"id": "protein_balanced", "label": "Hydrolyzed Protein Balance", "desc": "Prevents protein overload and strand brittleness"}
        ]
    },
    "body": {
        "id": "body",
        "name": "Bath & Body Care",
        "icon": "🧼",
        "description": "Body dermatology, keratosis pilaris, body barrier xerosis, and bacne prevention.",
        "target_areas": [
            {"id": "full_body", "name": "Full Body Surface", "icon": "🧍"},
            {"id": "back_chest", "name": "Back & Chest (Bacne Zone)", "icon": "🛡️"},
            {"id": "arms_legs", "name": "Arms & Legs (KP Areas)", "icon": "🦵"},
            {"id": "hands_feet", "name": "Hands & Feet", "icon": "🧤"}
        ],
        "categories": [
            "Body Washes", "Body Lotions", "Body Scrubs", "Hand Creams", "Foot Creams", "Body Sunscreens", "Body Oils"
        ],
        "key_concerns": [
            "Keratosis Pilaris (Strawberry Skin)", "Body Acne (Bacne)", 
            "Extreme Dryness (Xerosis)", "Rough Calluses", "Body Firming & Stretch Marks"
        ],
        "safety_guardrails": [
            {"id": "body_non_comedogenic", "label": "Bacne-Safe", "desc": "Will not congest sebaceous follicles on back/chest"},
            {"id": "urea_lactic_balance", "label": "Keratolytic Balancing", "desc": "Gentle exfoliation via Urea/Lactic Acid"},
            {"id": "hypoallergenic", "label": "Hypoallergenic", "desc": "Safe for eczema-prone body areas"}
        ]
    },
    "makeup": {
        "id": "makeup",
        "name": "Makeup & Complexion",
        "icon": "💄",
        "description": "Non-comedogenic cosmetics, hybrid skincare-makeup, pigment formulation, and wear testing.",
        "target_areas": [
            {"id": "complexion", "name": "Complexion & Base", "icon": "🎨"},
            {"id": "lips", "name": "Lips", "icon": "💋"},
            {"id": "eyes", "name": "Eyelids & Brows", "icon": "👁️"}
        ],
        "categories": [
            "Foundations", "Concealers", "Primers", "Tinted Moisturizers", "Setting Powders", "Lip Balms & Tints", "Setting Sprays"
        ],
        "key_concerns": [
            "Non-Acnegenic Coverage", "Hydrating vs Mattifying Finish", 
            "SPF Protection in Makeup", "Long-Wear Transfer Resistance", "Minimal Pore Accentuation"
        ],
        "safety_guardrails": [
            {"id": "non_acnegenic", "label": "Non-Acnegenic", "desc": "0 formulation triggers for inflammatory comedones"},
            {"id": "safe_pigments", "label": "Heavy Metal Tested Pigments", "desc": "High purity mineral oxides & FD&C colorants"},
            {"id": "eye_dermatologist_tested", "label": "Ophthalmologist Safe", "desc": "Non-migrating binders safe for tear duct contact"}
        ]
    }
}

# Multi-Source Ingredient Registries
SOURCES: Dict[str, Dict[str, Any]] = {
    "skintellect": {
        "id": "skintellect",
        "name": "Skintellect Community & Lab",
        "coverage": "Formulation breakdown, fungal safety, user tolerance ratings",
        "type": "Primary Scraped / Re-engineered"
    },
    "incidecoder": {
        "id": "incidecoder",
        "name": "INCIDecoder",
        "coverage": "Dermatological explanations, biochemical mechanisms, scientific citations",
        "type": "Educational Reference"
    },
    "cosdna": {
        "id": "cosdna",
        "name": "CosDNA",
        "coverage": "Historical safety, acnegenicity (1-5), irritancy (1-5)",
        "type": "Toxicology Benchmark"
    },
    "cir": {
        "id": "cir",
        "name": "Cosmetic Ingredient Review (CIR)",
        "coverage": "Official toxicological panel safety evaluations and maximum usage %",
        "type": "Regulatory Standard"
    },
    "pubchem": {
        "id": "pubchem",
        "name": "NCBI PubChem",
        "coverage": "Molecular weights, CAS registry numbers, SMILES, IUPAC nomenclature",
        "type": "Biochemical Foundation"
    }
}


def get_all_domains() -> List[Dict[str, Any]]:
    return list(DOMAINS.values())


def get_all_sources() -> List[Dict[str, Any]]:
    return list(SOURCES.values())
