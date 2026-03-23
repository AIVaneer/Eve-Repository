# ============================================================
# PCVR Studios — scenario.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# PCVR What-If Scenario Simulator
# Test before you deploy. Every parameter change is a bet
# on the token's future.
# ============================================================

import json
import os
import copy
import random
from datetime import datetime

# ── directory for saved results ───────────────────────────
_DIR        = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(_DIR, "scenario_results")

# ── default scenario parameters ──────────────────────────
_DEFAULTS = {
    "name":                "unnamed",
    "days":                30,
    "num_players":         5,
    "daily_earn_per_player": 10000,
    "spend_rate":          0.70,
    "burn_rate":           0.15,
    "lock_rate":           0.10,
    "buy_rate":            0.50,
    "whale_dump":          0,
    "whale_dump_day":      15,
    "new_players_per_day": 0,
    "starting_supply":     1_000_000_000,
    "starting_circ":       100_000_000,
    "daily_cap":           50_000,
}

# ── pre-built scenarios ───────────────────────────────────
SCENARIOS = {
    "baseline": {
        "name": "baseline",
        "days": 30,
        "num_players": 5,
        "daily_earn_per_player": 10000,
        "spend_rate": 0.70,
        "burn_rate": 0.15,
        "lock_rate": 0.10,
        "buy_rate": 0.50,
        "whale_dump": 0,
        "whale_dump_day": 15,
        "new_players_per_day": 0,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 50_000,
    },
    "double_burn": {
        "name": "double_burn",
        "days": 30,
        "num_players": 5,
        "daily_earn_per_player": 10000,
        "spend_rate": 0.70,
        "burn_rate": 0.30,
        "lock_rate": 0.10,
        "buy_rate": 0.50,
        "whale_dump": 0,
        "whale_dump_day": 15,
        "new_players_per_day": 0,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 50_000,
    },
    "triple_burn": {
        "name": "triple_burn",
        "days": 30,
        "num_players": 5,
        "daily_earn_per_player": 10000,
        "spend_rate": 0.70,
        "burn_rate": 0.45,
        "lock_rate": 0.10,
        "buy_rate": 0.50,
        "whale_dump": 0,
        "whale_dump_day": 15,
        "new_players_per_day": 0,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 50_000,
    },
    "mass_adoption": {
        "name": "mass_adoption",
        "days": 30,
        "num_players": 500,
        "daily_earn_per_player": 10000,
        "spend_rate": 0.70,
        "burn_rate": 0.15,
        "lock_rate": 0.10,
        "buy_rate": 0.50,
        "whale_dump": 0,
        "whale_dump_day": 15,
        "new_players_per_day": 50,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 50_000,
    },
    "ghost_town": {
        "name": "ghost_town",
        "days": 30,
        "num_players": 5,
        "daily_earn_per_player": 10000,
        "spend_rate": 0.0,
        "burn_rate": 0.15,
        "lock_rate": 0.10,
        "buy_rate": 0.0,
        "whale_dump": 0,
        "whale_dump_day": 15,
        "new_players_per_day": 0,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 50_000,
    },
    "whale_dump": {
        "name": "whale_dump",
        "days": 30,
        "num_players": 5,
        "daily_earn_per_player": 10000,
        "spend_rate": 0.70,
        "burn_rate": 0.15,
        "lock_rate": 0.10,
        "buy_rate": 0.50,
        "whale_dump": 50_000_000_000,
        "whale_dump_day": 15,
        "new_players_per_day": 0,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 50_000,
    },
    "low_emission": {
        "name": "low_emission",
        "days": 30,
        "num_players": 5,
        "daily_earn_per_player": 2000,
        "spend_rate": 0.70,
        "burn_rate": 0.15,
        "lock_rate": 0.10,
        "buy_rate": 0.50,
        "whale_dump": 0,
        "whale_dump_day": 15,
        "new_players_per_day": 0,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 10_000,
    },
    "high_lock": {
        "name": "high_lock",
        "days": 30,
        "num_players": 5,
        "daily_earn_per_player": 10000,
        "spend_rate": 0.70,
        "burn_rate": 0.15,
        "lock_rate": 0.30,
        "buy_rate": 0.50,
        "whale_dump": 0,
        "whale_dump_day": 15,
        "new_players_per_day": 0,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 50_000,
    },
    "death_spiral": {
        "name": "death_spiral",
        "days": 30,
        "num_players": 5,
        "daily_earn_per_player": 10000,
        "spend_rate": 0.10,
        "burn_rate": 0.05,
        "lock_rate": 0.0,
        "buy_rate": 0.05,
        "whale_dump": 0,
        "whale_dump_day": 15,
        "new_players_per_day": 0,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 50_000,
    },
    "utopia": {
        "name": "utopia",
        "days": 30,
        "num_players": 50,
        "daily_earn_per_player": 10000,
        "spend_rate": 0.90,
        "burn_rate": 0.35,
        "lock_rate": 0.25,
        "buy_rate": 0.80,
        "whale_dump": 0,
        "whale_dump_day": 15,
        "new_players_per_day": 10,
        "starting_supply": 1_000_000_000,
        "starting_circ": 100_000_000,
        "daily_cap": 50_000,
    },
}


