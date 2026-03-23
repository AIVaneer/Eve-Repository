# ============================================================
# PCVR Studios — live_data.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# PCVR Real-Time Market Data Engine
# Real data. Real decisions. No more guessing.
# ============================================================

import json
import os
import datetime

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# ── token config ───────────────────────────────────────────
TOKEN_ADDRESS = "0x05c870C5C6E7AF4298976886471c69Fc722107e4"
PAIR_ADDRESS  = "0x5a84Add7Ad701409F16C2c5B1CE213b024BCE68a"
CHAIN         = "cronos"
DATA_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "pcvr_market_data.json")

_DEXSCREENER_URL = (
    f"https://api.dexscreener.com/latest/dex/pairs/{CHAIN}/{PAIR_ADDRESS}"
)
_BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"
_BINANCE_SYMBOLS = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT"]

# ── defaults (used when API is unavailable) ────────────────
_DEFAULTS = {
    "price_usd":       0.000004063,
    "volume_24h":      0.0,
    "liquidity_usd":   0.0,
    "change_24h":      0.0,
    "change_1h":       0.0,
    "change_5m":       0.0,
    "buys":            0,
    "sells":           0,
    "pair_name":       "PCVR/WCRO",
    "market_cap":      0.0,
    "btc_price":       0.0,
    "eth_price":       0.0,
    "xrp_price":       0.0,
    "sol_price":       0.0,
    "btc_change_24h":  0.0,
    "source":          "defaults",
    "timestamp":       None,
}

# ── known wallet data ──────────────────────────────────────
WALLET_DATA = {
    "balance":          188_821_399.55,
    "liquidity_added":  12_547_410.08,
}


# ── API fetchers ───────────────────────────────────────────
def fetch_dexscreener():
    """
    Fetch live PCVR market data from DexScreener.
    Returns a dict with price, volume, liquidity, and change fields.
    Returns None on failure.
    """
    if not _HAS_REQUESTS:
        return None
    try:
        resp = _requests.get(_DEXSCREENER_URL, timeout=10)
        resp.raise_for_status()
        raw = resp.json()
        pairs = raw.get("pairs") or []
        if not pairs:
            return None
        pair = pairs[0]
        price_change = pair.get("priceChange") or {}
        txns_h24     = (pair.get("txns") or {}).get("h24") or {}
        liquidity    = pair.get("liquidity") or {}
        volume       = pair.get("volume") or {}
        return {
            "price_usd":     float(pair.get("priceUsd") or 0),
            "volume_24h":    float(volume.get("h24") or 0),
            "liquidity_usd": float(liquidity.get("usd") or 0),
            "change_24h":    float(price_change.get("h24") or 0),
            "change_1h":     float(price_change.get("h1") or 0),
            "change_5m":     float(price_change.get("m5") or 0),
            "buys":          int(txns_h24.get("buys") or 0),
            "sells":         int(txns_h24.get("sells") or 0),
            "pair_name":     pair.get("baseToken", {}).get("symbol", "PCVR")
                             + "/" + pair.get("quoteToken", {}).get("symbol", ""),
            "market_cap":    float(pair.get("marketCap") or pair.get("fdv") or 0),
        }
    except Exception:
        return None


def fetch_binance_btc():
    """
    Fetch BTC/ETH/XRP/SOL prices from Binance.
    Returns a dict or None on failure.
    """
    if not _HAS_REQUESTS:
        return None
    result = {}
    try:
        for sym in _BINANCE_SYMBOLS:
            resp = _requests.get(_BINANCE_URL, params={"symbol": sym}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            key = sym.replace("USDT", "").lower()
            result[f"{key}_price"]     = float(data.get("lastPrice") or 0)
            if sym == "BTCUSDT":
                result["btc_change_24h"] = float(data.get("priceChangePercent") or 0)
        return result
    except Exception:
        return None


# ── cache ──────────────────────────────────────────────────
def save_snapshot(data):
    """Save market data dict to DATA_FILE with current timestamp."""
    snapshot = dict(data)
    snapshot["timestamp"] = datetime.datetime.utcnow().isoformat()
    try:
        with open(DATA_FILE, "w") as fh:
            json.dump(snapshot, fh, indent=2)
    except IOError:
        pass


def load_snapshot():
    """Load last cached market data. Returns None if no cache exists."""
    if not os.path.exists(DATA_FILE):
        return None
    try:
        with open(DATA_FILE, "r") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, IOError):
        return None


