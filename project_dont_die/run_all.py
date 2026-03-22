# PCVR — Run Everything
# One script to see the full picture

from token_data import show as token_info
from economy import earn, buy, lock, spend, burn, report as econ_report, new_day
from vault import deposit_revenue, lock_tokens, report as vault_report
from detector import check
from atlas_graph_core import AtlasGraphCore
import economy as e

print("\n" + "=" * 50)
print("  PCVR STUDIOS — PROJECT DON'T DIE")
print("  Token Economy Engine · March 2026")
print("=" * 50)

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

# 6. Atlas Graph Core — quick economy health check
print("=" * 50)
print("  🧠 ATLAS GRAPH CORE v2 — Economy Health")
print("=" * 50)
atlas = AtlasGraphCore()
print(" ", atlas.quick_economy_health())
print(f"{'='*50}\n")
