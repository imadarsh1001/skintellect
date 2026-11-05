from pathlib import Path

from skintellect.catalog.store import get_catalog
from skintellect.database import database
from skintellect.formulation.ingredient_facts import classify_ingredients

"""
Skintellect Formula Lab Analysis Service
======================================
Provides in-depth formulation analysis, active classification,
skin type compatibility matrices, target concern efficacy scoring,
and comprehensive mathematical audit logs for raw ingredient decks.
"""

import json
import re
from typing import Any, Dict, List, Optional

from skintellect.catalog.personas import get_all_personas
from skintellect.formulation.scoring import (
    analyze_ingredients,
    calculate_darmeto_points,
    parse_ingredients_input,
    predict_skintellect_match,
)

_INGREDIENTS_DB: Optional[Dict[str, Dict[str, Any]]] = None
_INGREDIENTS_STAMP = None


def _get_ingredients_db() -> Dict[str, Dict[str, Any]]:
    """Loads and caches SQLite ingredients table for O(1) dictionary lookups."""
    global _INGREDIENTS_DB, _INGREDIENTS_STAMP
    stamp = get_catalog().stamp
    if _INGREDIENTS_DB is not None and stamp == _INGREDIENTS_STAMP:
        return _INGREDIENTS_DB

    db = {}
    if Path(get_catalog().path).exists():
        try:
            with database(get_catalog().path) as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT name, function, comedogenic, irritancy, is_pore_clogging, 
                           fungal_trigger, benefits_json, description 
                    FROM ingredients
                """)
                for row in c.fetchall():
                    name, function, comedogenic, irritancy, is_pore_clogging, fungal_trigger, benefits_json, description = row
                    key = name.strip().lower()
                    benefits = []
                    if benefits_json:
                        try:
                            benefits = json.loads(benefits_json)
                        except Exception:
                            pass

                    db[key] = {
                        "name": name.strip(),
                        "function": function.strip() if function else "",
                        "comedogenic": int(comedogenic) if comedogenic is not None else None,
                        "irritancy": int(irritancy) if irritancy is not None else None,
                        "is_pore_clogging": bool(is_pore_clogging),
                        "fungal_trigger": fungal_trigger.strip() if fungal_trigger else "",
                        "benefits": benefits,
                        "description": description.strip() if description else ""
                    }
        except Exception as e:
            print(f"Warning: Failed to load ingredients DB cache: {e}")

    _INGREDIENTS_DB = db
    _INGREDIENTS_STAMP = stamp
    return _INGREDIENTS_DB


def classify_single_ingredient(name: str) -> Dict[str, Any]:
    """Inspects a single ingredient against the DB and regex active dictionaries."""
    db = _get_ingredients_db()
    n_lower = name.strip().lower()

    # Exact identity and approved aliases only. Substring matches can misidentify ingredients.
    from skintellect.formulation.ingredient_facts import normalize
    db_match = db.get(n_lower)
    if not db_match:
        db_match = next((v for k, v in db.items() if normalize(k) == normalize(name)), None)

    comedogenic = db_match.get("comedogenic") if db_match else None
    irritancy = db_match.get("irritancy") if db_match else None
    is_pore_clogging = db_match.get("is_pore_clogging", False) if db_match else False
    fungal_trigger_note = db_match.get("fungal_trigger", "") if db_match else ""
    benefits = db_match.get("benefits", []) if db_match else []
    function_desc = db_match.get("function", "") if db_match else ""
    description = db_match.get("description", "") if db_match else ""

    facts = classify_ingredients([name]).groups
    is_brightener = bool(facts['brighteners'])
    is_barrier = bool(facts['barrier'])
    is_smoother = bool(facts['smoothers'])
    is_fa_trigger = bool(fungal_trigger_note) or bool(facts['fungal_triggers'])
    is_clogger = is_pore_clogging or (comedogenic is not None and comedogenic >= 3) or bool(facts['cloggers'])
    is_irritant = (irritancy is not None and irritancy >= 2) or bool(facts['irritants'])

    # Determine primary category badge
    if is_fa_trigger and is_clogger:
        badge = "⚠️ Fungal Trigger & Pore Clogger"
        safety_status = "trigger"
    elif is_fa_trigger:
        badge = "⚠️ Malassezia (Fungal) Trigger"
        safety_status = "trigger"
    elif is_clogger:
        badge = "⚠️ Comedogenic Pore Clogger"
        safety_status = "caution"
    elif is_irritant:
        badge = "⚠️ Sensitizer / Fragrance"
        safety_status = "caution"
    elif is_brightener:
        badge = "🌟 Brightener & Glow Active"
        safety_status = "beneficial"
    elif is_barrier:
        badge = "🛡️ Barrier Lipid & Hydrator"
        safety_status = "beneficial"
    elif is_smoother:
        badge = "🌿 Soothing & Texture Refiner"
        safety_status = "beneficial"
    elif "preservative" in function_desc.lower() or re.search(r'\b(phenoxyethanol|ethylhexylglycerin|paraben|benzoate)\b', n_lower):
        badge = "🧪 Preservative / Stabilizer"
        safety_status = "safe"
    elif "solvent" in function_desc.lower() or n_lower in ["water", "aqua", "glycerin", "butylene glycol", "propanediol", "dipropylene glycol"]:
        badge = "💧 Solvent & Vehicle"
        safety_status = "safe"
    elif "emollient" in function_desc.lower() or "silicone" in function_desc.lower() or "dimethicone" in n_lower:
        badge = "🧴 Emollient & Vehicle"
        safety_status = "safe"
    else:
        badge = "🔹 Formulation Base"
        safety_status = "safe"

    is_active = is_brightener or is_barrier or is_smoother

    if not db_match and not (is_fa_trigger or is_clogger or is_irritant):
        safety_status = "unknown"
        badge = "Unresolved ingredient"
    elif safety_status == "safe":
        safety_status = "unflagged"

    return {
        "name": name.strip(),
        "function": function_desc or ("Rule-matched active" if is_active else "Unknown"),
        "comedogenic": comedogenic,
        "irritancy": irritancy,
        "is_pore_clogging": is_clogger,
        "is_fungal_trigger": is_fa_trigger,
        "fungal_trigger_note": fungal_trigger_note or ("Malassezia food source (fatty acid/ester)" if is_fa_trigger else ""),
        "is_active": is_active,
        "category_badge": badge,
        "safety_status": safety_status,
        "benefits": benefits,
        "description": description
    }


def compute_skin_type_compatibilities(
    analysis: Dict[str, Any],
    ing_names: List[str],
    is_fungal_safe: bool,
    is_fragrance_free: bool,
    is_alcohol_free: bool
) -> Dict[str, Dict[str, Any]]:
    """Calculates compatibility scores and clinical rationale for 5 major skin types."""
    clogger_count = len(analysis["cloggers"])
    irritant_count = len(analysis["irritants"])
    barrier_count = len(analysis["barrier"])
    bright_count = len(analysis["brighteners"])
    smooth_count = len(analysis["smoothers"])
    has_oil = any("oil" in n.lower() for n in ing_names)

    # 1. Combination Skin
    comb_score = 100
    if not is_fungal_safe:
        comb_score -= 20
    if clogger_count > 0:
        comb_score -= min(clogger_count * 10, 25)
    if not is_fragrance_free:
        comb_score -= 10
    if barrier_count > 0:
        comb_score += min(barrier_count * 2, 8)
    comb_score = max(30, min(100, comb_score))

    comb_status = "Optimal" if comb_score >= 88 else ("Good" if comb_score >= 70 else "Caution")
    comb_reason = (
        "Balances hydration without heavy pore-clogging occlusives." if comb_score >= 88 else
        ("Contains potential comedogenic agents or triggers that may congest oily T-zone." if clogger_count > 0 else
         "Decent balance, but verify barrier hydration for dry cheek zones.")
    )

    # 2. Oily / Acne-Prone Skin
    oily_score = 100
    if clogger_count > 0:
        oily_score -= min(clogger_count * 15, 40)
    if has_oil:
        oily_score -= 15
    if not is_fungal_safe:
        oily_score -= 25
    if smooth_count > 0 or bright_count > 0:
        oily_score += 5
    oily_score = max(25, min(100, oily_score))

    oily_status = "Optimal" if oily_score >= 85 else ("Good" if oily_score >= 68 else "Not Recommended" if oily_score < 50 else "Caution")
    oily_reason = (
        "Lightweight, non-comedogenic vehicle ideal for high-sebum skin." if oily_score >= 85 else
        (f"Contains {clogger_count} pore-clogging lipids/esters that can trigger comedones." if clogger_count > 0 else
         "Oil-based vehicle may feel heavy on oily skin.")
    )

    # 3. Dry Skin
    dry_score = 75
    if barrier_count >= 3:
        dry_score += 20
    elif barrier_count >= 1:
        dry_score += 10
    else:
        dry_score -= 20
    if not is_alcohol_free:
        dry_score -= 20
    if has_oil or any("butter" in n.lower() or "squalane" in n.lower() or "ceramide" in n.lower() for n in ing_names):
        dry_score += 5
    dry_score = max(30, min(100, dry_score))

    dry_status = "Optimal" if dry_score >= 85 else ("Good" if dry_score >= 70 else "Needs Extra Moisture")
    dry_reason = (
        f"Rich in {barrier_count} biomimetic barrier lipids and humectants for deep stratum corneum replenishment." if dry_score >= 85 else
        ("Lacks sufficient emollients or ceramides; pair with a rich occlusive moisturizer." if barrier_count == 0 else
         "Provides hydration but could use richer emollient support for flakiness.")
    )

    # 4. Sensitive / Reactive Skin
    sens_score = 100
    if not is_fragrance_free:
        sens_score -= 30
    if not is_alcohol_free:
        sens_score -= 25
    if irritant_count > 0:
        sens_score -= min(irritant_count * 15, 30)
    if smooth_count > 0 or barrier_count >= 2:
        sens_score += 5
    sens_score = max(20, min(100, sens_score))

    sens_status = "Optimal" if sens_score >= 88 else ("Good" if sens_score >= 70 else "High Risk of Irritation")
    sens_reason = (
        "Hypoallergenic profile free from artificial perfumes, simple alcohols, and known allergens." if sens_score >= 88 else
        ("Contains potential sensitizers, synthetic fragrance, or drying alcohol." if (not is_fragrance_free or not is_alcohol_free) else
         "Mild formula; test patch if reactive to botanical extracts.")
    )

    # 5. Fungal Acne Prone (Malassezia)
    fa_score = 100 if is_fungal_safe else 35
    fa_status = "100% Malassezia Safe" if is_fungal_safe else "Unsafe (Triggers Present)"
    fa_reason = (
        "Free from fatty acids C11-C24, polysorbates, and lipid esters that nourish Malassezia yeast." if is_fungal_safe else
        f"Contains {len(analysis['fungal_triggers'])} triggers: {', '.join(analysis['fungal_triggers'][:3])}."
    )

    return {
        "combination": {"score": comb_score, "status": comb_status, "verdict": f"{comb_score}% Fit", "reason": comb_reason},
        "oily": {"score": oily_score, "status": oily_status, "verdict": f"{oily_score}% Fit", "reason": oily_reason},
        "dry": {"score": dry_score, "status": dry_status, "verdict": f"{dry_score}% Fit", "reason": dry_reason},
        "sensitive": {"score": sens_score, "status": sens_status, "verdict": f"{sens_score}% Fit", "reason": sens_reason},
        "fungal_safe": {"score": fa_score, "status": fa_status, "verdict": "Verified Safe" if is_fungal_safe else "Avoid", "reason": fa_reason}
    }


def compute_target_concern_efficacies(analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Evaluates formulation efficacy against major dermatological skin concerns."""
    brighteners = analysis.get("brighteners", [])
    barrier = analysis.get("barrier", [])
    smoothers = analysis.get("smoothers", [])
    cloggers = analysis.get("cloggers", [])

    # 1. Dark Spots & Hyperpigmentation
    if len(brighteners) >= 2:
        ds_status = "High Efficacy"
        ds_score = 94
        ds_mech = f"Multi-pathway tyrosinase inhibition & melanosome transfer blockade via {', '.join(brighteners[:3])}."
    elif len(brighteners) == 1:
        ds_status = "Targeted Support"
        ds_score = 80
        ds_mech = f"Focused brightening action powered by {brighteners[0]}."
    else:
        ds_status = "Lacks Actives"
        ds_score = 35
        ds_mech = "Formula lacks active tyrosinase inhibitors or melanin regulators."

    # 2. Skin Barrier & Moisture Retention
    if len(barrier) >= 3:
        bar_status = "Exceptional Barrier Matrix"
        bar_score = 98
        bar_mech = f"Multi-depth lipid restoration (NMF + Ceramides/Hyaluronics): {', '.join(barrier[:4])}."
    elif len(barrier) >= 1:
        bar_status = "Good Hydration"
        bar_score = 78
        bar_mech = f"Hygroscopic moisture-binding delivered by {', '.join(barrier)}."
    else:
        bar_status = "Minimal Hydration"
        bar_score = 30
        bar_mech = "Lacks physiological barrier lipids and natural moisturizing factors."

    # 3. Texture, Pores & Blemishes
    if len(cloggers) > 0:
        tex_status = "Pore Congestion Warning"
        tex_score = 45
        tex_mech = f"Contains {len(cloggers)} comedogenic agents ({', '.join(cloggers[:2])}) that may congest pores."
    elif len(smoothers) >= 2:
        tex_status = "High Smoothing Efficacy"
        tex_score = 92
        tex_mech = f"Gentle follicular desquamation and epidermal texture smoothing via {', '.join(smoothers)}."
    elif len(smoothers) == 1:
        tex_status = "Gentle Refining"
        tex_score = 75
        tex_mech = f"Mild texture refinement supported by {smoothers[0]}."
    else:
        tex_status = "Neutral"
        tex_score = 65
        tex_mech = "Non-congesting vehicle with neutral effect on pore surface."

    # 4. Redness & Soothing
    soothing_actives = [s for s in (smoothers + barrier) if any(k in s.lower() for k in ["centella", "allantoin", "panthenol", "licorice", "glycyrrhizate", "oat", "beta-glucan"])]
    if len(soothing_actives) >= 2:
        red_status = "Intensive Anti-Inflammatory"
        red_score = 95
        red_mech = f"Suppresses erythema and pro-inflammatory cytokines: {', '.join(soothing_actives)}."
    elif len(soothing_actives) == 1:
        red_status = "Mild Calming"
        red_score = 78
        red_mech = f"Soothes localized surface irritation via {soothing_actives[0]}."
    else:
        red_status = "Neutral"
        red_score = 60
        red_mech = "Neutral barrier profile without dedicated anti-redness phytocompounds."

    return {
        "dark_spots": {"status": ds_status, "score": ds_score, "actives": brighteners, "mechanism": ds_mech},
        "barrier": {"status": bar_status, "score": bar_score, "actives": barrier, "mechanism": bar_mech},
        "texture": {"status": tex_status, "score": tex_score, "actives": smoothers, "mechanism": tex_mech},
        "redness": {"status": red_status, "score": red_score, "actives": soothing_actives, "mechanism": red_mech}
    }


