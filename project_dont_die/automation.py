# ============================================================
# PCVR Studios — automation.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# V10 Automation — The system watches. The system responds. 24/7.
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# V10 Phase 3 — Automation Layer
# The system starts thinking for itself. When alerts fire,
# scenarios auto-run, parameters auto-adjust. 24/7 coverage.
# ============================================================

import json
import os
import datetime
import time
import threading

_DIR = os.path.dirname(os.path.abspath(__file__))
_LOG_FILE = os.path.join(_DIR, "automation_log.json")

# ── Graceful module imports ───────────────────────────────────────────────────

def _try_import(name):
    """Import a module from project_dont_die, return (module, None) or (None, err)."""
    import sys
    if _DIR not in sys.path:
        sys.path.insert(0, _DIR)
    try:
        import importlib
        mod = importlib.import_module(name)
        return mod, None
    except Exception as exc:
        return None, str(exc)


# ── Log helpers ───────────────────────────────────────────────────────────────

def _load_log():
    """Load automation log from disk."""
    if os.path.exists(_LOG_FILE):
        try:
            with open(_LOG_FILE, "r") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_log(entries):
    """Persist automation log to disk."""
    try:
        with open(_LOG_FILE, "w") as fh:
            json.dump(entries, fh, indent=2, default=str)
    except Exception:
        pass


# ── AutomationEngine ──────────────────────────────────────────────────────────

