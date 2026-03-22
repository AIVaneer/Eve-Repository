# PCVR — Token Economy Tracker
# The Earn > Hold > Spend > Buy loop

supply = 1_000_000_000
circ = 100_000_000
emitted = 0
burned = 0
spent = 0
locked = 0
cap = 50000
today = 0

def earn(a):
    global emitted, circ, today
    a = min(a, cap - today)
    if a <= 0: return 0
    emitted += a; circ += a; today += a
    return a

def spend(a):
    global spent
    spent += a; return a

def burn(a):
    global burned, circ, supply
    burned += a; circ -= a; supply -= a; return a

def lock(a):
    global locked
    locked += a; return a

def buy(a, burn_pct=15):
    spend(a); burn(a * burn_pct / 100)

def health():
    return spent / emitted if emitted > 0 else 1.0

def burn_ratio():
    return burned / emitted if emitted > 0 else 0.0

def net():
    return emitted - spent - burned

def new_day():
    global today
    today = 0

def report():
    h = health()
    s = "🟢" if h >= 1 else "🟡" if h >= .7 else "🟠" if h >= .5 else "🔴" if h >= .2 else "💀"
    n = net()
    ns = "🟢 Shrinking" if n <= 0 else "🔴 Growing"
    print(f"\n{'='*50}")
    print(f"  PCVR Economy Report")
    print(f"{'='*50}")
    print(f"  Supply:    {supply:>14,}")
    print(f"  Circulate: {circ:>14,}")
    print(f"  Emitted:   {emitted:>14,}")
    print(f"  Spent:     {spent:>14,}")
    print(f"  Burned:    {burned:>14,}")
    print(f"  Locked:    {locked:>14,}")
    print(f"  Net:       {n:>14,.0f} {ns}")
    print(f"  Health:    {h:>14.4f} {s}")
    print(f"  Burn Rate: {burn_ratio():>13.1%}")
    print(f"  Loop: Earn>Hold>Spend>Buy")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    earn(10000); buy(500); buy(300)
    lock(2000); earn(5000); buy(800)
    report()
