# PCVR — Debasement Detector
# Run daily. If it goes red, STOP.

def check(emitted, spent, burned, locked, circ, supply, cap, today):
    print(f"\n{'='*50}")
    print(f"  🔍 Debasement Detector")
    print(f"{'='*50}\n")
    issues = []
    h = spent / emitted if emitted > 0 else 1.0
    b = burned / emitted if emitted > 0 else 0
    n = emitted - spent - burned
    lr = locked / circ * 100 if circ > 0 else 0
    if h < 0.2: issues.append("💀 CRITICAL: Health < 0.2")
    elif h < 0.5: issues.append("🔴 DANGER: Health < 0.5")
    elif h < 0.7: issues.append("🟠 WARNING: Health < 0.7")
    if b < 0.05 and emitted > 0: issues.append("⚠️  Burn < 5%")
    if spent / emitted < 0.3 and emitted > 0: issues.append("⚠️  Spend < 30%")
    if circ > supply * 0.8: issues.append("⚠️  Circ > 80% of supply")
    if cap > 0 and today > cap * 0.9: issues.append("⚠️  Daily cap > 90%")
    if n > emitted * 0.5 and emitted > 0: issues.append("🔴 Net emission high")
    if lr < 10: issues.append("⚠️  Lock ratio < 10%")
    if issues:
        for i in issues: print(f"  {i}")
        print(f"\n  FIX: Lower rewards, add spend, raise burns")
    else:
        print("  ✅ No debasement risk detected")
    print(f"\n  Health: {h:.4f} | Burn: {b:.1%} | Lock: {lr:.1f}%")
    print(f"  Net: {n:,.0f} | {'🟢 Deflating' if n<=0 else '🔴 Inflating'}")
    print(f"{'='*50}\n")
    return len(issues) == 0

if __name__ == "__main__":
    check(50000, 15000, 3000, 8000, 100050000, 999997000, 50000, 45000)
