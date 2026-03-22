# © PCVR STUDIOS 2026 — PCVR Coin Store Engine
# Token: PCVR Coin | Chain: Cronos
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# Every purchase auto-burns a portion and deposits to vault.
# Burn rates and vault deposits happen automatically on every purchase.

import json
import os
import datetime

# ------------------------------------
# BURN & VAULT RATES PER CATEGORY
# ------------------------------------
BURN_RATES = {
    "cosmetic":   0.20,
    "boost":      0.15,
    "tournament": 0.25,
    "premium":    0.20,
    "exclusive":  0.30,
}
VAULT_RATE = 0.10

# ------------------------------------
# ITEM CATALOG
# ------------------------------------
CATALOG = [
    # Cosmetic
    {"name": "Neon Ship Skin",        "price": 100,  "category": "cosmetic",   "description": "Electric neon glow skin for your ship"},
    {"name": "Plasma Trail",          "price": 75,   "category": "cosmetic",   "description": "Vivid plasma exhaust trail effect"},
    {"name": "Explosion Pack",        "price": 50,   "category": "cosmetic",   "description": "Custom explosion VFX on kills"},
    {"name": "Holographic Wrap",      "price": 300,  "category": "cosmetic",   "description": "Full holographic ship wrap — rare look"},
    {"name": "Animated Frame",        "price": 125,  "category": "cosmetic",   "description": "Animated profile border frame"},
    # Boost
    {"name": "2x XP Boost (24h)",     "price": 40,   "category": "boost",      "description": "Double XP for 24 hours"},
    {"name": "Reward Multiplier (7d)","price": 150,  "category": "boost",      "description": "1.5x token rewards for 7 days"},
    # Tournament
    {"name": "Weekly Tournament Entry","price": 200, "category": "tournament", "description": "Entry ticket to weekly PCVR tournament"},
    {"name": "Champions Cup Entry",   "price": 500,  "category": "tournament", "description": "Entry to monthly Champions Cup — big prize pool"},
    # Premium
    {"name": "Battle Pass Season 1",  "price": 350,  "category": "premium",    "description": "Full season battle pass with 50 reward tiers"},
    {"name": "Premium Monthly Pass",  "price": 250,  "category": "premium",    "description": "Monthly premium access — bonus missions + rewards"},
    # Exclusive
    {"name": "Founders Ship Skin",    "price": 1000, "category": "exclusive",  "description": "Limited edition OG Founders skin — never restocked"},
    {"name": "OG Badge",              "price": 150,  "category": "exclusive",  "description": "Verified OG player badge — shows on profile"},
    {"name": "One-of-One Ship",       "price": 2500, "category": "exclusive",  "description": "Unique 1/1 generative ship — true digital scarcity"},
    {"name": "Animated Banner",       "price": 200,  "category": "exclusive",  "description": "Animated PCVR profile banner — exclusive drop"},
]

# ------------------------------------
# RUNTIME STATE
# ------------------------------------
purchase_history = []
_internal_spent = 0.0
_internal_burned = 0.0
_internal_vault  = 0.0

# ------------------------------------
# INTEGRATION: economy.py + vault.py
# ------------------------------------
try:
    from economy import spend as _econ_spend, burn as _econ_burn
    _has_economy = True
except ImportError:
    _has_economy = False

try:
    from vault import deposit_revenue as _vault_deposit
    _has_vault = True
except ImportError:
    _has_vault = False

def _do_spend(amount):
    global _internal_spent
    if _has_economy:
        _econ_spend(amount)
    else:
        _internal_spent += amount

def _do_burn(amount):
    global _internal_burned
    if _has_economy:
        _econ_burn(amount)
    else:
        _internal_burned += amount

def _do_vault(amount, source):
    global _internal_vault
    if _has_vault:
        _vault_deposit(amount, source)
    else:
        _internal_vault += amount

# ------------------------------------
# CATALOG HELPERS
# ------------------------------------
def _catalog_dir():
    return os.path.dirname(os.path.abspath(__file__))

def save_catalog():
    path = os.path.join(_catalog_dir(), "store_catalog.json")
    with open(path, "w") as f:
        json.dump(CATALOG, f, indent=2)