def generate_mathematical_audit_log(
    persona: Dict[str, Any],
    ing_names: List[str],
    analysis: Dict[str, Any],
    match_score: int,
    match_status: str,
    match_breakdown: List[Dict[str, Any]],
    darmeto_res: Dict[str, Any],
    is_fungal_safe: bool,
    is_fragrance_free: bool,
    is_alcohol_free: bool
) -> List[str]:
    """Generates an exhaustive, step-by-step mathematical trace of both algorithms."""
    logs = []
    username = persona.get("username", "uap")
    label = persona.get("label", "Default Persona")
    skin_type = persona.get("skin_type", "combination")
    concerns = persona.get("target_concerns", ["dark_spots", "dryness", "texture"])
    excl = persona.get("safety_exclusions", {})

    logs.append(f"═════════════════════════════════════════════════════════════════")
    logs.append(f"  🔬 SKINTELLECT & DARMETO MATHEMATICAL ENGINE AUDIT TRACE")
    logs.append(f"═════════════════════════════════════════════════════════════════")
    logs.append(f"[Active Persona] @{username} — {label}")
    logs.append(f"[Skin Profile]   Type: {skin_type.upper()} | Concerns: {', '.join(concerns)}")
    logs.append(f"[Safety Mandate] Fungal Safe: {excl.get('fungal_acne_safe', True)} | Fragrance Free: {excl.get('fragrance_free', True)} | Alcohol Free: {excl.get('alcohol_free', True)}")
    logs.append(f"[Input Deck]     {len(ing_names)} ingredients parsed from formula string")
    logs.append("")

    # --- Phase 1: Skintellect Match Score Trace ---
    logs.append(f"─── [PHASE 1: SKINTELLECT MATCH SCORE ENGINE (0% - 100%)] ───")
    logs.append(f"  [Init] Starting Baseline Match Score = 100.0%")

    # Fungal Check
    fa_triggers = analysis.get("fungal_triggers", [])
    if excl.get("fungal_acne_safe", True) and len(fa_triggers) > 0:
        penalty = min(55 + len(fa_triggers) * 2, 66)
        logs.append(f"  ❌ Step 1.1: [FUNGAL CLIFF TRIGGERED] Found {len(fa_triggers)} Malassezia food triggers: {', '.join(fa_triggers)}")
        logs.append(f"       -> Direct penalty applied: -{penalty}% (Hard Ceiling Capped)")
    else:
        logs.append(f"  ✅ Step 1.1: [Malassezia Safety] PASS (0 triggers detected; 0% deduction)")

    # Fragrance Check
    if not is_fragrance_free and excl.get("fragrance_free", True):
        logs.append(f"  ⚠️ Step 1.2: [Sensitizers/Fragrance] WARN (-15% deduction: artificial fragrance or allergens found)")
    else:
        logs.append(f"  ✅ Step 1.2: [Fragrance Audit] PASS (Zero synthetic fragrance or EU-26 allergens; 0% deduction)")

    # Alcohol Check
    if not is_alcohol_free and excl.get("alcohol_free", True):
        logs.append(f"  ⚠️ Step 1.3: [Drying Alcohols] WARN (-10% deduction: Alcohol Denat or SD alcohol found)")
    else:
        logs.append(f"  ✅ Step 1.3: [Alcohol Audit] PASS (Zero simple drying alcohols; 0% deduction)")

    # Comedogenicity for skin type
    cloggers = analysis.get("cloggers", [])
    if len(cloggers) > 0:
        logs.append(f"  ⚠️ Step 1.4: [Comedogenicity Audit] WARN (-5% deduction: {len(cloggers)} cloggers for combination skin: {', '.join(cloggers)})")
    else:
        logs.append(f"  ✅ Step 1.4: [Comedogenicity Audit] PASS (Zero high-comedogenic pore cloggers; 0% deduction)")

    # Concerns check
    bright_count = len(analysis.get("brighteners", []))
    barrier_count = len(analysis.get("barrier", []))
    if "dark_spots" in concerns:
        if bright_count > 0:
            logs.append(f"  ✅ Step 1.5a: [Dark Spots Concern] PASS ({bright_count} active brighteners present; 0% deduction)")
        else:
            logs.append(f"  ⚠️ Step 1.5a: [Dark Spots Concern] WARN (-4% deduction: lacks tyrosinase inhibitors)")

    if "dryness" in concerns:
        if barrier_count > 0:
            logs.append(f"  ✅ Step 1.5b: [Barrier & Dryness Concern] PASS ({barrier_count} barrier hydrators present; 0% deduction)")
        else:
            logs.append(f"  ⚠️ Step 1.5b: [Barrier & Dryness Concern] WARN (-4% deduction: lacks intercellular barrier lipids)")

    logs.append(f"  🎯 PHASE 1 RESULT: {match_score}% Match Score ({match_status})")
    logs.append("")

    # --- Phase 2: Darmeto Clinical Points Trace ---
    logs.append(f"─── [PHASE 2: CLINICAL DARMETO FIT SCORE (0 - 130+ PTS)] ───")
    logs.append(f"  [Base] Seed from Phase 1 Match Score = {match_score}.0 pts")

    # Additions
    additions = darmeto_res.get("additions", [])
    if additions:
        for add in additions:
            logs.append(f"  ➕ {add}")
    else:
        logs.append(f"  ℹ️ No active clinical additions qualified")

    # Deductions
    deductions = darmeto_res.get("deductions", [])
    if deductions:
        for ded in deductions:
            logs.append(f"  ➖ {ded}")
    else:
        logs.append(f"  ✅ Zero clinical deductions (No sensitizers, no pore cloggers)")

    final_pts = darmeto_res.get("darmeto_points", match_score)
    tier = darmeto_res.get("tier", "Safe Everyday Base")
    logs.append(f"  🏆 PHASE 2 RESULT: {final_pts} Darmeto Clinical Points")
    logs.append(f"  🏷️ Classification: {tier}")
    logs.append(f"═════════════════════════════════════════════════════════════════")

    return logs


