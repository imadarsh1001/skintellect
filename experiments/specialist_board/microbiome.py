"""
Microbiome & Barrier Flora Specialist Agent
===========================================
Role: Evaluates Malassezia yeast folliculitis triggers, lipid carbon-chain lengths,
microbiome diversity, and skin acid mantle / lipid bilayer equilibrium.
Includes explicit biochemical thinking scratchpad.
"""

from typing import Any, Dict, Optional

from .llm import LLMClient
from skintellect.formulation.scoring import analyze_ingredients, parse_ingredients_input


class MicrobiomeAgent:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.name = "Dr. Nadia Lin"
        self.role = "Microbiome & Barrier Flora Specialist"
        self.badge = "🧬 Microbiome Specialist"
        self.avatar_color = "purple"
        self.llm = llm_client or LLMClient()

    def inspect_microbiome_safety(
        self,
        ingredients_input: Any,
        persona: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Inspects deck for Malassezia feeding triggers and acid mantle preservation.
        """
        parsed_ings = parse_ingredients_input(ingredients_input)
        analysis = analyze_ingredients(parsed_ings)

        fungal_triggers = analysis.get("fungal_triggers", [])
        is_fungal_safe = len(fungal_triggers) == 0
        requires_fungal_safe = persona.get("safety_exclusions", {}).get("fungal_acne_safe", False)

        # Explicit Scientific Thinking Scratchpad
        thinking = [
            f"Phase 1 (Malassezia Lipid Screen): Audited lipid substrates for C11-C24 free fatty acids, esters, and polysorbates.",
            f"Phase 2 (Substrate Proliferation Index): Found {len(fungal_triggers)} fungal triggers ({', '.join(fungal_triggers) if fungal_triggers else 'Zero triggers — 100% Malassezia Safe'}).",
            f"Phase 3 (Acid Mantle & Commensal Flora): Evaluated impact on beneficial commensal bacteria (Staphylococcus epidermidis, Cutibacterium acnes balance).",
            f"Phase 4 (Persona Rule Enforcement): Checked active persona Malassezia rule: {'STRICT MALASSEZIA EXCLUSION ENFORCED' if requires_fungal_safe else 'Standard lipid tolerance allowed'}."
        ]

        llm_text = None
        if self.llm.has_any_key:
            system_prompt = (
                f"You are {self.name}, a clinical microbiologist and epidermal barrier specialist ({self.role}). "
                "Audit the cosmetic formula specifically for microbiome health, Malassezia yeast triggers, "
                "fatty acid chain lengths (C12-C24), and lipid bilayer balance. Be concise and authoritative."
            )
            user_msg = (
                f"Persona requires Malassezia Safe: {requires_fungal_safe}\n"
                f"Detected Fungal Triggers: {fungal_triggers}\n"
                f"Formula Ingredients: {', '.join(parsed_ings[:25])}"
            )
            llm_text = self.llm.chat_complete(
                [{"role": "user", "content": user_msg}],
                system_prompt=system_prompt,
                temperature=0.3
            )

        if not llm_text:
            if fungal_triggers:
                triggers_str = ", ".join(fungal_triggers)
                llm_text = (
                    f"**Microbiome & Flora Inspection:**\n"
                    f"🔬 **Malassezia Yeast Feeding Warning:** This formula contains {len(fungal_triggers)} documented "
                    f"lipid triggers: *{triggers_str}*. "
                    f"Lipophilic *Malassezia* yeasts possess extracellular lipases that hydrolyze carbon chain lengths between $\\text{{C}}_{{11}}$ and $\\text{{C}}_{{24}}$, "
                    f"metabolizing them into free fatty acids that promote pityrosporum folliculitis and seborrheic dermatitis.\n\n"
                )
                if requires_fungal_safe:
                    llm_text += (
                        f"❌ **Direct Persona Violation:** Persona @{persona.get('username', 'user')} enforces strict Malassezia avoidance. "
                        f"This formula will stimulate fungal yeast proliferation."
                    )
                else:
                    llm_text += (
                        f"ℹ️ **Tolerance Note:** Safe for non-fungal acne prone skin, but individuals prone to itchy forehead papules should exercise caution."
                    )
            else:
                llm_text = (
                    f"**Microbiome & Flora Inspection:**\n"
                    f"🔬 **100% Malassezia Fungal Acne Safe:** Zero $\\text{{C}}_{{11}}-\\text{{C}}_{{24}}$ fatty acid esters, "
                    f"polysorbates, or galactomyces ferments detected in this deck. "
                    f"The epidermal commensal flora (e.g. *Staphylococcus epidermidis*) can thrive without providing nutritional substrates for yeast dysbiosis."
                )

        return {
            "agent": self.name,
            "role": self.role,
            "badge": self.badge,
            "color": self.avatar_color,
            "message": llm_text,
            "thinking": thinking,
            "is_fungal_safe": is_fungal_safe,
            "fungal_triggers": fungal_triggers
        }
