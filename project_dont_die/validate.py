# ============================================================
# PCVR Studios — validate.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# PCVR System Integrity Validator
# Trust but verify. Every module, every function,
# every connection — validated.
# ============================================================

import json
import os
import re
import sys
import importlib
import traceback
from datetime import datetime

# ── Working directory (Pythonista-compatible — no absolute paths) ──
_HERE = os.path.dirname(os.path.abspath(__file__))

# ── Modules that must be importable ───────────────────────────────
REQUIRED_MODULES = [
    "token_data",
    "economy",
    "vault",
    "detector",
    "atlas_graph_core",
    "store",
    "history",
    "whale_tracker",
    "scenario",
    "alert",
    "live_data",
]

# ── Functions / attributes expected in each module ────────────────
REQUIRED_FUNCTIONS = {
    "economy":       ["earn", "spend", "burn", "lock", "report"],
    "vault":         ["deposit_revenue", "lock_tokens", "report"],
    "detector":      ["check"],
    "store":         ["purchase", "CATALOG", "revenue_report"],
    "history":       ["log_event", "get_all", "daily_summary"],
    "whale_tracker": ["add_wallet", "transfer", "concentration_report",
                      "gini_coefficient", "top_holders"],
    "scenario":      ["run_scenario", "compare", "run_all_scenarios",
                      "get_scenario", "list_scenarios"],
    "alert":         ["fire", "health_check", "risk_score",
                      "dashboard", "get_active"],
    "live_data":     ["fetch_dexscreener", "get_data", "market_status",
                      "market_report", "wallet_value"],
}

# ── Runtime data files (OK if absent — created at runtime) ────────
DATA_FILES = [
    ("pcvr_wallets.json",        "whale tracker wallets"),
    ("pcvr_whale_movements.json","whale movement log"),
    ("pcvr_alerts.json",         "alert log"),
    ("pcvr_ledger.json",         "transaction history"),
    ("pcvr_market_data.json",    "cached market data"),
]

# ── Pre-compiled regex patterns ────────────────────────────────────
_RE_ETH_ADDR    = re.compile(r"0x[0-9A-Fa-f]{40}")
_RE_ABS_PATH    = re.compile(r'["\'](?:/[^"\']+|[A-Za-z]:\\[^"\']+)["\']')


# ──────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────

def _add_project_dir_to_path():
    """Ensure project_dont_die/ is on sys.path for importlib."""
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)


def _import(module_name):
    """Import a module by name (from _HERE). Returns (module, error_str)."""
    _add_project_dir_to_path()
    try:
        mod = importlib.import_module(module_name)
        return mod, None
    except Exception as exc:
        return None, str(exc)


# ──────────────────────────────────────────────────────────────────
# 1. MODULE IMPORT VALIDATION
# ──────────────────────────────────────────────────────────────────

def validate_imports():
    """
    Try to import every module in REQUIRED_MODULES.

    Prints:
        ✅ module_name — imported successfully
        ❌ module_name — import failed: {error}

    Returns (passed, failed) counts.
    """
    print("\n── Module Import Validation ──────────────────────────")
    passed = 0
    failed = 0
    for name in REQUIRED_MODULES:
        mod, err = _import(name)
        if mod is not None:
            print(f"  ✅ {name}")
            passed += 1
        else:
            print(f"  ❌ {name} — import failed: {err}")
            failed += 1
    print(f"\n  Result: {passed} passed, {failed} failed")
    return passed, failed


# ──────────────────────────────────────────────────────────────────
# 2. FUNCTION / ATTRIBUTE VALIDATION
# ──────────────────────────────────────────────────────────────────

def validate_functions():
    """
    For each module in REQUIRED_FUNCTIONS, verify every listed
    function or attribute is present.

    Prints:
        ✅ module.function — exists
        ❌ module.function — missing

    Returns (passed, failed) counts.
    """
    print("\n── Function / Attribute Validation ───────────────────")
    passed = 0
    failed = 0
    for module_name, funcs in REQUIRED_FUNCTIONS.items():
        mod, err = _import(module_name)
        if mod is None:
            for fn in funcs:
                print(f"  ❌ {module_name}.{fn} — module not importable: {err}")
                failed += 1
            continue
        for fn in funcs:
            if hasattr(mod, fn):
                print(f"  ✅ {module_name}.{fn}")
                passed += 1
            else:
                print(f"  ❌ {module_name}.{fn} — missing")
                failed += 1
    print(f"\n  Result: {passed} passed, {failed} failed")
    return passed, failed


