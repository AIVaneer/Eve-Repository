# © PCVR Studios 2026 — Atlas Omega v1.0
# V7 Economy + V8 Risk + V9 Graph — UNIFIED COMMAND CENTER
#
# Atlas Omega sees everything. One command. Total visibility.
# Earn → Hold → Spend → Buy → Earn. If any link breaks, the token dies.
#
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
# Runs in Pythonista 3 on iOS — standard library only

import json
import os
import datetime
import time

_DIR = os.path.dirname(os.path.abspath(__file__))


# ─── Module loader ────────────────────────────────────────────────────────────

def _try_import(name):
    """Import a module from project_dont_die, return (module, error_str)."""
    import sys
    if _DIR not in sys.path:
        sys.path.insert(0, _DIR)
    try:
        import importlib
        mod = importlib.import_module(name)
        return mod, None
    except Exception as exc:
        return None, str(exc)


# ─── Module metadata ─────────────────────────────────────────────────────────

_MODULE_META = {
    "token_data":          "V7",
    "economy":             "V7",
    "vault":               "V7",
    "detector":            "V8",
    "atlas_graph_core":    "V9",
    "store":               "V7",
    "history":             "V7",
    "whale_tracker":       "V8",
    "scenario":            "V7/V8",
    "alert":               "V8",
    "live_data":           "V8",
    "validate":            "V9",
    "github_sync":         "V9",
    "smart_integrations":  "V10",
    "run_all":             "V7/V8/V9/V10",
}


# ─── OmegaEngine ─────────────────────────────────────────────────────────────

