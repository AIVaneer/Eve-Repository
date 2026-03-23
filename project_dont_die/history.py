# ============================================================
# PCVR Studios — history.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# PCVR Transaction Ledger — persistent log of every event.
# No more resetting every run. Every earn, burn, lock, and
# purchase is recorded with a timestamp and queryable forever.
# ============================================================

import json
import os
import csv
import datetime

# ── persistence path ───────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
LEDGER_FILE = os.path.join(_DIR, "pcvr_ledger.json")
CSV_FILE    = os.path.join(_DIR, "pcvr_ledger.csv")

# ── valid event types ──────────────────────────────────────
EVENT_TYPES = ("earn", "spend", "burn", "lock", "unlock",
               "purchase", "vault_deposit", "alert")

SEPARATOR_WIDTH = 38


# ── persistence ────────────────────────────────────────────
def load_ledger():
    """Load the ledger from disk. Returns a list of event dicts."""
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_ledger(ledger):
    """Write the full ledger list to disk."""
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)


# ── core write ─────────────────────────────────────────────
def log_event(event_type, amount, details="", source="system"):
    """
    Append one event to the persistent ledger.

    Parameters
    ----------
    event_type : str   — one of EVENT_TYPES
    amount     : float — token amount involved (use 0 for alerts)
    details    : str   — optional free-text description
    source     : str   — module or player that generated the event
    """
    ledger = load_ledger()
    next_id = (ledger[-1]["id"] + 1) if ledger else 1
    entry = {
        "id":         next_id,
        "timestamp":  datetime.datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "amount":     float(amount),
        "details":    details,
        "source":     source,
    }
    ledger.append(entry)
    save_ledger(ledger)
    return entry


# ── queries ────────────────────────────────────────────────
def get_all():
    """Return the full ledger."""
    return load_ledger()


def get_by_type(event_type):
    """Return all events matching the given event_type."""
    return [e for e in load_ledger() if e["event_type"] == event_type]


def get_by_date(date_str):
    """
    Return all events on a specific date.

    Parameters
    ----------
    date_str : str — date in YYYY-MM-DD format
    """
    return [e for e in load_ledger() if e["timestamp"].startswith(date_str)]


def get_range(start_date, end_date):
    """
    Return all events between start_date and end_date (inclusive).

    Parameters
    ----------
    start_date : str — YYYY-MM-DD
    end_date   : str — YYYY-MM-DD
    """
    return [
        e for e in load_ledger()
        if start_date <= e["timestamp"][:10] <= end_date
    ]


def get_last(n=10):
    """Return the last N events."""
    ledger = load_ledger()
    return ledger[-n:] if len(ledger) >= n else ledger


# ── aggregates ─────────────────────────────────────────────
def total_by_type(event_type):
    """Return the sum of all amounts for a given event_type."""
    return sum(e["amount"] for e in load_ledger()
               if e["event_type"] == event_type)


def daily_summary(date_str=None):
    """
    Return a summary dict for a specific day (defaults to today UTC).

    Returns keys: date, earned, spent, burned, locked, transactions
    """
    if date_str is None:
        date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    events = get_by_date(date_str)
    summary = {
        "date":         date_str,
        "earned":       sum(e["amount"] for e in events if e["event_type"] == "earn"),
        "spent":        sum(e["amount"] for e in events if e["event_type"] in ("spend", "purchase")),
        "burned":       sum(e["amount"] for e in events if e["event_type"] == "burn"),
        "locked":       sum(e["amount"] for e in events if e["event_type"] == "lock"),
        "transactions": len(events),
    }
    return summary


