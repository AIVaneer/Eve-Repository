# PCVR — Earnings Vault (3-Month Lock)
# Funded by REAL revenue, not minting

vault_balance = 0
total_locked = 0
lockers = {}

def deposit_revenue(amount, source="store"):
    global vault_balance
    vault_balance += amount
    print(f"  💰 +{amount:,.0f} PCVR to vault from {source}")

def lock_tokens(player, amount):
    global total_locked
    lockers[player] = {"amount": amount, "day": 0}
    total_locked += amount
    print(f"  🔒 {player} locked {amount:,.0f} PCVR for 90 days")

def advance_day():
    for p in lockers:
        lockers[p]["day"] += 1

def check_unlocks():
    unlocked = []
    for p, d in lockers.items():
        if d["day"] >= 90:
            share = d["amount"] / total_locked if total_locked > 0 else 0
            earnings = vault_balance * share
            print(f"  🔓 {p}: {d['amount']:,.0f} + {earnings:,.2f} earnings")
            unlocked.append(p)
    for p in unlocked:
        del lockers[p]

def vault_apy():
    if total_locked == 0: return 0
    daily = vault_balance / total_locked / 90
    return daily * 365 * 100

def report():
    print(f"\n{'='*50}")
    print(f"  PCVR Earnings Vault")
    print(f"{'='*50}")
    print(f"  Vault Balance:  {vault_balance:>12,.2f} PCVR")
    print(f"  Total Locked:   {total_locked:>12,.2f} PCVR")
    print(f"  Lockers:        {len(lockers):>12}")
    print(f"  Est. APY:       {vault_apy():>11.1f}%")
    r = total_locked / 100_000_000 * 100 if total_locked > 0 else 0
    s = "🟢" if r >= 20 else "🟡" if r >= 10 else "🔴"
    print(f"  Lock Ratio:     {r:>11.1f}% {s}")
    print(f"  Source: Real revenue only")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    deposit_revenue(5000, "store")
    deposit_revenue(2000, "tournament")
    deposit_revenue(1000, "premium")
    lock_tokens("player_1", 5000)
    lock_tokens("player_2", 10000)
    lock_tokens("player_3", 3000)
    report()
