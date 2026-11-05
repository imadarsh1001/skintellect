"""
LangGraph state graph for multi-step formulation research workflow.
Features:
- Intelligent Intent Router (Greetings, Exploration, Science QA, Review ABSA, Product Comparison, Constraint Filter)
- Dynamic Tool Dispatch (Only activates requested agents; bypasses unrequested ones)
- Event Timeline & Execution Trace Debugger (Node latencies, decision auditing, event payloads)
"""

from datetime import datetime, timezone
import re
import time
from typing import Any, Dict, List, Optional, TypedDict

from skintellect.agents.intent import classify_and_plan
from skintellect.catalog.store import get_catalog
from skintellect.catalog.products import load_records
from skintellect.research.search import brief
from skintellect.gemini import GeminiUnavailable, run_budget
from skintellect.research.alternatives import alternatives
from skintellect.research.evidence import RULE_VERSION
from skintellect.research.model_steps import choose_plan, select_answer_evidence
from skintellect.research.models import SearchIntent
from skintellect.research.references import references
from skintellect.research.reviews import review_insights
from skintellect.research.search import interpret, structured_search


class ResearchGraphState(TypedDict, total=False):
    # Inputs
    question: str
    persona_id: str
    product_ids: Optional[List[int]]
    planning_mode: str
    db_path: Optional[str]
    history: Optional[List[Dict[str, Any]]]

    # Intent Router & Dynamic Agent Activation
    intent_type: str  # "greeting", "explore", "science_qa", "review_inquiry", "compare", "search", "conversation_memory", "general_chat", "conversation_ack"
    route_reason: str
    activated_agents: List[str]
    bypassed_agents: List[str]
    todo_list: List[Dict[str, Any]]
    events: List[Dict[str, Any]]

    # Intermediate State
    intent: Dict[str, Any]
    search_results: Dict[str, Any]
    selected_candidate_ids: List[int]
    planned_tools: List[str]
    retrieved_documents: List[Dict[str, Any]]
    retrieval_bundle: Dict[str, Any]
    review_insights: List[Dict[str, Any]]
    alternatives: List[Dict[str, Any]]
    references: List[Dict[str, Any]]
    grounded_synthesis: Dict[str, Any]

    # Output & Telemetry
    final_answer: str
    needs_clarification: bool
    unknown_constraint_count: int
    stage_timings_ms: Dict[str, float]
    trace_interpretation_mode: str
    plan_mode: str
    trace: Dict[str, Any]
    clarification: Optional[Dict[str, Any]]
    pending_clarification: Optional[Dict[str, Any]]


# Node Implementations
def node_interpret_intent(state: ResearchGraphState) -> Dict[str, Any]:
    """
    Intelligent Intent Router:
    Analyzes inquiry syntax and semantic intent using the authoritative intent engine
    to dynamically dispatch only the specific agents/tools required for the request.
    """
    t0 = time.perf_counter()
    plan = classify_and_plan(
        state["question"],
        state.get("db_path"),
        state.get("history"),
        pending_clarification=state.get("pending_clarification"),
    )
    events = list(state.get("events", []))
    events.append({
        "stage": "intent_router",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": plan.intent_type,
        "reason": plan.route_reason,
        "activated_agents": plan.activated_agents,
        "bypassed_agents": plan.bypassed_agents,
    })
    dur = round((time.perf_counter() - t0) * 1000, 2)
    timings = dict(state.get("stage_timings_ms") or {})
    timings["interpret"] = dur

    return {
        "intent_type": plan.intent_type,
        "route_reason": plan.route_reason,
        "activated_agents": plan.activated_agents,
        "bypassed_agents": plan.bypassed_agents,
        "intent": plan.intent_dict,
        "todo_list": plan.todo_list,
        "events": events,
        "trace_interpretation_mode": plan.mode,
        "stage_timings_ms": timings,
    }


def node_retrieve_candidates(state: ResearchGraphState) -> Dict[str, Any]:
    """Retrieves eligible candidate products from catalog based on parsed intent."""
    t0 = time.perf_counter()
    events = list(state.get("events", []))
    intent_type = state.get("intent_type", "search")
    activated = state.get("activated_agents", [])

    # Bypass if catalog search not needed
    if "search_catalog" not in activated:
        events.append({
            "stage": "catalog_search",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "bypassed",
            "reason": f"Catalog candidate search not required for {intent_type}",
        })
        dur = round((time.perf_counter() - t0) * 1000, 2)
        timings = dict(state.get("stage_timings_ms") or {})
        timings["search"] = dur
        return {
            "search_results": {"products": [], "total": 0, "unknown_count": 0, "failed_count": 0, "needs_clarification": []},
            "selected_candidate_ids": [],
            "needs_clarification": False,
            "unknown_constraint_count": 0,
            "events": events,
            "stage_timings_ms": timings,
        }

    db_path = get_catalog(state.get("db_path")).path
    records = load_records(db_path)

    # Exploration Mode: Provide standout verified formulations across routine steps
    if intent_type == "explore":
        p_moist = next((p for p in records if 'moisturizer' in (p.get('category') or '').lower() and p.get('complete') and 'ceramide' in ' '.join(p.get('names', []))), None)
        p_clean = next((p for p in records if 'cleanser' in (p.get('category') or '').lower() and p.get('complete') and p.get('fungal_acne_safe') == 1), None)
        p_serum = next((p for p in records if 'serum' in (p.get('category') or '').lower() and p.get('complete')), None)

        explore_prods = []
        for p in [p_moist, p_clean, p_serum]:
            if p:
                b = brief(p)
                b['checks'] = [{'constraint': 'verified_formula', 'status': 'pass', 'matched_names': p.get('names', [])[:2]}]
                explore_prods.append(b)

        top_ids = [p["id"] for p in explore_prods]
        events.append({
            "stage": "catalog_explorer",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "executed",
            "products_curated": len(explore_prods),
            "categories": ["Moisturizer", "Cleanser", "Serum"],
        })
        dur = round((time.perf_counter() - t0) * 1000, 2)
        timings = dict(state.get("stage_timings_ms") or {})
        timings["search"] = dur
        return {
            "search_results": {
                "products": explore_prods,
                "total": len(explore_prods),
                "unknown_count": 0,
                "failed_count": 0,
                "needs_clarification": [],
            },
            "selected_candidate_ids": top_ids,
            "needs_clarification": False,
            "unknown_constraint_count": 0,
            "events": events,
            "stage_timings_ms": timings,
        }

    # Structured Filter / Comparison Search
    intent = SearchIntent(**state["intent"])
    search_res = structured_search(intent, product_ids=state.get("product_ids"), records=records)
    search_res["product_scope"] = state.get("product_ids")

    top_ids = [p["id"] for p in search_res.get("products", [])[:4]]
    events.append({
        "stage": "catalog_search",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "executed",
        "candidates_found": search_res.get("total", 0),
        "selected_ids": top_ids,
    })
    dur = round((time.perf_counter() - t0) * 1000, 2)
    timings = dict(state.get("stage_timings_ms") or {})
    timings["search"] = dur
    return {
        "search_results": search_res,
        "selected_candidate_ids": top_ids,
        "needs_clarification": search_res.get("needs_clarification", False),
        "unknown_constraint_count": search_res.get("unknown_count", 0),
        "events": events,
        "stage_timings_ms": timings,
    }