class OmegaEngine:
    """
    The unified brain.  Imports and orchestrates every module in the toolkit.
    Graceful — skips modules that fail to import and keeps going.
    """

    def __init__(self):
        self.modules = {}   # name → module object
        self.errors  = {}   # name → error string
        self.status  = {}   # name → True/False
        self.last_run = None
        self._load_all()

    # ── Loader ──────────────────────────────────────────────────────────────

    def _load_all(self):
        for name in _MODULE_META:
            mod, err = _try_import(name)
            if mod is not None:
                self.modules[name] = mod
                self.status[name]  = True
            else:
                self.errors[name] = err
                self.status[name]  = False

    # ── Data gathering helpers ───────────────────────────────────────────────

    def _market_data(self):
        """Return live_data snapshot dict or {}."""
        ld = self.modules.get("live_data")
        if not ld:
            return {}
        try:
            return ld.get_data(force_refresh=False) or {}
        except Exception:
            return {}

    def _economy_data(self):
        """Return economy module state dict."""
        ec = self.modules.get("economy")
        if not ec:
            return {}
        try:
            return {
                "supply":   getattr(ec, "supply",  1_000_000_000),
                "circ":     getattr(ec, "circ",    100_000_000),
                "cap":      getattr(ec, "cap",      50_000),
                "emitted":  getattr(ec, "emitted",  0),
                "burned":   getattr(ec, "burned",   0),
                "locked":   getattr(ec, "locked",   0),
                "spent":    getattr(ec, "spent",    0),
                "today":    getattr(ec, "today",    0),
            }
        except Exception:
            return {}

    def _vault_data(self):
        """Return vault state dict."""
        vt = self.modules.get("vault")
        if not vt:
            return {}
        try:
            return {
                "balance": getattr(vt, "vault_balance", 0),
                "locked":  getattr(vt, "total_locked",  0),
                "lockers": getattr(vt, "lockers",       []),
                "apy":     vt.vault_apy() if hasattr(vt, "vault_apy") else 0,
            }
        except Exception:
            return {}

    def _whale_data(self):
        """Return whale_tracker summary."""
        wt = self.modules.get("whale_tracker")
        if not wt:
            return {}
        try:
            wallets   = wt.load_wallets() if hasattr(wt, "load_wallets") else []
            top       = wt.top_holders(1) if hasattr(wt, "top_holders") else []
            gini_val, gini_label = (wt.gini_coefficient()
                                    if hasattr(wt, "gini_coefficient") else (0, "N/A"))
            circ, _   = (wt.get_supply() if hasattr(wt, "get_supply") else (1, 1))
            effective = max(circ, sum(w.get("balance", 0) for w in wallets)) or 1
            top_pct   = (top[0]["balance"] / effective * 100) if top else 0
            return {
                "total_wallets": len(wallets),
                "gini":          gini_val,
                "gini_label":    gini_label,
                "top_holder_pct": top_pct,
                "top_holder_id": top[0]["wallet_id"] if top else "N/A",
            }
        except Exception:
            return {}

    def _risk_data(self):
        """Return alert risk score and counts."""
        al = self.modules.get("alert")
        if not al:
            return {}
        try:
            score, interp = al.risk_score() if hasattr(al, "risk_score") else (0, "N/A")
            counts        = (al.count_by_severity()
                             if hasattr(al, "count_by_severity") else {})
            active        = al.get_active() if hasattr(al, "get_active") else []
            return {
                "score":    score,
                "interp":   interp,
                "active":   len(active),
                "critical": counts.get("critical", 0),
                "danger":   counts.get("danger",   0),
                "warning":  counts.get("warning",  0),
            }
        except Exception:
            return {}

    def _scenario_outlook(self):
        """Run baseline, utopia and death_spiral scenarios."""
        sc = self.modules.get("scenario")
        if not sc:
            return {}
        try:
            results = {}
            for name in ("baseline", "utopia", "death_spiral"):
                preset = (sc.get_scenario(name)
                          if hasattr(sc, "get_scenario") else None)
                if preset is None:
                    continue
                r = sc.run_scenario(preset) if hasattr(sc, "run_scenario") else {}
                results[name] = r.get("summary", {})
            return results
        except Exception:
            return {}

    def _graph_data(self):
        """Return atlas_graph_core summary."""
        ag = self.modules.get("atlas_graph_core")
        if not ag:
            return {}
        try:
            core = ag.AtlasGraphCore() if hasattr(ag, "AtlasGraphCore") else None
            if core is None:
                return {}
            core.build()
            core.build_economy()
            result = core.analyze() if hasattr(core, "analyze") else {}
            nodes = result.get("total_nodes", 0)
            edges = result.get("total_edges", 0)
            components = result.get("connected_components", 0)
            hubs       = result.get("hub_nodes", [])
            return {
                "nodes":      nodes,
                "edges":      edges,
                "components": components,
                "hubs":       hubs,
            }
        except Exception:
            return {}

    def _store_data(self):
        """Return store revenue summary."""
        st = self.modules.get("store")
        if not st:
            return {}
        try:
            cat    = getattr(st, "CATALOG",           [])
            txns   = (st._load_transactions()
                      if hasattr(st, "_load_transactions") else [])
            rev    = sum(t.get("price", 0) for t in txns)
            tops   = (st.top_sellers()
                      if hasattr(st, "top_sellers") else [])
            top    = tops[0]["item"] if tops else "N/A"
            return {
                "total_items": len(cat),
                "total_sales": len(txns),
                "revenue":     rev,
                "top_seller":  top,
            }
        except Exception:
            return {}

    def _ledger_data(self):
        """Return last ledger event summary."""
        hi = self.modules.get("history")
        if not hi:
            return {}
        try:
            all_events = hi.get_all() if hasattr(hi, "get_all") else []
            last       = all_events[-1] if all_events else {}
            return {
                "total":      len(all_events),
                "last_type":  last.get("event_type", "N/A"),
                "last_time":  last.get("timestamp", "N/A"),
            }
        except Exception:
            return {}

    def _sync_data(self):
        """Return github_sync last sync time."""
        gs = self.modules.get("github_sync")
        if not gs:
            return {}
        try:
            last = (gs.last_sync_time()
                    if hasattr(gs, "last_sync_time") else None)
            return {"last_sync": last}
        except Exception:
            return {}

    def _validate_data(self):
        """Return validate summary."""
        vl = self.modules.get("validate")
        if not vl:
            return {}
        try:
            passed, failed = (vl.validate_imports()
                              if hasattr(vl, "validate_imports") else (0, 0))
            fn_passed, fn_failed = (vl.validate_functions()
                                    if hasattr(vl, "validate_functions") else (0, 0))
            return {
                "modules_passed":   passed,
                "modules_failed":   failed,
                "functions_passed": fn_passed,
                "functions_failed": fn_failed,
            }
        except Exception:
            return {}

    # ── Recommendation engine ───────────────────────────────────────────────

    def generate_recommendations(self):
        """
        Analyze all available data and return a list of actionable
        recommendation strings.
        """
        recs = []

        risk  = self._risk_data()
        econ  = self._economy_data()
        whale = self._whale_data()
        mkt   = self._market_data()
        vault = self._vault_data()
        sync  = self._sync_data()
        val   = self._validate_data()

        # Risk level
        score = risk.get("score", 0)
        if score > 60:
            recs.append("⚠️  Critical risk level — review alert dashboard immediately")

        # Economy health
        emitted = econ.get("emitted", 0)
        burned  = econ.get("burned",  0)
        if emitted > 0:
            health_ratio = burned / emitted
        else:
            health_ratio = 1.0
        if health_ratio < 0.5:
            recs.append("🔴 Economy unhealthy — emission exceeding burns")

        # Whale concentration
        gini = whale.get("gini", 0)
        if gini > 0.7:
            recs.append("🐋 High whale concentration — distribution needed")

        # Volume
        volume = mkt.get("volume_24h", 0) or mkt.get("volume", 0)
        if 0 < volume < 1000:
            recs.append("📉 Low trading activity — market needs attention")

        # Price change
        change = mkt.get("change_24h", 0) or 0
        if change < -10:
            recs.append("🚨 Heavy dump detected — check whale movements")
        elif change > 10:
            recs.append("🚀 Parabolic move — take profits or add liquidity")

        # Vault
        if vault.get("balance", 0) == 0:
            recs.append("🏦 Vault empty — deposit revenue to build reserves")
        if vault.get("locked", 0) == 0:
            recs.append("🔒 Nothing locked — incentivize locking via vault APY")

        # Sync
        last_sync = sync.get("last_sync")
        if not last_sync:
            recs.append("🔄 Code not synced — run github_sync.py")

        # Validation issues
        if val.get("modules_failed", 0) > 0 or val.get("functions_failed", 0) > 0:
            recs.append("🔍 System issues detected — run validate.py")

        if not recs:
            recs.append("✅ All systems nominal — PCVR economy is healthy")

        # V10 Intelligence — sentiment-based recs
        si = self.modules.get("smart_integrations")
        if si:
            try:
                recs = si.enrich_recommendations(recs)
            except Exception:
                pass

        recs.append(
            "✅ Run scenario.py to test any parameter changes before deploying"
        )
        return recs

    # ── Formatted section builders ──────────────────────────────────────────

    def _section_market(self):
        mkt = self._market_data()
        if not mkt:
            return "  ⚠️  Market data unavailable (live_data module not loaded)"
        ld = self.modules.get("live_data")
        price   = mkt.get("price_usd",   0) or 0
        change  = mkt.get("change_24h",  0) or 0
        volume  = mkt.get("volume_24h",  0) or mkt.get("volume", 0) or 0
        liq     = mkt.get("liquidity",   0) or 0
        status  = ld.market_status()   if ld and hasattr(ld, "market_status")   else "N/A"
        pressure= ld.supply_pressure() if ld and hasattr(ld, "supply_pressure") else "N/A"
        lines = [
            f"  PCVR Price     : ${price:.10f}",
            f"  24h Change     : {change:+.2f}%",
            f"  Volume         : ${volume:,.0f}",
            f"  Liquidity      : ${liq:,.0f}",
            f"  Status         : {status}",
            f"  Supply Pressure: {pressure}",
        ]
        return "\n".join(lines)

    def _section_economy(self):
        ec = self._economy_data()
        if not ec:
            return "  ⚠️  Economy data unavailable (economy module not loaded)"
        emitted = ec.get("emitted", 0)
        burned  = ec.get("burned",  0)
        locked  = ec.get("locked",  0)
        ratio   = (burned / emitted) if emitted > 0 else 1.0
        net     = emitted - burned - locked
        lines = [
            f"  Total Supply   : {ec.get('supply', 0):>18,}",
            f"  Circulating    : {ec.get('circ',   0):>18,}",
            f"  Daily Cap      : {ec.get('cap',    0):>18,}",
            f"  Total Emitted  : {emitted:>18,}",
            f"  Total Burned   : {burned:>18,} 🔥",
            f"  Total Locked   : {locked:>18,} 🔒",
            f"  Health Ratio   : {ratio:.4f}",
            f"  Net Emission   : {net:>+18,}",
        ]
        return "\n".join(lines)

    def _section_vault(self):
        vt = self._vault_data()
        if not vt:
            return "  ⚠️  Vault data unavailable (vault module not loaded)"
        lines = [
            f"  Balance        : {vt.get('balance', 0):>18,} PCVR",
            f"  Locked         : {vt.get('locked',  0):>18,} PCVR",
            f"  APY            : {vt.get('apy',     0):.1f}%",
            f"  Lock Period    : 90 days",
        ]
        return "\n".join(lines)

    def _section_whale(self):
        wh = self._whale_data()
        if not wh:
            return "  ⚠️  Whale data unavailable (whale_tracker module not loaded)"
        gini  = wh.get("gini", 0)
        label = wh.get("gini_label", "N/A")
        top   = wh.get("top_holder_pct", 0)
        lines = [
            f"  Total Wallets  : {wh.get('total_wallets', 0)}",
            f"  Gini Coefficient: {gini:.4f}",
            f"  Top Holder     : {top:.2f}% of supply ({wh.get('top_holder_id','N/A')})",
            f"  Concentration  : {label}",
        ]
        return "\n".join(lines)

    def _section_risk(self):
        rk = self._risk_data()
        if not rk:
            return "  ⚠️  Risk data unavailable (alert module not loaded)"
        score  = rk.get("score",    0)
        interp = rk.get("interp",   "N/A")
        active = rk.get("active",   0)
        if score >= 70:
            indicator = "🔴"
        elif score >= 40:
            indicator = "🟡"
        else:
            indicator = "🟢"
        lines = [
            f"  Risk Score     : {score}/100",
            f"  Status         : {indicator} {interp}",
            f"  Active Alerts  : {active}",
            f"  Critical       : {rk.get('critical', 0)} | "
            f"Danger: {rk.get('danger', 0)} | "
            f"Warning: {rk.get('warning', 0)}",
        ]
        return "\n".join(lines)

    def _section_scenario(self):
        sc = self._scenario_outlook()
        if not sc:
            return "  ⚠️  Scenario data unavailable (scenario module not loaded)"

        def _fmt(name, summary):
            verdict = summary.get("verdict", "N/A")
            if "SURVIVES" in verdict.upper():
                icon = "✅"
            elif "THRIVES" in verdict.upper():
                icon = "🚀"
            elif "DIES" in verdict.upper():
                icon = "❌"
            else:
                icon = "❓"
            return f"  {name:<20}: {verdict} {icon}"

        lines = []
        for key, label in [
            ("baseline",     "Baseline 30-day"),
            ("utopia",       "Best Case (utopia)"),
            ("death_spiral", "Worst Case (death_spiral)"),
        ]:
            if key in sc:
                lines.append(_fmt(label, sc[key]))
            else:
                lines.append(f"  {label:<20}: N/A")
        return "\n".join(lines)

    def _section_graph(self):
        gd = self._graph_data()
        if not gd:
            return "  ⚠️  Graph data unavailable (atlas_graph_core module not loaded)"
        hubs = gd.get("hubs", [])
        hub_str = ", ".join(str(h) for h in hubs[:5]) if hubs else "none"
        lines = [
            f"  Total Nodes    : {gd.get('nodes', 0)}",
            f"  Total Edges    : {gd.get('edges', 0)}",
            f"  Components     : {gd.get('components', 0)}",
            f"  Hub Nodes      : [{hub_str}]",
        ]
        return "\n".join(lines)

    def _section_store(self):
        st = self._store_data()
        if not st:
            return "  ⚠️  Store data unavailable (store module not loaded)"
        lines = [
            f"  Total Items    : {st.get('total_items', 0)}",
            f"  Total Sales    : {st.get('total_sales', 0)}",
            f"  Revenue        : {st.get('revenue', 0):,.0f} PCVR",
            f"  Top Seller     : {st.get('top_seller', 'N/A')}",
        ]
        return "\n".join(lines)

    def _section_ledger(self):
        ld = self._ledger_data()
        if not ld:
            return "  ⚠️  Ledger data unavailable (history module not loaded)"
        lines = [
            f"  Total Events   : {ld.get('total', 0)}",
            f"  Last Event     : {ld.get('last_type', 'N/A')} at {ld.get('last_time', 'N/A')}",
        ]
        return "\n".join(lines)

    def _section_sync(self):
        sd = self._sync_data()
        if not sd:
            return "  ⚠️  Sync data unavailable (github_sync module not loaded)"
        last = sd.get("last_sync")
        if last:
            ts     = last[:19].replace("T", " ")
            status = "✅ Synced"
        else:
            ts     = "Never"
            status = "⚠️  Not synced"
        lines = [
            f"  Last Sync      : {ts}",
            f"  Status         : {status}",
        ]
        return "\n".join(lines)

    def _intel_data(self):
        """Return intelligence summary dict from smart_integrations, or {}."""
        si = self.modules.get("smart_integrations")
        if not si:
            return {}
        try:
            sent = si.sentiment_report()
            news = sent.get("pcvr_results", [])
            headline = news[0].get("title", "") if news else ""
            return {
                "combined":  sent.get("combined", {}),
                "pcvr":      sent.get("pcvr", {}),
                "market":    sent.get("market", {}),
                "headline":  headline,
                "available": True,
            }
        except Exception:
            return {}

    def _section_intel(self):
        """Formatted intelligence / sentiment section."""
        intel = self._intel_data()
        if not intel:
            return "  ⚠️  Intelligence data unavailable (smart_integrations not loaded)"
        combined = intel.get("combined", {})
        pcvr_s   = intel.get("pcvr", {})
        market_s = intel.get("market", {})
        headline = intel.get("headline", "")
        _label_emoji = {"BULLISH": "📈", "BEARISH": "📉", "NEUTRAL": "⚖️ "}
        c_label  = combined.get("label", "N/A")
        c_score  = combined.get("score",  0.0)
        c_emoji  = _label_emoji.get(c_label, "⚖️ ")
        lines = [
            f"  PCVR Sentiment : {pcvr_s.get('label','N/A')} "
            f"({pcvr_s.get('score', 0.0):+.2f})",
            f"  Market         : {market_s.get('label','N/A')} "
            f"({market_s.get('score', 0.0):+.2f})",
            f"  Combined       : {c_emoji} {c_label} ({c_score:+.2f})",
        ]
        if headline:
            lines.append(f"  Latest News    : {headline[:50]}")
        return "\n".join(lines)

    def _section_health(self):
        vd  = self._validate_data()
        loaded  = sum(1 for v in self.status.values() if v)
        total   = len(self.status)
        if not vd:
            fn_pass = "?"
            fn_total = "?"
            system_status = "⚠️  validate module not loaded"
        else:
            fn_pass  = vd.get("functions_passed", 0)
            fn_total = fn_pass + vd.get("functions_failed", 0)
            failed_m = vd.get("modules_failed",   0)
            failed_f = vd.get("functions_failed",  0)
            if failed_m == 0 and failed_f == 0:
                system_status = "🟢 ALL SYSTEMS GO"
            elif failed_m + failed_f <= 2:
                system_status = "🟡 MINOR ISSUES"
            else:
                system_status = "🔴 CRITICAL FAILURES"
        lines = [
            f"  Modules Loaded : {loaded}/{total}",
            f"  Functions OK   : {fn_pass}/{fn_total}",
            f"  Status         : {system_status}",
        ]
        return "\n".join(lines)

    # ── Master report ────────────────────────────────────────────────────────

    def omega_report(self):
        """Print the full Atlas Omega unified report."""
        self.last_run = datetime.datetime.utcnow().isoformat()
        W = 52  # box width (inner)

        def _box_top():
            return "╔" + "═" * W + "╗"

        def _box_sep():
            return "╠" + "═" * W + "╣"

        def _box_bot():
            return "╚" + "═" * W + "╝"

        def _box_line(text=""):
            # center text inside the box
            return "║" + text.center(W) + "║"

        print(_box_top())
        print(_box_line("🌐 ATLAS OMEGA — PCVR COMMAND CENTER"))
        print(_box_line("V7 Economy + V8 Risk + V9 Graph — UNIFIED"))
        print(_box_sep())

        # Market
        print("\n📡 MARKET STATUS (V8 — live_data)")
        print(self._section_market())

        # Economy
        print("\n💰 ECONOMY STATUS (V7 — economy)")
        print(self._section_economy())

        # Vault
        print("\n🏦 VAULT STATUS (V7 — vault)")
        print(self._section_vault())

        # Whale
        print("\n🐋 WHALE STATUS (V8 — whale_tracker)")
        print(self._section_whale())

        # Risk
        print("\n🚨 RISK ASSESSMENT (V8 — alert)")
        print(self._section_risk())

        # Scenario
        print("\n🔮 SCENARIO OUTLOOK (V7+V8 — scenario)")
        print(self._section_scenario())

        # Graph
        print("\n🕸️  SYSTEM GRAPH (V9 — atlas_graph_core)")
        print(self._section_graph())

        # Store
        print("\n🏪 STORE STATUS (V7 — store)")
        print(self._section_store())

        # Ledger
        print("\n📋 LEDGER (V7 — history)")
        print(self._section_ledger())

        # Sync
        print("\n🔄 SYNC STATUS (V9 — github_sync)")
        print(self._section_sync())

        # Intelligence (V10 — smart_integrations)
        print("\n🧠 INTELLIGENCE (V10 — smart_integrations)")
        print(self._section_intel())

        # Health
        print("\n🔍 SYSTEM HEALTH (V9 — validate)")
        print(self._section_health())

        # Recommendations
        print()
        print(_box_sep())
        print(_box_line("🧠 OMEGA RECOMMENDATIONS"))
        print(_box_sep())
        for i, rec in enumerate(self.generate_recommendations(), 1):
            print(f"  {i}. {rec}")

        print()
        print(_box_bot())
        print(f"  Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4")
        print("  Earn → Hold → Spend → Buy → Earn. The loop must never break.")

    # ── Quick commands ───────────────────────────────────────────────────────

    def quick_status(self):
        """One-line status summary."""
        mkt   = self._market_data()
        risk  = self._risk_data()
        econ  = self._economy_data()
        whale = self._whale_data()

        price  = mkt.get("price_usd",  0) or 0
        ld     = self.modules.get("live_data")
        status = (ld.market_status() if ld and hasattr(ld, "market_status") else "N/A")

        score  = risk.get("score",  0)
        if score >= 70:
            risk_icon = "🔴"
        elif score >= 40:
            risk_icon = "🟡"
        else:
            risk_icon = "🟢"

        emitted = econ.get("emitted", 0)
        burned  = econ.get("burned",  0)
        health  = (burned / emitted) if emitted > 0 else 1.0

        gini = whale.get("gini", 0)

        line = (
            f"PCVR: ${price:.6f} | {status} | "
            f"Risk: {score}/100 {risk_icon} | "
            f"Health: {health:.2f} | "
            f"Gini: {gini:.2f}"
        )
        ts = datetime.datetime.utcnow().strftime("%H:%M:%S UTC")
        print(f"[{ts}] {line}")
        return line

    def quick_risk(self):
        """Print just the risk section."""
        print("\n🚨 RISK ASSESSMENT (V8 — alert)")
        print(self._section_risk())

    def quick_economy(self):
        """Print just the economy section."""
        print("\n💰 ECONOMY STATUS (V7 — economy)")
        print(self._section_economy())

    def quick_market(self):
        """Print just the market section."""
        print("\n📡 MARKET STATUS (V8 — live_data)")
        print(self._section_market())

    def quick_whale(self):
        """Print just the whale section."""
        print("\n🐋 WHALE STATUS (V8 — whale_tracker)")
        print(self._section_whale())

    # ── Watch mode ───────────────────────────────────────────────────────────

    def watch(self, interval=60):
        """
        Continuous monitoring.  Prints quick_status every `interval` seconds.
        If market status changes severity, prints a full alert block.
        Press Ctrl-C to stop.
        """
        ld = self.modules.get("live_data")
        print(f"👁️  Atlas Omega Watch Mode — refreshing every {interval}s (Ctrl-C to stop)")
        last_status = None
        try:
            while True:
                mkt = self._market_data()
                cur_status = (ld.market_status()
                              if ld and hasattr(ld, "market_status") else "N/A")
                self.quick_status()
                if last_status is not None and cur_status != last_status:
                    print(f"\n⚠️  STATUS CHANGE: {last_status} → {cur_status}")
                    self.quick_risk()
                    self.quick_whale()
                last_status = cur_status
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👁️  Watch mode stopped.")

    # ── Module status ────────────────────────────────────────────────────────

    def module_status(self):
        """Print which modules loaded successfully."""
        loaded = 0
        total  = len(_MODULE_META)
        print("\n🔧 MODULE STATUS")
        print("─" * 42)
        for name, version in _MODULE_META.items():
            ok = self.status.get(name, False)
            if ok:
                loaded += 1
                print(f"  ✅ {name:<22} ({version})")
            else:
                err = self.errors.get(name, "unknown error")
                print(f"  ❌ {name:<22} — {err}")
        print("─" * 42)
        print(f"  Overall: {loaded}/{total} modules operational")

    # ── Trend summary ────────────────────────────────────────────────────────

    def trend_summary(self):
        """Show last 10 history events and activity trend."""
        hi = self.modules.get("history")
        if not hi:
            print("  ⚠️  history module not loaded — no trends available")
            return
        print("\n📈 HISTORY & TRENDS")
        print("─" * 42)
        try:
            all_events = hi.get_all() if hasattr(hi, "get_all") else []
            last10     = all_events[-10:]
            print(f"  Total events : {len(all_events)}")
            print()
            if last10:
                print("  Last 10 events:")
                for ev in reversed(last10):
                    ts  = ev.get("timestamp", "?")[:16].replace("T", " ")
                    typ = ev.get("event_type", "?")
                    amt = ev.get("amount", 0)
                    print(f"    {ts}  {typ:<14}  {amt:>12,.0f} PCVR")
            print()

            # event type breakdown using total_by_type per type
            EVENT_TYPES = getattr(hi, "EVENT_TYPES",
                                  ("earn", "spend", "burn", "lock", "unlock",
                                   "purchase", "vault_deposit", "alert"))
            if hasattr(hi, "total_by_type"):
                type_totals = {}
                for et in EVENT_TYPES:
                    try:
                        total = hi.total_by_type(et)
                        count = sum(1 for e in all_events
                                    if e.get("event_type") == et)
                        if count > 0:
                            type_totals[et] = (count, total)
                    except Exception:
                        pass
                if type_totals:
                    print("  Event type breakdown:")
                    for typ, (cnt, tot) in sorted(type_totals.items(),
                                                  key=lambda x: x[1][0],
                                                  reverse=True):
                        print(f"    {typ:<16} x{cnt:<5}  {tot:>12,.0f} PCVR")

            # simple trend heuristic
            if len(all_events) >= 10:
                recent = all_events[-5:]
                older  = all_events[-10:-5]
                recent_earns = sum(1 for e in recent if e.get("event_type") == "earn")
                older_earns  = sum(1 for e in older  if e.get("event_type") == "earn")
                if recent_earns > older_earns:
                    trend = "📈 Increasing activity"
                elif recent_earns < older_earns:
                    trend = "📉 Decreasing activity"
                else:
                    trend = "➡️  Stable activity"
                print(f"\n  Trend: {trend}")

        except Exception as exc:
            print(f"  ⚠️  Could not read trends: {exc}")
        print("─" * 42)

    # ── Save report ──────────────────────────────────────────────────────────

    def save_report(self, filename=None):
        """
        Save a full JSON report to omega_reports/<filename>.
        Default filename: omega_report_YYYYMMDD_HHMMSS.json
        """
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        if filename is None:
            filename = f"omega_report_{ts}.json"

        reports_dir = os.path.join(_DIR, "omega_reports")
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)

        data = {
            "timestamp":       datetime.datetime.utcnow().isoformat(),
            "version":         "Atlas Omega v1.0 — V7+V8+V9 Unified",
            "market":          self._market_data(),
            "economy":         self._economy_data(),
            "vault":           self._vault_data(),
            "whale":           self._whale_data(),
            "risk":            self._risk_data(),
            "store":           self._store_data(),
            "ledger":          self._ledger_data(),
            "sync":            self._sync_data(),
            "modules_loaded":  sum(1 for v in self.status.values() if v),
            "modules_total":   len(self.status),
            "recommendations": self.generate_recommendations(),
        }

        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)
            print(f"  ✅ Report saved → {filepath}")
        except Exception as exc:
            print(f"  ❌ Could not save report: {exc}")
        return filepath

    # ── Collect all data for CLI display ────────────────────────────────────

    def collect_all(self):
        """Return dict of all data sections (used by save_report)."""
        return {
            "market":   self._market_data(),
            "economy":  self._economy_data(),
            "vault":    self._vault_data(),
            "whale":    self._whale_data(),
            "risk":     self._risk_data(),
            "scenario": self._scenario_outlook(),
            "graph":    self._graph_data(),
            "store":    self._store_data(),
            "ledger":   self._ledger_data(),
            "sync":     self._sync_data(),
        }


