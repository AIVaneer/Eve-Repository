# ============================================================
# PCVR Studios — alert.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# PCVR Alert & Risk Engine
# The alert engine watches everything. If something breaks,
# you'll know before the market does.
# ============================================================

import json
import os
import datetime

# ── file paths ─────────────────────────────────────────────
_DIR       = os.path.dirname(os.path.abspath(__file__))
ALERT_FILE = os.path.join(_DIR, "pcvr_alerts.json")

# ── constants ──────────────────────────────────────────────
SEVERITIES  = ("info", "warning", "danger", "critical")
CATEGORIES  = (
    "debasement", "whale", "economy", "vault",
    "store", "concentration", "supply", "system",
)
_EMOJI = {
    "info":     "ℹ️",
    "warning":  "⚠️",
    "danger":   "🔴",
    "critical": "🚨",
}

# ── persistence ────────────────────────────────────────────
def load_alerts():
    """Return alert list from disk, or empty list on first run."""
    if os.path.exists(ALERT_FILE):
        try:
            with open(ALERT_FILE, "r") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_alerts(alerts):
    """Persist alert list to disk."""
    with open(ALERT_FILE, "w") as fh:
        json.dump(alerts, fh, indent=2)


# ── core functions ─────────────────────────────────────────
def fire(severity, category, message, source="system", data=None):
    """Create, persist, and print a new alert. Returns the alert dict."""
    if severity not in SEVERITIES:
        severity = "info"
    if category not in CATEGORIES:
        category = "system"

    alerts = load_alerts()
    alert_id = (max(a["id"] for a in alerts) + 1) if alerts else 1

    ts = datetime.datetime.utcnow().isoformat()
    alert = {
        "id":           alert_id,
        "timestamp":    ts,
        "severity":     severity,
        "category":     category,
        "message":      message,
        "source":       source,
        "acknowledged": False,
        "data":         data or {},
    }
    alerts.append(alert)
    save_alerts(alerts)

    emoji = _EMOJI.get(severity, "ℹ️")
    print(f"  {emoji}  [{severity.upper()}] [{category}] {message}  (src: {source})")

    # try to log to history ledger
    try:
        import history as _hist
        _hist.log_event("alert", 0,
                        details=f"[{severity}][{category}] {message}",
                        source=source)
    except Exception:
        pass

    return alert


def get_all():
    """Return every alert."""
    return load_alerts()


def get_active():
    """Return unacknowledged alerts."""
    return [a for a in load_alerts() if not a["acknowledged"]]


def get_by_severity(severity):
    """Return alerts matching *severity*."""
    return [a for a in load_alerts() if a["severity"] == severity]


def get_by_category(category):
    """Return alerts matching *category*."""
    return [a for a in load_alerts() if a["category"] == category]


def acknowledge(alert_id):
    """Mark a single alert as acknowledged. Returns True if found."""
    alerts = load_alerts()
    found = False
    for a in alerts:
        if a["id"] == alert_id:
            a["acknowledged"] = True
            found = True
            break
    if found:
        save_alerts(alerts)
    return found


def acknowledge_all():
    """Mark every alert as acknowledged."""
    alerts = load_alerts()
    for a in alerts:
        a["acknowledged"] = True
    save_alerts(alerts)
    return len(alerts)


def clear_old(days=7):
    """Remove alerts older than *days* days. Returns count removed."""
    alerts = load_alerts()
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    kept = []
    removed = 0
    for a in alerts:
        try:
            ts = datetime.datetime.fromisoformat(a["timestamp"])
        except (ValueError, KeyError):
            kept.append(a)
            continue
        if ts >= cutoff:
            kept.append(a)
        else:
            removed += 1
    save_alerts(kept)
    return removed


def count_by_severity():
    """Return dict mapping severity → count."""
    counts = {s: 0 for s in SEVERITIES}
    for a in load_alerts():
        sev = a.get("severity", "info")
        if sev in counts:
            counts[sev] += 1
    return counts


