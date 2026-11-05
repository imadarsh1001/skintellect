"""
Ingredient CSI Detective: Causal Contact Allergy & Breakout Investigator
========================================================================
Performs set-theoretic differential analysis and chemical clustering to
isolate the exact molecular culprits behind user breakouts and contact dermatitis.
"""

import os
import re
import sqlite3
from typing import Any, Dict, List, Optional, Set, Tuple

from skintellect.formulation.ingredient_facts import (
    FUNGAL_ACNE_TRIGGERS,
    IRRITANTS_ALLERGENS,
    KNOWN_PORE_CLOGGERS,
)
from skintellect.formulation.scoring import parse_ingredients_input

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
from skintellect.config import DB_PATH

# Chemical Culprit Classification Patterns
CHEMICAL_FAMILIES = {
    "Fatty Acid Esters & Comedogenic Lipids": [
        r'\bpalmitate\b', r'\bmyristate\b', r'\bstearate\b', r'\bisostearate\b',
        r'\boleate\b', r'\bcocos nucifera\b', r'\bcoconut\b', r'\bcocoa butter\b',
        r'\btheobroma cacao\b', r'\btriglyceride\b'
    ],
    "Fragrance Sensitizers & Essential Oils": [
        r'\bfragrance\b', r'\bparfum\b', r'\blimonene\b', r'\blinalool\b',
        r'\bcitronellol\b', r'\bgeraniol\b', r'\beugenol\b', r'\bcitral\b',
        r'\blavandula\b', r'\blavender\b', r'\bcitrus\b', r'\beucalyptus\b',
        r'\bmentha\b', r'\bpeppermint\b'
    ],
    "Preservatives & Biocides": [
        r'\bphenoxyethanol\b', r'\bbenzyl alcohol\b', r'\bchlorphenesin\b',
        r'\bmethylparaben\b', r'\bpropylparaben\b', r'\bethylhexylglycerin\b',
        r'\bbenzoate\b', r'\bpotassium sorbate\b', r'\bdehydroacetic acid\b'
    ],
    "Fatty Alcohols & Heavy Emulsifiers": [
        r'\bcetearyl alcohol\b', r'\bcetyl alcohol\b', r'\bstearyl alcohol\b',
        r'\bceteareth\b', r'\bpolysorbate\b', r'\bpeg-100 stearate\b'
    ],
    "Ferments & Yeasts (Malassezia Stimulants)": [
        r'\bgalactomyces\b', r'\bbifida\b', r'\blactobacillus\b', r'\bsaccharomyces\b',
        r'\bferment\b'
    ],
    "Volatile Drying Alcohols": [
        r'\balcohol denat\b', r'\bsd alcohol\b', r'\bisopropyl alcohol\b', r'\bethanol\b'
    ]
}