# ──────────────────────────────────────────────────────────────────
# 3. DATA FILE VALIDATION
# ──────────────────────────────────────────────────────────────────

def validate_data_files():
    """
    For each file in DATA_FILES, check existence and JSON validity.

    Prints:
        ✅ filename — valid JSON (N entries)
        ⚠️  filename — not found (will be created at runtime)
        ❌ filename — corrupt JSON: {error}

    Returns (passed, failed) counts  (missing files count as 0 / 0).
    """
    print("\n── Data File Validation ──────────────────────────────")
    passed = 0
    failed = 0
    for filename, description in DATA_FILES:
        filepath = os.path.join(_HERE, filename)
        if not os.path.exists(filepath):
            print(f"  ⚠️  {filename} — not found (will be created at runtime)  [{description}]")
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            count = len(data) if isinstance(data, (list, dict)) else 1
            print(f"  ✅ {filename} — valid JSON ({count} entries)  [{description}]")
            passed += 1
        except Exception as exc:
            print(f"  ❌ {filename} — corrupt JSON: {exc}  [{description}]")
            failed += 1
    print(f"\n  Result: {passed} valid, {failed} corrupt")
    return passed, failed


# ──────────────────────────────────────────────────────────────────
# 4. CROSS-MODULE INTEGRATION TESTS
# ──────────────────────────────────────────────────────────────────

def validate_integrations():
    """
    Verify that key modules can communicate with each other.

    Each test is wrapped in try/except so a single failure doesn't
    halt the whole suite.

    Prints:
        ✅ integration_name — working
        ❌ integration_name — failed: {error}

    Returns (passed, failed) counts.
    """
    print("\n── Cross-Module Integration Tests ────────────────────")
    results = []

    def _test(name, fn):
        try:
            fn()
            print(f"  ✅ {name}")
            results.append(True)
        except Exception as exc:
            print(f"  ❌ {name} — failed: {exc}")
            results.append(False)

    # economy → history
    def _economy_history():
        economy, _ = _import("economy")
        history, _ = _import("history")
        assert economy is not None, "economy not importable"
        assert history is not None, "history not importable"
        assert callable(getattr(history, "log_event", None)), \
            "history.log_event not callable"
        assert hasattr(economy, "emitted"), "economy.emitted missing"

    _test("economy → history (can log events?)", _economy_history)

    # whale_tracker → history
    def _whale_history():
        wt, _ = _import("whale_tracker")
        history, _ = _import("history")
        assert wt is not None, "whale_tracker not importable"
        assert history is not None, "history not importable"
        assert callable(getattr(wt, "add_wallet", None)), \
            "whale_tracker.add_wallet not callable"
        assert callable(getattr(history, "log_event", None)), \
            "history.log_event not callable"

    _test("whale_tracker → history (can log movements?)", _whale_history)

    # alert → economy
    def _alert_economy():
        alert, _ = _import("alert")
        economy, _ = _import("economy")
        assert alert is not None, "alert not importable"
        assert economy is not None, "economy not importable"
        assert hasattr(economy, "supply"), "economy.supply missing"
        assert callable(getattr(alert, "risk_score", None)), \
            "alert.risk_score not callable"

    _test("alert → economy (can read supply?)", _alert_economy)

    # alert → whale_tracker
    def _alert_whale():
        alert, _ = _import("alert")
        wt, _ = _import("whale_tracker")
        assert alert is not None, "alert not importable"
        assert wt is not None, "whale_tracker not importable"
        assert callable(getattr(wt, "gini_coefficient", None)), \
            "whale_tracker.gini_coefficient not callable"

    _test("alert → whale_tracker (can read Gini?)", _alert_whale)

    # live_data → alert
    def _live_alert():
        live_data, _ = _import("live_data")
        alert, _ = _import("alert")
        assert live_data is not None, "live_data not importable"
        assert alert is not None, "alert not importable"
        assert callable(getattr(live_data, "get_data", None)), \
            "live_data.get_data not callable"
        assert callable(getattr(alert, "fire", None)), \
            "alert.fire not callable"

    _test("live_data → alert (can fire alerts?)", _live_alert)

    # scenario → economy
    def _scenario_economy():
        scenario, _ = _import("scenario")
        economy, _ = _import("economy")
        assert scenario is not None, "scenario not importable"
        assert economy is not None, "economy not importable"
        assert callable(getattr(scenario, "run_scenario", None)), \
            "scenario.run_scenario not callable"
        assert hasattr(economy, "cap"), "economy.cap missing"

    _test("scenario → economy (can read params?)", _scenario_economy)

    # run_all imports all modules
    def _run_all_imports():
        for mod_name in REQUIRED_MODULES:
            mod, err = _import(mod_name)
            assert mod is not None, f"{mod_name} not importable: {err}"

    _test("run_all imports all modules", _run_all_imports)

    passed = sum(results)
    failed = len(results) - passed
    print(f"\n  Result: {passed} passed, {failed} failed")
    return passed, failed