# ── automated health check ─────────────────────────────────
def health_check():
    """
    Scan every toolkit module and fire alerts based on current state.
    Returns a summary dict: {total_fired, by_severity}.
    """
    fired = []

    # ── economy.py ─────────────────────────────────────────
    try:
        import economy as _econ
        circ   = _econ.circ
        supply = _econ.supply
        if supply > 0:
            ratio = circ / supply
            if ratio > 0.5:
                fired.append(fire("danger", "supply",
                                  "Circulating supply exceeding 50% of total",
                                  source="economy",
                                  data={"circ": circ, "supply": supply, "ratio": ratio}))
            elif ratio > 0.3:
                fired.append(fire("warning", "supply",
                                  "Circulating approaching 30% of total",
                                  source="economy",
                                  data={"circ": circ, "supply": supply, "ratio": ratio}))

        emitted = _econ.emitted
        burned  = _econ.burned
        if emitted > burned:
            fired.append(fire("warning", "economy",
                              "Net inflation — emitting more than burning",
                              source="economy",
                              data={"emitted": emitted, "burned": burned}))
    except Exception:
        pass

    # ── detector.py ────────────────────────────────────────
    try:
        import detector as _det
        import economy as _econ
        ok = _det.check(
            _econ.emitted, _econ.spent, _econ.burned,
            _econ.locked, _econ.circ, _econ.supply,
            _econ.cap, _econ.today,
        )
        if not ok:
            fired.append(fire("danger", "debasement",
                              "Debasement check flagged — economy health risk detected",
                              source="detector"))
    except Exception:
        pass

    # ── whale_tracker.py ───────────────────────────────────
    try:
        import whale_tracker as _wt
        gini_val, _ = _wt.gini_coefficient()
        if gini_val > 0.8:
            fired.append(fire("critical", "concentration",
                              "Extreme wallet concentration",
                              source="whale_tracker",
                              data={"gini": gini_val}))
        elif gini_val > 0.6:
            fired.append(fire("danger", "concentration",
                              "High wallet concentration",
                              source="whale_tracker",
                              data={"gini": gini_val}))

        wallets  = _wt.load_wallets()
        circ, _  = _wt.get_supply()
        total_bal = sum(w["balance"] for w in wallets)
        effective = max(circ, total_bal) or 1
        top1 = _wt.top_holders(1)
        if top1:
            top_pct = top1[0]["balance"] / effective
            if top_pct > 0.5:
                fired.append(fire("critical", "whale",
                                  "Single wallet controls majority of supply",
                                  source="whale_tracker",
                                  data={"wallet": top1[0]["wallet_id"], "pct": top_pct}))
    except Exception:
        pass

    # ── vault.py ───────────────────────────────────────────
    try:
        import vault as _vault
        if _vault.vault_balance == 0:
            fired.append(fire("warning", "vault",
                              "Vault is empty",
                              source="vault"))
        if _vault.total_locked == 0:
            fired.append(fire("warning", "vault",
                              "Nothing locked in vault",
                              source="vault"))
    except Exception:
        pass

    # ── store.py ───────────────────────────────────────────
    try:
        import store as _store
        catalog = _store.load_catalog()
        dead_items = [
            item["name"] for item in catalog
            if item.get("sales", 0) == 0
        ]
        if dead_items:
            fired.append(fire("info", "store",
                              f"{len(dead_items)} item(s) have zero sales",
                              source="store",
                              data={"items": dead_items}))
    except Exception:
        pass

    by_sev = count_by_severity()
    total  = len(fired)

    print(f"\n  🏥 Health check complete — {total} alert(s) fired")
    for sev in SEVERITIES:
        n = sum(1 for a in fired if a["severity"] == sev)
        if n:
            print(f"     {_EMOJI[sev]}  {sev}: {n}")

    return {"total_fired": total, "by_severity": by_sev}


# ── risk score ─────────────────────────────────────────────
def risk_score():
    """
    Calculate overall risk score 0-100 from active alerts.
    Returns (score, interpretation).
    """
    active = get_active()
    weights = {"critical": 25, "danger": 15, "warning": 5, "info": 0}
    raw = sum(weights.get(a["severity"], 0) for a in active)
    score = min(raw, 100)

    if score <= 20:
        interpretation = "🟢 LOW RISK — System healthy"
    elif score <= 40:
        interpretation = "🟡 MODERATE RISK — Monitor closely"
    elif score <= 60:
        interpretation = "🔴 HIGH RISK — Action needed"
    else:
        interpretation = "🚨 CRITICAL RISK — Immediate intervention required"

    return score, interpretation


