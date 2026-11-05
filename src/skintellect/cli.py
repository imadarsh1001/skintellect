"""
Skintellect Product Intelligence Suite - Master Entrypoint
===========================================================
Unified command-line interface for formulation scoring, personalized
recommendations, granular filtering, data export, multi-agent evaluation,
and the interactive Formulation Studio web application.

Usage Examples:
  # View catalog metrics, categories, origins, and skin goals
  python -m skintellect stats

  # Personalized recommendations by category, skin goal, and country
  python -m skintellect recommend --category sunscreens --country "South Korea" --min-match 85
  python -m skintellect recommend --goal "Brightening" --limit 10
  python -m skintellect recommend --category serums --fungal-safe

  # Granular database querying and filtering
  python -m skintellect filter --category toners --active niacinamide --fragrance-free
  python -m skintellect filter --country "Japan" --goal "Hydration"

  # Offline formulation evaluation and score breakdown
  python -m skintellect score --product "Barrier Restoring Cream"
  python -m skintellect score --ingredients "Water, Niacinamide, Glycerin, Ceramide NP"

  # Multi-Agent Formulation Board deliberation
  python -m skintellect agent --formula "Water, Salicylic Acid, Glycolic Acid" --persona acne_prone

  # Ingredient CSI investigation
  python -m skintellect agent --csi --csi-problems "Product A; Product B" --csi-safes "Safe Cream"

  # Launch interactive Formulation Studio web server
  python -m skintellect web --port 8000
"""

import argparse
import json
import sqlite3
import sys
from collections import Counter

# Ensure UTF-8 stdout
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


from skintellect.catalog.personas import export_personas_json
from skintellect.catalog.recommendations import get_recommendations, search_products
from skintellect.catalog.store import CATEGORIES, PRICE_RANGES
from skintellect.config import DB_PATH
from skintellect.database import export_json, export_reviews_json, init_db
from skintellect.formulation.scoring import score_any_product
from skintellect.ingestion.maintenance import clean_database, run_audit