def _snapshot_age_seconds(snapshot):
    """Return age of snapshot in seconds, or infinity if unknown."""
    ts = snapshot.get("timestamp")
    if not ts:
        return float("inf")
    try:
        t = datetime.datetime.fromisoformat(ts)
        return (datetime.datetime.utcnow() - t).total_seconds()
    except (ValueError, TypeError):
        return float("inf")


def get_data(force_refresh=False):
    """
    Smart market data getter.
    - Returns cached data if < 60 seconds old (unless force_refresh).
    - Otherwise fetches fresh data from APIs.
    - Falls back to cached data or defaults if fetch fails.
    """
    cached = load_snapshot()

    if not force_refresh and cached and _snapshot_age_seconds(cached) < 60:
        return cached

    # build a fresh snapshot
    dex  = fetch_dexscreener()
    bnb  = fetch_binance_btc()

    if dex is not None:
        data = dict(_DEFAULTS)
        data.update(dex)
        if bnb:
            data.update(bnb)
        data["source"] = "live"
        save_snapshot(data)
        return data

    # fetch failed — use cached if available
    if cached:
        return cached

    # nothing available — return defaults
    data = dict(_DEFAULTS)
    data["timestamp"] = datetime.datetime.utcnow().isoformat()
    return data


# ── derived metrics ────────────────────────────────────────
def price_to_pcvr(usd_amount):
    """Convert a USD amount to PCVR tokens at current price."""
    data  = get_data()
    price = data.get("price_usd") or 0
    if price <= 0:
        return 0.0
    return usd_amount / price


def pcvr_to_usd(pcvr_amount):
    """Convert a PCVR token amount to USD at current price."""
    data  = get_data()
    price = data.get("price_usd") or 0
    return pcvr_amount * price


def liquidity_ratio():
    """
    Return liquidity / market cap.
    Higher is healthier. Returns 0 if market cap is unknown.
    """
    data = get_data()
    liq  = data.get("liquidity_usd") or 0
    mcap = data.get("market_cap") or 0
    if mcap <= 0:
        return 0.0
    return liq / mcap


def volume_ratio():
    """
    Return 24h volume / liquidity (activity indicator).
    Returns 0 if liquidity is unknown.
    """
    data = get_data()
    vol  = data.get("volume_24h") or 0
    liq  = data.get("liquidity_usd") or 0
    if liq <= 0:
        return 0.0
    return vol / liq


def market_status():
    """
    Return a human-readable market status string based on V8 risk engine logic.
    """
    data       = get_data()
    change_24h = data.get("change_24h") or 0
    volume     = data.get("volume_24h") or 0

    if change_24h < -10:
        return "🚨 HEAVY DUMP"
    if change_24h > 10:
        return "🚀 PARABOLIC"
    if volume < 5000:
        return "⚠️ LOW ACTIVITY"
    if change_24h < -5:
        return "📉 BEARISH"
    if change_24h > 5:
        return "📈 BULLISH"
    return "✅ STABLE"


def supply_pressure():
    """
    Return supply pressure level based on V7 logic.
    Uses liquidity ratio as the primary signal.
    """
    ratio = liquidity_ratio()
    if ratio < 0.01:
        return "EXTREME"
    if ratio < 0.05:
        return "HIGH"
    if ratio < 0.15:
        return "MEDIUM"
    return "LOW"


# ── wallet tracker ─────────────────────────────────────────
def wallet_value():
    """Return current USD value of the known wallet balance."""
    return pcvr_to_usd(WALLET_DATA["balance"])