class CSIDetective:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_PATH
        self.name = "Inspector INCI"
        self.role = "Forensic Formulation Detective"
        self.badge = "🔍 Ingredient CSI"

    def _resolve_deck(self, item: Any) -> Tuple[str, List[str]]:
        """
        Resolves an item (product ID, product name, or raw ingredient string) into (label, ingredient_list).
        """
        # 1. If integer or digit string -> fetch from DB
        if isinstance(item, int) or (isinstance(item, str) and item.isdigit()):
            pid = int(item)
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            p = c.execute("SELECT brand, name, ingredients_json FROM products WHERE id = ?", (pid,)).fetchone()
            conn.close()
            if p:
                label = f"{p['brand']} {p['name']}"
                ings = parse_ingredients_input(p['ingredients_json'])
                return label, ings

        # 2. If dictionary
        if isinstance(item, dict):
            label = item.get("name") or item.get("title") or "Submitted Product"
            raw = item.get("ingredients") or item.get("ingredients_text") or []
            return label, parse_ingredients_input(raw)

        # 3. If raw string
        text = str(item).strip()
        # Check if it matches a product name in DB
        if len(text) < 80 and not any(sep in text for sep in [",", "\n", ";"]):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            p = c.execute("SELECT id, brand, name, ingredients_json FROM products WHERE name LIKE ? OR brand || ' ' || name LIKE ? LIMIT 1",
                          (f"%{text}%", f"%{text}%")).fetchone()
            conn.close()
            if p:
                label = f"{p['brand']} {p['name']}"
                ings = parse_ingredients_input(p['ingredients_json'])
                return label, ings

        # Fallback to parsing as raw text deck
        label = "Custom Ingredient Deck"
        ings = parse_ingredients_input(text)
        return label, ings

    def investigate(
        self,
        problematic_items: List[Any],
        safe_items: List[Any],
        reaction_type: str = "breakouts_acne"
    ) -> Dict[str, Any]:
        """
        Performs set differential and chemical classification to find suspect culprits.
        """
        prob_decks = []
        for it in problematic_items:
            lbl, ings = self._resolve_deck(it)
            if ings:
                prob_decks.append({"label": lbl, "ingredients": [i.lower() for i in ings]})

        safe_decks = []
        for it in safe_items:
            lbl, ings = self._resolve_deck(it)
            if ings:
                safe_decks.append({"label": lbl, "ingredients": [i.lower() for i in ings]})

        if not prob_decks:
            return {
                "error": "No valid problematic products provided. Please input at least one product that caused issues."
            }

        # Safe universe
        safe_universe: Set[str] = set()
        for sd in safe_decks:
            safe_universe.update(sd["ingredients"])

        # Problem frequency
        prob_freq: Dict[str, int] = {}
        for pd in prob_decks:
            for ing in set(pd["ingredients"]):
                prob_freq[ing] = prob_freq.get(ing, 0) + 1

        total_prob_count = len(prob_decks)

        # Candidates = In problematic decks AND NOT in safe decks
        suspects = []
        for ing, count in prob_freq.items():
            if ing not in safe_universe:
                # Classify chemical family
                matched_family = "Other Cosmetic Excipient / Active"
                for family_name, patterns in CHEMICAL_FAMILIES.items():
                    if any(re.search(pat, ing) for pat in patterns):
                        matched_family = family_name
                        break

                # Comedogenic / Irritancy flags
                is_pore_clogger = any(re.search(pat, ing) for pat in KNOWN_PORE_CLOGGERS)
                is_irritant = any(re.search(pat, ing) for pat in IRRITANTS_ALLERGENS)
                is_fungal = any(re.search(pat, ing) for pat in FUNGAL_ACNE_TRIGGERS)

                # Calculate Suspect Score (0 - 100)
                freq_ratio = count / total_prob_count
                score = round(freq_ratio * 40)  # Up to 40 for 100% presence in failure products
                if safe_decks:
                    score += 25  # Proven absence in safe products
                if is_pore_clogger:
                    score += 20
                if is_irritant:
                    score += 15
                if is_fungal:
                    score += 15
                score = min(score, 99)

                suspects.append({
                    "ingredient": ing.title(),
                    "frequency": f"{count}/{total_prob_count} problematic formulas",
                    "recurrence_rate": round(freq_ratio * 100),
                    "suspect_score": score,
                    "chemical_family": matched_family,
                    "is_pore_clogger": is_pore_clogger,
                    "is_irritant": is_irritant,
                    "is_fungal_trigger": is_fungal
                })

        # Sort suspects by score descending
        suspects.sort(key=lambda x: (x["suspect_score"], x["recurrence_rate"]), reverse=True)

        # Generate Clinical Action Recommendations
        recommended_exclusions = []
        top_suspects = suspects[:5]
        for s in top_suspects:
            if s["is_pore_clogger"]:
                recommended_exclusions.append("pore_clogger_free")
            if s["is_fungal_trigger"]:
                recommended_exclusions.append("fungal_acne_safe")
            if s["is_irritant"] or "Fragrance" in s["chemical_family"]:
                recommended_exclusions.append("fragrance_free")
            if "Drying Alcohols" in s["chemical_family"]:
                recommended_exclusions.append("alcohol_free")
        recommended_exclusions = list(set(recommended_exclusions))

        # Forensic Narrative
        summary_lines = [
            f"**CSI Forensic Investigation Complete**",
            f"Analyzed `{len(prob_decks)}` failure formulations against `{len(safe_decks)}` benchmark safe formulations.",
            f"Extracted `{len(safe_universe)}` confirmed safe molecular controls.",
        ]
        if suspects:
            prime = suspects[0]
            summary_lines.append(
                f"🎯 **Prime Suspect:** **{prime['ingredient']}** (Likelihood: `{prime['suspect_score']}%`). "
                f"Belongs to *{prime['chemical_family']}*. Present in {prime['frequency']} and absent from all safe products."
            )
        else:
            summary_lines.append(
                "ℹ️ No strict differential suspects found. All ingredients in the failure products were also found in your safe products. The issue may be dosage/concentration or active pairing rather than a single toxic molecule."
            )

        # Forensic Thinking Scratchpad
        thinking = [
            f"Phase 1 (Deck Standardization): Ingested {len(prob_decks)} problematic formulation(s) and {len(safe_decks)} safe benchmark formulation(s).",
            f"Phase 2 (Safe Universe Mapping): Isolated {len(safe_universe)} proven safe control molecules that this skin type tolerates without adverse reactions.",
            f"Phase 3 (Set-Theoretic Subtraction): Executed differential (Union(Problematic) \\ Safe_Universe). Identified {len(suspects)} unique molecular candidates absent from safe products.",
            f"Phase 4 (Chemical Family Clustering): Grouped suspects into PubChem structural classes (Fatty Acid Esters, Fragrance Sensitizers, Biocides, Heavy Emulsifiers).",
            f"Phase 5 (Causal Scoring): Weighted frequency across failures + CIR comedogenic/irritant assay penalties -> Ranked {min(15, len(suspects))} prime suspects."
        ]

        return {
            "detective": self.name,
            "badge": self.badge,
            "total_problem_products": len(prob_decks),
            "total_safe_products": len(safe_decks),
            "problem_product_names": [p["label"] for p in prob_decks],
            "safe_product_names": [s["label"] for s in safe_decks],
            "safe_molecules_count": len(safe_universe),
            "suspects_count": len(suspects),
            "top_suspects": suspects[:15],
            "recommended_exclusions": recommended_exclusions,
            "thinking": thinking,
            "forensic_summary": "\n\n".join(summary_lines)
        }
