"""
Deep module for query intent classification and task planning.
Single authoritative source of truth for intent routing, selective agent activation,
and Deep Agents todo_list generation.
"""

from dataclasses import asdict, dataclass, field
import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from skintellect.catalog.store import get_catalog
from skintellect.research.models import SearchIntent
from skintellect.research.search import interpret


# Semantic Intent Anchors for Vector Similarity Routing
SEMANTIC_ROUTE_ANCHORS: Dict[str, List[str]] = {
    "conversation_memory": [
        "what was my questions",
        "what did i ask earlier in this chat",
        "summarize our chat history and queries",
        "repeat my previous questions",
        "remind me what we discussed earlier",
        "recap our conversation thread so far",
        "which questions did i query",
        "what was the last thing i asked",
        "refresh my recollection of what we talked about",
        "what were we talking about",
    ],
    "science_qa": [
        "explain the scientific mechanism and difference between these actives",
        "why are sulfates or sles considered bad for hair and scalp",
        "sodium lauryl sulfate protein denaturation and lipid stripping",
        "how does this cosmetic chemical mechanism work biologically",
        "molecular weight penetration depth in the stratum corneum",
        "trans-epidermal water loss and lipid barrier physiology",
        "aquaporin channels and humectant water binding capacity",
        "difference between salicylic acid and glycolic acid",
        "how does niacinamide support skin barrier lipids",
        "cellular mechanism of active ingredients on keratinocytes",
        "explain the active ingredient chemistry and interaction",
    ],
    "compare": [
        "compare these formulations side by side",
        "how do these two products stack up against each other",
        "evaluate the tradeoffs between these barrier moisturizers",
        "versus comparison across price tiers and ingredients",
        "which product is better for barrier repair",
        "head to head comparison of moisturizers",
        "side by side breakdown of competing formulations",
    ],
    "review_inquiry": [
        "what do user reviews report about stinging or irritation",
        "buyer feedback on stickiness and texture finish",
        "do customers experience pilling or burning during application",
        "reported review experiences across skin types",
        "what do sensitive skin reviews say about fragrance or burning",
        "customer observations on tingling sensation and breakout risk",
    ],
    "explore": [
        "show me what you have in the catalog",
        "curated standout verified products across routine steps",
        "just browsing looking for routine inspiration",
        "popular trending skincare formulations",
        "i am a beginner looking to get started with good products",
        "show top rated formulations in the store",
        "look around at what is popular",
    ],
    "greeting": [
        "hello formulation copilot",
        "hi there good morning",
        "hey there good afternoon",
        "greetings to the assistant",
        "hello there assistant",
        "hey copilot howdy",
    ],
    "general_chat": [
        "do you know who won the football world cup",
        "sports match results and game scores",
        "are you sure about that",
        "double check why you cant answer this",
        "why did you not answer my question",
        "why cant you answer my question",
        "are you friendly or not",
        "can you be more helpful",
        "tell me something funny",
        "tell me a cosmetic chemistry joke",
        "who are you and what can you do",
        "what is your personality",
        "why are you repeating the same answer",
    ],
    "conversation_ack": [
        "thank you very much appreciate it",
        "got it that makes complete sense",
        "awesome cool sounds great",
        "understood thanks for the explanation",
        "thanks for the helpful breakdown",
    ],
}


def _vectorize_ngram(text: str) -> Counter:
    """Extracts word unigrams and character trigrams for fast subword vector representation."""
    tokens = re.findall(r"\b\w+\b", text.casefold())
    features = Counter(tokens)
    for t in tokens:
        if len(t) >= 3:
            for i in range(len(t) - 2):
                features["c:" + t[i:i+3]] += 1
    return features


