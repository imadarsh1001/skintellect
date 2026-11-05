from skintellect.formulation.ingredient_facts import classify_ingredients

"""
Skintellect Match & Dermatological Points Reverse-Engineered Scoring Engine
========================================================================
This module encapsulates the reverse-engineered formulas for both:
1. Skintellect Personalized Match Score (0% - 100%)
2. Dermatological Fit Score / "Darmeto Points" (0 - 130 pts)

Allows scoring ANY product or raw ingredient list offline, without needing
a paid Skintellect account or active browser cookies.
"""

import json
import re
import sys
from typing import Any, Dict, List, Optional

# Ensure UTF-8 stdout on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Malassezia (Fungal Acne) trigger dictionary

# Targeted Actives Dictionaries






def parse_ingredients_input(raw_input: Any) -> List[str]:
    """Normalizes raw input (string, comma list, or JSON dict) into clean ingredient names."""
    if isinstance(raw_input, list):
        clean = []
        for item in raw_input:
            if isinstance(item, dict):
                clean.append(item.get('name', '').strip())
            elif isinstance(item, str):
                clean.append(item.strip())
        return [c for c in clean if c]

    if isinstance(raw_input, str):
        # Could be JSON string or comma-separated string
        try:
            parsed = json.loads(raw_input)
            if isinstance(parsed, list):
                return parse_ingredients_input(parsed)
        except Exception:
            pass
        # Comma/newline split
        items = re.split(r'[,;\n]', raw_input)
        return [re.sub(r'^\d+[\.\)]\s*', '', it).strip() for it in items if it.strip()]

    return []


def analyze_ingredients(ing_names: List[str]) -> Dict[str, Any]:
    return classify_ingredients(ing_names).groups


def predict_skintellect_match(
    ingredients: Any,
    skin_type: str = "combination",
    concerns: Optional[List[str]] = None,
    avoid_fungal_triggers: bool = True,
    avoid_fragrance: bool = True,
    avoid_alcohol: bool = True
) -> Dict[str, Any]:
    """
    Reverse-engineers the Skintellect Personalized Match Score (0% to 100%).
    
    Formula Rules:
    1. Base: 100%
    2. Fungal Acne Trigger Cliff: If avoid_fungal_triggers=True and triggers exist,
       caps/slashes score directly into [34%, 45%].
    3. Sensitivity Penalties:
       - Fragrance / EU-Allergens: -15%
       - Drying Alcohol: -10%
    4. Pore Congestion & Oil (for combination skin):
       - High pore cloggers: -5%
       - Heavy oil/occlusives: -3%
    5. Concerns Alignment:
       - Fails to target dark spots/dullness: -4%
       - Fails to provide hydration: -4%
       - Contains ingredients that dry out skin: -8%
    """
    if concerns is None:
        concerns = ["dark_spots", "dryness", "dullness", "texture"]

    ing_names = parse_ingredients_input(ingredients)
    analysis = analyze_ingredients(ing_names)

    score = 100
    breakdown = []

    # 1. Fungal Acne Check (The Hard Cliff)
    if avoid_fungal_triggers and len(analysis['fungal_triggers']) > 0:
        penalty = min(55 + len(analysis['fungal_triggers']) * 2, 66)
        score = max(34, 100 - penalty)
        breakdown.append({
            "category": "Skin Condition / Hard Avoidance",
            "rule": "Contains Fungal Acne Triggers (Malassezia food)",
            "impact": f"-{penalty}% (Hard Ceiling)",
            "flagged_ingredients": analysis['fungal_triggers'][:3]
        })
        return {
            "predicted_match_score": score,
            "status": "Not a match" if score < 60 else "Fair match",
            "summary": "Contains fungal acne triggers which conflict with your skin condition profile.",
            "breakdown": breakdown,
            "analysis": analysis
        }

    # 2. Fragrance / Sensitizers Check
    has_frag = any(re.search(r'\b(fragrance|parfum|linalool|limonene|geraniol)\b', n.lower()) for n in ing_names)
    if avoid_fragrance and has_frag:
        score -= 15
        breakdown.append({
            "category": "Sensitivity Preference",
            "rule": "Artificial fragrance or EU fragrance allergens detected",
            "impact": "-15%",
            "flagged_ingredients": [n for n in ing_names if re.search(r'\b(fragrance|parfum|linalool|limonene|geraniol)\b', n.lower())]
        })

    # 3. Drying Alcohol Check
    has_alc = any(re.search(r'\b(alcohol denat|sd alcohol)\b', n.lower()) for n in ing_names)
    if avoid_alcohol and has_alc:
        score -= 10
        breakdown.append({
            "category": "Sensitivity Preference",
            "rule": "Drying simple alcohol detected",
            "impact": "-10%",
            "flagged_ingredients": [n for n in ing_names if re.search(r'\b(alcohol denat|sd alcohol)\b', n.lower())]
        })

    # 4. Pore Cloggers (Combination Skin)
    if len(analysis['cloggers']) > 0:
        score -= 5
        breakdown.append({
            "category": "Skin Type Compatibility",
            "rule": "High-comedogenic pore cloggers in formula",
            "impact": "-5%",
            "flagged_ingredients": analysis['cloggers'][:2]
        })

    # 5. Targeted Concerns
    if "dark_spots" in concerns and len(analysis['brighteners']) == 0:
        score -= 4
        breakdown.append({
            "category": "Targeted Concerns",
            "rule": "Lacks tyrosinase inhibitors for dark spots / dullness",
            "impact": "-4%",
            "flagged_ingredients": []
        })

    if "dryness" in concerns and len(analysis['barrier']) == 0:
        score -= 4
        breakdown.append({
            "category": "Targeted Concerns",
            "rule": "Lacks intercellular barrier lipids or hydrators",
            "impact": "-4%",
            "flagged_ingredients": []
        })

    # 6. Drying Ingredients (Conflicts with Dryness Concern)
    has_drying = any(re.search(r'\b(salicylic acid|bha)\b', n.lower()) for n in ing_names) and len(analysis['barrier']) <= 1
    if has_drying:
        score -= 6
        breakdown.append({
            "category": "Concern Conflict",
            "rule": "Exfoliating acid without sufficient barrier compensation",
            "impact": "-6%",
            "flagged_ingredients": ["Salicylic acid"]
        })

    score = max(20, min(100, score))
    status = "Excellent match" if score >= 95 else ("Great match" if score >= 85 else ("Good match" if score >= 75 else "Fair match"))

    return {
        "predicted_match_score": score,
        "status": status,
        "summary": "Formulation matches combination skin with active concern targeting." if not breakdown else f"Formulation meets {score}% of user requirements.",
        "breakdown": breakdown,
        "analysis": analysis
    }


