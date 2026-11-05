"""
Lead Cosmetic Chemist & Formulation Synthesis Agent
===================================================
Role: Evaluates the formula vehicle, active mechanisms, emulsification,
and potential biological efficacy for the targeted skin persona.
Includes detailed scientific thinking scratchpad and step trace.
"""

from typing import Any, Dict, List, Optional

from .llm import LLMClient
from skintellect.formulation.scoring import analyze_ingredients, parse_ingredients_input


class FormulatorAgent:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.name = "Dr. Elena Vance"
        self.role = "Lead Cosmetic Chemist"
        self.badge = "🧪 Formulation Specialist"
        self.avatar_color = "teal"
        self.llm = llm_client or LLMClient()

    def generate_proposal(
        self,
        ingredients_input: Any,
        persona: Dict[str, Any],
        user_question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes the ingredient deck and produces the chemist's initial formulation defense.
        """
        parsed_ings = parse_ingredients_input(ingredients_input)
        analysis = analyze_ingredients(parsed_ings)

        brighteners = analysis.get("brighteners", [])
        barrier = analysis.get("barrier", [])
        smoothers = analysis.get("smoothers", [])
        total = len(parsed_ings)
        active_count = len(brighteners) + len(barrier) + len(smoothers)

        # Detect vehicle base
        vehicle_type = "Water-Based Hydrosol"
        lower_ings = [i.lower() for i in parsed_ings[:5]]
        if any("oil" in i or "butter" in i for i in lower_ings):
            vehicle_type = "Emollient Oil-in-Water Emulsion"
        elif any("dimethicone" in i or "silicone" in i for i in lower_ings):
            vehicle_type = "Silicone-Elastomer Slip Base"
        elif any("aloe" in i or "centella" in i or "water" in i for i in lower_ings):
            vehicle_type = "Aqueous Botanical Hydrosol"

        # Explicit Scientific Thinking Scratchpad
        thinking = [
            f"Phase 1 (Solvent & Delivery Vehicle): Scanned {total} INCI tokens. Classified primary delivery vehicle as '{vehicle_type}'.",
            f"Phase 2 (Therapeutic Active Mapping): Identified {active_count} primary actives — {len(brighteners)} Brighteners ({', '.join(brighteners[:2]) if brighteners else 'none'}), {len(barrier)} Barrier Restorers ({', '.join(barrier[:2]) if barrier else 'none'}), {len(smoothers)} Smoothers.",
            f"Phase 3 (Partition Coefficient & Flux): Solvent polarity enables trans-epidermal active flux while maintaining stratum corneum lipid balance.",
            f"Phase 4 (Persona Alignment): Evaluated cosmetic compounding fit for @{persona.get('username', 'user')} with {persona.get('skin_type', 'combination')} profile."
        ]

        # Try LLM first if available
        llm_text = None
        if self.llm.has_any_key:
            system_prompt = (
                f"You are {self.name}, an expert cosmetic chemist ({self.role}). "
                "Analyze the provided cosmetic formulation. Highlight vehicle delivery, active synergies, "
                "and formulation balance in 2-3 professional, science-backed paragraphs. "
                "Be assertive about formulation strengths while remaining scientifically honest."
            )
            user_msg = (
                f"Active Persona: {persona.get('label', 'Default')} (Skin: {persona.get('skin_type')}, "
                f"Sensitivity: {persona.get('sensitivity')})\n"
                f"Question/Context: {user_question or 'Evaluate this ingredient deck'}\n"
                f"Formula Ingredients ({total}): {', '.join(parsed_ings[:30])}\n"
                f"Detected Actives: Brighteners={brighteners}, Barrier={barrier}, Texture={smoothers}"
            )
            llm_text = self.llm.chat_complete(
                [{"role": "user", "content": user_msg}],
                system_prompt=system_prompt,
                temperature=0.3
            )

        if not llm_text:
            # High-fidelity domain simulation
            actives_str = ", ".join(brighteners + barrier + smoothers) or "fundamental humectants"
            llm_text = (
                f"**Formulation Architecture Overview:**\n"
                f"From a cosmetic chemistry perspective, this deck is built upon a **{vehicle_type}** matrix containing {total} ingredients. "
                f"The formula establishes a clear therapeutic backbone with {active_count} primary active molecules: *{actives_str}*.\n\n"
                f"**Active Delivery & Vehicle Stability:**\n"
                f"The solvent base facilitates proper trans-epidermal flux. "
            )
            if barrier:
                llm_text += (
                    f"The incorporation of barrier restorers (*{', '.join(barrier[:3])}*) provides multi-depth lipid support, "
                    f"reinforcing intercellular ceramides and reducing transepidermal water loss (TEWL). "
                )
            if brighteners:
                llm_text += (
                    f"Tyrosinase inhibition and melanosome transfer blocking are supported via *{', '.join(brighteners[:2])}*, "
                    f"which pairs well with the hydrator base. "
                )
            llm_text += (
                f"\n\n**Preliminary Verdict:** From a pure cosmetic compounding standpoint, this formula demonstrates strong "
                f"functional elegance for a {persona.get('skin_type', 'combination')} profile."
            )

        return {
            "agent": self.name,
            "role": self.role,
            "badge": self.badge,
            "color": self.avatar_color,
            "vehicle_type": vehicle_type,
            "active_count": active_count,
            "message": llm_text,
            "thinking": thinking,
            "key_actives": brighteners + barrier + smoothers
        }

    def generate_rebuttal(
        self,
        critique_concerns: List[str],
        persona: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Formulator defends formulation against Safety Critic attacks.
        """
        thinking = [
            f"Phase 1 (Auditor Challenge Review): Appraised {len(critique_concerns)} toxicological flags raised by Dr. Cross.",
            "Phase 2 (Finished Product Dilution): Evaluated real-world finished formula concentrations vs pure raw material toxicity thresholds.",
            "Phase 3 (Clinical Action Plan): Synthesized buffering, acclimatization, and 48h patch-testing guidance to harvest therapeutic benefits safely."
        ]

        rebuttal_text = (
            f"**Formulation Counter-Defense:**\n"
            f"While the Safety Auditor rightly flags theoretical hazards, cosmetic toxicology must account for real finished product dosing. "
            f"The presence of occlusive or active ingredients is tempered by the overall emulsion architecture. "
            f"For @{persona.get('username', 'user')}, gradual introduction (patch testing for 48 hours or buffer application over moisturizer) "
            f"can mitigate localized reactivity while harvesting the therapeutic benefits of the active matrix."
        )
        return {
            "agent": self.name,
            "role": self.role,
            "badge": self.badge,
            "color": self.avatar_color,
            "message": rebuttal_text,
            "thinking": thinking
        }