# ──────────────────────────────────────────────────────────────────
# 5. CONFIGURATION VALIDATION
# ──────────────────────────────────────────────────────────────────

EXPECTED_CONTRACT  = "0x05c870C5C6E7AF4298976886471c69Fc722107e4"
# Pair address for the PCVR/USDC liquidity pool on DexScreener — expected in live_data.py and token_data.py
KNOWN_PAIR_ADDRESS = "0x5a84Add7Ad701409F16C2c5B1CE213b024BCE68a"

def validate_config():
    """
    Check critical config values for consistency:
      - Contract address is the same across all modules that define it
      - Supply / circ values are non-negative
      - All file paths used by modules are relative (Pythonista safe)

    Returns (passed, failed) counts.
    """
    print("\n── Configuration Validation ──────────────────────────")
    passed = 0
    failed = 0

    def _ok(label):
        nonlocal passed
        print(f"  ✅ {label}")
        passed += 1

    def _fail(label, reason):
        nonlocal failed
        print(f"  ❌ {label} — {reason}")
        failed += 1

    # Contract address consistency
    contract_holders = {}
    for mod_name in REQUIRED_MODULES + ["run_all"]:
        filepath = os.path.join(_HERE, f"{mod_name}.py")
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as fh:
            src = fh.read()
        # Collect every contract-like address in the file
        addresses = _RE_ETH_ADDR.findall(src)
        for addr in addresses:
            contract_holders.setdefault(addr, []).append(mod_name)

    if not contract_holders:
        _fail("contract address", "no contract addresses found in any module")
    else:
        # Remove the known DEX pair address — it's intentional, not a mismatch
        unexpected = {k: v for k, v in contract_holders.items()
                      if k not in (EXPECTED_CONTRACT, KNOWN_PAIR_ADDRESS)}
        if unexpected:
            _fail("contract address",
                  f"unexpected address(es) found: {list(unexpected.keys())}")
        elif EXPECTED_CONTRACT not in contract_holders:
            _fail("contract address",
                  f"expected address {EXPECTED_CONTRACT} not found in any module")
        else:
            _ok(f"contract address consistent ({EXPECTED_CONTRACT})")

    # Supply / circ sanity
    economy, err = _import("economy")
    if economy is None:
        _fail("economy supply/circ", f"module not importable: {err}")
    else:
        supply = getattr(economy, "supply", None)
        circ   = getattr(economy, "circ",   None)
        if supply is None:
            _fail("economy.supply", "attribute missing")
        elif supply < 0:
            _fail("economy.supply", f"negative value: {supply}")
        else:
            _ok(f"economy.supply = {supply:,}")

        if circ is None:
            _fail("economy.circ", "attribute missing")
        elif circ < 0:
            _fail("economy.circ", f"negative value: {circ}")
        else:
            _ok(f"economy.circ = {circ:,}")

    # No hardcoded absolute paths (Pythonista compatibility)
    for mod_name in REQUIRED_MODULES:
        filepath = os.path.join(_HERE, f"{mod_name}.py")
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as fh:
            src = fh.read()
        matches = _RE_ABS_PATH.findall(src)
        # Filter out things like version strings or URLs that look path-like
        real_paths = [m for m in matches
                      if not m.startswith(("'http", '"http', "'0x", '"0x'))]
        if real_paths:
            _fail(f"{mod_name} file paths",
                  f"possible hardcoded absolute path(s): {real_paths[:3]}")
        else:
            _ok(f"{mod_name} — no hardcoded absolute paths")

    print(f"\n  Result: {passed} passed, {failed} failed")
    return passed, failed