# ─────────────────────────────────────────────────────────────
# CORE SIMULATION ENGINE
# ─────────────────────────────────────────────────────────────

def run_scenario(scenario_dict):
    """Run a single scenario simulation.

    Returns a results dict containing:
      - 'params': the merged scenario parameters
      - 'days': list of day-by-day dicts
      - 'summary': final aggregate stats + health status + verdict
    """
    # Merge with defaults so partial dicts still work
    p = dict(_DEFAULTS)
    p.update(scenario_dict)

    # State
    supply      = float(p["starting_supply"])
    circ        = float(p["starting_circ"])
    num_players = float(p["num_players"])
    daily_cap   = float(p["daily_cap"])

    total_emitted = 0.0
    total_spent   = 0.0
    total_burned  = 0.0
    total_locked  = 0.0

    day_records = []

    for day_num in range(1, int(p["days"]) + 1):
        # Player growth
        num_players += float(p["new_players_per_day"])

        # ── Emission (earn) ──────────────────────────────────
        raw_earn   = num_players * float(p["daily_earn_per_player"])
        day_emit   = min(raw_earn, daily_cap)

        circ   += day_emit
        supply += day_emit          # minted into existence
        total_emitted += day_emit

        # ── Spend ────────────────────────────────────────────
        day_spend = day_emit * float(p["spend_rate"])
        total_spent += day_spend

        # ── Burn (% of spend) ────────────────────────────────
        day_burn = day_spend * float(p["burn_rate"])
        circ     = max(0.0, circ - day_burn)
        supply   = max(0.0, supply - day_burn)
        total_burned += day_burn

        # ── Lock (% of spend) ────────────────────────────────
        day_lock = day_spend * float(p["lock_rate"])
        total_locked += day_lock

        # ── Buy-from-store (additional burn) ─────────────────
        buyers     = int(num_players * float(p["buy_rate"]))
        store_burn = buyers * 50 * float(p["burn_rate"])  # ~50 PCVR avg purchase
        circ       = max(0.0, circ - store_burn)
        supply     = max(0.0, supply - store_burn)
        total_burned += store_burn

        # ── Whale dump (one-time event) ───────────────────────
        if int(p["whale_dump"]) > 0 and day_num == int(p["whale_dump_day"]):
            dump_amount = float(p["whale_dump"])
            circ   += dump_amount   # dumped tokens flood circulating supply
            total_emitted += dump_amount

        # ── Health & net emission ─────────────────────────────
        h_ratio     = total_spent / total_emitted if total_emitted > 0 else 1.0
        net_emit    = total_emitted - total_spent - total_burned

        day_records.append({
            "day":          day_num,
            "supply":       supply,
            "circulating":  circ,
            "emitted":      day_emit,
            "spent":        day_spend,
            "burned":       day_burn + store_burn,
            "locked":       day_lock,
            "health_ratio": h_ratio,
            "net_emission": net_emit,
        })

    # ── Final summary ─────────────────────────────────────────
    final_health = (total_spent / total_emitted) if total_emitted > 0 else 1.0
    final_burn_r = (total_burned / total_emitted) if total_emitted > 0 else 0.0
    net_total    = total_emitted - total_spent - total_burned

    if final_health >= 1.0:
        status  = "🟢"
        verdict = "TOKEN THRIVES 🚀"
    elif final_health >= 0.7:
        status  = "🟡"
        verdict = "TOKEN SURVIVES ✅"
    elif final_health >= 0.2:
        status  = "🔴"
        verdict = "TOKEN AT RISK ⚠️"
    else:
        status  = "💀"
        verdict = "TOKEN DIES ❌"

    survived = final_health >= 0.1

    summary = {
        "name":           p["name"],
        "final_supply":   supply,
        "final_circ":     circ,
        "total_emitted":  total_emitted,
        "total_spent":    total_spent,
        "total_burned":   total_burned,
        "total_locked":   total_locked,
        "health_ratio":   final_health,
        "burn_ratio":     final_burn_r,
        "net_emission":   net_total,
        "health_status":  status,
        "verdict":        verdict,
        "survived":       survived,
        "days_simulated": int(p["days"]),
        "timestamp":      datetime.now().isoformat(),
    }

    return {
        "params":  p,
        "days":    day_records,
        "summary": summary,
    }


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def get_scenario(name):
    """Return a pre-built scenario dict by name (raises KeyError if not found)."""
    if name not in SCENARIOS:
        raise KeyError(f"Scenario '{name}' not found. Available: {list(SCENARIOS)}")
    return copy.deepcopy(SCENARIOS[name])