# ─── Interactive CLI ──────────────────────────────────────────────────────────

def _print_menu():
    W = 52
    def _box_top(): return "╔" + "═" * W + "╗"
    def _box_sep(): return "╠" + "═" * W + "╣"
    def _box_bot(): return "╚" + "═" * W + "╝"
    def _box_line(t=""): return "║" + t.center(W) + "║"

    print(_box_top())
    print(_box_line("🌐 ATLAS OMEGA — COMMAND CENTER"))
    print(_box_line("V7 Economy + V8 Risk + V9 Graph — UNIFIED"))
    print(_box_sep())
    cmds = [
        (" 1. omega",    "full omega report (everything)"),
        (" 2. quick",    "one-line status"),
        (" 3. market",   "market data (V8)"),
        (" 4. economy",  "economy status (V7)"),
        (" 5. risk",     "risk assessment (V8)"),
        (" 6. whale",    "whale tracker (V8)"),
        (" 7. scenario", "scenario outlook"),
        (" 8. graph",    "system graph (V9)"),
        (" 9. recommend","AI recommendations"),
        ("10. watch",    "continuous monitoring"),
        ("11. modules",  "module status"),
        ("12. trends",   "history & trends"),
        ("13. intel",    "V10 intelligence report"),
        ("14. save",     "save report"),
        ("15. exit",     ""),
    ]
    print("║" + " Commands:".ljust(W) + "║")
    for cmd, desc in cmds:
        if desc:
            line = f"  {cmd:<12} → {desc}"
        else:
            line = f"  {cmd}"
        print("║" + line.ljust(W) + "║")
    print(_box_bot())