# ──────────────────────────────────────────────────────────────────
# 6. FULL VALIDATION REPORT
# ──────────────────────────────────────────────────────────────────

def full_validation():
    """
    Run all validation checks and produce a summary report.

    Returns a dict with results and overall status.
    """
    print("\n" + "=" * 50)
    print("  🔍 PCVR SYSTEM VALIDATOR")
    print("  Full System Validation Report")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    totals = {"passed": 0, "failed": 0}
    recommendations = []

    def _tally(label, p, f):
        totals["passed"] += p
        totals["failed"] += f
        if f:
            recommendations.append(f"Fix {f} failure(s) in: {label}")

    # 1. Module imports
    p, f = validate_imports()
    _tally("module imports", p, f)

    # 2. Functions
    p, f = validate_functions()
    _tally("function checks", p, f)

    # 3. Data files
    p, f = validate_data_files()
    _tally("data file checks", p, f)

    # 4. Integrations
    p, f = validate_integrations()
    _tally("integration tests", p, f)

    # 5. Config
    p, f = validate_config()
    _tally("config validation", p, f)

    # ── Final score ───────────────────────────────────────────────
    total_checks = totals["passed"] + totals["failed"]
    score_pct = (totals["passed"] / total_checks * 100) if total_checks else 0

    if totals["failed"] == 0:
        status = "🟢 ALL SYSTEMS GO"
    elif totals["failed"] <= 3:
        status = "🟡 MINOR ISSUES"
    else:
        status = "🔴 CRITICAL FAILURES"

    print("\n" + "=" * 50)
    print(f"  FINAL SCORE: {totals['passed']}/{total_checks} passed  ({score_pct:.0f}%)")
    print(f"  STATUS: {status}")

    if recommendations:
        print("\n  Recommendations:")
        for rec in recommendations:
            print(f"    • {rec}")

    print("=" * 50)

    return {
        "timestamp":       datetime.now().isoformat(),
        "passed":          totals["passed"],
        "failed":          totals["failed"],
        "total":           total_checks,
        "score_pct":       round(score_pct, 1),
        "status":          status,
        "recommendations": recommendations,
    }


# ──────────────────────────────────────────────────────────────────
# INTERACTIVE CLI
# ──────────────────────────────────────────────────────────────────

_MENU = """
==================================
🔍 PCVR SYSTEM VALIDATOR
==================================
Commands:
1. full         → full system validation
2. imports      → validate module imports
3. functions    → validate expected functions
4. data         → validate data files
5. integrations → test cross-module wiring
6. config       → validate configuration
7. exit
==================================
"""

_DISPATCH = {
    "1": ("full",         full_validation),
    "full": ("full",      full_validation),
    "2": ("imports",      validate_imports),
    "imports": ("imports",validate_imports),
    "3": ("functions",    validate_functions),
    "functions": ("functions", validate_functions),
    "4": ("data",         validate_data_files),
    "data": ("data",      validate_data_files),
    "5": ("integrations", validate_integrations),
    "integrations": ("integrations", validate_integrations),
    "6": ("config",       validate_config),
    "config": ("config",  validate_config),
}


if __name__ == "__main__":
    _add_project_dir_to_path()

    # If a command was passed as CLI argument, run it directly
    if len(sys.argv) > 1:
        cmd_arg = sys.argv[1].lower()
        if cmd_arg in _DISPATCH:
            _DISPATCH[cmd_arg][1]()
        else:
            print(f"Unknown command: {cmd_arg}")
            print("Valid commands: full, imports, functions, data, integrations, config")
        sys.exit(0)

    # Otherwise, interactive loop
    print(_MENU)
    while True:
        try:
            cmd = input("validate> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Validator shutting down.")
            break

        if cmd in ("7", "exit", "quit", "q"):
            print("👋 Validator shutting down.")
            break

        if cmd in _DISPATCH:
            _DISPATCH[cmd][1]()
        elif cmd == "":
            pass
        else:
            print(f"  Unknown command: '{cmd}'. Type a number 1-7 or name.")
            print(_MENU)
