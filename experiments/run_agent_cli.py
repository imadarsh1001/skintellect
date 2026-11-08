"""
Standalone Experimental CLI for Multi-Agent Formulation Board & Ingredient CSI Detective.
Belongs to the experiments track and imports directly from experiments packages.
"""
import argparse
import sys
from pathlib import Path

# Add project root to sys.path so experiments can be run standalone
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from experiments.ingredient_csi.detective import CSIDetective
from experiments.specialist_board.board import BoardOrchestrator


def run_csi(args):
    print("\n" + "=" * 60)
    print(" 🕵️‍♂️ INGREDIENT CSI DETECTIVE INVESTIGATION")
    print("=" * 60)
    detective = CSIDetective()

    problems = [p.strip() for p in args.csi_problems.split(";")] if args.csi_problems else []
    safes = [s.strip() for s in args.csi_safes.split(";")] if args.csi_safes else []

    if not problems:
        print("[!] Please provide at least one problematic product with --csi-problems 'Brand Name'")
        return

    report = detective.investigate(problematic_items=problems, safe_items=safes, reaction_type=args.reaction)
    print(f" Reaction Profile: {args.reaction.upper()}")
    print(f" Problem Products Tested: {report['total_problem_products']}")
    print(f" Safe Benchmarks Compared: {report['total_safe_products']}")
    print("-" * 60)
    print(" 🚨 PRIME SUSPECT INGREDIENTS:")
    for s in report["top_suspects"]:
        print(f"   • {s['ingredient']} (Suspect Score: {s['suspect_score']}, Recurrence: {s.get('recurrence_rate', 0)}%)")
        print(f"     Frequency: {s.get('frequency', '')} | Family: {s.get('chemical_family', 'Unknown')}")
        flags = []
        if s.get("is_pore_clogger"): flags.append("Pore Clogger")
        if s.get("is_fungal_trigger"): flags.append("Fungal Trigger")
        if s.get("is_irritant"): flags.append("Irritant")
        if flags:
            print(f"     Flags: {', '.join(flags)}")
    print("=" * 60)


def run_board(args):
    print("\n" + "=" * 60)
    print(" 🔬 MULTI-AGENT FORMULATION DELIBERATION BOARD")
    print("=" * 60)
    orch = BoardOrchestrator()
    formula = args.formula or "Water, Glycerin, Niacinamide, Butylene Glycol, Ceramide NP"
    persona = args.persona or "uap"
    print(f" Target Skin Persona : {persona.upper()}")
    print(f" User Query          : {args.question}")
    print(f" Formulation Deck    : {formula[:80]}...")
    print("-" * 60)
    res = orch.run_deliberation(ingredients_input=formula, persona_id=persona, user_question=args.question)
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
    parser = argparse.ArgumentParser(description="Experimental Formulation Board & CSI Detective")
    parser.add_argument("--formula", type=str, default=None, help="Raw ingredient list to deliberate")
    parser.add_argument("--persona", type=str, default="uap", help="Target skin persona (default: uap)")
    parser.add_argument("--question", type=str, default="Evaluate barrier safety and active balance", help="User question for board")
    parser.add_argument("--csi", action="store_true", help="Run Ingredient CSI Detective mode instead of Board")
    parser.add_argument("--csi-problems", type=str, default=None, help="Semicolon-separated failure product names or decks")
    parser.add_argument("--csi-safes", type=str, default=None, help="Semicolon-separated safe benchmark product names or decks")
    parser.add_argument("--reaction", type=str, default="breakouts_acne", choices=["breakouts_acne", "contact_dermatitis", "fungal_acne"], help="Reaction type")

    args = parser.parse_args()
    if args.csi:
        run_csi(args)
    else:
        run_board(args)


if __name__ == "__main__":
    main()