def analyze_formula_full(ingredients_text: str, persona_id: str = "uap") -> Dict[str, Any]:
    """Master orchestrator for the Formula Lab."""
    ing_names = parse_ingredients_input(ingredients_text)
    analysis = analyze_ingredients(ing_names)

    personas = get_all_personas()
    persona = next((x for x in personas if x["id"] == persona_id or x["username"] == persona_id), personas[0])
    excl = persona.get("safety_exclusions", {})

    # Predict Skintellect match
    match_res = predict_skintellect_match(
        ingredients=ing_names,
        skin_type=persona.get("skin_type", "combination"),
        concerns=persona.get("target_concerns", []),
        avoid_fungal_triggers=excl.get("fungal_acne_safe", True),
        avoid_fragrance=excl.get("fragrance_free", True),
        avoid_alcohol=excl.get("alcohol_free", True)
    )

    pred_score = match_res["predicted_match_score"]
    is_fungal_safe = len(analysis["fungal_triggers"]) == 0
    is_clogger_free = len(analysis["cloggers"]) == 0
    is_oil_free = not any("oil" in i.lower() for i in ing_names)
    is_fragrance_free = not any(re.search(r'\b(fragrance|parfum|linalool|limonene|geraniol)\b', i.lower()) for i in ing_names)
    is_alcohol_free = not any(re.search(r'\b(alcohol denat|sd alcohol)\b', i.lower()) for i in ing_names)

    # Calculate Darmeto points
    darmeto_res = calculate_darmeto_points(
        match_score=pred_score,
        analysis=analysis,
        fungal_acne_safe=is_fungal_safe,
        pore_clogger_free=is_clogger_free,
        oil_free=is_oil_free
    )

    # Parsed detailed breakdown
    parsed_details = [classify_single_ingredient(name) for name in ing_names]
    active_count = sum(1 for p in parsed_details if p["is_active"])
    total_ingredients = len(ing_names)
    active_ratio = round((active_count / max(1, total_ingredients)) * 100, 1)

    # Skin type compatibilities
    skin_compatibilities = compute_skin_type_compatibilities(
        analysis=analysis,
        ing_names=ing_names,
        is_fungal_safe=is_fungal_safe,
        is_fragrance_free=is_fragrance_free,
        is_alcohol_free=is_alcohol_free
    )

    # Target concern efficacies
    concern_efficacies = compute_target_concern_efficacies(analysis)
    for value in skin_compatibilities.values():
        value.update(status="Unverified heuristic", verdict="Individual compatibility is unknown",
                     reason="Computed from ingredient rules; concentration, pH and individual response are unavailable.")
    for value in concern_efficacies.values():
        value.update(status="Ingredient presence only",
                     mechanism="Recorded rule matches: " + (", ".join(value["actives"]) or "none") + ". Product efficacy is unverified.")

    # Mathematical engine audit log
    audit_log = generate_mathematical_audit_log(
        persona=persona,
        ing_names=ing_names,
        analysis=analysis,
        match_score=pred_score,
        match_status=match_res["status"],
        match_breakdown=match_res.get("breakdown", []),
        darmeto_res=darmeto_res,
        is_fungal_safe=is_fungal_safe,
        is_fragrance_free=is_fragrance_free,
        is_alcohol_free=is_alcohol_free
    )

    return {
        "predicted_match_score": pred_score,
        "darmeto_points": darmeto_res["darmeto_points"],
        "tier": "Heuristic score band",
        "status": "unknown" if any(p['safety_status'] == 'unknown' for p in parsed_details) else "heuristic_only",
        "summary": "Unvalidated ingredient-rule assessment. Absence of flags does not establish safety or efficacy.",
        "audit_log": ["Legacy rule arithmetic follows; PASS means no rule match, not verified safety."] + audit_log,
        "brighteners": analysis["brighteners"],
        "barrier": analysis["barrier"],
        "smoothers": analysis["smoothers"],
        "irritants": analysis["irritants"],
        "cloggers": analysis["cloggers"],
        "fungal_triggers": analysis["fungal_triggers"],
        "is_fungal_safe": False if not is_fungal_safe else None,
        "is_fragrance_free": False if not is_fragrance_free else None,
        "is_alcohol_free": False if not is_alcohol_free else None,
        "is_pore_clogger_free": False if not is_clogger_free else None,
        "is_oil_free": False if not is_oil_free else None,
        "total_ingredients": total_ingredients,
        "active_count": active_count,
        "active_ratio": active_ratio,
        "skin_compatibilities": skin_compatibilities,
        "concern_efficacies": concern_efficacies,
        "ingredients_breakdown": parsed_details,
        "persona_label": persona.get("label", "Default Persona")
    }
