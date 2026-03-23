# ============================================================
# PCVR Studios — whale_tracker.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# PCVR Wallet Concentration Monitor
# Distribution matters. If one wallet can crash the price,
# the token isn't decentralized.
# ============================================================

import json
import os
import datetime
import math

# ── file paths ─────────────────────────────────────────────
_DIR           = os.path.dirname(os.path.abspath(__file__))
WALLET_FILE    = os.path.join(_DIR, "pcvr_wallets.json")
MOVEMENT_LOG   = os.path.join(_DIR, "pcvr_whale_movements.json")

# ── default supply values (used when economy.py unavailable) ─
_DEFAULT_CIRC   = 100_000_000
_DEFAULT_SUPPLY = 1_000_000_000

# ── valid wallet types ────────────────────────────────────
WALLET_TYPES = ("founder", "player", "store", "vault", "burn", "pool", "exchange")

# ── pre-seeded wallets ────────────────────────────────────
_SEED_WALLETS = [
    {"wallet_id": "founder_main",   "wallet_type": "founder",  "balance": 300_000_000_000},
    {"wallet_id": "store_wallet",   "wallet_type": "store",    "balance": 0},
    {"wallet_id": "vault_wallet",   "wallet_type": "vault",    "balance": 0},
    {"wallet_id": "burn_address",   "wallet_type": "burn",     "balance": 0},
    {"wallet_id": "emission_pool",  "wallet_type": "pool",     "balance": 0},
]

SEPARATOR_WIDTH = 42


# ── supply helpers ────────────────────────────────────────
def get_supply():
    """Try to read live supply from economy.py; fall back to defaults."""
    try:
        import economy as _econ
        return _econ.circ, _econ.supply
    except Exception:
        return _DEFAULT_CIRC, _DEFAULT_SUPPLY


