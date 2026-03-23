# PCVR — Run Everything
# One script to see the full picture

# ── Quick import health check ──────────────────────────────
try:
    import validate as _validate
    _imp_passed, _imp_failed = _validate.validate_imports()
    if _imp_failed:
        print(f"\n⚠️  WARNING: {_imp_failed} module(s) failed to import.")
        print("   Run `validate.py` for full system validation.\n")
    else:
        print(f"\n✅ All {_imp_passed} modules imported successfully.\n")
except Exception:
    pass  # validate.py not available — continue anyway
# ──────────────────────────────────────────────────────────

from token_data import show as token_info
from economy import earn, buy, lock, spend, burn, report as econ_report, new_day
from vault import deposit_revenue, lock_tokens, report as vault_report
from detector import check
from atlas_graph_core import AtlasGraphCore
import economy as e
import store
import history
import whale_tracker
import scenario
import alert
import live_data
try:
    import github_sync as _github_sync
    _GITHUB_SYNC_AVAILABLE = True
except Exception:
    _GITHUB_SYNC_AVAILABLE = False
try:
    import atlas_omega as _atlas_omega
    _ATLAS_OMEGA_AVAILABLE = True
except Exception:
    _ATLAS_OMEGA_AVAILABLE = False
try:
    import smart_integrations as _smart_integrations
    _SMART_INTEGRATIONS_AVAILABLE = True
except Exception:
    _SMART_INTEGRATIONS_AVAILABLE = False
try:
    import automation as _automation
    _AUTOMATION_AVAILABLE = True
except Exception:
    _AUTOMATION_AVAILABLE = False
try:
    import wkapp_ui as _wkapp_ui
    _WKAPP_AVAILABLE = True
except Exception:
    _WKAPP_AVAILABLE = False

print("\n" + "=" * 50)
print("  PCVR STUDIOS — PROJECT DON'T DIE")
print("  Token Economy Engine · March 2026")
print("=" * 50)

# 0a. Live market snapshot
print("\n" + "=" * 50)
print("  📡 PCVR LIVE MARKET SNAPSHOT")
print("=" * 50)
try:
    _market = live_data.get_data(force_refresh=True)
    if _market.get("source") == "live":
        _mp  = _market.get("price_usd") or 0
        _mch = _market.get("change_24h") or 0
        _ms  = live_data.market_status()
        print(f"  Price    : ${_mp:.10f}")
        print(f"  24h Chg  : {_mch:+.2f}%")
        print(f"  Status   : {_ms}")
    else:
        print("  Market data unavailable — running with defaults")
except Exception:
    print("  Market data unavailable — running with defaults")
print(f"{'='*50}\n")

# 0b. Hook economy functions to auto-log to the ledger
history.hook_economy()

# 1. Token info
token_info()

# 2. Simulate 3 days
for day in range(1, 4):
    print(f"\n--- DAY {day} ---")
    new_day()
    earn(8000)
    buy(400); buy(250); buy(150)
    spend(300); burn(50)
    lock(500)
    deposit_revenue(400, "store")
    deposit_revenue(150, "tournament")
    deposit_revenue(100, "premium")

# 3. Lock some tokens in vault
lock_tokens("alpha_1", 5000)
lock_tokens("alpha_2", 8000)
lock_tokens("og_holder", 15000)

# 4. Reports
econ_report()
vault_report()

# 5. Debasement check
check(e.emitted, e.spent, e.burned, e.locked, e.circ, e.supply, e.cap, e.today)

print("© PCVR STUDIOS 2026")
print(f"{'='*50}\n")

# 5b. Whale concentration snapshot
print("=" * 50)
print("  🐋 PCVR WHALE TRACKER — Concentration Snapshot")
print("=" * 50)
_top3 = whale_tracker.top_holders(3)
_circ, _ = whale_tracker.get_supply()
_effective = max(_circ, sum(w["balance"] for w in whale_tracker.load_wallets())) or 1
for _i, _w in enumerate(_top3, 1):
    _pct = _w["balance"] / _effective * 100
    print(f"  #{_i} {_w['wallet_id']:<22} {_w['balance']:>18,}  ({_pct:.2f}%)")
