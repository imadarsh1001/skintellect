"""
Unit tests for decoupled experimental tracks:
- Standalone Formula Lab (experiments/formula_lab)
- Ingredient CSI Detective (experiments/ingredient_csi)
- Specialist Board Orchestrator (experiments/specialist_board)
"""
import os
import sys
import unittest
from pathlib import Path

# Add project root and src to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from experiments.formula_lab.formulas import analyze_formula_full
from experiments.ingredient_csi.detective import CSIDetective
from experiments.specialist_board.board import BoardOrchestrator


class ExperimentalFeaturesTests(unittest.TestCase):
    def setUp(self):
        # Force mock provider so tests run fully offline without API keys
        self.old_mode = os.environ.get("AGENT_LLM_MODE")
        os.environ["AGENT_LLM_MODE"] = "mock"

    def tearDown(self):
        if self.old_mode is not None:
            os.environ["AGENT_LLM_MODE"] = self.old_mode
        else:
            os.environ.pop("AGENT_LLM_MODE", None)

    def test_formula_lab_raw_text_analysis(self):
        res = analyze_formula_full(
            ingredients_text="Water, Houttuynia Cordata Extract, Glycerin, Niacinamide, Ceramide NP",
            persona_id="uap",
        )
        self.assertGreater(res["predicted_match_score"], 50)
        self.assertGreater(res["darmeto_points"], 0)
        self.assertGreater(len(res["ingredients_breakdown"]), 0)
        self.assertIsInstance(res["audit_log"], list)

    def test_ingredient_csi_investigation(self):
        detective = CSIDetective()
        report = detective.investigate(
            problematic_items=["Water, Ethylhexyl Palmitate, Cetearyl Alcohol"],
            safe_items=["Water, Glycerin, Butylene Glycol"],
            reaction_type="breakouts_acne",
        )
        self.assertEqual(report["total_problem_products"], 1)
        self.assertEqual(report["total_safe_products"], 1)
        self.assertGreater(report["suspects_count"], 0)
        self.assertGreater(len(report["top_suspects"]), 0)

    def test_specialist_board_deliberation(self):
        orch = BoardOrchestrator()
        res = orch.run_deliberation(
            ingredients_input="Water, Glycerin, Ceramide NP",
            persona_id="uap",
            user_question="Is this formula gentle?",
        )
        self.assertIn("debate", res)
        self.assertIn("verdict", res)
        self.assertGreaterEqual(len(res["debate"]), 4)
        verdict = res["verdict"]
        self.assertIn("status", verdict)
        self.assertIn("predicted_match", verdict)
        self.assertIn("darmeto_points", verdict)


if __name__ == "__main__":
    unittest.main()