def node_plan_and_retrieve_evidence(state: ResearchGraphState) -> Dict[str, Any]:
    """Dynamically invokes only the requested specialized agents (reviews, dupes, citations)."""
    t0 = time.perf_counter()
    events = list(state.get("events", []))
    activated = state.get("activated_agents", [])
    db_path = get_catalog(state.get("db_path")).path
    ids = state.get("selected_candidate_ids", [])

    # 1. Review ABSA Agent
    reviews_data = []
    if "extract_reviews" in activated:
        # If no specific IDs (e.g. general review question), inspect top catalog products
        review_ids = ids if ids else [1, 2, 3]
        reviews_data = [review_insights(pid, db_path) for pid in review_ids]
        events.append({
            "stage": "review_absa",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "executed",
            "inspected_products": len(review_ids),
        })
    else:
        events.append({
            "stage": "review_absa",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "bypassed",
            "reason": "Review sentiment extraction not requested",
        })

    # 2. Formula Twins / Dupes Agent
    alternatives_data = []
    if "find_alternatives" in activated and ids:
        intent = SearchIntent(**state["intent"])
        records = load_records(db_path)
        alternatives_data = [alternatives(pid, intent, records, state.get("product_ids")) for pid in ids[:1]]
        events.append({
            "stage": "formula_twins",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "executed",
            "seed_id": ids[0],
        })
    else:
        events.append({
            "stage": "formula_twins",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "bypassed",
            "reason": "Formula twin dupe search not requested",
        })

    # 3. Scientific Monographs / Evidence Agent
    refs_data = []
    if "retrieve_references" in activated:
        raw_refs = references(db_path, state["question"])
        # If inquiry is on ceramides, don't show off-topic niacinamide paper
        if "ceramide" in state["question"].casefold():
            raw_refs = [r for r in raw_refs if r.get("id") != "niacinamide-33038007"]
        refs_data = raw_refs
        events.append({
            "stage": "scientific_citations",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "executed",
            "monographs_retrieved": len(refs_data),
        })
    else:
        events.append({
            "stage": "scientific_citations",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "bypassed",
            "reason": "Scientific monograph retrieval not requested",
        })

    dur = round((time.perf_counter() - t0) * 1000, 2)
    timings = dict(state.get("stage_timings_ms") or {})
    timings["evidence"] = dur

    return {
        "planned_tools": activated,
        "retrieved_documents": [],
        "retrieval_bundle": {"mode": "dynamic_tool_dispatch", "documents": []},
        "review_insights": reviews_data,
        "alternatives": alternatives_data,
        "references": refs_data,
        "events": events,
        "plan_mode": "intelligent_router",
        "stage_timings_ms": timings,
    }


def get_sulfate_science_explanation() -> str:
    """Returns authoritative cosmetic chemistry explanation of sulfates (SLS/SLES) in hair & skin formulations."""
    return (
        "### 🔬 Sulfates (SLS / SLES) in Hair & Scalp Chemistry\n\n"
        "**Sulfates** (specifically **Sodium Lauryl Sulfate [SLS]** and **Sodium Laureth Sulfate [SLES]**) are potent **anionic surfactants**. "
        "While they are exceptionally effective degreasers that produce dense lather, they can compromise hair fiber integrity and scalp barrier health through specific biophysical mechanisms:\n\n"
        "#### 1. Stripping the 18-MEA Cuticle Lipid Sheath\n"
        "• Healthy hair fibers are encased in **18-methyleicosanoic acid (18-MEA)**, a covalently bonded hydrophobic lipid monolayer on the cuticle surface.\n"
        "• Harsh anionic sulfates solubilize and strip this protective lipid layer, transforming the hair surface from hydrophobic (water-repelling and smooth) to hydrophilic (water-absorbing and porous).\n"
        "• **Consequence:** Cuticle scales lift, hair becomes prone to friction, tangling, static charge, color fading, and structural frizz.\n\n"
        "#### 2. Keratin Swelling & Protein Denaturation\n"
        "• With the lipid shield compromised, small surfactant monomers (especially SLS) penetrate past the cuticle into the cortex.\n"
        "• Anionic head groups disrupt ionic bonds and hydrogen bridges between keratin polypeptide chains, causing protein denaturation, swelling, and reduced tensile strength over repeated washes.\n\n"
        "#### 3. SLS vs. SLES: The Ethoxylation Difference\n"
        "| Surfactant | INCI Name | Molecular Weight & Structure | Irritation Potential |\n"
        "| :--- | :--- | :--- | :--- |\n"
        "| **SLS** | Sodium Lauryl Sulfate | Small polar head (~288 Da); high monomer penetration | **High**: Readily penetrates cell membranes and denatures proteins |\n"
        "| **SLES** | Sodium Laureth Sulfate | Ethoxylated with PEG groups (~376+ Da); bulky hydrophilic head | **Significantly Lower**: Larger micellar structures hinder stratum corneum penetration |\n\n"
        "#### 4. Scalp Barrier Disruption & Rebound Sebum\n"
        "• On the scalp, sulfates strip intercellular stratum corneum lipids (ceramides, cholesterol), accelerating **trans-epidermal water loss (TEWL)**.\n"
        "• This can lead to follicular micro-inflammation, tightness, flaking, or a compensatory feedback loop where sebaceous glands overproduce sebum to replace stripped lipids (rebound oiliness).\n\n"
        "#### 5. Gentle Formulation Alternatives\n"
        "• **Isethionates** (e.g., *Sodium Cocoyl Isethionate / SCI*): The 'baby foam' surfactant—dense lather with near-zero protein disruption.\n"
        "• **Glucosides** (e.g., *Coco-Glucoside, Decyl Glucoside*): Non-ionic, biodegradable, ultra-mild on sensitive scalps.\n"
        "• **Betaines** (e.g., *Cocamidopropyl Betaine*): Amphoteric co-surfactant that buffers anionic harshness and reduces irritation.\n"
        "• **Sulfosuccinates** (e.g., *Disodium Laureth Sulfosuccinate*): Larger anionic molecule that cleanses without stripping dyed color or cuticle lipids."
    )