_gini_val, _gini_label = whale_tracker.gini_coefficient()
print(f"  Gini coefficient: {_gini_val}  {_gini_label}")
print(f"{'='*50}\n")

# 6. Atlas Graph Core — quick economy health check
print("=" * 50)
print("  🧠 ATLAS GRAPH CORE v2 — Economy Health")
print("=" * 50)
atlas = AtlasGraphCore()
print(" ", atlas.quick_economy_health())
print(f"{'='*50}\n")

# 7. Store — sample purchases (Spend Engine demo)
print("=" * 50)
print("  🏪 PCVR STORE — SPEND ENGINE DEMO")
print("=" * 50)
_demo_purchases = [
    ("player_001", "Neon Blade Skin"),
    ("player_002", "2x XP Boost (24h)"),
    ("player_003", "Weekly Arena Entry"),
    ("player_001", "Battle Pass — Season 1"),
    ("player_004", "Galaxy Cape"),
    ("player_005", "Reward Multiplier (7d)"),
    ("player_002", "Qualifier Pass"),
    ("player_006", "Genesis Founder Badge"),
]
for pid, item in _demo_purchases:
    try:
        tx = store.purchase(pid, item)
        print(f"  ✅ {pid} bought '{tx['item']}' "
              f"| {tx['price']} PCVR | burned {tx['burned']} 🔥 "
              f"| vaulted {tx['vaulted']} 🔒")
        history.log_event("purchase", tx["price"],
                          details=tx["item"], source=pid)
        history.log_event("burn",     tx["burned"],
                          details=f"store burn — {tx['item']}", source="store")
        history.log_event("vault_deposit", tx["vaulted"],
                          details=f"vault cut — {tx['item']}", source="store")
    except ValueError as ex:
        print(f"  ❌ {ex}")

print()
store.print_revenue_report()
store.print_category_breakdown()

# 8. Log vault locks
history.log_event("lock", 5000,  details="alpha_1 90-day lock",   source="vault")
history.log_event("lock", 8000,  details="alpha_2 90-day lock",   source="vault")
history.log_event("lock", 15000, details="og_holder 90-day lock", source="vault")

# 9. Ledger summary
print("=" * 50)
print("  📜 PCVR LEDGER — TODAY'S SUMMARY")
print("=" * 50)
today = history.daily_summary()
print(f"  Date:         {today['date']}")
print(f"  Earned:       {today['earned']:>10,.0f} PCVR")
print(f"  Spent:        {today['spent']:>10,.0f} PCVR")
print(f"  Burned:       {today['burned']:>10,.0f} PCVR 🔥")
print(f"  Locked:       {today['locked']:>10,.0f} PCVR 🔒")
print(f"  Transactions: {today['transactions']:>10}")
print()
history.report()

# 10. Scenario baseline — 30-day health forecast
print("=" * 50)
print("  🔮 PCVR SCENARIO — BASELINE 30-DAY FORECAST")
print("=" * 50)
_baseline_results = scenario.run_scenario(scenario.get_scenario("baseline"))
_bs = _baseline_results["summary"]
print(f"  Health ratio  : {_bs['health_ratio']:.4f}  {_bs['health_status']}")
print(f"  Total emitted : {_bs['total_emitted']:>14,.0f} PCVR")
print(f"  Total burned  : {_bs['total_burned']:>14,.0f} PCVR 🔥")
print(f"  Net emission  : {_bs['net_emission']:>14,.0f} PCVR")
print(f"  Verdict       : {_bs['verdict']}")
print()
print("  Run `scenario.py` for full what-if simulations")
print(f"{'='*50}\n")

# 11. Alert health check & risk score
print("=" * 50)
print("  🚨 PCVR ALERT ENGINE — Health Check")
print("=" * 50)
alert.health_check()
_score, _interp = alert.risk_score()
print(f"\n  Risk Score: {_score}/100  {_interp}")
_critical_alerts = alert.get_by_severity("critical")
_danger_alerts   = alert.get_by_severity("danger")
for _a in _critical_alerts + _danger_alerts:
    _emoji = "🚨" if _a["severity"] == "critical" else "🔴"
    print(f"  {_emoji}  [{_a['category']}] {_a['message']}")
print()
print("  Run `alert.py` for full alert dashboard")
print(f"{'='*50}\n")