# ── alert dashboard ────────────────────────────────────────
def dashboard():
    """Print a full alert dashboard."""
    score, interpretation = risk_score()
    counts   = count_by_severity()
    active   = get_active()
    all_alerts = get_all()

    print("\n" + "=" * 50)
    print("  🚨 PCVR ALERT DASHBOARD")
    print("=" * 50)

    print(f"\n  Risk Score: {score}/100  {interpretation}")

    print(f"\n  Active Alerts by Severity:")
    for sev in SEVERITIES:
        n = sum(1 for a in active if a["severity"] == sev)
        bar = "█" * n if n else "·"
        print(f"    {_EMOJI[sev]}  {sev:<10} {bar}  ({n})")

    print(f"\n  Last 10 Alerts:")
    recent = all_alerts[-10:] if len(all_alerts) >= 10 else all_alerts
    for a in reversed(recent):
        ts  = a["timestamp"][:19].replace("T", " ")
        ack = "✓" if a["acknowledged"] else " "
        emoji = _EMOJI.get(a["severity"], "ℹ️")
        print(f"    [{ack}] {ts}  {emoji}  [{a['category']}]  {a['message']}")

    # ── quick recommendations ─────────────────────────────
    print(f"\n  Recommendations:")
    crits  = [a for a in active if a["severity"] == "critical"]
    dangers = [a for a in active if a["severity"] == "danger"]
    warns  = [a for a in active if a["severity"] == "warning"]

    if crits:
        print("    🚨 CRITICAL alerts require immediate action!")
        for a in crits[:3]:
            print(f"       → {a['message']}")
    if dangers:
        print("    🔴 Danger alerts detected — investigate now")
        for a in dangers[:3]:
            print(f"       → {a['message']}")
    if warns:
        print("    ⚠️  Warnings present — monitor closely")
        for a in warns[:3]:
            print(f"       → {a['message']}")
    if not active:
        print("    ✅ No active alerts — system is healthy")

    print(f"\n{'='*50}")
    print("  Run `alert.py` for interactive alert management")
    print(f"{'='*50}\n")


# ── interactive CLI ────────────────────────────────────────
def _cli():
    print("""
==================================
🚨 PCVR ALERT ENGINE
==================================
Commands:
1. check      → run full health check
2. dashboard  → alert dashboard
3. risk       → risk score
4. active     → active (unacknowledged) alerts
5. ack        → acknowledge an alert
6. ack_all    → acknowledge all
7. history    → all alerts
8. clear      → clear old alerts
9. exit
==================================
""")
    while True:
        try:
            cmd = input("alert> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if cmd in ("1", "check"):
            health_check()

        elif cmd in ("2", "dashboard"):
            dashboard()

        elif cmd in ("3", "risk"):
            score, interp = risk_score()
            print(f"\n  Risk Score: {score}/100")
            print(f"  {interp}\n")

        elif cmd in ("4", "active"):
            alerts = get_active()
            if not alerts:
                print("  ✅ No active alerts.\n")
            else:
                print(f"\n  {len(alerts)} active alert(s):\n")
                for a in alerts:
                    ts    = a["timestamp"][:19].replace("T", " ")
                    emoji = _EMOJI.get(a["severity"], "ℹ️")
                    print(f"  #{a['id']:>4}  {ts}  {emoji}  [{a['category']}]  {a['message']}")
                print()

        elif cmd in ("5", "ack"):
            raw = input("  Alert ID to acknowledge: ").strip()
            try:
                aid = int(raw)
                if acknowledge(aid):
                    print(f"  ✅ Alert #{aid} acknowledged.\n")
                else:
                    print(f"  ❌ Alert #{aid} not found.\n")
            except ValueError:
                print("  ❌ Invalid ID.\n")

        elif cmd in ("6", "ack_all"):
            n = acknowledge_all()
            print(f"  ✅ {n} alert(s) acknowledged.\n")

        elif cmd in ("7", "history"):
            alerts = get_all()
            if not alerts:
                print("  No alerts on record.\n")
            else:
                print(f"\n  {len(alerts)} total alert(s):\n")
                for a in alerts:
                    ts    = a["timestamp"][:19].replace("T", " ")
                    ack   = "✓" if a["acknowledged"] else " "
                    emoji = _EMOJI.get(a["severity"], "ℹ️")
                    print(f"  #{a['id']:>4} [{ack}]  {ts}  {emoji}  [{a['category']}]  {a['message']}")
                print()

        elif cmd in ("8", "clear"):
            raw = input("  Clear alerts older than how many days? [7]: ").strip()
            days = 7
            try:
                days = int(raw) if raw else 7
            except ValueError:
                pass
            removed = clear_old(days)
            print(f"  🗑️  Removed {removed} alert(s) older than {days} day(s).\n")

        elif cmd in ("9", "exit", "quit"):
            print("  Bye.")
            break

        else:
            print("  Unknown command. Type 1-9.\n")


if __name__ == "__main__":
    _cli()