# ── wallet persistence ────────────────────────────────────
def load_wallets():
    """Load wallet registry from disk. Seeds defaults on first run."""
    if os.path.exists(WALLET_FILE):
        try:
            with open(WALLET_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    # First run — seed known wallets
    circ, _ = get_supply()
    wallets = []
    now = datetime.datetime.utcnow().isoformat()
    for seed in _SEED_WALLETS:
        w = dict(seed)
        w["last_activity"] = now
        w["created"]       = now
        # Emission pool starts from economy circulating supply
        if w["wallet_id"] == "emission_pool":
            w["balance"] = circ
        wallets.append(w)
    save_wallets(wallets)
    return wallets


def save_wallets(wallets):
    """Persist wallet registry to disk."""
    try:
        with open(WALLET_FILE, "w") as f:
            json.dump(wallets, f, indent=2)
    except IOError as exc:
        print(f"  ⚠️  Could not save wallets: {exc}")


# ── movement log persistence ──────────────────────────────
def _load_movements():
    if os.path.exists(MOVEMENT_LOG):
        try:
            with open(MOVEMENT_LOG, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save_movements(movements):
    try:
        with open(MOVEMENT_LOG, "w") as f:
            json.dump(movements, f, indent=2)
    except IOError as exc:
        print(f"  ⚠️  Could not save movements: {exc}")


# ── wallet CRUD ───────────────────────────────────────────
def add_wallet(wallet_id, wallet_type, balance=0):
    """Register a new wallet. Raises ValueError on duplicate or bad type."""
    if wallet_type not in WALLET_TYPES:
        raise ValueError(f"Unknown wallet_type '{wallet_type}'. "
                         f"Valid types: {WALLET_TYPES}")
    wallets = load_wallets()
    for w in wallets:
        if w["wallet_id"] == wallet_id:
            raise ValueError(f"Wallet '{wallet_id}' already exists.")
    now = datetime.datetime.utcnow().isoformat()
    wallets.append({
        "wallet_id":     wallet_id,
        "wallet_type":   wallet_type,
        "balance":       balance,
        "last_activity": now,
        "created":       now,
    })
    save_wallets(wallets)
    return wallets[-1]


def update_balance(wallet_id, amount):
    """Add *amount* to wallet balance (negative = send). Returns new balance."""
    wallets = load_wallets()
    for w in wallets:
        if w["wallet_id"] == wallet_id:
            w["balance"] += amount
            w["last_activity"] = datetime.datetime.utcnow().isoformat()
            save_wallets(wallets)
            return w["balance"]
    raise KeyError(f"Wallet '{wallet_id}' not found.")


def transfer(from_wallet, to_wallet, amount):
    """Move *amount* tokens between two wallets and log the movement."""
    if amount <= 0:
        raise ValueError("Transfer amount must be positive.")
    wallets = load_wallets()
    src = next((w for w in wallets if w["wallet_id"] == from_wallet), None)
    dst = next((w for w in wallets if w["wallet_id"] == to_wallet),   None)
    if src is None:
        raise KeyError(f"Source wallet '{from_wallet}' not found.")
    if dst is None:
        raise KeyError(f"Destination wallet '{to_wallet}' not found.")
    if src["balance"] < amount:
        raise ValueError(f"Insufficient balance in '{from_wallet}' "
                         f"({src['balance']:,} < {amount:,}).")
    now = datetime.datetime.utcnow().isoformat()
    src["balance"]       -= amount
    src["last_activity"]  = now
    dst["balance"]       += amount
    dst["last_activity"]  = now
    save_wallets(wallets)
    log_movement(from_wallet, amount, "out", details=f"→ {to_wallet}")
    log_movement(to_wallet,   amount, "in",  details=f"← {from_wallet}")
    detect_whale_move(from_wallet, amount)
    detect_whale_move(to_wallet,   amount)
    return {"from": from_wallet, "to": to_wallet, "amount": amount, "ts": now}


def get_wallet(wallet_id):
    """Return wallet dict or None."""
    for w in load_wallets():
        if w["wallet_id"] == wallet_id:
            return w
    return None


def get_all_wallets():
    """Return all wallet dicts."""
    return load_wallets()


def top_holders(n=10):
    """Return top *n* wallets sorted by balance descending."""
    return sorted(load_wallets(), key=lambda w: w["balance"], reverse=True)[:n]


def get_by_type(wallet_type):
    """Return all wallets matching *wallet_type*."""
    return [w for w in load_wallets() if w["wallet_type"] == wallet_type]


# ── concentration analysis ────────────────────────────────
def concentration_report():
    """Print a full concentration risk report. Returns a risk dict."""
    circ, _ = get_supply()
    wallets  = load_wallets()
    holders  = sorted(wallets, key=lambda w: w["balance"], reverse=True)[:10]

    total_bal = sum(w["balance"] for w in wallets)
    effective = max(circ, total_bal) or 1  # avoid div-by-zero

    top1_pct  = holders[0]["balance"] / effective * 100 if holders else 0
    top3_pct  = sum(w["balance"] for w in holders[:3])  / effective * 100
    top5_pct  = sum(w["balance"] for w in holders[:5])  / effective * 100

    # Risk level
    if top1_pct > 50:
        risk, badge = "CRITICAL", "💀"
    elif top1_pct > 30:
        risk, badge = "DANGER",   "🔴"
    elif top3_pct > 60:
        risk, badge = "DANGER",   "🔴"
    elif top5_pct > 70:
        risk, badge = "WARNING",  "🟡"
    else:
        risk, badge = "HEALTHY",  "🟢"

    print(f"\n{'=' * SEPARATOR_WIDTH}")
    print("  🐋 PCVR CONCENTRATION REPORT")
    print(f"{'=' * SEPARATOR_WIDTH}")
    print(f"  Circulating supply: {circ:>15,} PCVR")
    print(f"  Effective tracked:  {effective:>15,} PCVR")
    print()
    print(f"  {'Rank':<5} {'Wallet':<20} {'Balance':>18} {'% Circ':>8}")
    print(f"  {'-'*5} {'-'*20} {'-'*18} {'-'*8}")
    for i, w in enumerate(holders, 1):
        pct = w["balance"] / effective * 100
        print(f"  {i:<5} {w['wallet_id']:<20} {w['balance']:>18,} {pct:>7.2f}%")
    print()
    print(f"  Top-1  concentration: {top1_pct:.2f}%")
    print(f"  Top-3  concentration: {top3_pct:.2f}%")
    print(f"  Top-5  concentration: {top5_pct:.2f}%")
    print()
    print(f"  Risk Level: {badge} {risk}")
    print(f"{'=' * SEPARATOR_WIDTH}\n")

    return {
        "risk":     risk,
        "badge":    badge,
        "top1_pct": top1_pct,
        "top3_pct": top3_pct,
        "top5_pct": top5_pct,
    }


def gini_coefficient():
    """Calculate Gini index for wallet balances. Returns (coefficient, label)."""
    balances = [w["balance"] for w in load_wallets() if w["balance"] > 0]
    n = len(balances)
    if n == 0:
        return 0.0, "🟢 Well distributed"
    if n == 1:
        return 1.0, "💀 Extreme concentration"

    balances_sorted = sorted(balances)
    total = sum(balances_sorted)
    if total == 0:
        return 0.0, "🟢 Well distributed"

    cumulative = 0.0
    for i, b in enumerate(balances_sorted, 1):
        cumulative += (2 * i - n - 1) * b
    gini = cumulative / (n * total)

    if gini < 0.4:
        label = "🟢 Well distributed"
    elif gini < 0.6:
        label = "🟡 Moderate concentration"
    elif gini < 0.8:
        label = "🔴 High concentration"
    else:
        label = "💀 Extreme concentration"

    return round(gini, 4), label


# ── whale movement detection ──────────────────────────────
def log_movement(wallet_id, amount, direction, details=""):
    """Append a movement record to the persistent log."""
    movements = _load_movements()
    movements.append({
        "wallet_id":  wallet_id,
        "amount":     amount,
        "direction":  direction,
        "details":    details,
        "ts":         datetime.datetime.utcnow().isoformat(),
        "flagged":    False,
    })
    _save_movements(movements)


def detect_whale_move(wallet_id, amount, threshold_pct=1.0):
    """
    Flag movement if *amount* exceeds *threshold_pct* % of circulating supply.
    Returns True if flagged, False otherwise.
    """
    circ, _ = get_supply()
    threshold = circ * threshold_pct / 100
    if amount < threshold:
        return False

    movements = _load_movements()
    # Mark the most recent entry for this wallet as flagged
    for m in reversed(movements):
        if m["wallet_id"] == wallet_id and not m["flagged"]:
            m["flagged"] = True
            pct = amount / circ * 100 if circ else 0
            m["alert"] = (f"⚠️  WHALE ALERT: {wallet_id} moved "
                          f"{amount:,} PCVR ({pct:.2f}% of circ)")
            break
    _save_movements(movements)

    # Try to log alert to history.py ledger
    try:
        import history as _hist
        pct = amount / circ * 100 if circ else 0
        _hist.log_event(
            "alert",
            amount,
            details=f"Whale move — {wallet_id} {amount:,} PCVR ({pct:.2f}% circ)",
            source="whale_tracker",
        )
    except Exception:
        pass

    return True


def whale_alerts():
    """Return list of flagged whale movements."""
    return [m for m in _load_movements() if m.get("flagged")]


def movement_history(wallet_id=None):
    """Return movement history for a specific wallet or all wallets."""
    movements = _load_movements()
    if wallet_id:
        return [m for m in movements if m["wallet_id"] == wallet_id]
    return movements


# ── display helpers ───────────────────────────────────────
def print_wallets(wallets=None):
    if wallets is None:
        wallets = load_wallets()
    print(f"\n{'=' * SEPARATOR_WIDTH}")
    print("  🐋 PCVR WALLET REGISTRY")
    print(f"{'=' * SEPARATOR_WIDTH}")
    print(f"  {'ID':<22} {'Type':<10} {'Balance':>18}")
    print(f"  {'-'*22} {'-'*10} {'-'*18}")
    for w in wallets:
        print(f"  {w['wallet_id']:<22} {w['wallet_type']:<10} {w['balance']:>18,}")
    print(f"{'=' * SEPARATOR_WIDTH}\n")


# ── interactive CLI ────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * SEPARATOR_WIDTH)
    print("  🐋 PCVR WHALE TRACKER")
    print("=" * SEPARATOR_WIDTH)
    print("  © PCVR Studios 2026")
    print("  Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4")
    print()
    print("  Distribution matters. If one wallet can crash")
    print("  the price, the token isn't decentralized.")
    print("=" * SEPARATOR_WIDTH)
    print()
    print("Commands:")
    print("  1. wallets       → list all wallets")
    print("  2. top           → top 10 holders")
    print("  3. add           → add a wallet")
    print("  4. transfer      → move tokens")
    print("  5. concentration → concentration report")
    print("  6. gini          → Gini coefficient")
    print("  7. alerts        → whale movement alerts")
    print("  8. history       → movement history")
    print("  9. exit")
    print()

    while True:
        try:
            cmd = input("whale> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  👋 Bye.")
            break

        if cmd in ("1", "wallets"):
            print_wallets()

        elif cmd in ("2", "top"):
            holders = top_holders(10)
            circ, _ = get_supply()
            effective = max(circ, sum(w["balance"] for w in load_wallets())) or 1
            print(f"\n  Top 10 Holders (circ supply: {circ:,})")
            print(f"  {'Rank':<5} {'Wallet':<22} {'Balance':>18} {'% Circ':>8}")
            for i, w in enumerate(holders, 1):
                pct = w["balance"] / effective * 100
                print(f"  {i:<5} {w['wallet_id']:<22} {w['balance']:>18,} {pct:>7.2f}%")
            print()

        elif cmd in ("3", "add"):
            wid  = input("  wallet_id   : ").strip()
            wtyp = input("  wallet_type : ").strip()
            bal  = input("  balance     : ").strip()
            try:
                w = add_wallet(wid, wtyp, float(bal) if bal else 0)
                print(f"  ✅ Added: {w}")
            except (ValueError, KeyError) as ex:
                print(f"  ❌ {ex}")

        elif cmd in ("4", "transfer"):
            src = input("  from_wallet : ").strip()
            dst = input("  to_wallet   : ").strip()
            amt = input("  amount      : ").strip()
            try:
                tx = transfer(src, dst, float(amt))
                print(f"  ✅ Transferred {tx['amount']:,} PCVR "
                      f"from {tx['from']} → {tx['to']}")
            except (ValueError, KeyError) as ex:
                print(f"  ❌ {ex}")

        elif cmd in ("5", "concentration"):
            concentration_report()

        elif cmd in ("6", "gini"):
            coef, label = gini_coefficient()
            print(f"\n  Gini coefficient: {coef}  {label}\n")

        elif cmd in ("7", "alerts"):
            alerts = whale_alerts()
            if not alerts:
                print("  🟢 No whale alerts.\n")
            else:
                print(f"\n  ⚠️  {len(alerts)} Whale Alert(s):")
                for a in alerts:
                    print(f"    {a.get('alert', a)}")
                print()

        elif cmd in ("8", "history"):
            wid = input("  wallet_id (blank = all) : ").strip() or None
            hist = movement_history(wid)
            if not hist:
                print("  No movements recorded.\n")
            else:
                for m in hist[-20:]:
                    flag = "⚠️ " if m.get("flagged") else "   "
                    print(f"  {flag} {m['ts'][:19]}  "
                          f"{m['wallet_id']:<22} "
                          f"{m['direction']:>3}  "
                          f"{m['amount']:>18,}  "
                          f"{m.get('details','')}")
                print()

        elif cmd in ("9", "exit", "quit"):
            print("  👋 Bye.")
            break

        else:
            print("  ❓ Unknown command. Type a number 1-9.")