def _run_cli(engine):
    _print_menu()
    while True:
        try:
            raw = input("\natlas_omega> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Atlas Omega shutting down.")
            break

        if not raw:
            continue

        # Accept both number and text
        aliases = {
            "1": "omega",  "2": "quick",    "3": "market",
            "4": "economy","5": "risk",      "6": "whale",
            "7": "scenario","8": "graph",    "9": "recommend",
            "10":"watch",  "11":"modules",   "12":"trends",
            "13":"intel",  "14":"save",      "15":"exit",
        }
        cmd = aliases.get(raw, raw)

        if cmd == "omega":
            engine.omega_report()
        elif cmd == "quick":
            engine.quick_status()
        elif cmd == "market":
            engine.quick_market()
        elif cmd == "economy":
            engine.quick_economy()
        elif cmd == "risk":
            engine.quick_risk()
        elif cmd == "whale":
            engine.quick_whale()
        elif cmd == "scenario":
            print("\n🔮 SCENARIO OUTLOOK (V7+V8 — scenario)")
            print(engine._section_scenario())
        elif cmd == "graph":
            print("\n🕸️  SYSTEM GRAPH (V9 — atlas_graph_core)")
            print(engine._section_graph())
        elif cmd == "recommend":
            print("\n🧠 OMEGA RECOMMENDATIONS")
            for i, rec in enumerate(engine.generate_recommendations(), 1):
                print(f"  {i}. {rec}")
        elif cmd == "watch":
            try:
                interval = int(input("  Interval in seconds [60]: ").strip() or 60)
            except (ValueError, EOFError):
                interval = 60
            engine.watch(interval=interval)
        elif cmd == "modules":
            engine.module_status()
        elif cmd == "trends":
            engine.trend_summary()
        elif cmd == "intel":
            si = engine.modules.get("smart_integrations")
            if si:
                si.intelligence_report()
            else:
                print("  ⚠️  smart_integrations module not loaded — run smart_integrations.py")
        elif cmd == "save":
            engine.save_report()
        elif cmd in ("exit", "quit", "q"):
            print("👋 Atlas Omega shutting down.")
            break
        elif cmd == "help":
            _print_menu()
        else:
            print(f"  ❓ Unknown command: '{raw}'.  Type 'help' for the menu.")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Atlas Omega v1.0 — V7+V8+V9 Unified")
    print("  © PCVR Studios 2026")
    print("  Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4\n")
    print("  Initialising OmegaEngine — loading all modules …")
    engine = OmegaEngine()
    loaded = sum(1 for v in engine.status.values() if v)
    total  = len(engine.status)
    print(f"  ✅ {loaded}/{total} modules loaded\n")
    _run_cli(engine)