def weekly_summary():
    """Return daily_summary for each of the last 7 days."""
    summaries = []
    today = datetime.datetime.utcnow().date()
    for i in range(6, -1, -1):
        day = (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        summaries.append(daily_summary(day))
    return summaries


def trend(event_type, days=7):
    """
    Return daily totals for event_type over the last N days.

    Returns a dict with:
      - 'days'      : list of {'date', 'total'} dicts
      - 'direction' : 'up', 'down', or 'flat'
    """
    today = datetime.datetime.utcnow().date()
    daily_totals = []
    for i in range(days - 1, -1, -1):
        day = (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        total = sum(e["amount"] for e in get_by_date(day)
                    if e["event_type"] == event_type)
        daily_totals.append({"date": day, "total": total})

    # direction: compare first half vs second half average
    mid = days // 2
    first_avg  = sum(d["total"] for d in daily_totals[:mid]) / mid if mid else 0
    second_avg = sum(d["total"] for d in daily_totals[mid:]) / (days - mid) if (days - mid) else 0

    if second_avg > first_avg * 1.05:
        direction = "up"
    elif second_avg < first_avg * 0.95:
        direction = "down"
    else:
        direction = "flat"

    return {"days": daily_totals, "direction": direction}


def clear_ledger():
    """Wipe the ledger after confirmation. Returns True if cleared."""
    try:
        confirm = input("  ⚠️  Type YES to wipe the entire ledger: ").strip()
    except (EOFError, KeyboardInterrupt):
        return False
    if confirm == "YES":
        save_ledger([])
        print("  ✅ Ledger cleared.")
        return True
    print("  Cancelled.")
    return False


# ── display helpers ────────────────────────────────────────
def _print_separator(char="=", width=SEPARATOR_WIDTH):
    print(char * width)


def _print_event(e):
    ts  = e["timestamp"][:19].replace("T", " ")
    typ = e["event_type"].upper()
    amt = f"{e['amount']:,.0f}"
    src = e["source"]
    dtl = f" — {e['details']}" if e["details"] else ""
    print(f"  [{e['id']:>4}] {ts}  {typ:<14} {amt:>10} PCVR  ({src}){dtl}")


# ── reports ────────────────────────────────────────────────
def report():
    """Print a full ledger report."""
    ledger = load_ledger()
    today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    _print_separator()
    print("📜  PCVR TRANSACTION LEDGER — REPORT")
    _print_separator()
    print(f"  Total events logged: {len(ledger)}")

    if not ledger:
        print("  No events yet.")
        print()
        return

    # breakdown by type
    print("\n  — Breakdown by Type —")
    for et in EVENT_TYPES:
        events = [e for e in ledger if e["event_type"] == et]
        if events:
            total = sum(e["amount"] for e in events)
            print(f"  {et:<14} x{len(events)}  {total:>14,.0f} PCVR")

    # last 5 events
    print("\n  — Last 5 Events —")
    for e in get_last(5):
        _print_event(e)

    # today's summary
    today = daily_summary(today_str)
    print(f"\n  — Today ({today_str}) —")
    print(f"  Earned:       {today['earned']:>10,.0f} PCVR")
    print(f"  Spent:        {today['spent']:>10,.0f} PCVR")
    print(f"  Burned:       {today['burned']:>10,.0f} PCVR 🔥")
    print(f"  Locked:       {today['locked']:>10,.0f} PCVR 🔒")
    print(f"  Transactions: {today['transactions']:>10}")

    # 7-day trend for earn, spend, burn
    print("\n  — 7-Day Trends —")
    for et in ("earn", "spend", "burn"):
        t = trend(et, 7)
        arrow = "📈" if t["direction"] == "up" else "📉" if t["direction"] == "down" else "➡️"
        total = sum(d["total"] for d in t["days"])
        print(f"  {et:<8}  {total:>12,.0f} PCVR total  {arrow} {t['direction']}")

    print()


def export_csv():
    """Export the full ledger to pcvr_ledger.csv."""
    ledger = load_ledger()
    if not ledger:
        print("  Nothing to export.")
        return
    fieldnames = ["id", "timestamp", "event_type", "amount", "details", "source"]
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in ledger:
            writer.writerow({k: entry.get(k, "") for k in fieldnames})
    print(f"  ✅ Exported {len(ledger)} events → {CSV_FILE}")


# ── economy.py monkey-patch ────────────────────────────────
def hook_economy():
    """
    Monkey-patch economy.py's earn/spend/burn/lock functions to
    auto-log every call to the ledger.  Call this from run_all.py
    before running any economy operations.
    """
    try:
        import economy as _econ
    except ImportError:
        print("  ⚠️  economy.py not found — hook_economy() skipped.")
        return False

    _orig_earn  = _econ.earn
    _orig_spend = _econ.spend
    _orig_burn  = _econ.burn
    _orig_lock  = _econ.lock

    def _earn(a):
        result = _orig_earn(a)
        if result and result > 0:
            log_event("earn", result, source="economy")
        return result

    def _spend(a):
        result = _orig_spend(a)
        if result and result > 0:
            log_event("spend", result, source="economy")
        return result

    def _burn(a):
        result = _orig_burn(a)
        if result and result > 0:
            log_event("burn", result, source="economy")
        return result

    def _lock(a):
        result = _orig_lock(a)
        if result and result > 0:
            log_event("lock", result, source="economy")
        return result

    _econ.earn  = _earn
    _econ.spend = _spend
    _econ.burn  = _burn
    _econ.lock  = _lock
    return True


# ── interactive CLI ────────────────────────────────────────
if __name__ == "__main__":
    _print_separator()
    print("📜  PCVR TRANSACTION LEDGER")
    _print_separator()
    print("Commands:")
    print("  1. log      → manually log an event")
    print("  2. last     → show last 10 events")
    print("  3. today    → today's summary")
    print("  4. week     → weekly summary")
    print("  5. trend    → 7-day trend")
    print("  6. report   → full report")
    print("  7. export   → export to CSV")
    print("  8. search   → search by type or date")
    print("  9. exit")
    _print_separator()

    while True:
        try:
            cmd = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if cmd in ("1", "log"):
            print(f"  Event types: {', '.join(EVENT_TYPES)}")
            try:
                etype   = input("  Event type : ").strip().lower()
                amount  = float(input("  Amount     : ").strip())
                details = input("  Details    : ").strip()
                source  = input("  Source     : ").strip() or "manual"
                entry   = log_event(etype, amount, details, source)
                print(f"  ✅ Logged event #{entry['id']}  ({etype}  {amount:,.0f} PCVR)")
            except ValueError:
                print("  ❌ Invalid amount.")

        elif cmd in ("2", "last"):
            events = get_last(10)
            print("\n  — Last 10 Events —")
            if not events:
                print("  No events yet.")
            else:
                for e in events:
                    _print_event(e)

        elif cmd in ("3", "today"):
            s = daily_summary()
            print(f"\n  — Today ({s['date']}) —")
            print(f"  Earned  : {s['earned']:,.0f} PCVR")
            print(f"  Spent   : {s['spent']:,.0f} PCVR")
            print(f"  Burned  : {s['burned']:,.0f} PCVR 🔥")
            print(f"  Locked  : {s['locked']:,.0f} PCVR 🔒")
            print(f"  Events  : {s['transactions']}")

        elif cmd in ("4", "week"):
            weeks = weekly_summary()
            print("\n  — Weekly Summary (last 7 days) —")
            for s in weeks:
                print(f"  {s['date']}  "
                      f"earn {s['earned']:>8,.0f}  "
                      f"burn {s['burned']:>8,.0f}  "
                      f"spend {s['spent']:>8,.0f}  "
                      f"({s['transactions']} events)")

        elif cmd in ("5", "trend"):
            try:
                etype = input("  Event type (earn/spend/burn): ").strip().lower()
                for et in (etype,):
                    t = trend(et, 7)
                    arrow = ("📈" if t["direction"] == "up"
                             else "📉" if t["direction"] == "down"
                             else "➡️")
                    print(f"\n  7-day {et} trend {arrow} {t['direction']}")
                    max_total = max((d["total"] for d in t["days"]), default=1) or 1
                    for d in t["days"]:
                        bar = "█" * int(d["total"] / max_total * 20)
                        print(f"  {d['date']}  {d['total']:>10,.0f}  {bar}")
            except (ValueError, ZeroDivisionError):
                print("  ❌ Could not compute trend.")

        elif cmd in ("6", "report"):
            report()

        elif cmd in ("7", "export"):
            export_csv()

        elif cmd in ("8", "search"):
            print("  Search by: 1=type  2=date  3=date range")
            try:
                sub = input("  > ").strip()
                if sub in ("1", "type"):
                    etype  = input("  Event type: ").strip().lower()
                    events = get_by_type(etype)
                    print(f"\n  Found {len(events)} '{etype}' events:")
                    for e in events[-20:]:
                        _print_event(e)
                elif sub in ("2", "date"):
                    ds     = input("  Date (YYYY-MM-DD): ").strip()
                    events = get_by_date(ds)
                    print(f"\n  Found {len(events)} events on {ds}:")
                    for e in events:
                        _print_event(e)
                elif sub in ("3", "range"):
                    sd     = input("  Start date (YYYY-MM-DD): ").strip()
                    ed     = input("  End date   (YYYY-MM-DD): ").strip()
                    events = get_range(sd, ed)
                    print(f"\n  Found {len(events)} events from {sd} to {ed}:")
                    for e in events[-20:]:
                        _print_event(e)
                else:
                    print("  Unknown search option.")
            except (EOFError, KeyboardInterrupt):
                pass

        elif cmd in ("9", "exit", "quit", "q"):
            print("Goodbye.")
            break

        else:
            print("  Unknown command. Type 1-9.")
