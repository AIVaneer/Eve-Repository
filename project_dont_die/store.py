# ============================================================
# PCVR Studios — store.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# The PCVR Spend Engine — every purchase auto-burns tokens
# and deposits a share to the vault. No manual steps needed.
# ============================================================

import json
import os
import datetime

# ── try to hook into the existing toolkit ──────────────────
try:
    from economy import spend as econ_spend, burn as econ_burn
    _ECONOMY_OK = True
except ImportError:
    _ECONOMY_OK = False

try:
    from vault import deposit_revenue
    _VAULT_OK = True
except ImportError:
    _VAULT_OK = False

# ── internal fallback accumulators (standalone mode) ───────
_fallback_spent  = 0.0
_fallback_burned = 0.0
_fallback_vaulted = 0.0

# ── burn rates per category ────────────────────────────────
BURN_RATES = {
    "cosmetic":   0.20,
    "boost":      0.15,
    "tournament": 0.25,
    "premium":    0.20,
    "exclusive":  0.30,
}

VAULT_RATE = 0.10   # 10% of every purchase goes to vault

SEPARATOR_WIDTH = 38

# ── item catalog ───────────────────────────────────────────
CATALOG = [
    # cosmetic
    {
        "name":        "Neon Blade Skin",
        "price":       500,
        "category":    "cosmetic",
        "description": "Glowing neon sword skin for your avatar.",
    },
    {
        "name":        "Holographic Helmet",
        "price":       750,
        "category":    "cosmetic",
        "description": "Futuristic holographic VR helmet overlay.",
    },
    {
        "name":        "Galaxy Cape",
        "price":       1200,
        "category":    "cosmetic",
        "description": "Animated galaxy-print avatar cape.",
    },
    # boost
    {
        "name":        "2x XP Boost (24h)",
        "price":       300,
        "category":    "boost",
        "description": "Double your XP earnings for 24 hours.",
    },
    {
        "name":        "Reward Multiplier (7d)",
        "price":       800,
        "category":    "boost",
        "description": "1.5x token reward rate for a full week.",
    },
    {
        "name":        "Loot Drop Amplifier",
        "price":       450,
        "category":    "boost",
        "description": "Increases rare loot drop chance by 25%.",
    },
    # tournament
    {
        "name":        "Weekly Arena Entry",
        "price":       1000,
        "category":    "tournament",
        "description": "Entry ticket to the weekly PCVR Arena.",
    },
    {
        "name":        "Grand Championship Slot",
        "price":       5000,
        "category":    "tournament",
        "description": "Reserved spot in the quarterly grand championship.",
    },
    {
        "name":        "Qualifier Pass",
        "price":       600,
        "category":    "tournament",
        "description": "Entry to monthly qualifier rounds.",
    },
    # premium
    {
        "name":        "Battle Pass — Season 1",
        "price":       2000,
        "category":    "premium",
        "description": "Full seasonal battle pass with 30 reward tiers.",
    },
    {
        "name":        "VIP Member Pass",
        "price":       3500,
        "category":    "premium",
        "description": "Monthly VIP status: early access + bonus drops.",
    },
    # exclusive
    {
        "name":        "Genesis Founder Badge",
        "price":       10000,
        "category":    "exclusive",
        "description": "Limited-edition badge for early PCVR supporters.",
    },
    {
        "name":        "Diamond Avatar Frame",
        "price":       7500,
        "category":    "exclusive",
        "description": "Ultra-rare animated diamond border for your avatar.",
    },
    {
        "name":        "Vault Titan Title",
        "price":       15000,
        "category":    "exclusive",
        "description": "On-chain title for wallets that have locked 1M+ PCVR.",
    },
]

# Runtime catalog index for fast lookups
_CATALOG_INDEX = {item["name"].lower(): item for item in CATALOG}

# ── persistence paths ──────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH       = os.path.join(_DIR, "store_catalog.json")
TRANSACTIONS_PATH  = os.path.join(_DIR, "store_transactions.json")

# ── in-memory transaction history ─────────────────────────
purchase_history = []


# ── helpers ────────────────────────────────────────────────
def _save_catalog():
    """Persist the catalog to store_catalog.json."""
    with open(CATALOG_PATH, "w") as f:
        json.dump(CATALOG, f, indent=2)