def load_catalog():
    path = os.path.join(_catalog_dir(), "store_catalog.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return CATALOG

def find_item(name):
    for item in CATALOG:
        if item["name"].lower() == name.lower():
            return item
    return None

# ------------------------------------
# PURCHASE SYSTEM
# ------------------------------------
def purchase(player_id, item_name):
    """Buy an item. Auto-burns and deposits to vault on every purchase."""
    item = find_item(item_name)
    if item is None:
        print(f"  ❌ Item not found: {item_name}")
        return None

    price    = item["price"]
    category = item["category"]
    burn_rate = BURN_RATES.get(category, 0.20)

    burned       = round(price * burn_rate, 2)
    vault_amount = round(price * VAULT_RATE, 2)
    net_to_store = round(price - burned - vault_amount, 2)

    _do_spend(price)
    _do_burn(burned)
    _do_vault(vault_amount, "store")

    tx = {
        "player":       player_id,
        "item":         item["name"],
        "category":     category,
        "price":        price,
        "burned":       burned,
        "locked":       vault_amount,
        "net_to_store": net_to_store,
        "timestamp":    datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    purchase_history.append(tx)
    _save_transactions()

    print(f"  🛒 {player_id} bought '{item['name']}' for {price:,} PCVR")
    print(f"     🔥 Burned: {burned:,.2f} | 🏦 Vault: {vault_amount:,.2f} | 💼 Store: {net_to_store:,.2f}")
    return tx

def _save_transactions():
    path = os.path.join(_catalog_dir(), "store_transactions.json")
    with open(path, "w") as f:
        json.dump(purchase_history, f, indent=2)

# ------------------------------------
# ANALYTICS
# ------------------------------------
def top_sellers(n=5):
    counts = {}
    for tx in purchase_history:
        counts[tx["item"]] = counts.get(tx["item"], 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return ranked[:n]

def dead_items():
    sold = {tx["item"] for tx in purchase_history}
    return [item for item in CATALOG if item["name"] not in sold]

def revenue_report():
    total_rev   = sum(tx["price"]        for tx in purchase_history)
    total_burn  = sum(tx["burned"]       for tx in purchase_history)
    total_vault = sum(tx["locked"]       for tx in purchase_history)
    total_store = sum(tx["net_to_store"] for tx in purchase_history)

    item_rev = {}
    for tx in purchase_history:
        item_rev[tx["item"]] = item_rev.get(tx["item"], 0) + tx["price"]

    return {
        "total_revenue":   total_rev,
        "total_burned":    total_burn,
        "total_to_vault":  total_vault,
        "total_to_store":  total_store,
        "transactions":    len(purchase_history),
        "item_breakdown":  item_rev,
    }

def category_breakdown():
    breakdown = {}
    for tx in purchase_history:
        cat = tx["category"]
        breakdown[cat] = breakdown.get(cat, 0) + tx["price"]
    return breakdown

# ------------------------------------
# DISPLAY HELPERS
# ------------------------------------
def browse():
    print(f"\n{'='*50}")
    print("  🏪 PCVR STORE — Item Catalog")
    print(f"{'='*50}")
    current_cat = None
    for item in CATALOG:
        if item["category"] != current_cat:
            current_cat = item["category"]
            print(f"\n  [{current_cat.upper()}]")
        burn_pct = int(BURN_RATES[item["category"]] * 100)
        print(f"  • {item['name']:<30} {item['price']:>6,} PCVR  (burn {burn_pct}%)")
        print(f"    {item['description']}")
    print(f"\n  Vault deposit: {int(VAULT_RATE*100)}% on all items")
    print(f"{'='*50}\n")

def print_revenue_report():
    r = revenue_report()
    print(f"\n{'='*50}")
    print("  📊 PCVR Store — Revenue Report")
    print(f"{'='*50}")
    print(f"  Transactions: {r['transactions']:>10}")
    print(f"  Total Rev:    {r['total_revenue']:>10,.2f} PCVR")
    print(f"  Burned:       {r['total_burned']:>10,.2f} PCVR 🔥")
    print(f"  To Vault:     {r['total_to_vault']:>10,.2f} PCVR 🏦")
    print(f"  To Store:     {r['total_to_store']:>10,.2f} PCVR 💼")
    if r["item_breakdown"]:
        print(f"\n  Item Breakdown:")
        for item, rev in sorted(r["item_breakdown"].items(), key=lambda x: x[1], reverse=True):
            print(f"    {item:<34} {rev:>8,} PCVR")
    print(f"{'='*50}\n")

def print_category_breakdown():
    cb = category_breakdown()
    print(f"\n{'='*50}")
    print("  📂 Revenue by Category")
    print(f"{'='*50}")
    for cat, rev in sorted(cb.items(), key=lambda x: x[1], reverse=True):
        burn_pct = int(BURN_RATES.get(cat, 0.20) * 100)
        print(f"  {cat.capitalize():<14} {rev:>8,} PCVR  (burn rate {burn_pct}%)")
    print(f"{'='*50}\n")

# ------------------------------------
# INTERACTIVE CLI
# ------------------------------------
if __name__ == "__main__":
    save_catalog()

    print("""
==================================
🏪 PCVR STORE ENGINE
© PCVR STUDIOS 2026
Token: PCVR Coin | Chain: Cronos
Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4

"Earn → Hold → Spend → Buy → Earn.
 If any link breaks, the token dies."

Burn + vault deposit happen automatically
on every purchase.
==================================
Commands:
1. browse    → view all items
2. buy       → purchase an item
3. top       → top sellers
4. dead      → items nobody buys
5. revenue   → revenue report
6. category  → category breakdown
7. exit
==================================""")

    while True:
        cmd = input("\n> ").strip().lower()

        if cmd in ("1", "browse"):
            browse()

        elif cmd in ("2", "buy"):
            pid   = input("  Player ID: ").strip()
            iname = input("  Item name: ").strip()
            purchase(pid, iname)

        elif cmd in ("3", "top"):
            sellers = top_sellers()
            print("\n  🏆 Top Sellers:")
            if sellers:
                for rank, (name, count) in enumerate(sellers, 1):
                    print(f"  {rank}. {name} — {count} purchase(s)")
            else:
                print("  No sales yet.")

        elif cmd in ("4", "dead"):
            dead = dead_items()
            print("\n  💀 Dead Items (0 purchases):")
            if dead:
                for item in dead:
                    print(f"  • {item['name']}")
            else:
                print("  All items have been purchased!")

        elif cmd in ("5", "revenue"):
            print_revenue_report()

        elif cmd in ("6", "category"):
            print_category_breakdown()

        elif cmd in ("7", "exit", "quit", "q"):
            print("  👋 Closing PCVR Store. Earn → Hold → Spend → Buy → Earn.")
            break

        else:
            print("  ❓ Unknown command. Type a number 1-7.")
