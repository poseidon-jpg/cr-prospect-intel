#!/usr/bin/env python3
"""Budget scenario math for a Content Rewards conversation. Distribution math and business math are
kept separate on purpose: views are the delivery unit, not the outcome.

Usage:
  python3 money_math.py --budgets 5000,10000,25000,50000 --cpm 1.0 [--fee 0.10]
        [--paid-cpm 10] [--ctr 0.003] [--cvr 0.02] [--aov 45] [--ltv-mult 1.0]

Output per budget:
  distribution: creator budget after fee, paid-for views at the CPM, equivalent paid-social cost
  business (ONLY if --ctr/--cvr/--aov given): visits, orders, revenue, ROAS, break-even CVR
Every business number is labelled SCENARIO with its assumptions. Never present it as a forecast.

Benchmarks you may cite (all from public pages; re-check before quoting):
  - Content Rewards platform fee: 10% standard, 8% verified, $1,000 minimum (contentrewards.com/pricing)
  - Observed live CPMs on CR: $0.05 (music/logo) to $3+ per 1K; most campaigns $1 to $2 (/c/discover, Oct 2026)
  - Worked example: Michael Sartain campaign $6,841 spent, 4.5M views => ~$1.52 effective CPM
    (contentrewards.com/discover/86842687-ba2b-4638-a024-995dcf3d25a3, 2026-10-08)
  - Per-clip payout caps exist (e.g. $100-$200 max per clip), so budget spreads across many clips
"""
from __future__ import annotations

import argparse
import json
import sys


def scenario(budget: float, cpm: float, fee: float, paid_cpm: float | None, ctr, cvr, aov, ltv_mult) -> dict:
    creator_budget = budget * (1 - fee)
    views = creator_budget / cpm * 1000
    d = {
        "budget": budget,
        "platform_fee": round(budget * fee, 2),
        "creator_budget": round(creator_budget, 2),
        "paid_for_views": int(views),
        "effective_cpm_all_in": round(budget / views * 1000, 2),
    }
    if paid_cpm:
        d["paid_social_cost_for_same_views"] = round(views / 1000 * paid_cpm, 2)
        d["multiple_vs_paid_social"] = round(views / 1000 * paid_cpm / budget, 1)
    if ctr is not None and cvr is not None and aov is not None:
        visits = views * ctr
        orders = visits * cvr
        rev = orders * aov * ltv_mult
        d["SCENARIO_business"] = {
            "assumptions": {"ctr_view_to_visit": ctr, "cvr_visit_to_order": cvr, "aov": aov, "ltv_multiplier": ltv_mult},
            "visits": int(visits), "orders": round(orders, 1), "revenue": round(rev, 2),
            "roas": round(rev / budget, 2),
            "break_even_cvr": round(budget / (visits * aov * ltv_mult), 4) if visits and aov else None,
            "label": "SCENARIO, not a forecast. Organic clips rarely carry links; most impact is search/brand lift.",
        }
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budgets", default="5000,10000,25000,50000,100000")
    ap.add_argument("--cpm", type=float, default=1.0)
    ap.add_argument("--fee", type=float, default=0.10)
    ap.add_argument("--paid-cpm", type=float, default=None)
    ap.add_argument("--ctr", type=float, default=None)
    ap.add_argument("--cvr", type=float, default=None)
    ap.add_argument("--aov", type=float, default=None)
    ap.add_argument("--ltv-mult", type=float, default=1.0)
    a = ap.parse_args()
    if a.cpm <= 0:
        sys.exit("cpm must be > 0")
    rows = [scenario(float(b), a.cpm, a.fee, a.paid_cpm, a.ctr, a.cvr, a.aov, a.ltv_mult)
            for b in a.budgets.split(",") if b.strip()]
    json.dump({"inputs": vars(a), "scenarios": rows}, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