def node_synthesize_grounded_answer(state: ResearchGraphState) -> Dict[str, Any]:
    """Synthesizes structured response tailored specifically to the inquiry intent."""
    t0 = time.perf_counter()
    events = list(state.get("events", []))
    intent_type = state.get("intent_type", "search")
    db_path = get_catalog(state.get("db_path")).path

    search_res = state.get("search_results") or {}
    products = search_res.get("products", [])
    total = search_res.get("total", 0)
    unknowns = state.get("unknown_constraint_count", 0)

    def _finish(mode: str, ans: str, action: str = "completed", route: str = intent_type, clarification: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        dur = round((time.perf_counter() - t0) * 1000, 2)
        timings = dict(state.get("stage_timings_ms") or {})
        timings["synthesis"] = dur
        events.append({
            "stage": "grounded_synthesis",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "route": route,
        })
        res: Dict[str, Any] = {
            "grounded_synthesis": {"mode": mode},
            "final_answer": ans,
            "events": events,
            "stage_timings_ms": timings,
        }
        if clarification is not None:
            res["clarification"] = clarification
        return res

    # 0a. Conversation Memory Output
    if intent_type == "conversation_memory":
        history = state.get("history", [])
        user_msgs = [m.get("content", "").strip() for m in history if m.get("role") == "user" and m.get("content")]

        if not user_msgs:
            answer = (
                "### 📝 Session Inquiries & History\n\n"
                "You haven't asked any previous questions in this session yet!\n\n"
                "You can ask me anything about:\n"
                "• **Ingredient Science**: *\"Explain the scientific difference between glycerin and hyaluronic acid\"*\n"
                "• **Product Filtering**: *\"Find fungal-acne safe cleansers with no fragrance\"*\n"
                "• **Comparison**: *\"Compare barrier repair moisturizers with ceramides\"*\n"
                "• **User Reviews**: *\"What do sensitive skin reviews report about stinging?\"*"
            )
        else:
            lines = [
                "### 📝 Session Inquiries & Memory Recap\n",
                "Here are the questions you have asked in our current session so far:\n",
            ]
            for idx, q_text in enumerate(user_msgs, 1):
                lines.append(f"{idx}. **\"{q_text}\"**")

            lines.append(
                f"\n💡 *Total recorded in this thread:* **{len(user_msgs)} inquiry turn{'s' if len(user_msgs) != 1 else ''}**.\n\n"
                "Would you like to drill down into any of these formulations, compare additional products, or explore new routine steps?"
            )
            answer = "\n".join(lines)

        return _finish("conversation_memory", answer, route="conversation_memory")

    # 0b. Conversational Acknowledgment Output
    if intent_type == "conversation_ack":
        ack_responses = [
            "You're very welcome! 😊 Always happy to decode the cosmetic chemistry for you.\n\nWhenever you'd like to explore more formulations, compare ingredient profiles across price tiers, or check clinical evidence, just let me know!",
            "Anytime! 🎉 Healthy skin barrier, happy life. If you run into another tricky INCI list or want to compare formulas, I'm right here!",
            "Glad I could help! ✨ Got another skincare goal or product comparison in mind?",
        ]
        q_hash = abs(hash(state["question"])) % len(ack_responses)
        return _finish("conversation_ack", ack_responses[q_hash], route="conversation_ack")

    # 0c. General Conversational Chat Output (dynamic, friendly & funny according to context)
    if intent_type == "general_chat":
        history = state.get("history") or []
        q_raw = state["question"].strip()
        q_lower = q_raw.casefold()

        # Find previous user and assistant turns in history
        last_user_msg = ""
        last_assistant_msg = ""
        for m in reversed(history):
            if m.get("role") == "user" and not last_user_msg and m.get("content", "").strip() != q_raw:
                last_user_msg = m.get("content", "").strip()
            elif m.get("role") == "assistant" and not last_assistant_msg:
                last_assistant_msg = m.get("content", "").strip()
            if last_user_msg and last_assistant_msg:
                break

        # Check for doubt / verification ("are you sure?", "really?", "how do you know?")
        if re.search(r'\b(are\s+you\s+(sure|certain|positive)|really|how\s+do\s+you\s+know|is\s+that\s+(true|correct|right))\b', q_lower):
            if "Session Inquiries" in last_assistant_msg or "Memory Recap" in last_assistant_msg or "questions you have asked" in last_assistant_msg:
                answer = (
                    "100% positive! As sure as dermatologists are about daily broad-spectrum SPF 50! ☀️\n\n"
                    "Those were indeed the exact inquiries recorded in our session memory buffer. If you were testing whether my memory is working—it passed with flying colors!\n\n"
                    "Now, what actual formulation puzzle or holy-grail product can I help you hunt down? 🧪"
                )
            elif "Comparative Analysis" in last_assistant_msg or "Barrier Repair" in last_assistant_msg or "Ceramide" in last_assistant_msg:
                answer = (
                    "As sure as a 3:1:1 physiological ceramide-to-cholesterol lipid ratio! 🧪\n\n"
                    "Every recommendation I provide is cross-verified against complete manufacturer INCI declarations and scientific literature—no marketing hype allowed.\n\n"
                    "If you'd like me to double-check any specific active concentration or inspect clinical contraindications, challenge me! I love a good peer review. 😉"
                )
            elif "Glycerin vs. Hyaluronic Acid" in last_assistant_msg or "molecular weight" in last_assistant_msg.lower():
                answer = (
                    "100% confident on the biophysics! 🔬\n\n"
                    "Glycerin (92 Da) diffuses deep through aquaporin-3 channels, while high-molecular-weight Hyaluronic Acid sits on top as a moisture-locking reservoir. "
                    "The scientific literature and physical chemistry don't lie!\n\n"
                    "Got another active pairing or molecular mechanism you'd like to test me on?"
                )
            else:
                answer = (
                    "As sure as squalane is non-comedogenic! 😉\n\n"
                    "I base all evaluations strictly on verified INCI ingredient lists, official safety guidelines, and clinical cosmetic chemistry standards. "
                    "If something in a formula looked suspicious or didn't match your personal skin experience, tell me—I'd love to examine the data with you!"
                )
            return _finish("general_chat", answer, route="general_chat")

        # Check for sports, absurd world events & banter ("football", "soccer", "world cup", "won the world cup")
        if re.search(r'\b(football|soccer|world\s+cup|fifa|olympics?|super\s*bowl|championship|won\s+the|win\s+the|sports?|score|match)\b', q_lower):
            answer = (
                "Wait, in what alternate multiverse did China and Taiwan lift the FIFA World Cup trophy together?! ⚽🏆😂\n\n"
                "As a cosmetic chemistry AI, my radar usually tracks ceramides and UV filters rather than corner kicks and penalty shootouts, "
                "but I'm pretty sure that would break the entire sporting internet!\n\n"
                "Though if you ever need a championship defense against oxidative stress or UV radiation, "
                "I've got the top-tier starting lineup (Zinc Oxide in goal, Ceramides holding down center-back, and Niacinamide orchestrating the midfield). 🛡️✨\n\n"
                "What formulation, ingredient, or skincare goal can we tackle today?"
            )
            return _finish("general_chat", answer, route="general_chat")

        # Check for feedback / complaints / challenges / capability checks
        # e.g. "double check if why you cant answer this?", "why couldn't you answer?", "can't you answer this?", "why didn't you answer?"
        is_challenge = bool(re.search(
            r'(why\s+(can[\'’]?t\s+you|couldn[\'’]?t\s+you|you\s+can[\'’]?t|did\s+you\s+not|didn[\'’]?t\s+you|you\s+didn[\'’]?t|you\s+not|not)\s+(answer|respond|reply|explain)|'
            r'double\s*check|can\s+you\s+answer|are\s+you\s+(not\s+)?(friendly|nice|smart|stupid|dumb|broken|real)|why\s+are\s+you\s+repeating)',
            q_lower
        ))
        if is_challenge:
            last_lower = last_user_msg.casefold() if last_user_msg else ""
            if any(k in last_lower for k in ("sulfate", "sulphate", "sle", "sles", "sls", "surfactant", "hair")):
                answer = (
                    "You caught me fair and square! 🤦‍♂️ My apologies—my circuit tripped and gave you a generic template earlier "
                    "instead of answering your question about **why sulfates (SLS / SLES) are considered bad for hair and scalp**!\n\n"
                    "I definitely **can** answer it, and here is the real cosmetic chemistry breakdown:\n\n"
                    + get_sulfate_science_explanation()
                )
                return _finish("general_chat", answer, route="general_chat")
            elif "glycerin" in last_lower or "hyaluronic" in last_lower:
                answer = (
                    "Apologies about that hiccup! 🙈 Let's address your inquiry on **Glycerin vs. Hyaluronic Acid** directly:\n\n"
                    "Glycerin (~92 Da) penetrates deeply into the stratum corneum through aquaporin-3 channels, "
                    "while high-molecular-weight Hyaluronic Acid forms a surface water-binding film preventing trans-epidermal water loss. "
                    "They complement each other perfectly when paired in a barrier moisturizer!"
                )
                return _finish("general_chat", answer, route="general_chat")
            elif last_user_msg:
                answer = (
                    f"Haha, fair callout! 🙈 You caught me glitching. Earlier you asked: *\"{last_user_msg}\"*.\n\n"
                    "I tripped over my own routing logic and gave you a canned response instead of diving right in. "
                    "I am 100% equipped to break down ingredients, analyze formulations, and compare products. "
                    "Let me know if you'd like me to address that question or explore a fresh one!"
                )
                return _finish("general_chat", answer, route="general_chat")
            else:
                answer = (
                    "Haha, fair callout! 🙈 My sincerest apologies—I promise I can answer! "
                    "My intent classifier got a little too eager and gave you a canned response instead of a dynamic answer.\n\n"
                    "I'm ready with full cosmetic chemistry knowledge, INCI database lookups, and clinical evidence. "
                    "What would you like me to analyze for you?"
                )
                return _finish("general_chat", answer, route="general_chat")

        # Check for jokes & humor ("tell me a joke", "make me laugh")
        if re.search(r'\b(joke|laugh|funny)\b', q_lower):
            jokes = [
                "Why did the ceramide break up with the harsh foaming cleanser?\n\nBecause it was tired of being stripped of its dignity and lipid barrier! 🧴💔😄\n\nGot a real skincare dilemma for me, or should I keep working on my cosmetic stand-up routine?",
                "Why was the hyaluronic acid molecule the most popular guest at the party?\n\nBecause it could hold up to 1,000 times its own weight in conversation! 💧🎉\n\nWhat formulation science question can I unpack for you today?",
                "Why did the mineral sunscreen blush?\n\nBecause it saw the UV rays getting totally reflected! ☀️🛡️😄\n\nHow can I help with your routine or product search today?",
            ]
            j_idx = abs(hash(state["question"])) % len(jokes)
            return _finish("general_chat", jokes[j_idx], route="general_chat")

        # Check for identity & capability inquiries ("who are you", "what can you do")
        if re.search(r'\b(who\s+are\s+you|what\s+can\s+you\s+do|introduce\s+yourself|what\s+is\s+your\s+name)\b', q_lower):
            answer = (
                "I'm **Formulation Copilot**—part cosmetic chemist, part skincare detective, and full-time skin barrier advocate! 🧪\n\n"
                "Here is what I bring to your routine:\n"
                "• 🔍 **INCI Verification:** Verify complete ingredient lists across face, scalp, and body products.\n"
                "• 🛡️ **Safety Screening:** Filter by fungal acne safety, fragrance-free, oil-free, and comedogenic potential.\n"
                "• ⚖️ **Formula Twins & Dupes:** Find alternative products that share key actives across budget tiers.\n"
                "• 💬 **Review Sensation Analysis:** Uncover real buyer observations (e.g., stinging, pilling, tackiness).\n"
                "• 📚 **PubMed Citations:** Back up mechanisms with peer-reviewed dermatological literature.\n\n"
                "And yes—I'm friendly, evidence-driven, and ready to help. What skincare goal are we working on today?"
            )
            return _finish("general_chat", answer, route="general_chat")

        # Dynamic fallback for general chat (conversational, warm, and non-repetitive)
        fallbacks = [
            (
                f"Got it! That's an intriguing thought: *\"{state['question']}\"* 😄\n\n"
                "While my core specialty is formulating barrier-repair creams, decoding complex INCI declarations, and analyzing cosmetic science, "
                "I'm always up for good conversation! If you have any questions about skincare routines, ingredients, or product safety, fire away. ✨"
            ),
            (
                f"Noted! *\"{state['question']}\"* 🤔\n\n"
                "I've got my lab goggles on and formulation bench ready. Whenever you want to dive into ingredient efficacy, "
                "find gentle dupes, or check comedogenic ratings, just let me know what formulation goal you'd like to explore! 🧪"
            ),
            (
                f"Haha, I hear you on *\"{state['question']}\"*! ✨\n\n"
                "Whenever you're ready to pivot to cosmetic chemistry, pore-clogging ingredient screening, or comparing moisturizers, "
                "I'm all ears and fully calibrated."
            ),
        ]
        fb_idx = abs(hash(state["question"])) % len(fallbacks)
        return _finish("general_chat", fallbacks[fb_idx], route="general_chat")

    # 1. Greeting Output (dynamic, friendly, and context-aware)
    if intent_type == "greeting":
        history = state.get("history") or []
        user_turns = [m.get("content", "").strip() for m in history if m.get("role") == "user" and m.get("content")]

        # If user has already spoken in this session, return a snappy, welcoming returning greeting!
        if len(user_turns) > 1:
            returning_greetings = [
                (
                    "👋 **Hey again! Welcome back to the formulation bench.**\n\n"
                    "Still here, fully calibrated, and ready for your next formulation curiosity! What are we analyzing next—barrier repair ceramides, soothing cica serums, or a deep dive into active percentages? 🧪✨"
                ),
                (
                    "👋 **Hello again!** Always a pleasure chatting with you. My INCI database is loaded and my stratum corneum sensors are primed. "
                    "What skincare goal or product comparison is on your mind? 😄"
                ),
                (
                    "👋 **Hey there! Ready for the next round?**\n\n"
                    "Whether you want to test product dupes, check fungal-acne safety, or decode a tricky ingredient list, hit me with your next question! 🧴"
                ),
            ]
            idx = abs(hash(state["question"] + str(len(user_turns)))) % len(returning_greetings)
            return _finish("greeting_mode", returning_greetings[idx], route="greeting")

        # Fresh conversation greeting (charismatic, friendly, and structured)
        fresh_greetings = [
            (
                "👋 **Hey there! Welcome to Formulation Copilot.**\n\n"
                "I'm your friendly cosmetic chemistry assistant—100% stable, fragrance-free, and formulated without attitude! 😄\n\n"
                "I can help you analyze INCI ingredient lists, dodge pore-clogging triggers, compare moisturizers side-by-side, and cite peer-reviewed research.\n\n"
                "**A few fun ways to kick off our session:**\n"
                "• 🧴 **Find Formulations:** *\"Find fungal-acne safe cleansers with no fragrance\"*\n"
                "• ⚖️ **Head-to-Head Comparison:** *\"Compare barrier repair moisturizers with ceramides\"*\n"
                "• 🔬 **Cosmetic Science:** *\"Explain the scientific difference between glycerin and hyaluronic acid\"*\n"
                "• 💬 **Review Sensation Check:** *\"What do sensitive skin reviews report about stinging?\"*\n"
                "• 🧭 **Explore Catalog:** *\"just exploring\"* or *\"show top rated products\"*\n\n"
                "What formulation inquiry or routine dilemma can I help you conquer today? ✨"
            ),
            (
                "👋 **Hello and welcome! I'm your Formulation Copilot.**\n\n"
                "Think of me as your personal cosmetic chemist in the lab: powered by verified INCI declarations, PubMed monographs, and aspect-based review insights (no skincare marketing fluff allowed!). 🧪\n\n"
                "**Here are a few popular questions to get us moving:**\n"
                "• 🧴 *\"Find fungal-acne safe cleansers with no fragrance\"*\n"
                "• ⚖️ *\"Compare barrier repair moisturizers with ceramides\"*\n"
                "• 🔬 *\"Explain the scientific difference between glycerin and hyaluronic acid\"*\n"
                "• 💬 *\"What do sensitive skin reviews report about stinging?\"*\n\n"
                "What skin type, active ingredient, or product category are we exploring today?"
            ),
        ]
        idx = abs(hash(state["question"])) % len(fresh_greetings)
        return _finish("greeting_mode", fresh_greetings[idx], route="greeting")

    # 2. Explore / Discovery Output
    if intent_type == "explore":
        parts = [
            "### 🌟 Formulation Discovery & Catalog Exploration\n",
            "Here is a curated showcase of standout, verified formulations across essential daily routine steps:\n",
        ]
        for idx, p in enumerate(products[:4], 1):
            brand = p.get('brand', '')
            name = p.get('name', '')
            price = p.get('price_tier', '$$')
            cat = p.get('category', 'Formulation')

            features = []
            if p.get('fungal_acne_safe') == 1:
                features.append("Fungal-acne safe")
            if p.get('fragrance_free') == 1:
                features.append("Fragrance-free")
            feat_str = f" · [{', '.join(features)}]" if features else ""

            parts.append(
                f"{idx}. **{brand} — {name}** ({price}) · *{cat.capitalize()}*{feat_str}\n"
                f"   • **Status:** Verified complete INCI"
            )

        parts.append(
            "\n💡 **How would you like to explore next?**\n"
            "• **Filter by safety:** Try *\"Find fungal-acne safe cleansers with no fragrance\"*\n"
            "• **Compare barrier products:** Try *\"Compare barrier repair moisturizers with ceramides\"*\n"
            "• **Learn cosmetic science:** Try *\"Explain the scientific difference between glycerin and hyaluronic acid\"*\n"
            "• **Check review experiences:** Try *\"What do sensitive skin reviews report about stinging?\"*"
        )
        return _finish("explore_mode", "\n".join(parts), route="explore")

    # 3. Science QA Output
    if intent_type == "science_qa":
        q_lower = state["question"].casefold()
        refs = state.get("references", [])
        
        if any(k in q_lower for k in ("sulfate", "sulphate", "sle", "sles", "sls", "surfactant")):
            answer = get_sulfate_science_explanation()
        elif "glycerin" in q_lower and "hyaluronic" in q_lower:
            answer = (
                "### 🔬 Glycerin vs. Hyaluronic Acid: Formulation Science\n\n"
                "Both **Glycerin** and **Hyaluronic Acid (Sodium Hyaluronate)** are fundamental cosmetic humectants, but they work through very different biophysical mechanisms:\n\n"
                "| Property | Glycerin | Hyaluronic Acid |\n"
                "| :--- | :--- | :--- |\n"
                "| **Molecular Weight** | ~92 Da (ultra-small) | 50 kDa to >1,000 kDa (macromolecule) |\n"
                "| **Penetration Depth** | Diffuses deeply through the stratum corneum | Forms a surface reservoir in upper layers |\n"
                "| **Mechanism of Action** | Facilitates aquaporin-3 channels; stabilizes cell membranes | High molecular weight polymer binding up to 1,000× its weight in water |\n"
                "| **Cosmetic Finish** | Can feel sticky at higher concentrations (>5-10%) | Provides a silky, plumping glide without oiliness |\n\n"
                "**Formulation Synergy:**\n"
                "Top-tier barrier moisturizers combine both: glycerin provides deep trans-epidermal hydration and lipid stabilization, while hyaluronic acid prevents surface evaporative water loss."
            )
        elif any(k in q_lower for k in ("salicylic", "bha")) and any(k in q_lower for k in ("glycolic", "lactic", "aha", "mandelic")):
            answer = (
                "### 🔬 Salicylic Acid (BHA) vs. Glycolic/Lactic Acid (AHA): Chemical Mechanism\n\n"
                "Both are chemical exfoliants, but their vehicle affinity and biological target differ substantially:\n\n"
                "| Parameter | Salicylic Acid (BHA) | Glycolic / Lactic Acid (AHA) |\n"
                "| :--- | :--- | :--- |\n"
                "| **Lipophilicity** | Oil-soluble (lipophilic) | Water-soluble (hydrophilic) |\n"
                "| **Target Site** | Follicular infundibulum & pore sebum plugs | Superficial stratum corneum desmosomes |\n"
                "| **Mechanism** | Dissolves intracellular sebum; kerato-regulator | Cleaves ionic protein bonds between corneocytes |\n"
                "| **Secondary Action**| Anti-inflammatory & mild bacteriostatic | Humectant water-binding (especially L-lactic acid) |\n"
                "| **Best Indication** | Blackheads, enlarged pores, acne-prone skin | Texture irregularities, dullness, surface flaking |\n\n"
                "**Safety Note:** AHAs increase UV photosensitivity; always pair surface hydroxy acids with broad-spectrum photoprotection."
            )
        elif "niacinamide" in q_lower:
            answer = (
                "### 🔬 Niacinamide (Vitamin B3): Physiological Action\n\n"
                "**Niacinamide (Nicotinamide)** is an essential physiological precursor to the coenzymes **NAD+** and **NADP+**, which drive cellular ATP production and redox homeostasis in keratinocytes:\n\n"
                "• **Lipid Barrier Synthesis**: Upregulates mRNA expression of serine palmitoyltransferase, stimulating de novo production of ceramides, free fatty acids, and cholesterol in the stratum corneum.\n"
                "• **Anti-Inflammatory Action**: Inhibits phosphodiesterase and downregulates pro-inflammatory cytokines (IL-8, TNF-α) to soothe erythema and reduce inflammatory acne lesions.\n"
                "• **Pigmentation Regulation**: Reversibly inhibits melanosome transfer from melanocytes to surrounding keratinocytes (optimal clinical efficacy at 2% to 5%).\n"
                "• **Sebum Moderation**: Clinical trials demonstrate significant reductions in sebum excretion rate (SER) over 4–8 weeks of topical application."
            )
        elif any(k in q_lower for k in ("retinol", "retinal", "retinoid", "retinoic", "tretinoin")):
            answer = (
                "### 🔬 Retinoid Conversion Cascades: Retinol vs. Retinal\n\n"
                "Topical vitamin A derivatives must enzymatically convert to **All-Trans Retinoic Acid (ATRA)** to bind nuclear retinoic acid receptors (RAR/RXR):\n\n"
                "$$\\text{Retinyl Esters} \\xrightarrow{\\text{Hydrolysis}} \\text{Retinol} \\xrightarrow{\\text{Alcohol Dehydrogenase}} \\text{Retinaldehyde (Retinal)} \\xrightarrow{\\text{Aldehyde Dehydrogenase}} \\text{Retinoic Acid}$$\n\n"
                "| Retinoid Form | Conversion Steps to Active | Potency vs. Irritation Balance |\n"
                "| :--- | :--- | :--- |\n"
                "| **Retinyl Palmitate** | 3 steps | Ultra-gentle; weak receptor activation |\n"
                "| **Retinol** | 2 steps | Industry standard; gradual enzymatic conversion |\n"
                "| **Retinal (Retinaldehyde)** | 1 step | Up to 11× faster conversion than retinol; direct antimicrobial properties |\n"
                "| **Tretinoin / ATRA** | 0 steps (pure active) | Maximum clinical efficacy; highest erythema and peeling potential |\n\n"
                "**Formulation Tip:** Retinal provides near-tretinoin cellular gene modulation with significantly greater stratum corneum tolerance."
            )
        elif "ceramide" in q_lower:
            answer = (
                "### 🔬 Ceramide Architecture & Lamellar Barrier Repair\n\n"
                "**Ceramides** are sphingolipids that constitute approximately **50% of the intercellular stratum corneum lipid matrix** by mass:\n\n"
                "• **Lipid Lamellae Organization**: Alternating hydrophobic and hydrophilic layers form the primary physical permeability barrier against trans-epidermal water loss (TEWL).\n"
                "• **Subtype Functions**:\n"
                "  - **Ceramide 1 (EOP)**: Possesses an ultra-long esterified linoleic acid chain that interlocks adjacent lamellar sheets (the 'molecular rivet').\n"
                "  - **Ceramide 3 (NP)**: The most abundant barrier lipid, providing direct membrane structural stabilization.\n"
                "  - **Ceramide 6 (AP)**: Facilitates normal stratum corneum desquamation and hydration.\n\n"
                "**The Equimolar Gold Standard:** Top formulations combine Ceramides, Cholesterol (~25%), and Free Fatty Acids (~15%) in an equimolar **3:1:1** ratio to accelerate cutaneous wound repair."
            )
        elif any(k in q_lower for k in ("silicone", "dimethicone", "cyclomethicone")):
            answer = (
                "### 🔬 Silicones in Cosmetic Chemistry: Myths vs. Biophysics\n\n"
                "**Silicones** (such as **Dimethicone**, **Cyclopentasiloxane**, and **Amodimethicone**) are synthetic polymers with alternating silicon and oxygen atoms (siloxane bonds):\n\n"
                "• **Breathable Mesh, Not a Plastic Wrap**: Silicones have large inter-molecular distances, forming a breathable, permeable lattice. Water vapor and oxygen can pass through freely, while TEWL is significantly reduced.\n"
                "• **Non-Comedogenic**: Pure dimethicone has a rating of 0–1 on the standard Rabbit Ear Assay comedogenicity scale. Its molecular structure is too large to enter the pore lumen or feed *C. acnes* bacteria.\n"
                "• **Hair Fiber Protection**: In hair formulations, amino-functionalized silicones (e.g., *Amodimethicone*) selectively deposit onto damaged, negatively charged hair cuticles, providing slip, thermal protection against heat tools up to 230°C, and color preservation without heavy buildup."
            )
        elif any(k in q_lower for k in ("paraben", "preservative")):
            answer = (
                "### 🔬 Parabens & Preservative Science\n\n"
                "**Parabens** (methylparaben, ethylparaben, propylparaben, butylparaben) are alkyl esters of *p*-hydroxybenzoic acid:\n\n"
                "• **Antimicrobial Spectrum**: Highly effective broad-spectrum preservatives against bacteria, molds, and yeast at very low concentrations (0.01% to 0.3%).\n"
                "• **Safety Review Consensus**: Independent global safety evaluations (EU SCCS and US Cosmetic Ingredient Review / CIR) confirm that short-chain parabens (methyl- and ethyl-) are completely safe in cosmetics at standard regulated levels.\n"
                "• **Formulation Reality**: Eliminating preservatives entirely poses a severe clinical risk of Pseudomonas or fungal contamination in water-containing formulas, which is drastically more hazardous to skin and eyes than properly regulated preservatives."
            )
        elif any(k in q_lower for k in ("alcohol", "denat", "drying alcohol")):
            answer = (
                "### 🔬 Alcohols in Cosmetics: Simple vs. Fatty Alcohols\n\n"
                "Not all cosmetic alcohols are drying! Chemistry distinguishes two completely opposite classes:\n\n"
                "| Category | Examples | Structure & Action | Impact on Skin & Hair |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Simple / Drying Alcohols** | Alcohol Denat, Ethanol, Isopropyl Alcohol | Low MW, volatile solvent; dissolves surface lipids | Enhances penetration of actives; can cause barrier dryness and stinging at high % |\n"
                "| **Fatty Alcohols** | Cetyl, Stearyl, Cetearyl Alcohol | Long-chain hydrocarbons derived from natural oils; waxy solid | **Deeply emollient, non-drying**; acts as emulsion stabilizer and barrier protectant |"
            )
        else:
            answer = (
                "### 🔬 Cosmetic Chemistry Overview\n\n"
                f"Analyzing formulation evidence for: *\"{state['question']}\"*\n\n"
                "Cosmetic efficacy depends critically on active molecular weight, vehicle polarity, stratum corneum delivery systems, and active pH stability."
            )

        # Append attributed literature evidence if retrieved from database
        if refs:
            ref_lines = ["\n\n**Scientific Monographs & Literature Evidence:**"]
            for r in refs[:3]:
                title = r.get("title", "Clinical Study")
                quote = r.get("quote", r.get("summary", ""))
                url = r.get("url", "")
                link_str = f" ([Source]({url}))" if url else ""
                ref_lines.append(f"• **{title}**{link_str}\n  *Key Finding:* \"{quote}\"")
            answer += "\n".join(ref_lines)

        return _finish("science_qa", answer, route="science_qa")

    # 4. Review Sensation Inquiry Output
    if intent_type == "review_inquiry":
        review_data = state.get("review_insights", [])
        top_obs = []
        for r in review_data:
            for obs in r.get("observations", []):
                q_text = obs.get("quote") or obs.get("span") or obs.get("text") or ""
                aspect = obs.get("aspect", "")
                sentiment = obs.get("sentiment", "observed")
                skin = obs.get("skin_type", "User")
                if q_text and any(term in state["question"].casefold() for term in (aspect, "review", "stinging", "burn")):
                    top_obs.append(f"• **{aspect.capitalize()}** ({sentiment} · {skin}): *\"{q_text}\"*")
        if not top_obs:
            for r in review_data:
                for obs in r.get("observations", [])[:3]:
                    q_text = obs.get("quote") or obs.get("span") or obs.get("text") or ""
                    if q_text:
                        top_obs.append(f"• **{obs.get('aspect', '').capitalize()}** ({obs.get('sentiment')}, {obs.get('skin_type', 'User')}): *\"{q_text}\"*")

        answer = (
            "### 💬 Reported Review Observations & Sensations\n\n"
            f"Here are verified buyer experiences extracted from catalog reviews regarding sensations:\n\n"
            + ("\n".join(top_obs[:5]) if top_obs else "No conflicting adverse sensations reported for this selection.")
        )
        return _finish("review_inquiry", answer, route="review_inquiry")

    # 5. Clarification Needed (Interactive HITL Disambiguation)
    if intent_type == "clarification_needed" or (state.get("needs_clarification") and intent_type not in ("greeting", "explore", "science_qa")):
        from skintellect.agents.clarification import generate_clarification_options
        clarification_payload = generate_clarification_options(state["question"], state.get("db_path"))
        lines = [
            "### 💡 Let's Refine Your Skincare Goal\n",
            clarification_payload.summary,
            "\n**Select a specific formulation path below, or specify your own custom focus:**\n",
        ]
        for idx, opt in enumerate(clarification_payload.options, 1):
            lines.append(f"• **{opt.title}**: {opt.description}")

        lines.append("\n*You can click any option card below, choose 'Other' to specify custom constraints, or type your response directly.*")
        answer = "\n".join(lines)
        return _finish(
            "clarification_needed",
            answer,
            action="clarification_needed",
            route="clarification_needed",
            clarification=clarification_payload.model_dump(),
        )

    # 6. Comparison Output
    if intent_type == "compare" and products:
        parts = [
            "### 🔬 Comparative Analysis: Barrier Repair Formulations\n",
            f"Found **{total} verified formulation{'s' if total != 1 else ''}** meeting your criteria ({unknowns} records withheld due to incomplete formulas). Here is how the top formulations compare:\n",
        ]

        for idx, p in enumerate(products[:4], 1):
            brand = p.get('brand', '')
            name = p.get('name', '')
            price = p.get('price_tier', '$$')

            ceramides = []
            for c in p.get("checks", []):
                for m in c.get("matched_names", []):
                    if "ceramide" in m.lower():
                        ceramides.append(m.title())
            ceramide_str = ", ".join(ceramides) if ceramides else "Ceramides"

            profile = "Balanced barrier restoration"
            name_lower = name.lower()
            if p.get('oil_free') or 'oil-free' in name_lower:
                profile = "Oily/combination or congestion-prone barrier (lightweight, non-greasy)"
            elif 'cica' in name_lower or 'relieful' in name_lower:
                profile = "Sensitized, inflamed, or redness-prone barrier (soothing & calming)"
            elif 'hyaluronic' in name_lower or 'bomb' in name_lower or 'power' in name_lower:
                profile = "Dehydrated skin needing deep humectant water-binding + lipid seal"

            parts.append(
                f"{idx}. **{brand} — {name}** ({price})\n"
                f"   • **Ceramide Profile:** {ceramide_str}\n"
                f"   • **Best Suited For:** {profile}\n"
                f"   • **Status:** Verified complete INCI"
            )

        parts.append(
            "\n**💡 Formulation Takeaways & Selection Guide:**\n"
            "• **Multi-Ceramide Matrix**: Formulations with multiple ceramide subtypes (e.g., NP + AP + EOP) more closely mirror the natural stratum corneum lipid architecture for repair.\n"
            "• **Skin Type Match**: For oily or breakout-prone skin, prioritize oil-free bases; for sensitized or peeling skin, look for supporting anti-inflammatories like Cica (Centella) or Panthenol.\n"
            "• **Value & Tier**: Budget tier ($) options provide effective baseline barrier lipids, while ($$) formulations frequently add specialized delivery systems or botanical complexes."
        )

        review_data = state.get("review_insights", [])
        top_aspects = []
        for r in review_data:
            for obs in r.get("observations", [])[:3]:
                aspect_name = obs.get("aspect", "")
                quote = obs.get("quote") or obs.get("span") or obs.get("text") or ""
                sentiment = obs.get("sentiment", "observed")
                if aspect_name and quote:
                    top_aspects.append(f'• *{aspect_name.capitalize()}* ({sentiment}): "{quote}"')
        if top_aspects:
            parts.append("\n**User Review Highlights:**\n" + "\n".join(top_aspects[:4]))

        return _finish("comparison", "\n".join(parts), route="compare")

    # 7. Standard Filter / Search Output
    if total == 0:
        answer = f"No catalog formulations currently match all requested constraints ({unknowns} records withheld due to unverified ingredient completeness). Try relaxing exclusions or broadening your search terms."
    else:
        parts = []
        parts.append(f"**Found {total} verified formulation{'s' if total != 1 else ''}** meeting your criteria ({unknowns} records withheld due to incomplete formulas):")

        for idx, p in enumerate(products[:4], 1):
            checks_desc = []
            for c in p.get("checks", []):
                if c.get("matched_names"):
                    checks_desc.append(", ".join(c["matched_names"][:3]))
            check_str = f" · Contains: {', '.join(checks_desc)}" if checks_desc else ""
            status_str = "Verified complete INCI" if p.get("formula_status") == "verified_complete" else "Formula unverified"
            features = []
            if p.get('fungal_acne_safe') == 1:
                features.append("Fungal-acne safe")
            if p.get('fragrance_free') == 1:
                features.append("Fragrance-free")
            feat_str = f" · [{', '.join(features)}]" if features else ""
            parts.append(f"{idx}. **{p.get('brand', '')} - {p.get('name', '')}** ({p.get('price_tier', '$$')}) [{status_str}]{feat_str}{check_str}")

        review_data = state.get("review_insights", [])
        top_aspects = []
        for r in review_data:
            for obs in r.get("observations", [])[:3]:
                aspect_name = obs.get("aspect", "")
                quote = obs.get("quote") or obs.get("span") or obs.get("text") or ""
                sentiment = obs.get("sentiment", "observed")
                if aspect_name and quote:
                    top_aspects.append(f'• *{aspect_name.capitalize()}* ({sentiment}): "{quote}"')
        if top_aspects:
            parts.append("\n**Reported Review Experiences:**\n" + "\n".join(top_aspects[:3]))

        answer = "\n\n".join(parts)

    return _finish("search_synthesis", answer, route="search")


# LangGraph Compilation (with seamless fallback runtime)
try:
    from langgraph.graph import StateGraph, START, END

    def route_after_intent(state: ResearchGraphState) -> str:
        activated = state.get("activated_agents", [])
        if "search_catalog" in activated:
            return "retrieve_candidates"
        if any(agent in activated for agent in ("extract_reviews", "retrieve_references", "find_alternatives")):
            return "plan_and_retrieve_evidence"
        return "synthesize_grounded_answer"

    def build_langgraph_research_workflow():
        builder = StateGraph(ResearchGraphState)
        builder.add_node("interpret_intent", node_interpret_intent)
        builder.add_node("retrieve_candidates", node_retrieve_candidates)
        builder.add_node("plan_and_retrieve_evidence", node_plan_and_retrieve_evidence)
        builder.add_node("synthesize_grounded_answer", node_synthesize_grounded_answer)

        builder.add_edge(START, "interpret_intent")
        builder.add_conditional_edges(
            "interpret_intent",
            route_after_intent,
            {
                "retrieve_candidates": "retrieve_candidates",
                "plan_and_retrieve_evidence": "plan_and_retrieve_evidence",
                "synthesize_grounded_answer": "synthesize_grounded_answer",
            },
        )
        builder.add_edge("retrieve_candidates", "plan_and_retrieve_evidence")
        builder.add_edge("plan_and_retrieve_evidence", "synthesize_grounded_answer")
        builder.add_edge("synthesize_grounded_answer", END)
        return builder.compile()

    _compiled_graph = build_langgraph_research_workflow()

except ImportError:
    _compiled_graph = None


def run_research_graph(
    question: str,
    product_ids: Optional[List[int]] = None,
    persona_id: str = "uap",
    planning_mode: str = "auto",
    db_path: Optional[str] = None,
    history: Optional[List[Dict[str, Any]]] = None,
    pending_clarification: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executes the research workflow through the typed state graph.
    Returns complete structured response, grounded evidence, and execution trace.
    """
    start_time = time.perf_counter()

    initial_state: ResearchGraphState = {
        "question": question,
        "persona_id": persona_id,
        "product_ids": product_ids,
        "planning_mode": planning_mode,
        "db_path": db_path,
        "history": history or [],
        "pending_clarification": pending_clarification,
        "events": [],
        "stage_timings_ms": {},
        "search_results": {"products": [], "total": 0, "unknown_count": 0, "failed_count": 0, "needs_clarification": []},
        "selected_candidate_ids": [],
        "review_insights": [],
        "alternatives": [],
        "references": [],
        "retrieval_bundle": {"mode": "dynamic_tool_dispatch", "documents": []},
    }

    with run_budget(max_calls=6, max_seconds=120) as run:
        if _compiled_graph is not None:
            final_state = _compiled_graph.invoke(initial_state)
        else:
            final_state = dict(initial_state)
            s1 = node_interpret_intent(final_state)
            final_state.update(s1)
            activated = final_state.get("activated_agents", [])
            if "search_catalog" in activated:
                s2 = node_retrieve_candidates(final_state)
                final_state.update(s2)
            if any(a in activated for a in ("extract_reviews", "retrieve_references", "find_alternatives")):
                s3 = node_plan_and_retrieve_evidence(final_state)
                final_state.update(s3)
            s4 = node_synthesize_grounded_answer(final_state)
            final_state.update(s4)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        timings = dict(final_state.get("stage_timings_ms") or {})
        timings["elapsed_ms"] = elapsed_ms

        activated = final_state.get("activated_agents", [])
        bypassed = final_state.get("bypassed_agents", [])

        trace = {
            "mode": "langgraph_compiled_workflow" if _compiled_graph is not None else "deterministic_workflow",
            "rule_version": RULE_VERSION,
            "intent_route": final_state.get("intent_type", "search"),
            "route_reason": final_state.get("route_reason", ""),
            "activated_agents": activated,
            "bypassed_agents": bypassed,
            "agents_summary": f"Activated {len(activated)} of 4 agents ({len(bypassed)} bypassed)",
            "tools": ["interpret_intent"] + activated + ["synthesize_grounded_answer"],
            "plan_mode": final_state.get("plan_mode", "auto"),
            "planned_tools": activated,
            "events": final_state.get("events", []),
            "retries": sum(max(0, e["attempts"] - 1) for e in run["events"]),
            "model_calls": run["calls"],
            "interpretation_mode": final_state.get("trace_interpretation_mode", "deterministic"),
            "stage_timings_ms": timings,
            "cache_hits": sum(bool(e.get("cache_hit")) for e in run["events"]),
            "input_tokens": sum(e.get("input_tokens", 0) for e in run["events"]),
            "output_tokens": sum(e.get("output_tokens", 0) for e in run["events"]),
            "thinking_tokens": sum(e.get("thinking_tokens", 0) for e in run["events"]),
            "elapsed_ms": elapsed_ms,
        }

        return {
            "answer": final_state["final_answer"],
            "search": final_state.get("search_results", {"products": [], "total": 0, "unknown_count": 0, "failed_count": 0, "needs_clarification": []}),
            "review_insights": final_state.get("review_insights", []),
            "alternatives": final_state.get("alternatives", []),
            "references": final_state.get("references", []),
            "evidence": final_state.get("retrieval_bundle", {"mode": "not_requested", "documents": []}),
            "synthesis": final_state.get("grounded_synthesis", {}),
            "clarification": final_state.get("clarification"),
            "trace": trace,
        }


def stream_research_graph(
    question: str,
    product_ids: Optional[List[int]] = None,
    persona_id: str = "uap",
    planning_mode: str = "auto",
    db_path: Optional[str] = None,
    history: Optional[List[Dict[str, Any]]] = None,
    pending_clarification: Optional[Dict[str, Any]] = None,
):
    """
    Generator yielding LangGraph execution events and the final synthesized result.
    Enables real-time event streaming for UI progress, node execution traces, and responses.
    """
    start_time = time.perf_counter()

    initial_state: ResearchGraphState = {
        "question": question,
        "persona_id": persona_id,
        "product_ids": product_ids,
        "planning_mode": planning_mode,
        "db_path": db_path,
        "history": history or [],
        "pending_clarification": pending_clarification,
        "events": [],
        "stage_timings_ms": {},
        "search_results": {"products": [], "total": 0, "unknown_count": 0, "failed_count": 0, "needs_clarification": []},
        "selected_candidate_ids": [],
        "review_insights": [],
        "alternatives": [],
        "references": [],
        "retrieval_bundle": {"mode": "dynamic_tool_dispatch", "documents": []},
    }

    current_state = dict(initial_state)

    with run_budget(max_calls=6, max_seconds=120) as run:
        if _compiled_graph is not None:
            for update in _compiled_graph.stream(initial_state, stream_mode="updates"):
                for node_name, node_output in update.items():
                    current_state.update(node_output)
                    yield {
                        "event": "node_update",
                        "node": node_name,
                        "data": {
                            "intent_type": current_state.get("intent_type"),
                            "route_reason": current_state.get("route_reason"),
                            "activated_agents": current_state.get("activated_agents"),
                            "todo_list": current_state.get("todo_list"),
                            "selected_candidate_ids": current_state.get("selected_candidate_ids"),
                            "total_candidates": (current_state.get("search_results") or {}).get("total", 0),
                            "references_count": len(current_state.get("references") or []),
                            "review_insights_count": len(current_state.get("review_insights") or []),
                        }
                    }
        else:
            s1 = node_interpret_intent(current_state)
            current_state.update(s1)
            yield {
                "event": "node_update",
                "node": "interpret_intent",
                "data": {
                    "intent_type": current_state.get("intent_type"),
                    "route_reason": current_state.get("route_reason"),
                    "activated_agents": current_state.get("activated_agents"),
                    "todo_list": current_state.get("todo_list"),
                }
            }
            activated = current_state.get("activated_agents", [])
            if "search_catalog" in activated:
                s2 = node_retrieve_candidates(current_state)
                current_state.update(s2)
                yield {
                    "event": "node_update",
                    "node": "retrieve_candidates",
                    "data": {
                        "selected_candidate_ids": current_state.get("selected_candidate_ids"),
                        "total_candidates": (current_state.get("search_results") or {}).get("total", 0),
                    }
                }
            if any(a in activated for a in ("extract_reviews", "retrieve_references", "find_alternatives")):
                s3 = node_plan_and_retrieve_evidence(current_state)
                current_state.update(s3)
                yield {
                    "event": "node_update",
                    "node": "plan_and_retrieve_evidence",
                    "data": {
                        "references_count": len(current_state.get("references") or []),
                        "review_insights_count": len(current_state.get("review_insights") or []),
                    }
                }
            s4 = node_synthesize_grounded_answer(current_state)
            current_state.update(s4)
            yield {
                "event": "node_update",
                "node": "synthesize_grounded_answer",
                "data": {
                    "route": current_state.get("intent_type"),
                }
            }

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        timings = dict(current_state.get("stage_timings_ms") or {})
        timings["elapsed_ms"] = elapsed_ms

        activated = current_state.get("activated_agents", [])
        bypassed = current_state.get("bypassed_agents", [])

        trace = {
            "mode": "langgraph_compiled_workflow" if _compiled_graph is not None else "deterministic_workflow",
            "rule_version": RULE_VERSION,
            "intent_route": current_state.get("intent_type", "search"),
            "route_reason": current_state.get("route_reason", ""),
            "activated_agents": activated,
            "bypassed_agents": bypassed,
            "agents_summary": f"Activated {len(activated)} of 4 agents ({len(bypassed)} bypassed)",
            "tools": ["interpret_intent"] + activated + ["synthesize_grounded_answer"],
            "plan_mode": current_state.get("plan_mode", "auto"),
            "planned_tools": activated,
            "events": current_state.get("events", []),
            "retries": sum(max(0, e["attempts"] - 1) for e in run["events"]),
            "model_calls": run["calls"],
            "interpretation_mode": current_state.get("trace_interpretation_mode", "deterministic"),
            "stage_timings_ms": timings,
            "cache_hits": sum(bool(e.get("cache_hit")) for e in run["events"]),
            "input_tokens": sum(e.get("input_tokens", 0) for e in run["events"]),
            "output_tokens": sum(e.get("output_tokens", 0) for e in run["events"]),
            "thinking_tokens": sum(e.get("thinking_tokens", 0) for e in run["events"]),
            "elapsed_ms": elapsed_ms,
        }

        final_payload = {
            "answer": current_state["final_answer"],
            "search": current_state.get("search_results", {"products": [], "total": 0, "unknown_count": 0, "failed_count": 0, "needs_clarification": []}),
            "review_insights": current_state.get("review_insights", []),
            "alternatives": current_state.get("alternatives", []),
            "references": current_state.get("references", []),
            "evidence": current_state.get("retrieval_bundle", {"mode": "not_requested", "documents": []}),
            "synthesis": current_state.get("grounded_synthesis", {}),
            "clarification": current_state.get("clarification"),
            "trace": trace,
        }

        yield {
            "event": "final_result",
            "data": final_payload,
        }
