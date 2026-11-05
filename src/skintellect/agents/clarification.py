"""
Intelligent Human-In-The-Loop (HITL) Clarification & Disambiguation Engine.

Features:
- Detects underspecified, ambiguous, or broad cosmetic/skincare inquiries.
- Two-tier option generation:
  Tier 1: Dynamic Gemini structured generation (when online).
  Tier 2: High-precision domain facet matrix (Categories x Actives x Tolerance) for offline/sandbox.
- Shorthand conversational resolution (e.g. "1", "A", "first one", "serums").
- Structured payload with multiple choices + custom option flag.
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from skintellect.gemini import GeminiClient, GeminiUnavailable


class ClarificationOption(BaseModel):
    id: str = Field(description="Unique identifier for the option, e.g. opt_1")
    title: str = Field(description="Short human-friendly title of the option")
    description: str = Field(description="Brief explanation of what this path targets")
    query: str = Field(description="Complete, actionable query to execute on selection")


class ClarificationPayload(BaseModel):
    needs_clarification: bool = Field(default=True)
    summary: str = Field(description="Clear explanation of the ambiguity and formulation pathways")
    options: List[ClarificationOption] = Field(description="3-4 distinct disambiguation paths")
    allow_custom: bool = Field(default=True, description="Whether to show the blank/custom option")


# ==============================================================================
# Domain Facet Matrix (Deterministic Offline Fallback)
# Maps skincare topics & broad inquiries to 3-4 distinct actionable paths
# ==============================================================================

FACET_CLUSTERS = [
    {
        "id": "acne",
        "patterns": [r"\bacne\b", r"\bpimples?\b", r"\bbreakouts?\b", r"\bclogged\s+pores?\b", r"\bblackheads?\b"],
        "summary": "Acne and congestion can be addressed across several distinct formulation mechanisms. Which approach fits your current skin needs?",
        "options": [
            ClarificationOption(
                id="opt_1",
                title="BHA / Salicylic Acid Pore-Clearing Cleanser",
                description="Oil-soluble beta-hydroxy acid that penetrates pore sebum to dissolve blackheads.",
                query="Find salicylic acid BHA cleansers for acne and blackheads",
            ),
            ClarificationOption(
                id="opt_2",
                title="Niacinamide & Zinc Sebum-Control Serum",
                description="Reduces sebum excretion rate (SER) and soothes inflammatory redness.",
                query="Find niacinamide serums for acne and oily skin with no fragrance",
            ),
            ClarificationOption(
                id="opt_3",
                title="Lightweight Oil-Free Barrier Moisturizer",
                description="Hydrates without clogging pores (fungal-acne safe and non-comedogenic).",
                query="Find fungal-acne safe oil-free moisturizers for acne-prone skin",
            ),
            ClarificationOption(
                id="opt_4",
                title="Azelaic Acid / Post-Blemish Fading Treatment",
                description="Targets post-inflammatory erythema (red marks) and regulates follicular keratinization.",
                query="Find azelaic acid serums for acne and redness",
            ),
        ],
    },
    {
        "id": "acids",
        "patterns": [r"\bwhich\s+acid\b", r"\bwhat\s+acid\b", r"\bacids?\s+for\b", r"\bexfoliat\w*\s+acid\b", r"\bbha\s+or\s+aha\b", r"\baha\s+or\s+bha\b"],
        "summary": "Cosmetic acids target fundamentally different depths and skin concerns. Which biological target are you looking to treat?",
        "options": [
            ClarificationOption(
                id="opt_1",
                title="Salicylic Acid (BHA) for Pores & Blackheads",
                description="Lipophilic (oil-soluble): penetrates the pore lumen to dissolve sebum and prevent breakouts.",
                query="Explain the scientific difference between salicylic acid BHA and glycolic acid AHA",
            ),
            ClarificationOption(
                id="opt_2",
                title="Glycolic / Lactic Acid (AHA) for Surface Texture",
                description="Hydrophilic (water-soluble): loosens dead surface corneocytes for radiance and smoothing.",
                query="Find gentle AHA lactic acid exfoliants for smooth texture",
            ),
            ClarificationOption(
                id="opt_3",
                title="Azelaic Acid for Redness & Rosacea",
                description="Dicarboxylic acid: reduces inflammatory cytokines and regulates keratinocyte turnover.",
                query="Find azelaic acid treatments for redness and skin tone",
            ),
            ClarificationOption(
                id="opt_4",
                title="Hyaluronic Acid for Deep Humectant Hydration",
                description="Non-exfoliating: large molecule moisture reservoir holding up to 1,000x its weight in water.",
                query="Explain the scientific difference between glycerin and hyaluronic acid",
            ),
        ],
    },
    {
        "id": "oily_skin",
        "patterns": [r"\boily\s+skin\b", r"\bgreasy\s+skin\b", r"\bsebum\s+control\b", r"\bshine\s+control\b", r"\boily\s+routine\b"],
        "summary": "Managing oily skin requires balancing sebum regulation with barrier preservation. Which routine step do you want to optimize?",
        "options": [
            ClarificationOption(
                id="opt_1",
                title="Sulfate-Free Foaming Cleansers",
                description="Thoroughly removes excess sebum without stripping the protective 18-MEA lipid layer.",
                query="Find gentle foaming cleansers for oily skin with no fragrance",
            ),
            ClarificationOption(
                id="opt_2",
                title="Mattifying Gel Moisturizer",
                description="Ultra-lightweight humectant-rich water-gels that hydrate with zero greasy residue.",
                query="Find lightweight oil-free gel moisturizers for oily skin",
            ),
            ClarificationOption(
                id="opt_3",
                title="Niacinamide Pore-Minimizing Serum",
                description="Clinically proven to reduce sebum excretion rate and tighten appearance of pores.",
                query="Find niacinamide serums for oily skin",
            ),
        ],
    },
    {
        "id": "dry_barrier",
        "patterns": [r"\bdry\s+skin\b", r"\bflaky\s+skin\b", r"\bbarrier\s+(repair|damage|cream)\b", r"\bpeeling\s+skin\b", r"\bparched\b"],
        "summary": "Dry or compromised skin requires replenishing intercellular lipids and reducing TEWL. Which formulation approach would you like to explore?",
        "options": [
            ClarificationOption(
                id="opt_1",
                title="3:1:1 Ceramide Barrier Repair Cream",
                description="Physiological ratio of ceramides, cholesterol, and free fatty acids to seal damaged barriers.",
                query="Compare barrier repair moisturizers with ceramides",
            ),
            ClarificationOption(
                id="opt_2",
                title="Non-Foaming Cream / Milk Cleanser",
                description="Cleanses with gentle fatty alcohols and humectants without disrupting stratum corneum lipids.",
                query="Find gentle hydrating cream cleansers for dry skin fragrance free",
            ),
            ClarificationOption(
                id="opt_3",
                title="Deep Hydrating Glycerin & Squalane Serum",
                description="Low-molecular-weight humectants combined with biocompatible lipid replenishment.",
                query="Find hydrating barrier serums with glycerin and squalane",
            ),
        ],
    },
    {
        "id": "sensitive_redness",
        "patterns": [r"\bsensitive\s+skin\b", r"\bredness\b", r"\brosacea\b", r"\birritat\w*\b", r"\bsooth\w*\b", r"\bcalming\b"],
        "summary": "Sensitive and reactive skin needs ultra-minimalist, hypoallergenic formulations with proven soothing bio-actives. Which category are you looking for?",
        "options": [
            ClarificationOption(
                id="opt_1",
                title="Fragrance-Free, Essential-Oil-Free Cleansers",
                description="Eliminates the top dermatological contact allergens and irritants.",
                query="Find gentle cleansers for sensitive skin fragrance free",
            ),
            ClarificationOption(
                id="opt_2",
                title="Cica (Centella) & Panthenol Soothing Serums",
                description="Madecassoside and provitamin B5 to suppress neuro-inflammatory stinging and redness.",
                query="Find soothing serums with centella and panthenol for redness",
            ),
            ClarificationOption(
                id="opt_3",
                title="Colloidal Oat Barrier Creams",
                description="FDA-recognized skin protectant rich in beta-glucans and avenanthramides to relieve itch.",
                query="Find colloidal oat barrier creams for sensitive reactive skin",
            ),
        ],
    },
    {
        "id": "hyperpigmentation",
        "patterns": [r"\bdark\s+spots?\b", r"\bhyperpigmentation\b", r"\bmelasma\b", r"\bsun\s+spots?\b", r"\buneven\s+tone\b", r"\bbrighten\w*\b"],
        "summary": "Hyperpigmentation treatment combines tyrosinase inhibitors, melanosome transfer blockers, and daily photoprotection. Which strategy do you want to target?",
        "options": [
            ClarificationOption(
                id="opt_1",
                title="Vitamin C (L-Ascorbic Acid) Antioxidant Serum",
                description="Potent tyrosinase inhibitor and free-radical scavenger for morning photoprotection synergy.",
                query="Find vitamin C L-ascorbic acid brightening serums fragrance free",
            ),
            ClarificationOption(
                id="opt_2",
                title="Tranexamic Acid & Alpha Arbutin Complex",
                description="Non-irritating tyrosinase blocking ideal for melasma and post-acne dark marks.",
                query="Find tranexamic acid and alpha arbutin serums for dark spots",
            ),
            ClarificationOption(
                id="opt_3",
                title="Broad-Spectrum High UVA-PF / PPD Sunscreens",
                description="Crucial baseline: prevents UV-A stimulated melanogenesis and dark spot darkening.",
                query="Find daily broad spectrum mineral sunscreens with zinc oxide",
            ),
        ],
    },
    {
        "id": "anti_aging",
        "patterns": [r"\banti[- ]aging\b", r"\bwrinkles?\b", r"\bfine\s+lines?\b", r"\bfirming\b", r"\bloss\s+of\s+firmness\b", r"\bcollagen\b"],
        "summary": "Age-defying cosmetic chemistry centers on retinoic acid receptor activation, signal peptides, and extracellular matrix protection. Which step would you like to review?",
        "options": [
            ClarificationOption(
                id="opt_1",
                title="Retinol vs. Retinaldehyde Night Treatments",
                description="Gold-standard vitamin A derivatives that stimulate collagen synthesis and epidermal thickening.",
                query="Explain the difference between retinol and retinal for anti aging",
            ),
            ClarificationOption(
                id="opt_2",
                title="Multi-Peptide & Copper Peptide Serums",
                description="Matrix-signaling peptides that support elastin and collagen production without retinoid irritation.",
                query="Find peptide firming serums for fine lines fragrance free",
            ),
            ClarificationOption(
                id="opt_3",
                title="Ceramide & Lipid Replenishing Creams",
                description="Counters age-related epidermal lipid depletion and restores skin elasticity.",
                query="Compare barrier repair moisturizers with ceramides",
            ),
        ],
    },
    {
        "id": "brands",
        "patterns": [r"\bthe\s+ordinary\b", r"\bcerave\b", r"\bpaula[\'’]?s\s+choice\b", r"\bla\s+roche\b", r"\bcosrx\b", r"\bcetaphil\b"],
        "summary": "Brand catalogs offer distinct hero formulations across treatment, cleansing, and barrier hydration. What would you like to analyze?",
        "options": [
            ClarificationOption(
                id="opt_1",
                title="Analyze Hero Active Serums (Niacinamide, BHA, Retinoids)",
                description="Compare single-molecule actives against multi-ingredient alternatives.",
                query="Find top rated treatment serums with verified active concentrations",
            ),
            ClarificationOption(
                id="opt_2",
                title="Inspect Barrier Creams & Physiological Lipids",
                description="Cross-reference INCI lipid profiles and ceramide ratios.",
                query="Compare barrier repair moisturizers with ceramides",
            ),
            ClarificationOption(
                id="opt_3",
                title="Find Formula Twins & Dupes Across Budget Tiers",
                description="Discover alternative products with matching ingredient profiles.",
                query="Find alternative products with matching active ingredients",
            ),
        ],
    },
]

# Default broad clarification fallback
DEFAULT_FACET = ClarificationPayload(
    needs_clarification=True,
    summary="To give you the most accurate cosmetic formulation recommendations, which routine step or goal would you like to focus on?",
    options=[
        ClarificationOption(
            id="opt_1",
            title="Gentle Daily Cleansers",
            description="Low-pH, sulfate-free cleansers that protect the skin's lipid sheath.",
            query="Find gentle hydrating cleansers with no fragrance",
        ),
        ClarificationOption(
            id="opt_2",
            title="Targeted Treatment Serums",
            description="Active formulations containing niacinamide, hyaluronic acid, or exfoliating acids.",
            query="Find soothing treatment serums for sensitive skin",
        ),
        ClarificationOption(
            id="opt_3",
            title="Barrier Repair Moisturizers",
            description="Formulations containing ceramides, squalane, and physiological lipids.",
            query="Compare barrier repair moisturizers with ceramides",
        ),
        ClarificationOption(
            id="opt_4",
            title="Daily Photoprotection (Sunscreen)",
            description="Non-comedogenic, broad-spectrum UV defense with high cosmetic elegance.",
            query="Find fungal-acne safe mineral sunscreens with zinc oxide",
        ),
    ],
    allow_custom=True,
)


# ==============================================================================
# Detection & Triggering Heuristics
# ==============================================================================

def is_ambiguous_skincare_inquiry(query: str, history: Optional[List[Dict[str, Any]]] = None) -> bool:
    """
    Determines if a query is relevant to cosmetics/skincare but broad, underspecified,
    or ambiguous, requiring Human-In-The-Loop (HITL) clarification.
    """
    q = query.strip().casefold()
    tokens = set(re.findall(r'\b\w+\b', q))

    # 1. Bypass pure greetings, identity, and memory inquiries
    if re.match(r'^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening)|help)[\s!.?]*$', q):
        return False
    if re.match(r'^(who\s+are\s+you|what\s+can\s+you\s+do|what\s+was\s+my\s+previous)[\s!.?]*$', q):
        return False
    if re.search(r'\b(are\s+you\s+(sure|certain|positive)|really|joke|funny|laugh)\b', q):
        return False
    if re.search(r'\b(football|soccer|world\s+cup|olympics?)\b', q):
        return False

    # 2. Bypass explicit, specific, already-constrained queries
    # e.g., "Find fungal-acne safe cleansers with no fragrance", "Compare barrier repair moisturizers with ceramides"
    has_category = bool(tokens & {"cleanser", "cleansers", "moisturizer", "moisturizers", "serum", "serums", "toner", "toners", "sunscreen", "sunscreens"})
    has_specific_constraint = any(term in q for term in (
        "fungal-acne", "fungal acne", "no fragrance", "fragrance free", "fragrance-free",
        "oil-free", "oil free", "alcohol free", "alcohol-free", "with ceramides", "with glycerin"
    ))
    has_explicit_science = any(term in q for term in (
        "explain the difference", "scientific difference", "difference between",
        "why sulphate", "why sulfate", "why sls", "why sles", "how does"
    ))
    has_explicit_comparison = bool(re.search(r'\b(compare|versus|vs\.?)\b', q)) and has_category

    # If already sharply specified, do not interrupt the user!
    if (has_category and has_specific_constraint) or has_explicit_science or has_explicit_comparison:
        return False

    # 3. Check for broad/underspecified trigger indicators
    broad_patterns = [
        r'\bwhat\s+(is|are)\s+(best|good|recommended)\s+(for|to)\b',
        r'\bwhich\s+(acid|cleanser|moisturizer|serum|sunscreen|product|one)\s+(should|to|is\s+best)\b',
        r'\b(recommend|suggest)\s+(me\s+)?(a|something|products?|routine)\b',
        r'\bwhat\s+routine\b',
        r'\bhow\s+to\s+(treat|fix|clear|handle|help)\b',
        r'\bhelp\s+(me\s+)?(with\s+)?(my\s+)?(acne|skin|pores|breakouts|dryness|oiliness|redness|texture)\b',
        r'\bis\s+(the\s+ordinary|cerave|paula|la\s+roche|cosrx)\s+(good|worth|effective)\b',
        r'\bwhat\s+about\s+(acne|acids?|vitamin\s+c|retinol|ceramides?|hyaluronic|niacinamide|sunscreen)\b',
    ]
    if any(re.search(pat, q) for pat in broad_patterns):
        return True

    # 4. Check for standalone broad concept keywords without category or action
    standalone_broad = [
        "acne", "pimples", "breakouts", "which acid", "oily skin", "dry skin",
        "sensitive skin", "anti aging", "wrinkles", "dark spots", "hyperpigmentation",
        "the ordinary", "cerave", "paulas choice", "cosrx", "routine"
    ]
    if any(q == sb or q == f"for {sb}" or q == f"what about {sb}" for sb in standalone_broad):
        return True

    return False


# ==============================================================================
# Dynamic Option Generation
# ==============================================================================

def generate_clarification_options(query: str, db_path: Optional[str] = None) -> ClarificationPayload:
    """
    Generates 3-4 structured clarification options for an underspecified inquiry.
    Uses Gemini structured output when available; falls back to domain-facet matrix.
    """
    q = query.strip().casefold()

    # Tier 1: Try Gemini structured model if online & client available
    try:
        client = GeminiClient(db_path)
        if client.available:
            prompt = (
                "You are an expert cosmetic chemistry and formulation assistant. "
                "The user asked a broad, underspecified, or ambiguous skincare inquiry: "
                f"\"{query}\".\n\n"
                "Break down this inquiry into 3 or 4 distinct, highly relevant formulation pathways or specific "
                "routine directions. Provide an overarching summary, and for each option include an id (opt_1, opt_2, ...), "
                "a crisp title, a scientific/practical description, and an actionable executable query that our catalog "
                "or cosmetic science engine can fulfill."
            )
            structured_res = client.structured(
                task="clarification",
                prompt=prompt,
                input_data={"query": query},
                schema_cls=ClarificationPayload,
                version="clarification-v1",
                timeout_seconds=4,
            )
            if structured_res and structured_res.options:
                return structured_res
    except (GeminiUnavailable, Exception):
        pass

    # Tier 2: Deterministic Domain-Facet Matrix Fallback
    for cluster in FACET_CLUSTERS:
        if any(re.search(pat, q) for pat in cluster["patterns"]):
            return ClarificationPayload(
                needs_clarification=True,
                summary=cluster["summary"],
                options=cluster["options"],
                allow_custom=True,
            )

    # General fallback
    return DEFAULT_FACET


# ==============================================================================
# Shorthand Conversational Resolution
# ==============================================================================

def resolve_shorthand_clarification(
    reply: str,
    pending_options: List[Dict[str, Any]],
    original_query: str = "",
) -> Optional[str]:
    """
    Resolves conversational shorthand answers (e.g. "1", "A", "first one", "cleansers")
    against a list of active clarification options.
    Returns the resolved executable query, or None if not a shorthand match.
    """
    if not pending_options:
        return None

    r = reply.strip().casefold()

    # Numeric & ordinal shortcuts
    ord_map = {
        "1": 0, "first": 0, "1st": 0, "one": 0, "a": 0, "option 1": 0, "opt 1": 0, "the first one": 0,
        "2": 1, "second": 1, "2nd": 1, "two": 1, "b": 1, "option 2": 1, "opt 2": 1, "the second one": 1,
        "3": 2, "third": 2, "3rd": 2, "three": 2, "c": 2, "option 3": 2, "opt 3": 2, "the third one": 2,
        "4": 3, "fourth": 3, "4th": 3, "four": 3, "d": 3, "option 4": 3, "opt 4": 3, "the fourth one": 3,
    }

    if r in ord_map and ord_map[r] < len(pending_options):
        return pending_options[ord_map[r]].get("query")

    # Match by key topic words in option title
    for opt in pending_options:
        opt_title = opt.get("title", "").casefold()
        opt_query = opt.get("query", "")
        # If user typed an exact distinctive active or category from an option title
        for keyword in ("cleanser", "serum", "moisturizer", "sunscreen", "bha", "aha", "salicylic", "niacinamide", "azelaic", "ceramide", "retinol", "cica", "oat"):
            if keyword in r and keyword in opt_title:
                return opt_query

    return None
