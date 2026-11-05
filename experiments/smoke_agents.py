"""
Verification Suite for Stage 6: Multi-Agent System & CSI Detective
===================================================================
Tests the multi-agent board, deliberation orchestration, CSI forensic analysis,
deterministic judge grounding, and decoupled router endpoints.
"""

import os
import sys

# Ensure UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root and src are in sys.path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_THIS_DIR)
for p in [_ROOT_DIR, os.path.join(_ROOT_DIR, "src"), os.path.join(_ROOT_DIR, ".runtime")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Force offline deterministic mode for fast, zero-flakiness verification
os.environ['AGENT_LLM_MODE'] = 'offline'

from experiments.specialist_board.board import BoardOrchestrator
from experiments.ingredient_csi.detective import CSIDetective
from experiments.specialist_board.formulator import FormulatorAgent
from experiments.specialist_board.judge import DeterministicJudgeAgent
from experiments.specialist_board.microbiome import MicrobiomeAgent
from experiments.specialist_board.safety_critic import SafetyCriticAgent


def test_individual_agents():
    print("\n[+] 1. Testing Individual Specialist Agents...")
    sample_deck = "Water, Glycerin, Niacinamide, Ceramide NP, Cetearyl Alcohol, Fragrance, Phenoxyethanol"
    persona = {
        "id": "uap",
        "label": "Ultra-Acne Prone",
        "skin_type": "oily",
        "concerns": ["acne", "pores"],
        "avoid_ingredients": ["fragrance"]
    }

    # 1. Formulator
    formulator = FormulatorAgent()
    f_res = formulator.generate_proposal(sample_deck, persona=persona)
    assert f_res["role"] == "Lead Cosmetic Chemist"
    assert "vehicle_type" in f_res
    print("  ✓ FormulatorAgent passed proposal generation")

    # 2. Safety Critic
    critic = SafetyCriticAgent()
    c_res = critic.audit_formulation(sample_deck, persona=persona, formulator_statement=f_res["message"])
    assert c_res["role"] == "Clinical Safety & Toxicology Critic"
    assert any("fragrance" in str(f).lower() for f in c_res.get("flags", []))
    print("  ✓ SafetyCriticAgent passed audit (flagged Fragrance)")

    # 3. Microbiome
    micro = MicrobiomeAgent()
    m_res = micro.inspect_microbiome_safety(sample_deck, persona=persona)
    assert m_res["role"] == "Microbiome & Barrier Flora Specialist"
    assert "is_fungal_safe" in m_res
    print("  ✓ MicrobiomeAgent passed microbiome inspection")

    # 4. Deterministic Judge
    judge = DeterministicJudgeAgent()
    j_res = judge.adjudicate(sample_deck, persona, f_res, c_res, m_res)
    assert j_res["role"] == "Deterministic Scoring Engine"
    assert j_res["predicted_match"] > 0
    assert isinstance(j_res["status"], str) and len(j_res["status"]) > 0
    print(f"  ✓ DeterministicJudgeAgent passed (Verdict: {j_res['predicted_match']}%, Status: {j_res['status']})")


def test_board_orchestrator():
    print("\n[+] 2. Testing Multi-Agent Board Orchestration...")
    orchestrator = BoardOrchestrator()
    sample_deck = "Centella Asiatica Extract, Madecassoside, Panthenol, Squalane, Butylene Glycol"
    
    board_output = orchestrator.run_deliberation(
        ingredients_input=sample_deck,
        persona_id="uap",
        user_question="Is this soothing for barrier repair?"
    )

    assert board_output["status"] == "success"
    assert board_output["rounds_count"] == 5
    assert board_output["verdict"]["role"] == "Deterministic Scoring Engine"
    assert board_output["verdict"]["predicted_match"] >= 80
    assert "telemetry" in board_output
    print(f"  ✓ BoardOrchestrator executed successfully")
    print(f"    - Predicted Match: {board_output['verdict']['predicted_match']}%")
    print(f"    - Consensus: {board_output['verdict']['summary'][:60]}...")


def test_csi_detective():
    print("\n[+] 3. Testing Ingredient CSI Detective...")
    detective = CSIDetective()

    # Product A and B caused breakouts, Product C and D were completely fine
    breakout_products = [
        "Water, Glycerin, Isopropyl Myristate, Cetearyl Alcohol, Phenoxyethanol",
        "Water, Butylene Glycol, Isopropyl Myristate, Squalane, Tocopherol"
    ]
    safe_products = [
        "Water, Glycerin, Squalane, Ceramide NP",
        "Water, Butylene Glycol, Centella Asiatica, Sodium Hyaluronate"
    ]

    report = detective.investigate(
        problematic_items=breakout_products,
        safe_items=safe_products,
        reaction_type="breakouts_acne"
    )

    assert report["suspects_count"] > 0
    top_suspect = report["top_suspects"][0]
    assert top_suspect["ingredient"].lower() == "isopropyl myristate"
    assert top_suspect["recurrence_rate"] == 100
    assert top_suspect["is_pore_clogger"] is True
    
    print("  ✓ CSIDetective correctly isolated top suspect:")
    print(f"    - Suspect: {top_suspect['ingredient']}")
    print(f"    - Recurrence: {top_suspect['recurrence_rate']}% (Pore Clogger: {top_suspect['is_pore_clogger']})")
    print(f"    - Family: {top_suspect['chemical_family']}")


def test_decoupled_router():
    print("\n[+] 4. Testing Decoupled Agent API Router Endpoints...")
    try:
        from skintellect.api.agents import (
            AgentBoardRequest,
            CsiInvestigateRequest,
            deliberate_formulation,
            get_agents_meta,
            investigate_allergies,
        )
    except (ModuleNotFoundError, ImportError):
        print("  ℹ️ /api/agents router retired to experiments. Skipping router direct test.")
        return

    meta = get_agents_meta()
    assert len(meta["board_agents"]) == 4
    assert meta["csi_detective"]["name"] == "Inspector INCI"
    print(f"  ✓ /api/agents/meta returned {len(meta['board_agents'])} agents and CSI detective")


if __name__ == "__main__":
    print("=" * 60)
    print(" 🧪 STAGE 6: MULTI-AGENT SYSTEM & CSI VERIFICATION SUITE")
    print("=" * 60)
    test_individual_agents()
    test_board_orchestrator()
    test_csi_detective()
    test_decoupled_router()
    print("=" * 60)
    print(" ✅ ALL AGENT & CSI DETECTIVE TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