def calculate_darmeto_points(
    match_score: int,
    analysis: Dict[str, Any],
    fungal_acne_safe: bool = True,
    pore_clogger_free: bool = True,
    oil_free: bool = True,
    rating: Optional[float] = None
) -> Dict[str, Any]:
    """
    Computes clinical 'Darmeto Points' (Dermatological Fit Score).
    
    Formula:
      Score = Baseline Match Score (0 - 100)
            + Brightener Bonus (min 3 * count, 9)
            + Barrier Bonus (min 2 * count, 8)
            + Texture/Smoothing Bonus (min 2 * count, 6)
            + Fungal Acne Safe Bonus (+4)
            + Pore Clogger Free Bonus (+3)
            + Oil-Free Bonus (+2)
            + Community Consensus Boost (+3 if rating >= 4.0)
            - Pore Clogger Penalty (4 * count)
            - Irritant Penalty (6 * count)
    """
    pts = float(match_score)
    additions = []
    deductions = []

    # 1. Brighteners Bonus
    bright_count = len(analysis.get('brighteners', []))
    bright_bonus = min(bright_count * 3, 9)
    if bright_bonus > 0:
        pts += bright_bonus
        additions.append(f"+{bright_bonus} pts: {bright_count} active brighteners targeting dark spots/dullness")

    # 2. Barrier & Hydration Bonus
    barrier_count = len(analysis.get('barrier', []))
    barrier_bonus = min(barrier_count * 2, 8)
    if barrier_bonus > 0:
        pts += barrier_bonus
        additions.append(f"+{barrier_bonus} pts: {barrier_count} biomimetic barrier lipids/hydrators")

    # 3. Texture & Smoothing Bonus
    smooth_count = len(analysis.get('smoothers', []))
    smooth_bonus = min(smooth_count * 2, 6)
    if smooth_bonus > 0:
        pts += smooth_bonus
        additions.append(f"+{smooth_bonus} pts: {smooth_count} gentle texture refining agents")

    # 4. Safety Formulation Bonuses
    if fungal_acne_safe:
        pts += 4
        additions.append("+4 pts: 100% Malassezia / Fungal Acne Safe")

    if pore_clogger_free:
        pts += 3
        additions.append("+3 pts: 100% Non-comedogenic (0 high pore cloggers)")

    if oil_free:
        pts += 2
        additions.append("+2 pts: Oil-Free vehicle (optimal for combination T-zone)")

    # 5. Community Rating Boost
    if rating and rating >= 4.0:
        pts += 3
        additions.append(f"+3 pts: High community consensus (⭐ {rating}/5.0)")

    # 6. Deductions
    clogger_count = len(analysis.get('cloggers', []))
    if clogger_count > 0:
        clogger_ded = clogger_count * 4
        pts -= clogger_ded
        deductions.append(f"-{clogger_ded} pts: {clogger_count} potential pore-clogging ingredients")

    irritant_count = len(analysis.get('irritants', []))
    if irritant_count > 0:
        irritant_ded = irritant_count * 6
        pts -= irritant_ded
        deductions.append(f"-{irritant_ded} pts: {irritant_count} sensitizing fragrance/essential oils")

    final_score = round(max(0, pts), 1)

    tier = (
        "🏆 Tier 1: Holy Grail Formulation (120+ pts)" if final_score >= 120 else
        ("🌟 Tier 2: Highly Targeted Treatment (105 - 119 pts)" if final_score >= 105 else
        ("✅ Tier 3: Safe Everyday Base (90 - 104 pts)" if final_score >= 90 else
        "⚠️ Tier 4: Suboptimal / Potential Irritants (< 90 pts)"))
    )

    return {
        "darmeto_points": final_score,
        "tier": tier,
        "baseline_match": match_score,
        "additions": additions,
        "deductions": deductions
    }