def _load_transactions():
    """Load existing transactions from disk into memory."""
    global purchase_history
    if os.path.exists(TRANSACTIONS_PATH):
        try:
            with open(TRANSACTIONS_PATH, "r") as f:
                purchase_history = json.load(f)
        except (json.JSONDecodeError, IOError):
            purchase_history = []


def _save_transactions():
    """Flush all in-memory transactions to disk."""
    with open(TRANSACTIONS_PATH, "w") as f:
        json.dump(purchase_history, f, indent=2)


# ── core API ───────────────────────────────────────────────
def purchase(player_id, item_name):
    """
    Process a store purchase.

    Parameters
    ----------
    player_id : str   — wallet address or username
    item_name : str   — exact item name (case-insensitive)

    Returns
    -------
    dict with keys: player, item, price, burned, vaulted,
                    net_to_store, timestamp
    Raises ValueError if item is not found in the catalog.
    """
    global _fallback_spent, _fallback_burned, _fallback_vaulted

    key = item_name.strip().lower()
    if key not in _CATALOG_INDEX:
        raise ValueError(f"Item '{item_name}' not found in store catalog.")

    item      = _CATALOG_INDEX[key]
    price     = item["price"]
    category  = item["category"]
    burn_rate = BURN_RATES.get(category, 0.20)

    burned       = round(price * burn_rate, 2)
    vaulted      = round(price * VAULT_RATE, 2)
    net_to_store = round(price - burned - vaulted, 2)

    # ── hook into economy.py ───────────────────────────────
    if _ECONOMY_OK:
        econ_spend(price)
        econ_burn(burned)
    else:
        _fallback_spent  += price
        _fallback_burned += burned

    # ── hook into vault.py ────────────────────────────────
    if _VAULT_OK:
        deposit_revenue(vaulted, source="store_purchase")
    else:
        _fallback_vaulted += vaulted

    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    record = {
        "player":       player_id,
        "item":         item["name"],
        "category":     category,
        "price":        price,
        "burned":       burned,
        "vaulted":      vaulted,
        "net_to_store": net_to_store,
        "timestamp":    timestamp,
    }
    purchase_history.append(record)
    _save_transactions()

    return record


