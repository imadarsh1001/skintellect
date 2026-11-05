"""
Tests for Core Domain Policies, LangChain Tools, LangGraph Workflow, and Deep Agents Copilot.
"""

import unittest
from skintellect.core.entities import (
    PersonaExclusionsEntity,
    ProductEntity,
    SkinPersonaEntity,
)
from skintellect.core.policies import (
    evaluate_persona_match,
    normalize_ingredient_name,
)
from skintellect.agents.copilot import (
    ResearchCopilotSession,
    get_or_create_copilot_session,
)
from skintellect.agents.graph import run_research_graph
from skintellect.agents.tools import (
    get_ingredient_graph_tool,
    get_product_detail_tool,
    get_review_insights_tool,
    get_scientific_references_tool,
    search_catalog_tool,
)
from tests import test_research as fixtures


class AgentsAndCoreTests(unittest.TestCase):
    def setUp(self):
        fixtures.ResearchTests.setUp(self)

    def tearDown(self):
        fixtures.ResearchTests.tearDown(self)

    def test_ingredient_name_normalization(self):
        self.assertEqual(normalize_ingredient_name("  Ceramide NP*  "), "ceramide np")
        self.assertEqual(normalize_ingredient_name('Water / Aqua"'), "water / aqua")

    def test_persona_matching_policies(self):
        product_safe = ProductEntity(
            id=101,
            brand="BarrierBrand",
            name="Safe Cream",
            formula_status="verified",
            ingredients=["Water", "Ceramide NP", "Glycerin", "Squalane"],
        )
        persona_fa = SkinPersonaEntity(
            id="fa_user",
            username="fa_user",
            label="Fungal Acne Sensitive",
            skin_type="dry",
            exclusions=PersonaExclusionsEntity(fungal_acne_safe=True, fragrance_free=True),
        )
        res_safe = evaluate_persona_match(product_safe, persona_fa)
        self.assertTrue(res_safe.is_eligible)
        self.assertGreaterEqual(res_safe.match_percentage, 80)
        self.assertEqual(len(res_safe.flagged_concerns), 0)

        # Trigger fungal acne violation
        product_trigger = ProductEntity(
            id=102,
            brand="OilBrand",
            name="Coconut Cream",
            formula_status="verified",
            ingredients=["Water", "Coconut Oil", "Fragrance"],
        )
        res_trigger = evaluate_persona_match(product_trigger, persona_fa)
        self.assertFalse(res_trigger.is_eligible)
        self.assertTrue(any("fungal acne" in c.lower() for c in res_trigger.flagged_concerns))
        self.assertTrue(any("fragrance" in c.lower() for c in res_trigger.flagged_concerns))

    def test_persona_matching_missing_formula_reports_unknown(self):
        product_unknown = ProductEntity(
            id=103,
            brand="MysteryBrand",
            name="Mystery Cream",
            formula_status="missing",
            ingredients=[],
        )
        persona = SkinPersonaEntity(id="u", username="u", label="User")
        res = evaluate_persona_match(product_unknown, persona)
        self.assertEqual(res.status, "partial_unknown")
        self.assertEqual(res.coverage_score, 0.0)
        self.assertTrue(res.unknown_factors)

    def test_langchain_tools_execution(self):
        # 1. Search tool
        search_res = search_catalog_tool("ceramides", db_path=self.path)
        self.assertIn("products", search_res)
        self.assertIn("total", search_res)

        # 2. Graph connections tool
        graph_res = get_ingredient_graph_tool(1, limit=3, db_path=self.path)
        self.assertIn("product_id", graph_res)
        self.assertIn("nodes", graph_res)
        self.assertIn("edges", graph_res)

        # 3. Review insights tool
        review_res = get_review_insights_tool(1, db_path=self.path)
        self.assertIn("aspects", review_res)

        # 4. References tool
        ref_res = get_scientific_references_tool("ceramide", db_path=self.path)
        self.assertIsInstance(ref_res, list)

    def test_langgraph_research_workflow_execution(self):
        result = run_research_graph(
            question="moisturizer with ceramides",
            planning_mode="fixed",
            db_path=self.path,
        )
        self.assertIn("answer", result)
        self.assertIn("search", result)
        self.assertIn("trace", result)
        self.assertIn("stage_timings_ms", result["trace"])
        self.assertIn("interpret", result["trace"]["stage_timings_ms"])

    def test_deep_agents_copilot_session_planning_and_memory(self):
        session = get_or_create_copilot_session("test_session_id_42", "uap")
        self.assertIsInstance(session, ResearchCopilotSession)

        result = session.ask("lightweight moisturizer for oily skin", planning_mode="fixed", db_path=self.path)
        self.assertEqual(len(session.messages), 2)  # 1 user + 1 assistant
        self.assertEqual(session.messages[0]["role"], "user")
        self.assertEqual(session.messages[1]["role"], "assistant")
        self.assertTrue(len(result["todo_list"]) >= 4)
        self.assertTrue(all(t["status"] == "completed" for t in result["todo_list"]))

    def test_conversational_followup_and_streaming(self):
        from skintellect.agents.intent import classify_and_plan
        from skintellect.agents.graph import stream_research_graph

        # Intent routing test for conversational challenges & complaints
        plan_doubt = classify_and_plan("are you sure?")
        self.assertEqual(plan_doubt.intent_type, "general_chat")

        plan_complaint = classify_and_plan("so why you didnt answer it ? are you not friendly?")
        self.assertEqual(plan_complaint.intent_type, "general_chat")

        plan_joke = classify_and_plan("tell me a joke")
        self.assertEqual(plan_joke.intent_type, "general_chat")

        # Streaming verification
        events = list(stream_research_graph("hi", db_path=self.path))
        self.assertTrue(any(e["event"] == "node_update" for e in events))
        self.assertTrue(any(e["event"] == "final_result" for e in events))
        final_ev = next(e for e in events if e["event"] == "final_result")
        self.assertIn("answer", final_ev["data"])
        self.assertIn("trace", final_ev["data"])

    def test_dynamic_witty_and_sulfate_science_qa(self):
        from skintellect.agents.intent import classify_and_plan
        from skintellect.agents.graph import node_synthesize_grounded_answer

        # 1. Sports / Off-topic banter query
        p1 = classify_and_plan("do you know china and taiwan won the footbal world cup?")
        self.assertEqual(p1.intent_type, "general_chat")
        s1 = {"question": "do you know china and taiwan won the footbal world cup?", "intent_type": "general_chat", "history": []}
        ans1 = node_synthesize_grounded_answer(s1)["final_answer"]
        self.assertIn("World Cup", ans1)
        self.assertIn("multiverse", ans1)
        self.assertNotIn("I hear you! You mentioned:", ans1)

        # 2. Genuine science query on sulfates & hair
        p2 = classify_and_plan("ok why sulphate or SLE are bad for hair?")
        self.assertEqual(p2.intent_type, "science_qa")
        s2 = {"question": "ok why sulphate or SLE are bad for hair?", "intent_type": "science_qa", "history": []}
        ans2 = node_synthesize_grounded_answer(s2)["final_answer"]
        self.assertIn("18-MEA", ans2)
        self.assertIn("SLS", ans2)
        self.assertIn("SLES", ans2)
        self.assertIn("anionic surfactants", ans2)

        # 3. Follow-up challenge with conversational history
        p3 = classify_and_plan("double check if why you cant answer this?")
        self.assertEqual(p3.intent_type, "general_chat")
        history = [
            {"role": "user", "content": "ok why sulphate or SLE are bad for hair?"},
            {"role": "assistant", "content": "generic template"},
        ]
        s3 = {"question": "double check if why you cant answer this?", "intent_type": "general_chat", "history": history}
        ans3 = node_synthesize_grounded_answer(s3)["final_answer"]
        self.assertIn("fair and square", ans3)
        self.assertIn("sulfates (SLS / SLES)", ans3)
        self.assertIn("18-MEA", ans3)
        self.assertNotIn("I hear you! You mentioned:", ans3)

    def test_hitl_clarification_and_shorthand_resolution(self):
        from skintellect.agents.intent import classify_and_plan
        from skintellect.agents.copilot import ResearchCopilotSession

        # 1. Ambiguous query routes to clarification_needed
        plan = classify_and_plan("what is best for acne?", db_path=self.path)
        self.assertEqual(plan.intent_type, "clarification_needed")

        # 2. Session execution generates structured options
        session = ResearchCopilotSession(session_id="test_hitl_clarification_session", persona_id="uap")
        res1 = session.ask("what is best for acne?", db_path=self.path)
        self.assertIsNotNone(res1.get("clarification"))
        self.assertTrue(len(res1["clarification"]["options"]) >= 3)
        self.assertTrue(res1["clarification"]["allow_custom"])

        # 3. User responds with shorthand "1" -> resolves to option 1 query
        res2 = session.ask("1", db_path=self.path)
        combined_text = (res2.get("answer", "") + str(res2.get("search", {}))).casefold()
        self.assertIn("salicylic", combined_text)

        # 4. Other ambiguous queries trigger clarification
        p_acid = classify_and_plan("which acid should I use?", db_path=self.path)
        self.assertEqual(p_acid.intent_type, "clarification_needed")

        p_brand = classify_and_plan("is the ordinary good?", db_path=self.path)
        self.assertEqual(p_brand.intent_type, "clarification_needed")

        p_oily = classify_and_plan("recommend a routine for oily skin", db_path=self.path)
        self.assertEqual(p_oily.intent_type, "clarification_needed")

        # 5. Specific constrained queries continue to bypass clarification
        p_spec = classify_and_plan("find fungal-acne safe cleansers with no fragrance", db_path=self.path)
        self.assertNotEqual(p_spec.intent_type, "clarification_needed")


if __name__ == "__main__":
    unittest.main()