# 12. GitHub Sync status
print("=" * 50)
print("  🔄 PCVR GITHUB SYNC STATUS")
print("=" * 50)
if _GITHUB_SYNC_AVAILABLE:
    _last = _github_sync.last_sync_time()
    if _last:
        _ts = _last[:19].replace("T", " ")
        print(f"  Last sync: {_ts} UTC")
    else:
        print("  ⚠️  Not synced — run github_sync.py")
    print("  Run `github_sync.py` to sync with GitHub")
else:
    print("  ⚠️  github_sync.py not available")
print(f"{'='*50}\n")

_OMEGA_HINT = "  Run `atlas_omega.py` for the full unified command center"

# 13. Atlas Omega — unified command center
if _ATLAS_OMEGA_AVAILABLE:
    print("=" * 50)
    print("  🌐 ATLAS OMEGA — QUICK STATUS")
    print("=" * 50)
    _omega = _atlas_omega.OmegaEngine()
    _omega.quick_status()
    print()
    print(_OMEGA_HINT)
    print(f"{'='*50}\n")
else:
    print(_OMEGA_HINT + "\n")

# 14. Smart Integrations — quick sentiment score
if _SMART_INTEGRATIONS_AVAILABLE:
    print("=" * 50)
    print("  🧠 V10 INTELLIGENCE — SENTIMENT SNAPSHOT")
    print("=" * 50)
    try:
        _sent_data = _smart_integrations.sentiment_report()
        _combined  = _sent_data.get("combined", {})
        _pcvr_s    = _sent_data.get("pcvr", {})
        _market_s  = _sent_data.get("market", {})
        _emoji     = {"BULLISH": "📈", "BEARISH": "📉", "NEUTRAL": "⚖️ "}
        _cl        = _combined.get("label", "N/A")
        _cs        = _combined.get("score",  0.0)
        print(f"  PCVR    : {_pcvr_s.get('label','N/A')} "
              f"({_pcvr_s.get('score', 0.0):+.2f})")
        print(f"  Market  : {_market_s.get('label','N/A')} "
              f"({_market_s.get('score', 0.0):+.2f})")
        print(f"  Combined: {_emoji.get(_cl,'⚖️ ')} {_cl} ({_cs:+.2f})")
        _news = _sent_data.get("pcvr_results", [])
        if _news:
            print(f"  Headline: {_news[0].get('title','')[:55]}")
    except Exception:
        print("  Sentiment data unavailable")
    print("  Run `smart_integrations.py` for full intelligence report")
    print(f"{'='*50}\n")

# ── Dashboard hint ─────────────────────────────────────────────────────────
print("=" * 50)
print("  📊 V10 VISUAL DASHBOARD")
print("=" * 50)
print("  Run `dashboard.py` to launch the visual web dashboard")
print("  → Real-time charts, risk gauges, whale activity,")
print("    economy stats, and market data in any browser.")
print("  → Or use the 'dashboard' command in atlas_omega.py")
print(f"{'='*50}\n")

# ── Automation status ───────────────────────────────────────────────────────
print("=" * 50)
print("  🤖 V10 AUTOMATION ENGINE")
print("=" * 50)
if _AUTOMATION_AVAILABLE:
    try:
        _ae = _automation.AutomationEngine()
        _auto_status = "INACTIVE (not started)"
        print(f"  Automation: {_auto_status}")
        print(f"  Rules     : {len(_ae.rules)} pre-built rules loaded")
        print(f"  Run `automation.py` to start the automation engine")
    except Exception:
        print("  ⚠️  Automation engine could not be initialised")
else:
    print("  ⚠️  automation.py not available")
print(f"{'='*50}\n")

# ── iOS UI hint ─────────────────────────────────────────────────────────────
print("=" * 50)
print("  📱 V10 PYTHONISTA UI")
print("=" * 50)
if _WKAPP_AVAILABLE:
    print("  Run `wkapp_ui.py` in Pythonista for native iOS interface")
    print("  → Native buttons, WKWebView dashboard, live notifications")
    print("  → Requires Pythonista 3 from the iOS App Store")
else:
    print("  Run `wkapp_ui.py` in Pythonista for native iOS interface")
    print("  → Requires Pythonista 3 from the iOS App Store")
print(f"{'='*50}\n")