class AutomationEngine:
    """
    V10 Automation Engine — evaluates rules continuously and acts on conditions.
    When alerts fire, scenarios auto-run. 24/7 coverage with full safety controls.
    """

    def __init__(self, interval=60, dry_run=False, max_actions_per_hour=10):
        self.rules               = []          # list of rule dicts
        self.running             = False       # is the engine active
        self.paused              = False       # temporarily paused
        self.interval            = interval   # seconds between checks
        self.action_log          = []          # in-memory action history
        self.cooldowns           = {}          # rule_name → last trigger time
        self.dry_run             = dry_run     # if True: log only, don't execute
        self.max_actions_per_hour = max_actions_per_hour
        self._thread             = None
        self._lock               = threading.Lock()

        # Load persisted log
        self.action_log = _load_log()

        # Register all 10 pre-built rules
        self._register_builtin_rules()

    # ── Module access helpers ────────────────────────────────────────────────

    def _mod(self, name):
        """Return a module by name (imports on demand), or None."""
        mod, _ = _try_import(name)
        return mod

    # ── Pre-built rule registration ──────────────────────────────────────────

    def _register_builtin_rules(self):
        """Register all 10 pre-built automation rules."""

        # 1. heavy_dump_response
        def _cond_heavy_dump():
            det = self._mod("detector")
            econ = self._mod("economy")
            if not (det and econ):
                return False
            try:
                result = det.check(
                    getattr(econ, "emitted", 0),
                    getattr(econ, "spent", 0),
                    getattr(econ, "burned", 0),
                    getattr(econ, "locked", 0),
                    getattr(econ, "circ", 0),
                    getattr(econ, "supply", 1_000_000_000),
                    getattr(econ, "cap", 50_000),
                    getattr(econ, "today", 0),
                )
                return result is False
            except Exception:
                return False

        def _act_heavy_dump():
            al = self._mod("alert")
            sc = self._mod("scenario")
            if al:
                al.fire("critical", "debasement",
                        "HEAVY DUMP pattern detected — auto-response triggered",
                        source="automation")
            if sc:
                preset = sc.get_scenario("death_spiral") if hasattr(sc, "get_scenario") else None
                if preset:
                    sc.run_scenario(preset)
            return "Fired CRITICAL alert + ran death_spiral scenario"

        self.add_rule("heavy_dump_response", _cond_heavy_dump, _act_heavy_dump,
                      cooldown_seconds=1800, severity="critical")

        # 2. low_volume_warning
        def _cond_low_volume():
            ld = self._mod("live_data")
            if not ld:
                return False
            try:
                data = ld.get_data(force_refresh=False) or {}
                vol = data.get("volume_24h_usd") or 0
                return vol < 500
            except Exception:
                return False

        def _act_low_volume():
            al = self._mod("alert")
            sc = self._mod("scenario")
            if al:
                al.fire("warning", "economy",
                        "24h volume below $500 — extremely low activity",
                        source="automation")
            if sc:
                preset = sc.get_scenario("baseline") if hasattr(sc, "get_scenario") else None
                if preset:
                    sc.run_scenario(preset)
            return "Fired WARNING alert + ran baseline scenario"

        self.add_rule("low_volume_warning", _cond_low_volume, _act_low_volume,
                      cooldown_seconds=3600, severity="warning")

        # 3. whale_accumulation
        def _cond_whale():
            wt = self._mod("whale_tracker")
            if not wt:
                return False
            try:
                gini_val, _ = wt.gini_coefficient()
                return gini_val > 0.8
            except Exception:
                return False

        def _act_whale():
            al = self._mod("alert")
            sc = self._mod("scenario")
            if al:
                al.fire("danger", "concentration",
                        "Whale concentration critical — Gini > 0.8",
                        source="automation")
            if sc:
                preset = sc.get_scenario("whale_dump") if hasattr(sc, "get_scenario") else None
                if preset:
                    sc.run_scenario(preset)
            return "Fired DANGER alert (whale concentration) + ran whale_dump scenario"

        self.add_rule("whale_accumulation", _cond_whale, _act_whale,
                      cooldown_seconds=7200, severity="danger")

        # 4. health_ratio_critical
        def _cond_health_ratio():
            econ = self._mod("economy")
            if not econ:
                return False
            try:
                emitted = getattr(econ, "emitted", 0)
                burned  = getattr(econ, "burned",  0)
                if emitted <= 0:
                    return False
                return (burned / emitted) < 0.3
            except Exception:
                return False

        def _act_health_ratio():
            al = self._mod("alert")
            sc = self._mod("scenario")
            if al:
                al.fire("critical", "economy",
                        "Economy health ratio below 0.3 — critical inflation risk",
                        source="automation")
            if sc:
                for name in ("death_spiral", "hyperinflation"):
                    preset = sc.get_scenario(name) if hasattr(sc, "get_scenario") else None
                    if preset:
                        sc.run_scenario(preset)
            return "Fired CRITICAL alert + ran death_spiral + hyperinflation scenarios"

        self.add_rule("health_ratio_critical", _cond_health_ratio, _act_health_ratio,
                      cooldown_seconds=3600, severity="critical")

        # 5. positive_momentum
        def _cond_positive_momentum():
            ld = self._mod("live_data")
            if not ld:
                return False
            try:
                data = ld.get_data(force_refresh=False) or {}
                change = data.get("change_24h") or 0
                vol    = data.get("volume_24h_usd") or 0
                return change > 15 and vol > 5000
            except Exception:
                return False

        def _act_positive_momentum():
            al = self._mod("alert")
            sc = self._mod("scenario")
            if al:
                al.fire("info", "economy",
                        "Positive momentum detected — 24h change >+15% with strong volume",
                        source="automation")
            if sc:
                preset = sc.get_scenario("utopia") if hasattr(sc, "get_scenario") else None
                if preset:
                    sc.run_scenario(preset)
            return "Fired INFO alert (positive momentum) + ran utopia scenario"

        self.add_rule("positive_momentum", _cond_positive_momentum, _act_positive_momentum,
                      cooldown_seconds=7200, severity="info")

        # 6. sync_reminder
        def _cond_sync_reminder():
            gs = self._mod("github_sync")
            if not gs:
                return False
            try:
                last = gs.last_sync_time() if hasattr(gs, "last_sync_time") else None
                if not last:
                    return True
                # parse ISO timestamp
                if isinstance(last, str):
                    last_dt = datetime.datetime.fromisoformat(last.replace("Z", "+00:00"))
                    now_dt = datetime.datetime.now(datetime.timezone.utc)
                    delta = now_dt - last_dt
                    return delta.total_seconds() > 86400
                return False
            except Exception:
                return False

        def _act_sync_reminder():
            al = self._mod("alert")
            if al:
                al.fire("warning", "system",
                        "Code out of sync for 24+ hours — run github_sync.py",
                        source="automation")
            return "Fired WARNING alert (sync reminder)"

        self.add_rule("sync_reminder", _cond_sync_reminder, _act_sync_reminder,
                      cooldown_seconds=21600, severity="warning")

        # 7. sentiment_crash
        def _cond_sentiment_crash():
            si = self._mod("smart_integrations")
            if not si:
                return False
            try:
                sent = si.sentiment_report() if hasattr(si, "sentiment_report") else {}
                combined = sent.get("combined", {})
                score = combined.get("score", 0)
                return score < -0.7
            except Exception:
                return False

        def _act_sentiment_crash():
            al = self._mod("alert")
            sc = self._mod("scenario")
            if al:
                al.fire("danger", "economy",
                        "Extremely negative sentiment detected — score below -0.7",
                        source="automation")
            if sc:
                preset = sc.get_scenario("bear_market") if hasattr(sc, "get_scenario") else None
                if preset:
                    sc.run_scenario(preset)
            return "Fired DANGER alert (sentiment crash) + ran bear_market scenario"

        self.add_rule("sentiment_crash", _cond_sentiment_crash, _act_sentiment_crash,
                      cooldown_seconds=3600, severity="danger")

        # 8. vault_empty
        def _cond_vault_empty():
            vt  = self._mod("vault")
            ld  = self._mod("live_data")
            if not vt:
                return False
            try:
                balance = getattr(vt, "vault_balance", None)
                if balance is None and hasattr(vt, "vault_balance"):
                    balance = vt.vault_balance
                if balance is None:
                    balance = 0
                # Check if any revenue streams exist
                has_revenue = False
                if ld:
                    data = ld.get_data(force_refresh=False) or {}
                    has_revenue = (data.get("volume_24h_usd") or 0) > 0
                return balance == 0 and has_revenue
            except Exception:
                return False

        def _act_vault_empty():
            al = self._mod("alert")
            if al:
                al.fire("warning", "vault",
                        "Revenue available but vault is empty — deposit funds",
                        source="automation")
            return "Fired WARNING alert (vault empty with revenue)"

        self.add_rule("vault_empty", _cond_vault_empty, _act_vault_empty,
                      cooldown_seconds=14400, severity="warning")

        # 9. system_degraded
        def _cond_system_degraded():
            val = self._mod("validate")
            if not val:
                return False
            try:
                passed, failed = val.validate_imports()
                return passed < 12
            except Exception:
                return False

        def _act_system_degraded():
            al = self._mod("alert")
            if al:
                al.fire("warning", "system",
                        "System integrity compromised — fewer than 12/16 modules loaded",
                        source="automation")
            return "Fired WARNING alert (system degraded)"

        self.add_rule("system_degraded", _cond_system_degraded, _act_system_degraded,
                      cooldown_seconds=3600, severity="warning")

        # 10. parabolic_move
        def _cond_parabolic():
            ld = self._mod("live_data")
            if not ld:
                return False
            try:
                data   = ld.get_data(force_refresh=False) or {}
                change = data.get("change_24h") or 0
                return change > 50
            except Exception:
                return False

        def _act_parabolic():
            al = self._mod("alert")
            sc = self._mod("scenario")
            if al:
                al.fire("info", "economy",
                        "Parabolic move detected (+50% 24h) — consider taking profits",
                        source="automation")
            if sc:
                preset = (sc.get_scenario("parabolic_crash")
                          if hasattr(sc, "get_scenario") else None)
                if preset:
                    sc.run_scenario(preset)
            return "Fired INFO alert (parabolic move) + ran parabolic_crash scenario"

        self.add_rule("parabolic_move", _cond_parabolic, _act_parabolic,
                      cooldown_seconds=1800, severity="info")

    # ── Rule management ──────────────────────────────────────────────────────

    def add_rule(self, name, condition_fn, action_fn,
                 cooldown_seconds=3600, severity="info", enabled=True):
        """Add a new automation rule."""
        rule = {
            "name":             name,
            "condition_fn":     condition_fn,
            "action_fn":        action_fn,
            "cooldown_seconds": cooldown_seconds,
            "severity":         severity,
            "enabled":          enabled,
            "last_triggered":   None,
            "trigger_count":    0,
        }
        # Replace if exists
        self.rules = [r for r in self.rules if r["name"] != name]
        self.rules.append(rule)

    def remove_rule(self, name):
        """Remove a rule by name. Returns True if found."""
        before = len(self.rules)
        self.rules = [r for r in self.rules if r["name"] != name]
        return len(self.rules) < before

    def enable_rule(self, name):
        """Enable a rule by name. Returns True if found."""
        for r in self.rules:
            if r["name"] == name:
                r["enabled"] = True
                return True
        return False

    def disable_rule(self, name):
        """Disable a rule by name. Returns True if found."""
        for r in self.rules:
            if r["name"] == name:
                r["enabled"] = False
                return True
        return False

    def list_rules(self):
        """Return list of rule summary dicts."""
        result = []
        now = datetime.datetime.utcnow()
        for r in self.rules:
            last = r.get("last_triggered")
            if last:
                try:
                    last_dt = datetime.datetime.fromisoformat(last)
                    elapsed = (now - last_dt).total_seconds()
                    on_cooldown = elapsed < r["cooldown_seconds"]
                    cooldown_remaining = max(0, r["cooldown_seconds"] - elapsed)
                except Exception:
                    on_cooldown = False
                    cooldown_remaining = 0
            else:
                on_cooldown = False
                cooldown_remaining = 0

            result.append({
                "name":               r["name"],
                "enabled":            r["enabled"],
                "severity":           r["severity"],
                "cooldown_seconds":   r["cooldown_seconds"],
                "last_triggered":     last,
                "trigger_count":      r.get("trigger_count", 0),
                "on_cooldown":        on_cooldown,
                "cooldown_remaining": int(cooldown_remaining),
            })
        return result

    def rule_status(self):
        """Print formatted status of all rules."""
        print("\n" + "=" * 52)
        print("  🤖 AUTOMATION RULES STATUS")
        print("=" * 52)
        for info in self.list_rules():
            status = "✅" if info["enabled"] else "⏸️ "
            cd_str = ""
            if info["on_cooldown"]:
                mins = info["cooldown_remaining"] // 60
                cd_str = f"  [cooldown: {mins}m remaining]"
            last = info["last_triggered"]
            last_str = last[:16].replace("T", " ") if last else "never"
            print(f"  {status}  {info['name']:<26}  [{info['severity']:<8}]"
                  f"  triggers: {info['trigger_count']:<4}  last: {last_str}{cd_str}")
        print("=" * 52)

    # ── Cooldown / rate-limit helpers ────────────────────────────────────────

    def _is_on_cooldown(self, rule):
        """Return True if rule is on cooldown."""
        last = rule.get("last_triggered")
        if not last:
            return False
        try:
            last_dt = datetime.datetime.fromisoformat(last)
            elapsed = (datetime.datetime.utcnow() - last_dt).total_seconds()
            return elapsed < rule["cooldown_seconds"]
        except Exception:
            return False

    def _actions_this_hour(self):
        """Return number of actions taken in the last 60 minutes."""
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        count = 0
        for entry in self.action_log:
            try:
                ts = datetime.datetime.fromisoformat(entry.get("timestamp", ""))
                if ts >= cutoff:
                    count += 1
            except Exception:
                pass
        return count

    # ── Core evaluation ──────────────────────────────────────────────────────

    def evaluate_rule(self, rule):
        """
        Check condition, respect cooldown and rate limit, execute action.
        Returns True if the action was triggered.
        """
        if not rule.get("enabled", True):
            return False

        if self._is_on_cooldown(rule):
            return False

        # Safety rate cap
        if self._actions_this_hour() >= self.max_actions_per_hour:
            return False

        try:
            triggered = rule["condition_fn"]()
        except Exception:
            triggered = False

        if not triggered:
            return False

        # Execute action
        result = "DRY RUN — action not executed"
        if not self.dry_run:
            try:
                result = rule["action_fn"]()
                if result is None:
                    result = "action executed"
            except Exception as exc:
                result = f"action failed: {exc}"

        # Update rule state
        now_iso = datetime.datetime.utcnow().isoformat()
        rule["last_triggered"] = now_iso
        rule["trigger_count"]  = rule.get("trigger_count", 0) + 1

        # Log action
        self.log_action(rule["name"], rule["action_fn"].__name__, result,
                        rule["severity"])

        # Also log to history module if available
        hi = self._mod("history")
        if hi and hasattr(hi, "log_event"):
            try:
                hi.log_event("alert", 0,
                             details=f"[automation] {rule['name']}: {result}",
                             source="automation")
            except Exception:
                pass

        return True

    def check_once(self):
        """Run all enabled rules once. Returns count of triggered rules."""
        triggered = 0
        for rule in self.rules:
            if self.evaluate_rule(rule):
                triggered += 1
        return triggered

    # ── Automation loop ──────────────────────────────────────────────────────

    def _loop(self):
        """Background thread loop — runs check_once every self.interval seconds."""
        while self.running:
            if not self.paused:
                try:
                    self.check_once()
                except Exception:
                    pass
            time.sleep(self.interval)

    def start(self):
        """Start the automation loop in a background thread."""
        if self.running:
            print("  ⚠️  Automation engine already running.")
            return
        self.running = True
        self.paused  = False
        self._thread = threading.Thread(target=self._loop, daemon=True, name="AutomationEngine")
        self._thread.start()
        mode = " [DRY RUN]" if self.dry_run else ""
        print(f"  🤖 Automation engine started{mode} — checking every {self.interval}s")

    def stop(self):
        """Stop the automation loop."""
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._thread = None
        print("  🛑 Automation engine stopped.")

    def pause(self):
        """Temporarily pause rule evaluation without stopping the thread."""
        self.paused = True
        print("  ⏸️  Automation engine paused.")

    def resume(self):
        """Resume rule evaluation."""
        self.paused = False
        print("  ▶️   Automation engine resumed.")

    # ── Action logging ───────────────────────────────────────────────────────

    def log_action(self, rule_name, action, result, severity="info"):
        """Log an automated action to memory and disk."""
        entry = {
            "timestamp":          datetime.datetime.utcnow().isoformat(),
            "rule_name":          rule_name,
            "severity":           severity,
            "action_description": action,
            "result":             result,
            "dry_run":            self.dry_run,
        }
        with self._lock:
            self.action_log.append(entry)
            _save_log(self.action_log)

        severity_icons = {
            "info": "ℹ️", "warning": "⚠️", "danger": "🔴", "critical": "🚨"
        }
        icon = severity_icons.get(severity, "ℹ️")
        ts   = entry["timestamp"][:19].replace("T", " ")
        dr   = " [DRY RUN]" if self.dry_run else ""
        print(f"  {icon}  [{ts}] [{rule_name}]{dr} → {result}")

    def action_history(self, n=20):
        """Return last N automated actions."""
        return self.action_log[-n:] if len(self.action_log) >= n else self.action_log[:]

    def action_stats(self):
        """Return breakdown of actions: by rule, by severity, total."""
        stats = {
            "total":      len(self.action_log),
            "by_severity": {},
            "by_rule":     {},
            "dry_run_pct": 0,
        }
        dry_count = 0
        for entry in self.action_log:
            sev  = entry.get("severity", "info")
            name = entry.get("rule_name", "unknown")
            stats["by_severity"][sev]  = stats["by_severity"].get(sev, 0) + 1
            stats["by_rule"][name]     = stats["by_rule"].get(name, 0) + 1
            if entry.get("dry_run"):
                dry_count += 1
        if stats["total"] > 0:
            stats["dry_run_pct"] = round(dry_count / stats["total"] * 100, 1)
        return stats

    def print_action_history(self, n=20):
        """Print last N actions in a formatted table."""
        history = self.action_history(n)
        print("\n" + "=" * 52)
        print(f"  🤖 AUTOMATION HISTORY (last {n})")
        print("=" * 52)
        if not history:
            print("  No automated actions recorded yet.")
        else:
            icons = {"info": "ℹ️", "warning": "⚠️", "danger": "🔴", "critical": "🚨"}
            for entry in reversed(history):
                ts   = entry.get("timestamp", "")[:16].replace("T", " ")
                rule = entry.get("rule_name", "?")
                sev  = entry.get("severity", "info")
                res  = entry.get("result", "")
                dr   = " [DRY]" if entry.get("dry_run") else ""
                icon = icons.get(sev, "ℹ️")
                print(f"  {icon}  {ts}  {rule:<26}{dr}")
                print(f"       └─ {res}")
        print("=" * 52)

    def print_action_stats(self):
        """Print formatted action statistics."""
        stats = self.action_stats()
        print("\n" + "=" * 52)
        print("  🤖 AUTOMATION STATISTICS")
        print("=" * 52)
        print(f"  Total actions   : {stats['total']}")
        print(f"  Dry-run actions : {stats['dry_run_pct']}%")
        print()
        if stats["by_severity"]:
            print("  By severity:")
            icons = {"info": "ℹ️", "warning": "⚠️", "danger": "🔴", "critical": "🚨"}
            for sev, count in sorted(stats["by_severity"].items()):
                print(f"    {icons.get(sev, 'ℹ️')}  {sev:<10}  {count}")
        if stats["by_rule"]:
            print()
            print("  By rule:")
            for name, count in sorted(stats["by_rule"].items(),
                                      key=lambda x: x[1], reverse=True):
                print(f"    {name:<30}  {count}")
        print("=" * 52)

    # ── Status summary ───────────────────────────────────────────────────────

    def status_summary(self):
        """Return a one-line status string for integration with other modules."""
        active_rules  = sum(1 for r in self.rules if r.get("enabled"))
        total_actions = len(self.action_log)
        last_action   = "never"
        if self.action_log:
            last_ts = self.action_log[-1].get("timestamp", "")
            last_action = last_ts[:16].replace("T", " ") if last_ts else "unknown"
        state = "ACTIVE" if self.running else "INACTIVE"
        if self.running and self.paused:
            state = "PAUSED"
        mode = " [DRY RUN]" if self.dry_run else ""
        return (f"{state}{mode} | {active_rules} rules | "
                f"{total_actions} actions | last: {last_action}")