def wallet_report():
    """Print and return a full wallet breakdown dict."""
    data    = get_data()
    price   = data.get("price_usd") or 0
    balance = WALLET_DATA["balance"]
    liq     = WALLET_DATA["liquidity_added"]
    usd_val = balance * price

    print("\n  💼 WALLET REPORT")
    print(f"  Balance          : {balance:>22,.2f} PCVR")
    print(f"  Current price    : ${price:.10f}")
    print(f"  USD value        : ${usd_val:>18.4f}")
    print(f"  Liquidity added  : {liq:>22,.2f} PCVR")

    return {
        "balance":         balance,
        "price_usd":       price,
        "usd_value":       usd_val,
        "liquidity_added": liq,
    }


# ── market report ──────────────────────────────────────────
def market_report():
    """Print a full PCVR market report."""
    data     = get_data(force_refresh=True)
    price    = data.get("price_usd") or 0
    ch24     = data.get("change_24h") or 0
    ch1h     = data.get("change_1h") or 0
    ch5m     = data.get("change_5m") or 0
    vol      = data.get("volume_24h") or 0
    liq      = data.get("liquidity_usd") or 0
    buys     = data.get("buys") or 0
    sells    = data.get("sells") or 0
    pair     = data.get("pair_name") or "PCVR"
    btc_p    = data.get("btc_price") or 0
    eth_p    = data.get("eth_price") or 0
    xrp_p    = data.get("xrp_price") or 0
    sol_p    = data.get("sol_price") or 0
    btc_ch   = data.get("btc_change_24h") or 0
    status   = market_status()
    pressure = supply_pressure()
    liq_r    = liquidity_ratio()
    vol_r    = volume_ratio()
    w_val    = wallet_value()
    total_tx = buys + sells
    buy_ratio = (buys / total_tx * 100) if total_tx > 0 else 0.0
    source   = data.get("source", "unknown")
    ts       = (data.get("timestamp") or "")[:19].replace("T", " ")

    print("\n" + "=" * 50)
    print("  📡 PCVR LIVE MARKET REPORT")
    print("=" * 50)
    print(f"  Pair             : {pair}")
    print(f"  Price USD        : ${price:.10f}")
    print(f"  24h Change       : {ch24:+.2f}%")
    print(f"  1h Change        : {ch1h:+.2f}%")
    print(f"  5m Change        : {ch5m:+.2f}%")
    print(f"  24h Volume       : ${vol:>14,.2f}")
    print(f"  Liquidity        : ${liq:>14,.2f}")
    print()
    print(f"  BTC              : ${btc_p:>14,.2f}  ({btc_ch:+.2f}%)")
    print(f"  ETH              : ${eth_p:>14,.2f}")
    print(f"  XRP              : ${xrp_p:>14,.4f}")
    print(f"  SOL              : ${sol_p:>14,.2f}")
    print()
    print(f"  Market Status    : {status}")
    print(f"  Supply Pressure  : {pressure}")
    print(f"  Liquidity Ratio  : {liq_r:.4f}")
    print(f"  Volume Ratio     : {vol_r:.4f}")
    print()
    print(f"  Wallet Value     : ${w_val:>14,.4f}")
    print(f"  Buy/Sell Ratio   : {buys} buys / {sells} sells"
          + (f"  ({buy_ratio:.1f}% buys)" if total_tx else ""))
    print()
    print(f"  Source: {source}  |  As of: {ts} UTC")
    print("=" * 50)

    # ── fire alerts for significant market events ──────────
    try:
        import alert as _alert
        if data.get("change_24h", 0) < -10:
            _alert.fire("critical", "economy", "HEAVY DUMP detected on PCVR",
                        source="live_data",
                        data={"change_24h": data.get("change_24h")})
        elif data.get("change_24h", 0) > 10:
            _alert.fire("warning", "economy", "PARABOLIC move detected on PCVR",
                        source="live_data",
                        data={"change_24h": data.get("change_24h")})
        elif (data.get("volume_24h") or 0) < 5000:
            _alert.fire("warning", "economy", "Low PCVR trading activity (volume < $5,000)",
                        source="live_data",
                        data={"volume_24h": data.get("volume_24h")})
    except Exception:
        pass

    # ── log significant moves to history ledger ────────────
    try:
        import history as _hist
        if abs(data.get("change_24h", 0)) >= 5:
            _hist.log_event("price_alert", 0,
                            details=f"PCVR 24h change: {ch24:+.2f}%  status: {status}",
                            source="live_data")
    except Exception:
        pass

    return data