def cmd_stats(args):
    """Displays current database metrics, category breakdown, countries, and skin goals."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products WHERE has_detail = 1")
    detailed = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products WHERE match_score = 100")
    score_100 = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products WHERE match_score >= 95")
    score_95 = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products WHERE match_score >= 90")
    score_90 = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products WHERE fungal_acne_safe = 1")
    fa_safe = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products WHERE fragrance_free = 1")
    frag_free = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products WHERE oil_free = 1")
    oil_free = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM ingredients")
    total_ings = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM product_ingredients")
    total_links = cur.fetchone()[0]

    # Review counts
    cur.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cur.fetchone()[0]

    # Category counts
    cur.execute("SELECT category_slug, COUNT(*) FROM products GROUP BY category_slug ORDER BY COUNT(*) DESC")
    cat_counts = cur.fetchall()

    # Brand Origin breakdown
    cur.execute("SELECT brand_country, COUNT(*) FROM products GROUP BY brand_country ORDER BY COUNT(*) DESC LIMIT 10")
    country_counts = cur.fetchall()

    # Price Tier breakdown
    cur.execute("SELECT price_tier, COUNT(*) FROM products GROUP BY price_tier ORDER BY price_tier_num ASC")
    price_counts = cur.fetchall()

    # Skin goals aggregation
    cur.execute("SELECT skin_goals FROM products WHERE skin_goals IS NOT NULL AND skin_goals != ''")
    goal_counter = Counter()
    for row in cur.fetchall():
        try:
            goals = json.loads(row[0])
            if isinstance(goals, list):
                goal_counter.update(goals)
        except Exception:
            pass

    conn.close()

    print("\n" + "=" * 65)
    print("       🔬 SKINTELLECT FORMULATION INTELLIGENCE METRICS")
    print("=" * 65)
    print(f"  Total Catalog Products : {total:,}")
    print(f"  Deeply Enriched Profiles: {detailed:,} ({round(detailed/total*100 if total else 0, 1)}%)")
    print(f"  Ingredients Master DB  : {total_ings:,} ingredients ({total_links:,} links)")
    print(f"  User Reviews Database  : {total_reviews:,} parsed community reviews")
    print("-" * 65)
    print("  Formulation Match Distribution (Target: Oily/Acne/Sensitive):")
    print(f"    • 100% Perfect Matches : {score_100:,} products")
    print(f"    • 95%+ Compatible      : {score_95:,} products")
    print(f"    • 90%+ Compatible      : {score_90:,} products")
    print("-" * 65)
    print("  Ingredient Safety Flags:")
    print(f"    • Fungal Acne (Malassezia) Safe : {fa_safe:,} products")
    print(f"    • Fragrance-Free                : {frag_free:,} products")
    print(f"    • Oil-Free                      : {oil_free:,} products")
    print("-" * 65)
    print("  Category Coverage:")
    for cat_slug, cnt in cat_counts:
        display = CATEGORIES.get(cat_slug, cat_slug.capitalize())
        print(f"    • {display:<16} : {cnt:>4} products")
    print("-" * 65)
    print("  Price Tier Distribution:")
    for tier, cnt in price_counts:
        range_str = PRICE_RANGES.get(tier, 'Moderate ($15-$30)')
        print(f"    • {tier:<6} ({range_str:<20}) : {cnt:>4} products")
    print("-" * 65)
    print("  Top Brand Origin Countries:")
    for country, cnt in country_counts:
        print(f"    • {country:<16} : {cnt:>4} products")
    if goal_counter:
        print("-" * 65)
        print("  Top Skin Goals Targeted:")
        for goal, cnt in goal_counter.most_common(8):
            print(f"    • {goal:<22} : {cnt:>4} products")
    print("=" * 65 + "\n")


def cmd_recommend(args):
    """Executes multi-criteria personalized recommendation algorithm and prints formatted rankings."""
    cat_slug = args.category.strip().lower() if args.category else None
    results = get_recommendations(
        category=cat_slug,
        brand_country=args.country,
        skin_goal=args.goal,
        min_match=args.min_match,
        limit=args.limit,
        max_cloggers=args.max_cloggers,
        require_fungal_safe=args.fungal_safe,
        require_oil_free=args.oil_free,
        require_fragrance_free=not args.allow_fragrance,
        require_alcohol_free=not args.allow_alcohol,
        price_tier=args.price_tier,
        max_price_tier=args.max_price,
        search_query=args.search
    )

    cat_title = args.category.upper() if args.category else "ALL CATEGORIES"
    filters = []
    if args.country: filters.append(f"Origin: {args.country}")
    if args.goal: filters.append(f"Goal: {args.goal}")
    if args.price_tier: filters.append(f"Price: {args.price_tier}")
    if args.max_price: filters.append(f"Max Price: {['$', '$$', '$$$', '$$$$'][args.max_price-1]}")
    if args.fungal_safe: filters.append("Fungal Acne Safe")
    if args.oil_free: filters.append("Oil-Free")
    filter_str = f" [{', '.join(filters)}]" if filters else ""

    print("\n" + "=" * 80)
    print(f" ⭐ TOP FORMULATION RECOMMENDATIONS: {cat_title}{filter_str}")
    print("=" * 80)

    if not results:
        print("\n [!] No products found matching your exact criteria.")
        print("     Try loosening filters (e.g. lowering --min-match or removing country filter).\n")
        return

    for idx, p in enumerate(results, 1):
        country = p.get('brand_country', 'International')
        p_tier = p.get('price_tier', '$$')
        p_range = p.get('price_range', 'Moderate ($15-$30)')
        p_size = p.get('size', '50 ml')
        p_step = p.get('routine_step', 'Routine Step')
        score = p['match_score']

        print(f"\n#{idx} [{score}% Match] {p['brand']} - {p['name']}")
        print(f"    Origin: {country} | Category: {p['category']} | Routine: {p_step}")
        print(f"    Price: {p_tier} ({p_range}) | Size: {p_size} | Rating: {p['rating']}★ ({p['review_count']} reviews)")
        print(f"    Safety: FA-Safe: {'✓' if p['fungal_acne_safe']==1 else '✗'} | Frag-Free: {'✓' if p['fragrance_free']==1 else '✗'} | Oil-Free: {'✓' if p['oil_free']==1 else '✗'} | Pore Cloggers: {p['comedogenic_max']}")

        if p.get('skin_goals'):
            try:
                goals = json.loads(p['skin_goals']) if isinstance(p['skin_goals'], str) else p['skin_goals']
                if goals:
                    print(f"    Skin Goals: {', '.join(goals)}")
            except Exception:
                pass

        if p['analysis']['brighteners']:
            print(f"    Brightening Actives: {', '.join(p['analysis']['brighteners'])}")
        if p['analysis']['hydrators']:
            print(f"    Barrier & Hydration: {', '.join(p['analysis']['hydrators'])}")
        if p['analysis']['soothers']:
            print(f"    Soothing & Calming : {', '.join(p['analysis']['soothers'])}")
        if p['short_desc']:
            print(f"    Summary: {p['short_desc'][:120]}...")

    print("\n" + "=" * 80 + "\n")


def cmd_filter(args):
    """Granular interactive querying of the SQLite database across multiple attributes."""
    cat_slug = args.category.strip().lower() if args.category else None
    results = search_products(
        category=cat_slug,
        brand_country=args.country,
        skin_goal=args.goal,
        price_tier=args.price_tier,
        max_price_tier=args.max_price,
        min_match=args.min_match,
        fragrance_free=args.fragrance_free,
        fungal_safe=args.fungal_safe,
        oil_free=args.oil_free,
        silicone_free=args.silicone_free,
        alcohol_free=args.alcohol_free,
        min_rating=args.min_rating,
        active_ingredient=args.active,
        search_query=args.search,
        max_cloggers=args.max_cloggers,
        limit=args.limit
    )

    print(f"\n[*] Found {len(results)} matching products:")
    print("-" * 70)
    if not results:
        print("\n [!] No products matched your query.\n")
        return

    for idx, p in enumerate(results, 1):
        country = p.get('brand_country', 'International')
        category = p.get('category_slug', 'moisturizers')
        p_tier = p.get('price_tier', '$$')
        p_range = p.get('price_range', 'Moderate ($15-$30)')
        print(f"\n#{idx} [{p['match_score']}% Match] {p['brand']} - {p['name']} ({country} · {category})")
        print(f"    Price: {p_tier} ({p_range}) | Rating: {p['rating']} ({p['review_count']} reviews) | URL: {p['url']}")
        print(f"    Badges: FA Safe: {p['fungal_acne_safe']} | Fragrance-Free: {p['fragrance_free']} | Oil-Free: {p['oil_free']}")
        print(f"    Actives: {', '.join((p['analysis']['brighteners'] + p['analysis']['hydrators'])[:4]) or 'Gentle base'}")
    print("\n" + "-" * 70 + "\n")


def cmd_report(args):
    """Exports JSON data (standalone dashboard generation is retired)."""
    export_json()
    export_personas_json()
    print("[*] Exported products and personas JSON. Standalone dashboard generation is retired in favor of web UI.")


def cmd_export(args):
    """Exports SQLite products table to a clean, indented JSON file."""
    count = export_json()
    export_personas_json()
    print(f"[OK] Successfully exported {count} products and personas.")


def cmd_score(args):
    """Evaluates and explains both Skintellect Match % and Darmeto Points for any formula."""
    ings = None
    if args.ingredients:
        ings = args.ingredients
    elif args.product:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE name LIKE ? OR brand LIKE ? LIMIT 1", (f"%{args.product}%", f"%{args.product}%"))
        row = cur.fetchone()
        conn.close()
        if row and row['ingredients_json']:
            ings = json.loads(row['ingredients_json'])
            print(f"\n[*] Loaded formulation for: {row['brand']} - {row['name']}")
            print(f"[*] Actual Recorded Skintellect Match: {row['match_score']}%")
        else:
            print(f"[!] Could not find detailed ingredients for '{args.product}' in local DB.")
            return

    if not ings:
        print("[!] Please provide ingredients via --ingredients \"Water, Niacinamide, ...\" or --product \"Brand Name\"")
        return

    res = score_any_product(ings, skin_type=args.skin_type, rating=args.rating)
    match_data = res.get('skintellect_match', res.get('skinsort_match', {}))
    darmeto_data = res['darmeto_points']
    actives = res['actives_summary']

    print("\n" + "=" * 65)
    print(" 🔬 REVERSE-ENGINEERED DERMATOLOGICAL EVALUATION")
    print("=" * 65)
    print(f" 🎯 Predicted Skintellect Match   : {match_data['predicted_match_score']}% ({match_data['status']})")
    print(f" 🏆 Clinical Darmeto Points    : {darmeto_data['darmeto_points']} pts ({darmeto_data['tier']})")
    print("=" * 65)

    print("\n 📋 1. Skintellect Match Breakdown:")
    print("    • Baseline Starting Score: 100%")
    if match_data['breakdown']:
        for b in match_data['breakdown']:
            print(f"    • [{b['impact']}] {b['rule']}")
            if b['flagged_ingredients']:
                print(f"      Triggered by: {', '.join(b['flagged_ingredients'])}")
    else:
        print("    • All profile criteria met! Zero sensitivity or condition penalties.")

    print("\n 🔬 2. Darmeto Points Clinical Breakdown:")
    print(f"    • Baseline Compatibility : {darmeto_data['baseline_match']} pts")
    for add in darmeto_data['additions']:
        print(f"    • {add}")
    for ded in darmeto_data['deductions']:
        print(f"    • {ded}")

    print("\n 🌿 3. Detected Targeted Actives:")
    print(f"    • Brighteners (Dark Spots/Dullness): {', '.join(actives['brighteners']) or 'None'}")
    print(f"    • Barrier Reinforcement / Hydrators: {', '.join(actives['barrier_lipids']) or 'None'}")
    print(f"    • Texture / Calming Smoothers      : {', '.join(actives['smoothers']) or 'None'}")
    print(f"    • Malassezia (Fungal Acne) Triggers: {', '.join(actives['fungal_triggers']) or '0 (Safe)'}")
    print(f"    • High Comedogenic Pore Cloggers   : {', '.join(actives['pore_cloggers']) or '0 (Safe)'}")
    print("=" * 65 + "\n")


def cmd_clean(args):
    """Cleans and standardizes categories, ratings, and routine steps."""
    clean_database()


def cmd_audit(args):
    """Runs comprehensive data completeness, ingredient, and review integrity audit."""
    run_audit(DB_PATH)


def cmd_web(args):
    """Starts the FastAPI Formulation Studio web server."""
    try:
        import uvicorn
    except ImportError:
        print("[!] Error: uvicorn is required to run the web server.")
        print("    Install it via: pip install uvicorn fastapi")
        return

    print("\n" + "=" * 65)
    print(" 🚀 STARTING SKINTELLECT FORMULATION STUDIO WEB SERVER")
    print(f" 🌐 URL: http://{args.host}:{args.port}")
    print("=" * 65 + "\n")
    uvicorn.run("skintellect.api.app:app", host=args.host, port=args.port, reload=args.reload)


def cmd_agent(args):
    """Executes Multi-Agent Formulation Board deliberation or Ingredient CSI Detective."""
    import importlib.util

    if args.csi:
        print("\n" + "=" * 60)
        print(" 🕵️‍♂️ INGREDIENT CSI DETECTIVE INVESTIGATION")
        print("=" * 60)
        from skintellect.agents.csi import CSIDetective
        detective = CSIDetective()

        problems = [p.strip() for p in args.csi_problems.split(";")] if args.csi_problems else []
        safes = [s.strip() for s in args.csi_safes.split(";")] if args.csi_safes else []

        if not problems:
            print("[!] Please provide at least one problematic product with --csi-problems 'Brand Name'")
            return

        report = detective.investigate(problems, safes, reaction_type=args.reaction)
        print(f" Reaction Profile: {report['reaction_type'].upper()}")
        print(f" Problem Products Tested: {len(report['problematic_products'])}")
        print(f" Safe Benchmarks Compared: {len(report['safe_products'])}")
        print("-" * 60)
        print(" 🚨 PRIME SUSPECT INGREDIENTS:")
        for s in report["top_suspects"]:
            print(f"   • {s['ingredient']} (Suspect Score: {s['suspect_score']})")
            print(f"     Found in {s['found_in_count']} breakout products; 0 safe benchmarks")
            if s.get("reasons"):
                print(f"     Evidence: {'; '.join(s['reasons'])}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print(" 🔬 MULTI-AGENT FORMULATION DELIBERATION BOARD")
        print("=" * 60)
        from skintellect.agents.board import BoardOrchestrator
        orch = BoardOrchestrator()
        formula = args.formula or "Water, Glycerin, Niacinamide, Butylene Glycol, Ceramide NP"
        persona = args.persona or "uap"
        print(f" Target Skin Persona : {persona.upper()}")
        print(f" User Query          : {args.question}")
        print(f" Formulation Deck    : {formula[:80]}...")
        print("-" * 60)
        res = orch.run_deliberation(formula, persona_id=persona, user_question=args.question)
        for r in res.get("debate", []):
            print(f"\n[{r['round']}] {r['agent']} ({r['badge']})")
            print("-" * 50)
            print(r.get("message") or r.get("summary"))
        print("\n" + "=" * 60)
        v = res.get("verdict", {})
        print(f" ⚖️ FINAL BINDING VERDICT: {v.get('status')} ({v.get('predicted_match')}%)")
        print(f" Darmeto Fit Points: {v.get('darmeto_points')} / 130 pts ({v.get('tier')})")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Skintellect Personalized Skincare Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. stats
    subparsers.add_parser("stats", help="Show database metrics, categories, origins, and skin goals")

    # 2. recommend
    p_rec = subparsers.add_parser("recommend", help="Display top ranked product recommendations")
    p_rec.add_argument("--category", type=str, default=None, help="Filter by category (e.g. sunscreens, serums, toners, moisturizers)")
    p_rec.add_argument("--country", type=str, default=None, help="Filter by brand origin country (e.g. 'South Korea', 'Japan')")
    p_rec.add_argument("--goal", type=str, default=None, help="Filter by target skin goal (e.g. 'Brightening', 'Barrier Repair')")
    p_rec.add_argument("--min-match", type=int, default=85, help="Minimum Skintellect match score")
    p_rec.add_argument("--limit", type=int, default=10, help="Number of recommendations to show")
    p_rec.add_argument("--max-cloggers", type=int, default=1, help="Max allowed pore clogging ingredients")
    p_rec.add_argument("--fungal-safe", action="store_true", help="Require fungal acne safe")
    p_rec.add_argument("--oil-free", action="store_true", help="Require oil-free")
    p_rec.add_argument("--price-tier", type=str, default=None, choices=['$', '$$', '$$$', '$$$$'], help="Filter by price tier ($, $$, $$$, $$$$)")
    p_rec.add_argument("--max-price", type=int, default=None, choices=[1, 2, 3, 4], help="Maximum price tier (1: $, 2: $$, 3: $$$, 4: $$$$)")
    p_rec.add_argument("--search", type=str, default=None, help="Search text across name, brand, or actives")
    p_rec.add_argument("--allow-fragrance", action="store_true", help="Allow formulations with fragrance")
    p_rec.add_argument("--allow-alcohol", action="store_true", help="Allow formulations with drying alcohol")
    p_rec.set_defaults(func=cmd_recommend)

    # 3. filter
    p_filt = subparsers.add_parser("filter", help="Search and filter products interactively")
    p_filt.add_argument("--category", type=str, default=None, help="Filter by category slug")
    p_filt.add_argument("--country", type=str, default=None, help="Filter by brand country")
    p_filt.add_argument("--goal", type=str, default=None, help="Filter by skin goal")
    p_filt.add_argument("--price-tier", type=str, default=None, choices=['$', '$$', '$$$', '$$$$'], help="Filter by price tier ($, $$, $$$, $$$$)")
    p_filt.add_argument("--max-price", type=int, default=None, choices=[1, 2, 3, 4], help="Maximum price tier (1: $, 2: $$, 3: $$$, 4: $$$$)")
    p_filt.add_argument("--min-match", type=int, default=80, help="Minimum Skintellect match score")
    p_filt.add_argument("--fragrance-free", action="store_true", help="Require fragrance-free")
    p_filt.add_argument("--fungal-safe", action="store_true", help="Require fungal acne safe")
    p_filt.add_argument("--oil-free", action="store_true", help="Require oil-free")
    p_filt.add_argument("--silicone-free", action="store_true", help="Require silicone-free")
    p_filt.add_argument("--alcohol-free", action="store_true", help="Require alcohol-free")
    p_filt.add_argument("--min-rating", type=float, default=0.0, help="Minimum user rating")
    p_filt.add_argument("--active", type=str, default=None, help="Specific active ingredient to search for")
    p_filt.add_argument("--search", type=str, default=None, help="Text search across title, brand, and ingredients")
    p_filt.add_argument("--max-cloggers", type=int, default=1, help="Max allowed pore clogging ingredients")
    p_filt.add_argument("--limit", type=int, default=15, help="Max results to display")
    p_filt.set_defaults(func=cmd_filter)

    # 4. report
    p_rep = subparsers.add_parser("report", help="Generate Markdown and HTML dashboards")
    p_rep.add_argument("--format", choices=['all', 'html', 'md'], default='all', help="Report format to generate")
    p_rep.set_defaults(func=cmd_report)

    # 4b. export
    p_exp = subparsers.add_parser("export", help="Export products to clean JSON file")
    p_exp.set_defaults(func=cmd_export)

    # 5. score
    p_score = subparsers.add_parser("score", help="Score any custom formula or product offline")
    p_score.add_argument("--ingredients", type=str, default=None, help="Comma-separated ingredients string")
    p_score.add_argument("--product", type=str, default=None, help="Name or brand of product to score from DB")
    p_score.add_argument("--skin-type", type=str, default="combination", help="User skin type (default: combination)")
    p_score.add_argument("--rating", type=float, default=4.5, help="Product community rating")
    p_score.set_defaults(func=cmd_score)

    # 6. clean
    p_cln = subparsers.add_parser("clean", help="Clean & canonicalize categories, ratings, and routine steps")
    p_cln.add_argument("--no-report", action="store_true", help="Skip regenerating reports after cleaning")
    p_cln.set_defaults(func=cmd_clean)

    # 7. audit
    p_aud = subparsers.add_parser("audit", help="Audit database integrity, missing fields, and duplicate entries")
    p_aud.set_defaults(func=cmd_audit)

    # 8. web
    p_web = subparsers.add_parser("web", help="Start the interactive Formulation Studio web server (FastAPI)")
    p_web.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    p_web.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    p_web.add_argument("--reload", action="store_true", help="Enable live auto-reloading")
    p_web.set_defaults(func=cmd_web)

    # 9. agent
    p_agt = subparsers.add_parser('agent', help='Convene Multi-Agent Formulation Board or run Ingredient CSI investigation')
    p_agt.add_argument('--formula', type=str, default=None, help='Raw ingredient list to deliberate')
    p_agt.add_argument('--persona', type=str, default='uap', help='Target skin persona (default: uap)')
    p_agt.add_argument('--question', type=str, default='Evaluate barrier safety and active balance', help='User question for board')
    p_agt.add_argument('--csi', action='store_true', help='Run Ingredient CSI Detective mode instead of Board')
    p_agt.add_argument('--csi-problems', type=str, default=None, help='Semicolon-separated failure product names or decks')
    p_agt.add_argument('--csi-safes', type=str, default=None, help='Semicolon-separated safe benchmark product names or decks')
    p_agt.add_argument('--reaction', type=str, default='breakouts_acne', choices=['breakouts_acne', 'contact_dermatitis', 'fungal_acne'], help='Reaction type')
    p_agt.set_defaults(func=cmd_agent)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    elif args.command == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()