def list_scenarios():
    """Print all available pre-built scenario names."""
    print("\n  Available scenarios:")
    for name in SCENARIOS:
        s = SCENARIOS[name]
        print(f"    • {name:<18}  burn={s['burn_rate']*100:.0f}%  "
              f"spend={s['spend_rate']*100:.0f}%  "
              f"players={int(s['num_players'])}  "
              f"days={s['days']}")
    print()


# ─────────────────────────────────────────────────────────────
# REPORTING
# ─────────────────────────────────────────────────────────────

def _health_emoji(h):
    if h >= 1.0:  return "🟢"
    if h >= 0.7:  return "🟡"
    if h >= 0.5:  return "🟠"
    if h >= 0.2:  return "🔴"
    return "💀"


def _trend_emoji(prev, curr):
    if curr > prev + 0.01:  return "📈"
    if curr < prev - 0.01:  return "📉"
    return "➡️"


def scenario_report(results):
    """Print a detailed report for a single scenario result."""
    p  = results["params"]
    s  = results["summary"]
    dr = results["days"]

    print("\n" + "=" * 54)
    print(f"  🔮 SCENARIO: {s['name'].upper()}")
    print("=" * 54)
    print(f"  Days simulated : {s['days_simulated']}")
    print(f"  Players        : {int(p['num_players'])}"
          + (f"  (+{int(p['new_players_per_day'])}/day)" if p['new_players_per_day'] else ""))
    print(f"  Earn/player/day: {int(p['daily_earn_per_player']):,}")
    print(f"  Daily cap      : {int(p['daily_cap']):,}")
    print(f"  Spend rate     : {p['spend_rate']*100:.0f}%")
    print(f"  Burn rate      : {p['burn_rate']*100:.0f}%")
    print(f"  Lock rate      : {p['lock_rate']*100:.0f}%")
    print(f"  Buy rate       : {p['buy_rate']*100:.0f}%")
    if p["whale_dump"] > 0:
        print(f"  Whale dump     : {int(p['whale_dump']):,} on day {int(p['whale_dump_day'])}")
    print()

    # Day-by-day mini chart (sample every ~5 days or all if <= 10 days)
    step = max(1, len(dr) // 10)
    prev_h = dr[0]["health_ratio"] if dr else 1.0
    print("  Day-by-day health trend:")
    for rec in dr[::step]:
        h    = rec["health_ratio"]
        icon = _health_emoji(h)
        tr   = _trend_emoji(prev_h, h)
        print(f"    Day {rec['day']:>3}  health={h:.3f}  {icon}  {tr}")
        prev_h = h
    print()

    # Final stats
    print(f"  {'─'*48}")
    print(f"  Final supply    : {s['final_supply']:>18,.0f} PCVR")
    print(f"  Final circ      : {s['final_circ']:>18,.0f} PCVR")
    print(f"  Total emitted   : {s['total_emitted']:>18,.0f} PCVR")
    print(f"  Total spent     : {s['total_spent']:>18,.0f} PCVR")
    print(f"  Total burned    : {s['total_burned']:>18,.0f} PCVR 🔥")
    print(f"  Total locked    : {s['total_locked']:>18,.0f} PCVR 🔒")
    print(f"  {'─'*48}")
    print(f"  Health ratio    : {s['health_ratio']:>18.4f}  {s['health_status']}")
    print(f"  Burn ratio      : {s['burn_ratio']:>17.1%}")
    net_label = "🟢 Shrinking" if s['net_emission'] <= 0 else "🔴 Growing"
    print(f"  Net emission    : {s['net_emission']:>18,.0f}  {net_label}")
    print()
    print(f"  ► {s['verdict']}")
    print("=" * 54 + "\n")


def comparison_report(results1, results2):
    """Print a side-by-side comparison of two scenario results."""
    s1 = results1["summary"]
    s2 = results2["summary"]

    def _arrow(v1, v2, higher_is_better=True):
        if v1 == v2:      return "  ="
        if higher_is_better:
            return "  ✅" if v1 > v2 else "  ❌"
        else:
            return "  ✅" if v1 < v2 else "  ❌"

    print("\n" + "=" * 70)
    print("  ⚔️  SCENARIO COMPARISON")
    print("=" * 70)
    lw, rw = 28, 16

    def row(label, v1, v2, fmt="{:,.0f}", hib=True):
        sv1 = fmt.format(v1)
        sv2 = fmt.format(v2)
        arr = _arrow(v1, v2, hib)
        print(f"  {label:<{lw}}  {sv1:>{rw}}  {sv2:>{rw}} {arr}")

    print(f"  {'Metric':<{lw}}  {s1['name']:>{rw}}  {s2['name']:>{rw}}   Winner")
    print(f"  {'─'*66}")

    row("Health ratio",        s1["health_ratio"],  s2["health_ratio"],  fmt="{:.4f}")
    row("Burn ratio",          s1["burn_ratio"],    s2["burn_ratio"],    fmt="{:.1%}")
    row("Total burned (PCVR)", s1["total_burned"],  s2["total_burned"])
    row("Total spent (PCVR)",  s1["total_spent"],   s2["total_spent"])
    row("Net emission (PCVR)", s1["net_emission"],  s2["net_emission"],  hib=False)
    row("Final supply (PCVR)", s1["final_supply"],  s2["final_supply"],  hib=False)
    row("Final circ (PCVR)",   s1["final_circ"],    s2["final_circ"],    hib=False)
    print(f"  {'─'*66}")
    print(f"  {s1['name']:<{lw}}: {s1['verdict']}")
    print(f"  {s2['name']:<{lw}}: {s2['verdict']}")
    print()

    # Winner by health
    if s1["health_ratio"] > s2["health_ratio"]:
        print(f"  🏆 WINNER: {s1['name'].upper()}")
    elif s2["health_ratio"] > s1["health_ratio"]:
        print(f"  🏆 WINNER: {s2['name'].upper()}")
    else:
        print("  🏆 WINNER: TIE")
    print("=" * 70 + "\n")


# ─────────────────────────────────────────────────────────────
# COMPARISON & BULK RUNS
# ─────────────────────────────────────────────────────────────

def compare(scenario_name_1, scenario_name_2):
    """Run both named scenarios and print a side-by-side comparison."""
    r1 = run_scenario(get_scenario(scenario_name_1))
    r2 = run_scenario(get_scenario(scenario_name_2))
    comparison_report(r1, r2)
    return r1, r2


def run_all_scenarios():
    """Run every pre-built scenario and rank by final health ratio."""
    print("\n" + "=" * 54)
    print("  🔮 PCVR SCENARIO SIMULATOR — ALL SCENARIOS")
    print("=" * 54)

    all_results = []
    for name in SCENARIOS:
        r = run_scenario(get_scenario(name))
        all_results.append(r)

    # Sort by health descending
    all_results.sort(key=lambda r: r["summary"]["health_ratio"], reverse=True)

    print(f"\n  {'Rank':<5} {'Name':<18} {'Health':>8} {'Verdict'}")
    print(f"  {'─'*52}")
    for rank, r in enumerate(all_results, 1):
        s = r["summary"]
        print(f"  #{rank:<4} {s['name']:<18} {s['health_ratio']:>8.4f}  {s['verdict']}")
    print("=" * 54 + "\n")
    return all_results


# ─────────────────────────────────────────────────────────────
# SAVE / LOAD
# ─────────────────────────────────────────────────────────────

def save_results(results, filename=None):
    """Save scenario results to a JSON file in RESULTS_DIR."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    if filename is None:
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_slug = results["summary"]["name"].replace(" ", "_")
        filename = f"{name_slug}_{ts}.json"
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  💾 Results saved → {path}")
    return path


def _list_saved_results():
    """Print saved result files in RESULTS_DIR."""
    if not os.path.isdir(RESULTS_DIR):
        print("  No saved results found.")
        return
    files = sorted(f for f in os.listdir(RESULTS_DIR) if f.endswith(".json"))
    if not files:
        print("  No saved results found.")
        return
    print(f"\n  Saved results in {RESULTS_DIR}:")
    for f in files:
        print(f"    • {f}")
    print()


# ─────────────────────────────────────────────────────────────
# CUSTOM SCENARIO BUILDER
# ─────────────────────────────────────────────────────────────

def custom_scenario():
    """Interactive builder: prompts the user for each parameter, then runs the scenario."""
    print("\n" + "=" * 54)
    print("  ✏️  CUSTOM SCENARIO BUILDER")
    print("=" * 54)

    def _ask(prompt, default, cast=float):
        raw = input(f"  {prompt} [{default}]: ").strip()
        if raw == "":
            return default if isinstance(default, cast) else cast(default)
        try:
            return cast(raw)
        except ValueError:
            print(f"    Invalid — using default ({default})")
            return default if isinstance(default, cast) else cast(default)

    name    = input("  Scenario name [custom]: ").strip() or "custom"
    days    = _ask("Days to simulate", 30, int)
    players = _ask("Number of players", 5, int)
    earn_pp = _ask("Daily earn per player", 10000, float)
    cap     = _ask("Daily emission cap", 50000, float)
    spend_r = _ask("Spend rate (0.0–1.0)", 0.70, float)
    burn_r  = _ask("Burn rate  (0.0–1.0)", 0.15, float)
    lock_r  = _ask("Lock rate  (0.0–1.0)", 0.10, float)
    buy_r   = _ask("Buy rate   (0.0–1.0)", 0.50, float)
    new_pp  = _ask("New players per day", 0, float)
    w_dump  = _ask("Whale dump amount (0 = none)", 0, float)
    w_day   = _ask("Whale dump day", 15, int)

    sc = {
        "name":                  name,
        "days":                  days,
        "num_players":           players,
        "daily_earn_per_player": earn_pp,
        "spend_rate":            spend_r,
        "burn_rate":             burn_r,
        "lock_rate":             lock_r,
        "buy_rate":              buy_r,
        "whale_dump":            w_dump,
        "whale_dump_day":        w_day,
        "new_players_per_day":   new_pp,
        "starting_supply":       1_000_000_000,
        "starting_circ":         100_000_000,
        "daily_cap":             cap,
    }

    results = run_scenario(sc)
    scenario_report(results)

    save_q = input("  Save results? [y/N]: ").strip().lower()
    if save_q == "y":
        save_results(results)

    return results


# ─────────────────────────────────────────────────────────────
# INTERACTIVE CLI
# ─────────────────────────────────────────────────────────────

def _cli():
    print("\n" + "=" * 38)
    print("  🔮 PCVR SCENARIO SIMULATOR")
    print("=" * 38)
    print("  © PCVR Studios 2026")
    print("  Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4")
    print()
    print("  'Earn → Hold → Spend → Buy → Earn.")
    print("   If any link breaks, the token dies.'")
    print()
    print("  Test before you deploy.")
    print("  Every parameter change is a bet on")
    print("  the token's future.")
    print("=" * 38)
    print()

    menu = """  Commands:
  1. list       → list all scenarios
  2. run        → run a scenario
  3. compare    → compare two scenarios
  4. all        → run all scenarios + rank
  5. custom     → build custom scenario
  6. results    → view saved results
  7. exit
"""
    print(menu)

    while True:
        try:
            cmd = input("  scenario> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye! 🔮")
            break

        if cmd in ("1", "list"):
            list_scenarios()

        elif cmd in ("2", "run"):
            list_scenarios()
            name = input("  Enter scenario name: ").strip()
            try:
                r = run_scenario(get_scenario(name))
                scenario_report(r)
                save_q = input("  Save results? [y/N]: ").strip().lower()
                if save_q == "y":
                    save_results(r)
            except KeyError as e:
                print(f"  ❌ {e}")

        elif cmd in ("3", "compare"):
            list_scenarios()
            n1 = input("  Scenario 1 name: ").strip()
            n2 = input("  Scenario 2 name: ").strip()
            try:
                compare(n1, n2)
            except KeyError as e:
                print(f"  ❌ {e}")

        elif cmd in ("4", "all"):
            run_all_scenarios()

        elif cmd in ("5", "custom"):
            custom_scenario()

        elif cmd in ("6", "results"):
            _list_saved_results()

        elif cmd in ("7", "exit", "quit", "q"):
            print("\n  Goodbye! 🔮\n")
            break

        else:
            print("  Unknown command. Try: list, run, compare, all, custom, results, exit")
            print()


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    _cli()
