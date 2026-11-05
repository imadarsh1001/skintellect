"""
Deterministic Scoring Judge Agent
=================================
Role: Serves as the ultimate authority, grounding multi-agent deliberation in the
mathematically verified scoring engine from skintellect.formulation.scoring.
Includes explicit step-by-step judicial thinking and mathematical audit trace.
"""

from typing import Any, Dict

from skintellect.formulation.scoring import (
    analyze_ingredients,
    calculate_darmeto_points,
    parse_ingredients_input,
    predict_skintellect_match,
)


class DeterministicJudgeAgent:
    def __init__(self):
        self.name = "Chief Justice Darmeto"
        self.role = "Deterministic Scoring Engine"
        self.badge = "⚖️ Mathematical Judge"
        self.avatar_color = "indigo"

    def adjudicate(
        self,
        ingredients_input: Any,
        persona: Dict[str, Any],
        formulator_report: Dict[str, Any],
        critic_report: Dict[str, Any],
        microbiome_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes the reverse-engineered scoring formulas and outputs the binding verdict.
        """
        parsed_ings = parse_ingredients_input(ingredients_input)
        analysis = analyze_ingredients(parsed_ings)

        # Extract persona exclusions & preferences
        exclusions = persona.get("safety_exclusions", {})
        avoid_fa = exclusions.get("fungal_acne_safe", True)
        avoid_frag = exclusions.get("fragrance_free", True)
        avoid_alc = exclusions.get("alcohol_free", True)
        skin_type = persona.get("skin_type", "combination")
        concerns = persona.get("target_concerns", ["dark_spots", "dryness", "dullness", "texture"])

        # 1. Calculate Skintellect Match Score
        match_res = predict_skintellect_match(
            ingredients=parsed_ings,
            skin_type=skin_type,
            concerns=concerns,
            avoid_fungal_triggers=avoid_fa,
            avoid_fragrance=avoid_frag,
            avoid_alcohol=avoid_alc
        )
        predicted_match = match_res.get("predicted_match_score", 100)

        # 2. Calculate Darmeto Points
        is_fa_safe = len(analysis.get("fungal_triggers", [])) == 0
        is_clogger_free = len(analysis.get("cloggers", [])) == 0
        is_oil_free = not any("oil" in n.lower() for n in parsed_ings)

        darmeto_res = calculate_darmeto_points(
            match_score=predicted_match,
            analysis=analysis,
            fungal_acne_safe=is_fa_safe,
            pore_clogger_free=is_clogger_free,
            oil_free=is_oil_free,
            rating=None
        )
        darmeto_pts = darmeto_res.get("darmeto_points", 0.0)
        tier = darmeto_res.get("tier", "Safe Everyday Base")
        audit_log = darmeto_res.get("additions", []) + darmeto_res.get("deductions", [])

        # Determine consensus status
        if predicted_match >= 90:
            consensus_status = "Approved — High Compatibility"
            verdict_badge = "✅ Approved"
        elif predicted_match >= 75:
            consensus_status = "Conditionally Approved — Moderate Fit"
            verdict_badge = "⚠️ Conditional"
        else:
            consensus_status = "Rejected / High Friction — Incompatible"
            verdict_badge = "❌ Incompatible"

        # Explicit Judicial Thinking Scratchpad
        thinking = [
            f"Phase 1 (Argument Ingestion): Weighed testimonies from Dr. Vance (Vehicle: {formulator_report.get('vehicle_type', 'Hydrosol')}), Dr. Cross ({len(critic_report.get('cloggers', []))} cloggers, {len(critic_report.get('irritants', []))} irritants), and Dr. Lin ({'FA-Safe' if microbiome_report.get('is_fungal_safe') else 'FA-Triggers'}).",
            f"Phase 2 (Deterministic Grounding): Executed skintellect.formulation.scoring.predict_skintellect_match on {len(parsed_ings)} INCI tokens -> Predicted Match: {predicted_match}%.",
            f"Phase 3 (Darmeto Mathematical Scoring): Applied 29-step scoring rubric ({len(darmeto_res.get('additions', []))} additions, {len(darmeto_res.get('deductions', []))} deductions) -> Darmeto Points: {darmeto_pts}/130 pts.",
            f"Phase 4 (Final Judicial Ruling): Assigned Clinical Tier '{tier}' with status '{consensus_status}' for persona @{persona.get('username', 'user')}."
        ]

        # Construct authoritative summary
        summary = (
            f"**Authoritative Mathematical Ruling:**\n"
            f"Having weighed arguments from {formulator_report.get('agent', 'Formulator')} (Vehicle & Delivery), "
            f"{critic_report.get('agent', 'Critic')} (Toxicology & Comedogenicity), and "
            f"{microbiome_report.get('agent', 'Microbiome')} (Malassezia Flora), the court issues the binding verdict:\n\n"
            f"• **Predicted Skintellect Match:** `{predicted_match}%`\n"
            f"• **Dermatological Fit Points:** `{darmeto_pts} / 130 pts`\n"
            f"• **Clinical Tier:** `{tier}`\n"
            f"• **Ruling:** **{consensus_status}** for persona **@{persona.get('username', 'user')}**."
        )

        return {
            "agent": self.name,
            "role": self.role,
            "badge": self.badge,
            "color": self.avatar_color,
            "predicted_match": predicted_match,
            "darmeto_points": darmeto_pts,
            "tier": tier,
            "status": consensus_status,
            "verdict_badge": verdict_badge,
            "summary": summary,
            "thinking": thinking,
            "audit_log": audit_log,
            "breakdown": {
                "brighteners": analysis.get("brighteners", []),
                "barrier": analysis.get("barrier", []),
                "smoothers": analysis.get("smoothers", []),
                "irritants": analysis.get("irritants", []),
                "cloggers": analysis.get("cloggers", []),
                "fungal_triggers": analysis.get("fungal_triggers", [])
            }
        }