def _cosine_similarity(v1: Counter, v2: Counter) -> float:
    dot = sum(v1[k] * v2.get(k, 0) for k in v1)
    norm1 = math.sqrt(sum(v*v for v in v1.values()))
    norm2 = math.sqrt(sum(v*v for v in v2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


_VECTORIZED_ANCHORS: Dict[str, List[Counter]] = {
    route: [_vectorize_ngram(a) for a in anchors]
    for route, anchors in SEMANTIC_ROUTE_ANCHORS.items()
}


def classify_semantic(query: str, threshold: float = 0.25) -> Tuple[str, float]:
    """Matches an input query against semantic anchor clusters using vector cosine similarity."""
    qv = _vectorize_ngram(query)
    best_route = "unknown"
    best_score = 0.0
    for route, anchors in _VECTORIZED_ANCHORS.items():
        score = max(_cosine_similarity(qv, a) for a in anchors)
        if score > best_score:
            best_score = score
            best_route = route
    if best_score >= threshold:
        return best_route, round(best_score, 3)
    return "unknown", round(best_score, 3)


@dataclass
class IntentRoutePlan:
    """Encapsulates intent routing decision, task plan, and agent dispatch policy."""
    intent_type: str  # "greeting", "explore", "science_qa", "review_inquiry", "compare", "search"
    route_reason: str
    activated_agents: List[str]
    bypassed_agents: List[str]
    todo_list: List[Dict[str, Any]]
    mode: str = "deterministic"
    confidence: float = 1.0
    intent_dict: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def classify_and_plan(
    query: str,
    db_path: Optional[str] = None,
    history: Optional[List[Dict[str, Any]]] = None,
    pending_clarification: Optional[Dict[str, Any]] = None,
) -> IntentRoutePlan:
    """
    Classifies a user's natural language inquiry into a structured route plan.
    Determines which agents are activated vs bypassed, and sets the Deep Agents task plan.
    """
    from skintellect.agents.clarification import (
        is_ambiguous_skincare_inquiry,
        resolve_shorthand_clarification,
    )

    # 0. Shorthand Conversational Resolution (if prior turn asked for clarification)
    if pending_clarification:
        resolved_shorthand = resolve_shorthand_clarification(
            query,
            pending_clarification.get("options", []),
            pending_clarification.get("original_query", ""),
        )
        if resolved_shorthand:
            return classify_and_plan(resolved_shorthand, db_path=db_path, history=history)

    q = query.strip().casefold()
    history = history or []

    # 1. Meta-conversation & Conversation Memory Inquiries
    # Matches explicit questions like "what was my questions?" as well as shorthand/slang like "hey which are que of my?"
    question_tokens = {"que", "ques", "question", "questions", "query", "queries", "inquiry", "inquiries", "asked", "ask", "prompt", "prompts"}
    memory_tokens = {"my", "mine", "i", "we", "our", "me", "chat", "conversation", "thread", "session", "earlier", "previous", "past", "history", "recap", "summarize", "repeat", "remember"}
    raw_tokens = set(re.findall(r"\b\w+\b", q))

    memory_patterns = (
        r"\bwhat\s+(was|were)\s+(my|the)\s+(question|questions|que|queries)\b",
        r"\b(which|what)\s+(were|are)\s+(my|the)\s+(question|questions|que|queries|inquiries)\b",
        r"\b(which|what)\s+are\s+(the\s+)?(que|questions|queries)\s+of\s+(my|mine)\b",
        r"\b(que|questions?|queries)\s+(of\s+my|of\s+mine|i\s+asked|from\s+me)\b",
        r"\bwhat\s+did\s+i\s+(ask|say|query)\b",
        r"\bwhat\s+have\s+we\s+(discussed|talked\s+about)\b",
        r"\bsummarize\s+(our\s+)?(chat|conversation|discussion|history)\b",
        r"\b(repeat|recap)\s+(that|our\s+conversation|your\s+last\s+answer)\b",
        r"\bwhat\s+was\s+(the\s+last|the\s+previous|my\s+last)\s+(question|topic)\b",
    )
    if bool(raw_tokens & question_tokens and raw_tokens & memory_tokens) or any(re.search(pat, q) for pat in memory_patterns):
        return IntentRoutePlan(
            intent_type="conversation_memory",
            route_reason="Conversation history / memory query detected; activating conversation memory agent",
            activated_agents=["conversation_memory"],
            bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
            todo_list=[
                {"id": "task_1", "task": "Inspect session conversation history & turns", "status": "pending"},
                {"id": "task_2", "task": "Extract user inquiries and assistant recommendations", "status": "pending"},
                {"id": "task_3", "task": "Synthesize conversational memory summary", "status": "pending"},
            ],
            mode="conversation_memory_router",
            intent_dict=SearchIntent(text=query).model_dump(),
        )

    # 2. Conversational Acknowledgment / Feedback
    if re.match(r'^(thanks|thank\s+you|awesome|great|cool|ok|okay|got\s+it|understood)[\s!.?]*$', q):
        return IntentRoutePlan(
            intent_type="conversation_ack",
            route_reason="User conversational acknowledgment; heavy catalog and literature agents bypassed",
            activated_agents=["greeting_handler"],
            bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
            todo_list=[
                {"id": "task_1", "task": "Acknowledge user feedback & offer next steps", "status": "pending"},
            ],
            mode="acknowledgment_router",
            intent_dict=SearchIntent(text=query).model_dump(),
        )

    # 3. Conversational Follow-up, Verification & Chat Questions
    doubt_pat = r'^(are\s+you\s+(sure|certain|positive)|really\??|for\s+real\??|how\s+do\s+you\s+know|is\s+that\s+(true|correct|right)\??)[\s!.?]*$'
    feedback_pat = (
        r'(why\s+(did\s+you\s+not|didn[\'’]?t\s+you|you\s+didn[\'’]?t|you\s+not|not|can[\'’]?t\s+you|you\s+can[\'’]?t)\s+(answer|respond|reply)|'
        r'double\s+check\s+.*(cant|can[\'’]?t|why|answer)|'
        r'why\s+(cant|can\'?t)\s+you|'
        r'can\s+you\s+answer|'
        r'answer\s+this|'
        r'why\s+didn\'?t\s+you\s+answer|'
        r'are\s+you\s+(not\s+)?(friendly|nice|human|bot|real|mean)|'
        r'why\s+are\s+you\s+(repeating|saying\s+the\s+same)|'
        r'tell\s+me\s+a\s+joke|make\s+me\s+laugh|say\s+something\s+funny|who\s+made\s+you|what\s+is\s+your\s+name)'
    )
    if re.match(doubt_pat, q) or re.search(feedback_pat, q):
        return IntentRoutePlan(
            intent_type="general_chat",
            route_reason="Conversational follow-up or personality query; bypassed catalog search",
            activated_agents=["greeting_handler"],
            bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
            todo_list=[
                {"id": "task_1", "task": "Interpret conversational context & synthesize dynamic friendly response", "status": "pending"},
            ],
            mode="general_chat_router",
            intent_dict=SearchIntent(text=query).model_dump(),
        )

    # 4. Greeting & Capability Discovery
    if re.match(r'^(hi|hello|hey|greetings|howdy|sup|yo|good\s+(morning|afternoon|evening)|help)[\s!.?]*$', q):
        return IntentRoutePlan(
            intent_type="greeting",
            route_reason="User greeting / capability discovery; heavy catalog and literature agents bypassed",
            activated_agents=["greeting_handler"],
            bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
            todo_list=[
                {"id": "task_1", "task": "Acknowledge greeting & present copilot capabilities", "status": "pending"},
            ],
            mode="greeting_router",
            intent_dict=SearchIntent(text=query).model_dump(),
        )

    # 5. General Catalog Exploration & Discovery
    if any(w in q for w in ("just exploring", "exploring", "explore", "browse", "looking around", "show me products", "popular products", "what do you have", "trending", "routine ideas", "recommendations", "top formulations", "top rated", "discover")):
        return IntentRoutePlan(
            intent_type="explore",
            route_reason="Catalog exploration requested; bypassed review ABSA, formula twins, and PubMed citations",
            activated_agents=["search_catalog"],
            bypassed_agents=["extract_reviews", "find_alternatives", "retrieve_references"],
            todo_list=[
                {"id": "task_1", "task": "Identify exploration intent & catalog scope", "status": "pending"},
                {"id": "task_2", "task": "Retrieve standout verified formulations across routine steps", "status": "pending"},
                {"id": "task_3", "task": "Synthesize curated catalog showcase with suggestions", "status": "pending"},
            ],
            mode="explore_router",
            intent_dict=SearchIntent(text=query).model_dump(),
        )

    # 6. Pure Cosmetic Chemistry & Science QA (Fast Path)
    science_patterns = (
        r'\b(explain|difference\s+between|scientific\s+difference|mechanism\s+of)\b',
        r'\bhow\s+does\s+\w+\s+(work|penetrate|function|affect|interact)\b',
        r'\bwhat\s+(is|are)\s+(the\s+)?(mechanism|biological|difference|biophysical|science|function\s+of|ph\s+of|molecular)\b',
        r'\bwhy\s+(is|are|do|does)?\s*.*(bad|good|harmful|irritating|drying|comedogenic|safe|unsafe|toxic|avoid|strip|damage|cause)\b',
        r'\b(why|is|are)\s+.*(sulphate|sulfate|sle|sles|sls|surfactant|paraben|silicone|alcohol|fragrance)\b',
        r'\b(sulphate|sulfate|sle|sles|sls|surfactants?|parabens?|silicones?|niacinamide|ceramide|retinol|tretinoin|salicylic|glycolic|lactic|azelaic|ascorbic|hyaluronic|glycerin|panthenol)\s+(benefit|benefits|harm|side\s+effects?|safety|science|mechanism|function|interaction)\b',
    )
    is_buying_search = any(w in q for w in ("find", "search", "looking for", "recommend", "best for", "products for", "top rated", "under $", "buy"))
    if any(re.search(pat, q) for pat in science_patterns) and not is_buying_search:
        return IntentRoutePlan(
            intent_type="science_qa",
            route_reason="Cosmetic chemistry explanation requested; bypassed catalog search and review extraction",
            activated_agents=["retrieve_references"],
            bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives"],
            todo_list=[
                {"id": "task_1", "task": "Parse cosmetic chemistry topics & active ingredients", "status": "pending"},
                {"id": "task_2", "task": "Retrieve scientific monographs & clinical references", "status": "pending"},
                {"id": "task_3", "task": "Synthesize evidence-backed formulation explanation", "status": "pending"},
            ],
            mode="science_qa_router",
            intent_dict=SearchIntent(text=query).model_dump(),
        )

    # 4. Review Sentiment / Sensation Inquiry
    if any(w in q for w in ("stinging", "burn", "burning", "pilling", "sticky", "texture", "scent", "smell", "review", "reviews")) and not any(cat in q for cat in ('cleanser', 'moisturizer', 'serum', 'toner', 'sunscreen')):
        return IntentRoutePlan(
            intent_type="review_inquiry",
            route_reason="Review experience feedback requested; bypassed catalog filtering and formula twins",
            activated_agents=["extract_reviews"],
            bypassed_agents=["search_catalog", "find_alternatives", "retrieve_references"],
            todo_list=[
                {"id": "task_1", "task": "Identify aspect-based sentiment target from reviews", "status": "pending"},
                {"id": "task_2", "task": "Extract verbatim buyer quotes across skin types", "status": "pending"},
                {"id": "task_3", "task": "Synthesize reported review experience summary", "status": "pending"},
            ],
            mode="review_inquiry_router",
            intent_dict=SearchIntent(text=query).model_dump(),
        )

    # 5. Product Comparison (Fast Path)
    if re.search(r'\b(compare|versus|vs\.?)\b', q):
        resolved_db = get_catalog(db_path).path
        parsed = interpret(query, resolved_db)
        intent_dict = SearchIntent(**parsed.get("intent", {})).model_dump()
        return IntentRoutePlan(
            intent_type="compare",
            route_reason="Comparative formulation requested; activated catalog search & comparative review ABSA",
            activated_agents=["search_catalog", "extract_reviews"],
            bypassed_agents=["find_alternatives", "retrieve_references"],
            todo_list=[
                {"id": "task_1", "task": "Identify target active lipids & formula category", "status": "pending"},
                {"id": "task_2", "task": "Retrieve top eligible formulations for comparative analysis", "status": "pending"},
                {"id": "task_3", "task": "Extract review sentiments & key active differences", "status": "pending"},
                {"id": "task_4", "task": "Synthesize side-by-side comparison across skin types & budgets", "status": "pending"},
            ],
            mode=parsed.get("mode", "deterministic"),
            confidence=1.0,
            intent_dict=intent_dict,
        )

    # 6. Underspecified / Ambiguous Skincare Inquiry (HITL Clarification Trigger)
    if is_ambiguous_skincare_inquiry(query, history=history):
        return IntentRoutePlan(
            intent_type="clarification_needed",
            route_reason="Broad or underspecified skincare inquiry; generated interactive HITL disambiguation choices",
            activated_agents=["clarification_generator"],
            bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
            todo_list=[
                {"id": "task_1", "task": "Decompose broad inquiry into distinct formulation pathways", "status": "pending"},
                {"id": "task_2", "task": "Present interactive HITL clarification options & custom choice", "status": "pending"},
            ],
            mode="clarification_router",
            intent_dict=SearchIntent(text=query).model_dump(),
        )

    # 7. Tier 2: Vector Semantic Similarity Routing
    # Evaluates conceptual inquiry intent against semantic route anchor clusters
    sem_route, sem_score = classify_semantic(query, threshold=0.25)
    category_tokens = {"cleanser", "cleansers", "moisturizer", "moisturizers", "serum", "serums", "toner", "toners", "sunscreen", "sunscreens", "shampoo", "shampoos", "conditioner", "conditioners"}
    has_explicit_category = bool(raw_tokens & category_tokens)

    if sem_route != "unknown" and not (has_explicit_category and sem_route in ("science_qa", "greeting", "conversation_memory", "conversation_ack")):
        if sem_route == "compare":
            resolved_db = get_catalog(db_path).path
            parsed = interpret(query, resolved_db)
            intent_dict = SearchIntent(**parsed.get("intent", {})).model_dump()
            return IntentRoutePlan(
                intent_type="compare",
                route_reason=f"Semantic vector similarity (compare, confidence: {sem_score:.2f})",
                activated_agents=["search_catalog", "extract_reviews"],
                bypassed_agents=["find_alternatives", "retrieve_references"],
                todo_list=[
                    {"id": "task_1", "task": "Identify target active lipids & formula category", "status": "pending"},
                    {"id": "task_2", "task": "Retrieve top eligible formulations for comparative analysis", "status": "pending"},
                    {"id": "task_3", "task": "Extract review sentiments & key active differences", "status": "pending"},
                    {"id": "task_4", "task": "Synthesize side-by-side comparison across skin types & budgets", "status": "pending"},
                ],
                mode="semantic_vector_router",
                confidence=sem_score,
                intent_dict=intent_dict,
            )

        if sem_route == "science_qa":
            return IntentRoutePlan(
                intent_type="science_qa",
                route_reason=f"Semantic vector similarity (science_qa, confidence: {sem_score:.2f})",
                activated_agents=["retrieve_references"],
                bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives"],
                todo_list=[
                    {"id": "task_1", "task": "Parse cosmetic chemistry topics & active ingredients", "status": "pending"},
                    {"id": "task_2", "task": "Retrieve scientific monographs & clinical references", "status": "pending"},
                    {"id": "task_3", "task": "Synthesize evidence-backed formulation explanation", "status": "pending"},
                ],
                mode="semantic_vector_router",
                confidence=sem_score,
                intent_dict=SearchIntent(text=query).model_dump(),
            )

        if sem_route == "review_inquiry":
            return IntentRoutePlan(
                intent_type="review_inquiry",
                route_reason=f"Semantic vector similarity (review_inquiry, confidence: {sem_score:.2f})",
                activated_agents=["extract_reviews"],
                bypassed_agents=["search_catalog", "find_alternatives", "retrieve_references"],
                todo_list=[
                    {"id": "task_1", "task": "Identify aspect-based sentiment target from reviews", "status": "pending"},
                    {"id": "task_2", "task": "Extract verbatim buyer quotes across skin types", "status": "pending"},
                    {"id": "task_3", "task": "Synthesize reported review experience summary", "status": "pending"},
                ],
                mode="semantic_vector_router",
                confidence=sem_score,
                intent_dict=SearchIntent(text=query).model_dump(),
            )

        if sem_route == "explore":
            return IntentRoutePlan(
                intent_type="explore",
                route_reason=f"Semantic vector similarity (explore, confidence: {sem_score:.2f})",
                activated_agents=["search_catalog"],
                bypassed_agents=["extract_reviews", "find_alternatives", "retrieve_references"],
                todo_list=[
                    {"id": "task_1", "task": "Identify exploration intent & catalog scope", "status": "pending"},
                    {"id": "task_2", "task": "Retrieve standout verified formulations across routine steps", "status": "pending"},
                    {"id": "task_3", "task": "Synthesize curated catalog showcase with suggestions", "status": "pending"},
                ],
                mode="semantic_vector_router",
                confidence=sem_score,
                intent_dict=SearchIntent(text=query).model_dump(),
            )

        if sem_route == "conversation_memory":
            return IntentRoutePlan(
                intent_type="conversation_memory",
                route_reason=f"Semantic vector similarity (conversation_memory, confidence: {sem_score:.2f})",
                activated_agents=["conversation_memory"],
                bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
                todo_list=[
                    {"id": "task_1", "task": "Inspect session conversation history & turns", "status": "pending"},
                    {"id": "task_2", "task": "Extract user inquiries and assistant recommendations", "status": "pending"},
                    {"id": "task_3", "task": "Synthesize conversational memory summary", "status": "pending"},
                ],
                mode="semantic_vector_router",
                confidence=sem_score,
                intent_dict=SearchIntent(text=query).model_dump(),
            )

        if sem_route == "greeting":
            return IntentRoutePlan(
                intent_type="greeting",
                route_reason=f"Semantic vector similarity (greeting, confidence: {sem_score:.2f})",
                activated_agents=["greeting_handler"],
                bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
                todo_list=[
                    {"id": "task_1", "task": "Acknowledge greeting & present copilot capabilities", "status": "pending"},
                ],
                mode="semantic_vector_router",
                confidence=sem_score,
                intent_dict=SearchIntent(text=query).model_dump(),
            )

        if sem_route == "conversation_ack":
            return IntentRoutePlan(
                intent_type="conversation_ack",
                route_reason=f"Semantic vector similarity (conversation_ack, confidence: {sem_score:.2f})",
                activated_agents=["greeting_handler"],
                bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
                todo_list=[
                    {"id": "task_1", "task": "Acknowledge user feedback & offer next steps", "status": "pending"},
                ],
                mode="semantic_vector_router",
                confidence=sem_score,
                intent_dict=SearchIntent(text=query).model_dump(),
            )

        if sem_route == "general_chat":
            return IntentRoutePlan(
                intent_type="general_chat",
                route_reason=f"Semantic vector similarity (general_chat, confidence: {sem_score:.2f})",
                activated_agents=["greeting_handler"],
                bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
                todo_list=[
                    {"id": "task_1", "task": "Interpret conversational context & synthesize dynamic friendly response", "status": "pending"},
                ],
                mode="semantic_vector_router",
                confidence=sem_score,
                intent_dict=SearchIntent(text=query).model_dump(),
            )

    # 7. Structured Filter & Search (Default)
    activated = ["search_catalog"]
    bypassed = []
    if any(w in q for w in ("review", "reviews", "stinging", "pilling", "sticky", "texture")):
        activated.append("extract_reviews")
    else:
        bypassed.append("extract_reviews")

    if any(w in q for w in ("dupe", "dupes", "alternative", "alternatives", "similar", "twin")):
        activated.append("find_alternatives")
    else:
        bypassed.append("find_alternatives")

    if any(w in q for w in ("study", "studies", "evidence", "pubmed", "clinical")):
        activated.append("retrieve_references")
    else:
        bypassed.append("retrieve_references")

    reason = f"Structured formulation filter; activated {len(activated)} agents, bypassed {len(bypassed)} unrequested agents"
    resolved_db = get_catalog(db_path).path
    parsed = interpret(query, resolved_db)

    # Contextual Follow-up Resolution: If category is missing/unresolved but previous turn had one, inherit it
    if history and parsed.get("intent", {}).get("category") == "all":
        last_user_query = None
        for msg in reversed(history):
            if msg.get("role") == "user" and msg.get("content"):
                last_user_query = msg.get("content")
                break
        if last_user_query:
            prev_parsed = interpret(last_user_query, resolved_db)
            prev_cat = prev_parsed.get("intent", {}).get("category", "all")
            if prev_cat != "all":
                parsed["intent"]["category"] = prev_cat
                unresolved = parsed.get("intent", {}).get("unresolved_terms", [])
                parsed["intent"]["unresolved_terms"] = [
                    u for u in unresolved if "Choose a product category" not in u
                ]
                if not parsed.get("intent", {}).get("required_ingredients") and prev_parsed.get("intent", {}).get("required_ingredients"):
                    parsed["intent"]["required_ingredients"] = prev_parsed["intent"]["required_ingredients"]
                reason += f"; inherited context (category: '{prev_cat}') from previous turn"

    intent_dict = SearchIntent(**parsed.get("intent", {})).model_dump()

    # Intelligent Catalog Dispatch: Only execute heavy catalog search if the query actually contains product search signals!
    has_category = parsed.get("intent", {}).get("category") != "all"
    has_ingredients = bool(parsed.get("intent", {}).get("required_ingredients") or parsed.get("intent", {}).get("excluded_ingredients"))
    has_preferences = bool(parsed.get("intent", {}).get("preferences"))
    has_prices = bool(parsed.get("intent", {}).get("preferred_price_tiers"))
    has_search_keywords = any(w in q for w in ("find", "search", "looking for", "recommend", "suggestion", "best for", "products for", "product", "products", "under"))

    is_catalog_search = has_category or has_ingredients or has_preferences or has_prices or has_search_keywords

    if not is_catalog_search:
        return IntentRoutePlan(
            intent_type="general_chat",
            route_reason="General conversational inquiry; catalog search bypassed because no cosmetic category or ingredient was requested",
            activated_agents=["greeting_handler"],
            bypassed_agents=["search_catalog", "extract_reviews", "find_alternatives", "retrieve_references"],
            todo_list=[
                {"id": "task_1", "task": "Interpret conversational question & synthesize helpful formulation guidance", "status": "pending"},
            ],
            mode="general_chat_router",
            intent_dict=intent_dict,
        )

    todo = [
        {"id": "task_1", "task": "Interpret cosmetic intent & active constraints", "status": "pending"},
        {"id": "task_2", "task": "Retrieve matching formulations across catalog", "status": "pending"},
        {"id": "task_3", "task": "Extract aspect reviews & scientific monographs", "status": "pending"},
    ]
    if "find_alternatives" in activated:
        todo.append({"id": "task_alt", "task": "Identify formula twin alternatives", "status": "pending"})
    if "retrieve_references" in activated and "retrieve_references" not in [t["id"] for t in todo]:
        todo.append({"id": "task_ref", "task": "Consult PubMed & FDA reference monographs", "status": "pending"})
    todo.append({"id": f"task_{len(todo)+1}", "task": "Synthesize grounded evidence-backed response", "status": "pending"})

    return IntentRoutePlan(
        intent_type="search",
        route_reason=reason,
        activated_agents=activated,
        bypassed_agents=bypassed,
        todo_list=todo,
        mode=parsed.get("mode", "deterministic"),
        intent_dict=intent_dict,
    )
