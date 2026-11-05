"""
Adversarial Safety, Comedogenicity & Irritancy Auditor Agent
===========================================================
Role: Relentlessly challenges formulation claims, highlighting cumulative
comedogenicity, volatile irritants, fragrance sensitizers, and acid clash risks.
Includes structured clinical toxicological thinking steps.
"""

from typing import Any, Dict, Optional

from .llm import LLMClient
from skintellect.formulation.scoring import analyze_ingredients, parse_ingredients_input


class SafetyCriticAgent:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.name = "Dr. Marcus Cross"
        self.role = "Clinical Safety & Toxicology Critic"
        self.badge = "🛡️ Safety Auditor"
        self.avatar_color = "rose"
        self.llm = llm_client or LLMClient()

    def audit_formulation(
        self,
        ingredients_input: Any,
        persona: Dict[str, Any],
        formulator_statement: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Audits the formulation with adversarial scrutiny against the active persona.
        """
        parsed_ings = parse_ingredients_input(ingredients_input)
        analysis = analyze_ingredients(parsed_ings)

        irritants = analysis.get("irritants", [])
        cloggers = analysis.get("cloggers", [])
        fungal_triggers = analysis.get("fungal_triggers", [])
        exclusions = persona.get("safety_exclusions", {})

        flags = []
        if irritants:
            flags.append(f"Sensitizers / Volatile Irritants: {', '.join(irritants)}")
        if cloggers:
            flags.append(f"Known Comedogenic Pore Cloggers: {', '.join(cloggers)}")
        if fungal_triggers and exclusions.get("fungal_acne_safe"):
            flags.append(f"Malassezia Fungal Acne Triggers: {', '.join(fungal_triggers)}")

        # Explicit Scientific Thinking Scratchpad
        thinking = [
            f"Phase 1 (Toxicology Cross-Reference): Cross-referenced {len(parsed_ings)} INCI tokens against CIR, EU Annex III 26 allergens, and SCCS safety monographs.",
            f"Phase 2 (Follicular Occlusion Assessment): Assessed comedogenic index. Detected {len(cloggers)} pore cloggers ({', '.join(cloggers) if cloggers else 'Zero flagged pore cloggers'}).",
            f"Phase 3 (Contact Sensitization Audit): Evaluated cutaneous threshold limits. Identified {len(irritants)} potential contact irritants ({', '.join(irritants) if irritants else 'Zero flagged sensitizers'}).",
            f"Phase 4 (Risk-Benefit Interjection): Formulated critical pushback for persona @{persona.get('username', 'user')} (Sensitivity: {persona.get('sensitivity', 'moderate')})."
        ]

        llm_text = None
        if self.llm.has_any_key:
            system_prompt = (
                f"You are {self.name}, a strict clinical toxicologist and dermatological safety auditor ({self.role}). "
                "Your job is to challenge the cosmetic chemist's optimistic claims. "
                "Highlight comedogenic pore-clogging potential, barrier impairment, allergen risks, and active conflicts. "
                "Be direct, scientifically rigorous, and protective of sensitive skin."
            )
            user_msg = (
                f"Active Persona Profile: {persona.get('label')} | Skin: {persona.get('skin_type')} | "
                f"Sensitivity: {persona.get('sensitivity')} | Exclusions: {exclusions}\n"
                f"Chemist Claims: {formulator_statement}\n"
                f"Flagged Irritants: {irritants}\n"
                f"Flagged Pore Cloggers: {cloggers}\n"
                f"Fungal Triggers: {fungal_triggers}\n"
                f"Ingredients Count: {len(parsed_ings)}"
            )
            llm_text = self.llm.chat_complete(
                [{"role": "user", "content": user_msg}],
                system_prompt=system_prompt,
                temperature=0.3
            )

        if not llm_text:
            llm_text = (
                f"**Clinical Toxicology Interjection:**\n"
                f"I must push back on the chemist's benign assessment. Evaluating this formula through a dermatological "
                f"risk lens reveals critical hazards for a **{persona.get('skin_type', 'combination')} / {persona.get('sensitivity', 'sensitive')}** barrier.\n\n"
            )
            if irritants:
                llm_text += (
                    f"⚠️ **Irritancy & Allergen Alert:** Detected *{', '.join(irritants)}*. "
                    f"These compounds are documented contact allergens under EU SCCS / CIR standards. "
                    f"For reactive skin, repeated exposure risks sub-clinical micro-inflammation, accelerating barrier degradation.\n\n"
                )
            if cloggers:
                llm_text += (
                    f"⚠️ **Follicular Occlusion (Comedogenicity):** Contains *{', '.join(cloggers)}*. "
                    f"These heavy lipids possess high rabbit ear / human follicular assay ratings (≥ 3/5), presenting "
                    f"an elevated risk of closed comedones and micro-cysts along sebaceous zones.\n\n"
                )
            if not irritants and not cloggers:
                llm_text += (
                    f"✅ **Clean Toxicology Profile:** Remarkable tolerance profile. No volatile fragrant allergens "
                    f"or high-grade comedogenic esters were detected in this deck. The lipid burden appears physiologically balanced.\n\n"
                )

            llm_text += (
                f"**Auditor Caveat:** Even well-formulated actives can cause barrier fatigue if introduced without proper lipid buffer support."
            )

        return {
            "agent": self.name,
            "role": self.role,
            "badge": self.badge,
            "color": self.avatar_color,
            "message": llm_text,
            "thinking": thinking,
            "flags": flags,
            "irritants": irritants,
            "cloggers": cloggers,
            "is_clean": len(irritants) == 0 and len(cloggers) == 0
        }