# ── analytics ──────────────────────────────────────────────
def top_sellers(n=5):
    """Return the top-n most purchased items."""
    counts = {}
    for tx in purchase_history:
        counts[tx["item"]] = counts.get(tx["item"], 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return ranked[:n]


def dead_items():
    """Return catalog items that have never been purchased."""
    sold = {tx["item"] for tx in purchase_history}
    return [item for item in CATALOG if item["name"] not in sold]


def revenue_report():
    """
    Return a summary dict with total revenue, total burned,
    total to vault, and a per-item breakdown.
    """
    total_revenue = 0.0
    total_burned  = 0.0
    total_vaulted = 0.0
    breakdown     = {}

    for tx in purchase_history:
        total_revenue += tx["price"]
        total_burned  += tx["burned"]
        total_vaulted += tx["vaulted"]
        item = tx["item"]
        if item not in breakdown:
            breakdown[item] = {"purchases": 0, "revenue": 0.0,
                               "burned": 0.0, "vaulted": 0.0}
        breakdown[item]["purchases"] += 1
        breakdown[item]["revenue"]   += tx["price"]
        breakdown[item]["burned"]    += tx["burned"]
        breakdown[item]["vaulted"]   += tx["vaulted"]

    return {
        "total_revenue": round(total_revenue, 2),
        "total_burned":  round(total_burned, 2),
        "total_vaulted": round(total_vaulted, 2),
        "net_to_store":  round(total_revenue - total_burned - total_vaulted, 2),
        "transactions":  len(purchase_history),
        "breakdown":     breakdown,
    }


def category_breakdown():
    """Return revenue totals grouped by category."""
    cats = {}
    for tx in purchase_history:
        cat = tx["category"]
        if cat not in cats:
            cats[cat] = {"purchases": 0, "revenue": 0.0,
                         "burned": 0.0, "vaulted": 0.0}
        cats[cat]["purchases"] += 1
        cats[cat]["revenue"]   += tx["price"]
        cats[cat]["burned"]    += tx["burned"]
        cats[cat]["vaulted"]   += tx["vaulted"]
    # round values
    for cat in cats:
        for k in ("revenue", "burned", "vaulted"):
            cats[cat][k] = round(cats[cat][k], 2)
    return cats


# ── display helpers ────────────────────────────────────────
def _print_separator(char="=", width=SEPARATOR_WIDTH):
    print(char * width)


def browse():
    """Print the full item catalog grouped by category."""
    by_cat = {}
    for item in CATALOG:
        by_cat.setdefault(item["category"], []).append(item)

    _print_separator()
    print("🏪  PCVR STORE — ITEM CATALOG")
    _print_separator()
    for cat, items in by_cat.items():
        print(f"\n  [{cat.upper()}]")
        for it in items:
            burn_pct = int(BURN_RATES[cat] * 100)
            print(f"  • {it['name']:<30} {it['price']:>6} PCVR  "
                  f"(burn {burn_pct}%)")
            print(f"    {it['description']}")
    print()


def print_revenue_report():
    """Pretty-print the revenue report."""
    r = revenue_report()
    _print_separator()
    print("📊  PCVR STORE — REVENUE REPORT")
    _print_separator()
    print(f"  Transactions  : {r['transactions']}")
    print(f"  Total Revenue : {r['total_revenue']:,.0f} PCVR")
    print(f"  Total Burned  : {r['total_burned']:,.0f} PCVR 🔥")
    print(f"  Total Vaulted : {r['total_vaulted']:,.0f} PCVR 🔒")
    print(f"  Net to Store  : {r['net_to_store']:,.0f} PCVR")
    if r["breakdown"]:
        print("\n  — Item Breakdown —")
        for name, d in sorted(r["breakdown"].items(),
                               key=lambda x: x[1]["revenue"], reverse=True):
            print(f"  • {name:<32} x{d['purchases']}  "
                  f"{d['revenue']:,.0f} PCVR")
    print()


def print_category_breakdown():
    """Pretty-print the category breakdown."""
    cats = category_breakdown()
    _print_separator()
    print("📂  PCVR STORE — CATEGORY BREAKDOWN")
    _print_separator()
    if not cats:
        print("  No purchases yet.")
    else:
        for cat, d in sorted(cats.items(),
                              key=lambda x: x[1]["revenue"], reverse=True):
            print(f"  {cat.upper():<12}  "
                  f"x{d['purchases']} buys  "
                  f"{d['revenue']:,.0f} PCVR revenue  "
                  f"{d['burned']:,.0f} burned")
    print()


# ── initialisation ─────────────────────────────────────────
_save_catalog()         # always write the current catalog to disk
_load_transactions()    # reload existing history from disk


# ── interactive CLI ────────────────────────────────────────
if __name__ == "__main__":
    _print_separator()
    print("🏪  PCVR STORE ENGINE")
    _print_separator()
    print("Commands:")
    print("  1. browse    → view all items")
    print("  2. buy       → purchase an item")
    print("  3. top       → top sellers")
    print("  4. dead      → items nobody buys")
    print("  5. revenue   → revenue report")
    print("  6. category  → category breakdown")
    print("  7. exit")
    _print_separator()

    while True:
        try:
            cmd = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if cmd in ("1", "browse"):
            browse()

        elif cmd in ("2", "buy"):
            player = input("  Player ID : ").strip()
            item   = input("  Item name : ").strip()
            try:
                tx = purchase(player, item)
                print(f"\n  ✅ Purchase recorded!")
                print(f"     Item      : {tx['item']}")
                print(f"     Price     : {tx['price']} PCVR")
                print(f"     Burned    : {tx['burned']} PCVR 🔥")
                print(f"     Vaulted   : {tx['vaulted']} PCVR 🔒")
                print(f"     Net Store : {tx['net_to_store']} PCVR")
            except ValueError as e:
                print(f"\n  ❌ {e}")

        elif cmd in ("3", "top"):
            sellers = top_sellers()
            print("\n  🏆 TOP SELLERS")
            if not sellers:
                print("  No purchases yet.")
            else:
                for i, (name, cnt) in enumerate(sellers, 1):
                    print(f"  {i}. {name}  ({cnt} sold)")

        elif cmd in ("4", "dead"):
            dead = dead_items()
            print("\n  💀 DEAD ITEMS (0 purchases)")
            if not dead:
                print("  Everything is selling!")
            else:
                for it in dead:
                    print(f"  • {it['name']}")

        elif cmd in ("5", "revenue"):
            print_revenue_report()

        elif cmd in ("6", "category"):
            print_category_breakdown()

        elif cmd in ("7", "exit", "quit", "q"):
            print("Goodbye.")
            break

        else:
            print("  Unknown command. Type 1-7.")