def score_any_product(
    ingredients: Any,
    skin_type: str = "combination",
    rating: Optional[float] = None
) -> Dict[str, Any]:
    """Unified master function that evaluates any product and returns both scores and full analysis."""
    match_result = predict_skintellect_match(ingredients, skin_type=skin_type)
    analysis = match_result['analysis']

    is_fa_safe = len(analysis['fungal_triggers']) == 0
    is_clogger_free = len(analysis['cloggers']) == 0
    is_oil_free = not any('oil' in n.lower() for n in parse_ingredients_input(ingredients))

    darmeto_result = calculate_darmeto_points(
        match_score=match_result['predicted_match_score'],
        analysis=analysis,
        fungal_acne_safe=is_fa_safe,
        pore_clogger_free=is_clogger_free,
        oil_free=is_oil_free,
        rating=rating
    )

    return {
        "skintellect_match": match_result,
        "darmeto_points": darmeto_result,
        "actives_summary": {
            "brighteners": analysis['brighteners'],
            "barrier_lipids": analysis['barrier'],
            "smoothers": analysis['smoothers'],
            "pore_cloggers": analysis['cloggers'],
            "fungal_triggers": analysis['fungal_triggers']
        }
    }


if __name__ == "__main__":
    sample_formula = [
        "Water", "Niacinamide", "Glycerin", "Panthenol", "Ceramide NP",
        "Centella Asiatica Extract", "Sodium Hyaluronate", "Allantoin", "1,2-Hexanediol"
    ]
    res = score_any_product(sample_formula, rating=4.5)
    print("\n" + "=" * 55)
    print(" SAMPLE TEST FORMULATION EVALUATION")
    print("=" * 55)
    print(f" Predicted Skintellect Match : {res['skinsort_match']['predicted_match_score']}% ({res['skinsort_match']['status']})")
    print(f" Darmeto Fit Points       : {res['darmeto_points']['darmeto_points']} pts ({res['darmeto_points']['tier']})")
    print("\n Actives Breakdown:")
    print("   Brighteners  :", res['actives_summary']['brighteners'])
    print("   Barrier/Hydra:", res['actives_summary']['barrier_lipids'])
    print("   Fungal Safe? :", "YES" if not res['actives_summary']['fungal_triggers'] else "NO")
    print("=" * 55 + "\n")


# Backward-compatibility alias
predict_skinsort_match = predict_skintellect_match
