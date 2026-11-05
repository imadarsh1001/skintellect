"""
Board Orchestrator: Multi-Turn Deliberation & Stream Dispatcher
==============================================================
Coordinates the adversarial debate between Formulator, Safety Critic,
Microbiome Specialist, and the Deterministic Judge.
"""

import json
import time
from typing import Any, Dict, Generator, Optional

from .formulator import FormulatorAgent
from .judge import DeterministicJudgeAgent
from .llm import LLMClient
from .microbiome import MicrobiomeAgent
from .safety_critic import SafetyCriticAgent
from skintellect.catalog.personas import get_all_personas


class BoardOrchestrator:
    def __init__(self):
        self.llm = LLMClient()
        self.formulator = FormulatorAgent(self.llm)
        self.safety_critic = SafetyCriticAgent(self.llm)
        self.microbiome = MicrobiomeAgent(self.llm)
        self.judge = DeterministicJudgeAgent()

    def _resolve_persona(self, persona_id: Optional[str] = "uap") -> Dict[str, Any]:
        """Resolves persona dict from core personas."""
        personas = get_all_personas()
        pid = (persona_id or "uap").lower().strip()
        found = next((p for p in personas if p.get("id") == pid or p.get("username") == pid), None)
        if not found and personas:
            found = personas[0]
        return found or {
            "id": "uap",
            "username": "uap",
            "label": "Universal Combination Profile",
            "skin_type": "combination",
            "sensitivity": "slightly_sensitive",
            "safety_exclusions": {"fungal_acne_safe": True}
        }

    def run_deliberation(
        self,
        ingredients_input: Any,
        persona_id: Optional[str] = "uap",
        user_question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a complete 5-step deliberation round and returns full structured debate.
        """
        persona = self._resolve_persona(persona_id)

        # Round 1: Formulator Proposal
        p1 = self.formulator.generate_proposal(ingredients_input, persona, user_question)

        # Round 2: Safety Critic Audit
        p2 = self.safety_critic.audit_formulation(ingredients_input, persona, p1["message"])

        # Round 3: Microbiome Specialist Inspection
        p3 = self.microbiome.inspect_microbiome_safety(ingredients_input, persona)

        # Round 4: Formulator Rebuttal
        p4 = self.formulator.generate_rebuttal(p2.get("flags", []), persona)

        # Round 5: Deterministic Judge Adjudication
        verdict = self.judge.adjudicate(ingredients_input, persona, p1, p2, p3)

        debate_rounds = [
            {"round": 1, "stage": "Formulation Proposal", **p1},
            {"round": 2, "stage": "Adversarial Safety Audit", **p2},
            {"round": 3, "stage": "Microbiome Inspection", **p3},
            {"round": 4, "stage": "Chemist Defense & Rebuttal", **p4},
            {"round": 5, "stage": "Deterministic Ruling", **verdict}
        ]

        telemetry = {
            "mode": self.llm.last_telemetry.get("mode", "offline"),
            "provider": self.llm.last_telemetry.get("provider", "Domain Simulation Engine"),
            "model": self.llm.last_telemetry.get("model", "cosmetic-rule-engine"),
            "latency_ms": self.llm.last_telemetry.get("latency_ms", 1),
            "key_summary": self.llm.key_summary,
            "error": self.llm.last_telemetry.get("error")
        }

        # Terminal inspection logging
        print("\n" + "=" * 65)
        print(f"  [AI BOARD DELIBERATION] Active Persona: @{persona.get('username')} ({persona.get('skin_type')})")
        print(f"  [ENGINE] Provider: {telemetry['provider']} | Model: {telemetry['model']} | ⏱️ {telemetry['latency_ms']}ms")
        print(f"  [ROUND 1 - CHEMIST] Vehicle: {p1.get('vehicle_type')} | Actives: {p1.get('active_count')}")
        print(f"  [ROUND 2 - CRITIC] Cloggers: {len(p2.get('cloggers', []))} | Irritants: {len(p2.get('irritants', []))}")
        print(f"  [ROUND 3 - MICROBIOME] Fungal Triggers: {len(p3.get('fungal_triggers', []))} | FA-Safe: {p3.get('is_fungal_safe')}")
        print(f"  [ROUND 5 - JUDGE] Match: {verdict.get('predicted_match')}% | Darmeto: {verdict.get('darmeto_points')}/130 pts | Tier: {verdict.get('tier')}")
        print("=" * 65 + "\n")

        return {
            "status": "success",
            "persona": {
                "id": persona.get("id"),
                "username": persona.get("username"),
                "label": persona.get("label"),
                "skin_type": persona.get("skin_type"),
                "sensitivity": persona.get("sensitivity")
            },
            "user_question": user_question or "Comprehensive Formulation Review",
            "rounds_count": len(debate_rounds),
            "telemetry": telemetry,
            "debate": debate_rounds,
            "verdict": verdict
        }

    def stream_deliberation(
        self,
        ingredients_input: Any,
        persona_id: Optional[str] = "uap",
        user_question: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Server-Sent Events (SSE) generator streaming each agent turn with live delays.
        """
        persona = self._resolve_persona(persona_id)
        username = persona.get("username", "user")
        init_payload = {
            "type": "init",
            "message": f"Convening Clinical Formulation Board for @{username}",
            "persona": persona
        }
        yield f"data: {json.dumps(init_payload)}\n\n"
        time.sleep(0.3)

        # Round 1: Formulator
        yield f"data: {json.dumps({'type': 'typing', 'agent': self.formulator.name, 'role': self.formulator.role})}\n\n"
        p1 = self.formulator.generate_proposal(ingredients_input, persona, user_question)
        yield f"data: {json.dumps({'type': 'turn', 'round': 1, 'data': p1})}\n\n"
        time.sleep(0.4)

        # Round 2: Safety Critic
        yield f"data: {json.dumps({'type': 'typing', 'agent': self.safety_critic.name, 'role': self.safety_critic.role})}\n\n"
        p2 = self.safety_critic.audit_formulation(ingredients_input, persona, p1["message"])
        yield f"data: {json.dumps({'type': 'turn', 'round': 2, 'data': p2})}\n\n"
        time.sleep(0.4)

        # Round 3: Microbiome Specialist
        yield f"data: {json.dumps({'type': 'typing', 'agent': self.microbiome.name, 'role': self.microbiome.role})}\n\n"
        p3 = self.microbiome.inspect_microbiome_safety(ingredients_input, persona)
        yield f"data: {json.dumps({'type': 'turn', 'round': 3, 'data': p3})}\n\n"
        time.sleep(0.4)

        # Round 4: Chemist Rebuttal
        yield f"data: {json.dumps({'type': 'typing', 'agent': self.formulator.name, 'role': 'Rebuttal'})}\n\n"
        p4 = self.formulator.generate_rebuttal(p2.get("flags", []), persona)
        yield f"data: {json.dumps({'type': 'turn', 'round': 4, 'data': p4})}\n\n"
        time.sleep(0.4)

        # Round 5: Deterministic Judge
        yield f"data: {json.dumps({'type': 'typing', 'agent': self.judge.name, 'role': self.judge.role})}\n\n"
        verdict = self.judge.adjudicate(ingredients_input, persona, p1, p2, p3)
        yield f"data: {json.dumps({'type': 'turn', 'round': 5, 'data': verdict})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'verdict': verdict})}\n\n"