# ── Interactive CLI ───────────────────────────────────────────────────────────

def _print_menu():
    print("""
==================================
🤖 V10 AUTOMATION ENGINE
==================================
Commands:
 1. start      → start automation loop
 2. stop       → stop automation loop
 3. check      → run all rules once
 4. rules      → list all rules
 5. enable     → enable a rule
 6. disable    → disable a rule
 7. history    → action history
 8. stats      → action statistics
 9. dry_run    → toggle dry run mode
10. interval   → change check interval
11. add_rule   → add custom rule
12. pause      → pause automation
13. resume     → resume automation
14. exit
==================================
""")


def _run_cli(engine):
    _print_menu()
    while True:
        try:
            raw = input("\nautomation> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Automation engine shutting down.")
            if engine.running:
                engine.stop()
            break

        if not raw:
            continue

        aliases = {
            "1":  "start",    "2":  "stop",     "3":  "check",
            "4":  "rules",    "5":  "enable",   "6":  "disable",
            "7":  "history",  "8":  "stats",    "9":  "dry_run",
            "10": "interval", "11": "add_rule", "12": "pause",
            "13": "resume",   "14": "exit",
        }
        cmd = aliases.get(raw, raw)

        if cmd == "start":
            engine.start()

        elif cmd == "stop":
            engine.stop()

        elif cmd == "check":
            print("\n  🔍 Running all rules once…")
            triggered = engine.check_once()
            print(f"  ✅ Check complete — {triggered} rule(s) triggered.\n")

        elif cmd == "rules":
            engine.rule_status()

        elif cmd == "enable":
            name = input("  Rule name to enable: ").strip()
            if engine.enable_rule(name):
                print(f"  ✅ Rule '{name}' enabled.\n")
            else:
                print(f"  ❌ Rule '{name}' not found.\n")

        elif cmd == "disable":
            name = input("  Rule name to disable: ").strip()
            if engine.disable_rule(name):
                print(f"  ✅ Rule '{name}' disabled.\n")
            else:
                print(f"  ❌ Rule '{name}' not found.\n")

        elif cmd == "history":
            try:
                n_raw = input("  How many entries? [20]: ").strip()
                n = int(n_raw) if n_raw else 20
            except ValueError:
                n = 20
            engine.print_action_history(n)

        elif cmd == "stats":
            engine.print_action_stats()

        elif cmd == "dry_run":
            engine.dry_run = not engine.dry_run
            state = "ON" if engine.dry_run else "OFF"
            print(f"  🔄 Dry-run mode: {state}\n")

        elif cmd == "interval":
            try:
                new_interval = int(input("  New check interval (seconds) [60]: ").strip() or 60)
                engine.interval = new_interval
                print(f"  ✅ Interval set to {new_interval}s.\n")
            except ValueError:
                print("  ❌ Invalid interval.\n")

        elif cmd == "add_rule":
            print("  ℹ️  Custom rules require Python functions.")
            print("      Use engine.add_rule() in a script for custom rules.\n")

        elif cmd == "pause":
            engine.pause()

        elif cmd == "resume":
            engine.resume()

        elif cmd in ("exit", "quit", "q", "14"):
            print("  👋 Bye.")
            if engine.running:
                engine.stop()
            break

        elif cmd == "help":
            _print_menu()

        else:
            print(f"  ❓ Unknown command: '{raw}'.  Type 'help' for the menu.\n")


if __name__ == "__main__":
    print("\n  © PCVR Studios 2026")
    print("  Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4")
    print("  V10 Automation — The system watches. The system responds. 24/7.\n")
    _engine = AutomationEngine()
    _run_cli(_engine)