# ── economy bridge ─────────────────────────────────────────
def get_price():
    """Return current PCVR price in USD. Used by other modules."""
    return get_data().get("price_usd") or 0.0


# expose live price to economy module if possible
try:
    import economy as _econ
    _econ._live_price = get_price
except Exception:
    pass


# ── interactive CLI ────────────────────────────────────────
def _cli():
    print("""
==================================
📡 PCVR LIVE DATA ENGINE
==================================
Commands:
1. price      → current PCVR price
2. market     → full market report
3. wallet     → wallet value
4. btc        → BTC/ETH/XRP/SOL prices
5. status     → market status
6. pressure   → supply pressure
7. convert    → USD ↔ PCVR converter
8. monitor    → auto-refresh every 30 seconds
9. exit
==================================
""")
    import time

    while True:
        try:
            cmd = input("live_data> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if cmd in ("1", "price"):
            data  = get_data(force_refresh=True)
            price = data.get("price_usd") or 0
            ch24  = data.get("change_24h") or 0
            print(f"\n  PCVR Price  : ${price:.10f}")
            print(f"  24h Change  : {ch24:+.2f}%\n")

        elif cmd in ("2", "market"):
            market_report()

        elif cmd in ("3", "wallet"):
            wallet_report()

        elif cmd in ("4", "btc"):
            data  = get_data(force_refresh=True)
            print(f"\n  BTC  : ${data.get('btc_price', 0):>14,.2f}  "
                  f"({data.get('btc_change_24h', 0):+.2f}%)")
            print(f"  ETH  : ${data.get('eth_price', 0):>14,.2f}")
            print(f"  XRP  : ${data.get('xrp_price', 0):>14,.4f}")
            print(f"  SOL  : ${data.get('sol_price', 0):>14,.2f}\n")

        elif cmd in ("5", "status"):
            print(f"\n  Market Status: {market_status()}\n")

        elif cmd in ("6", "pressure"):
            print(f"\n  Supply Pressure: {supply_pressure()}\n")

        elif cmd in ("7", "convert"):
            try:
                raw = input("  Enter amount (e.g. 10 USD or 1000000 PCVR): ").strip()
                parts = raw.split()
                amount = float(parts[0])
                unit   = parts[1].upper() if len(parts) > 1 else "USD"
                if unit == "USD":
                    result = price_to_pcvr(amount)
                    print(f"\n  ${amount:.4f} USD  =  {result:,.2f} PCVR\n")
                else:
                    result = pcvr_to_usd(amount)
                    print(f"\n  {amount:,.2f} PCVR  =  ${result:.6f} USD\n")
            except (ValueError, IndexError):
                print("  ❌ Invalid input. Example: 10 USD or 1000000 PCVR\n")

        elif cmd in ("8", "monitor"):
            print("  🔄 Auto-refresh every 30s. Press Ctrl+C to stop.\n")
            try:
                while True:
                    data   = get_data(force_refresh=True)
                    price  = data.get("price_usd") or 0
                    ch24   = data.get("change_24h") or 0
                    status = market_status()
                    now    = datetime.datetime.utcnow().strftime("%H:%M:%S")
                    print(f"  [{now}]  ${price:.10f}  {ch24:+.2f}%  {status}")
                    time.sleep(30)
            except KeyboardInterrupt:
                print("\n  Monitor stopped.\n")

        elif cmd in ("9", "exit", "quit"):
            print("  Bye.")
            break

        else:
            print("  Unknown command. Type 1-9.\n")


if __name__ == "__main__":
    _cli()
