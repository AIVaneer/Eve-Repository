# © PCVR Studios 2026 — Multi-Chain Tracker v1.0
# V10 Phase 5 — Multi-Chain Expansion Beyond Cronos
#
# One token. Every chain. Total visibility.
# Earn → Hold → Spend → Buy → Earn. Across every chain.
#
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
# Runs in Pythonista 3 on iOS — requests + standard library only

import json
import os
import datetime
import time
import hashlib

_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Config / Cache paths ─────────────────────────────────────────────────────

MULTICHAIN_CONFIG = os.path.join(_DIR, "multichain_config.json")
MULTICHAIN_CACHE  = os.path.join(_DIR, "multichain_cache.json")

PCVR_CONTRACT = "0x05c870C5C6E7AF4298976886471c69Fc722107e4"

DEXSCREENER_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search?q="
DEXSCREENER_PAIRS_URL  = "https://api.dexscreener.com/latest/dex/pairs/"

# requests is optional (but available in Pythonista 3)
try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False


# ─── Graceful module imports ──────────────────────────────────────────────────

def _try_import(name):
    import sys
    if _DIR not in sys.path:
        sys.path.insert(0, _DIR)
    try:
        import importlib
        return importlib.import_module(name), None
    except Exception as exc:
        return None, str(exc)


_live_data,        _ = _try_import("live_data")
_alert,            _ = _try_import("alert")
_smart_integrations,_ = _try_import("smart_integrations")
_history,          _ = _try_import("history")
_automation,       _ = _try_import("automation")


# ─── Chain Registry ───────────────────────────────────────────────────────────

CHAINS = {
    "cronos": {
        "chain_id": 25,
        "name": "Cronos",
        "symbol": "CRO",
        "explorer": "https://cronoscan.com",
        "dex_screener_id": "cronos",
        "rpc": "https://evm.cronos.org",
        "color": "#002D74",
        "active": True,
    },
    "ethereum": {
        "chain_id": 1,
        "name": "Ethereum",
        "symbol": "ETH",
        "explorer": "https://etherscan.io",
        "dex_screener_id": "ethereum",
        "rpc": "https://eth.llamarpc.com",
        "color": "#627EEA",
        "active": True,
    },
    "bsc": {
        "chain_id": 56,
        "name": "BNB Smart Chain",
        "symbol": "BNB",
        "explorer": "https://bscscan.com",
        "dex_screener_id": "bsc",
        "rpc": "https://bsc-dataseed.binance.org",
        "color": "#F0B90B",
        "active": True,
    },
    "polygon": {
        "chain_id": 137,
        "name": "Polygon",
        "symbol": "MATIC",
        "explorer": "https://polygonscan.com",
        "dex_screener_id": "polygon",
        "rpc": "https://polygon-rpc.com",
        "color": "#8247E5",
        "active": True,
    },
    "arbitrum": {
        "chain_id": 42161,
        "name": "Arbitrum One",
        "symbol": "ETH",
        "explorer": "https://arbiscan.io",
        "dex_screener_id": "arbitrum",
        "rpc": "https://arb1.arbitrum.io/rpc",
        "color": "#28A0F0",
        "active": True,
    },
    "avalanche": {
        "chain_id": 43114,
        "name": "Avalanche C-Chain",
        "symbol": "AVAX",
        "explorer": "https://snowtrace.io",
        "dex_screener_id": "avalanche",
        "rpc": "https://api.avax.network/ext/bc/C/rpc",
        "color": "#E84142",
        "active": True,
    },
    "base": {
        "chain_id": 8453,
        "name": "Base",
        "symbol": "ETH",
        "explorer": "https://basescan.org",
        "dex_screener_id": "base",
        "rpc": "https://mainnet.base.org",
        "color": "#0052FF",
        "active": True,
    },
    "solana": {
        "chain_id": None,   # Solana is non-EVM — no EVM-style chain ID
        "name": "Solana",
        "symbol": "SOL",
        "explorer": "https://solscan.io",
        "dex_screener_id": "solana",
        "rpc": "https://api.mainnet-beta.solana.com",
        "color": "#14F195",
        "active": True,
    },
}

# Known bridges to pre-register.
# Contracts listed are illustrative placeholders — replace with real
# deployed bridge contract addresses when available.
_DEFAULT_BRIDGES = [
    {
        "from_chain": "cronos",
        "to_chain": "ethereum",
        "bridge_name": "Cronos Bridge",
        "contract": None,   # placeholder — register real address via add_bridge_contract()
    },
    {
        "from_chain": "cronos",
        "to_chain": "ethereum",
        "bridge_name": "Multichain (deprecated)",
        "contract": None,   # placeholder
    },
    {
        "from_chain": "cronos",
        "to_chain": "bsc",
        "bridge_name": "Celer cBridge",
        "contract": None,   # placeholder
    },
    {
        "from_chain": "cronos",
        "to_chain": "ethereum",
        "bridge_name": "LayerZero",
        "contract": None,   # placeholder
    },
]


# ─── Cache helpers ────────────────────────────────────────────────────────────

def _load_cache():
    if not os.path.exists(MULTICHAIN_CACHE):
        return {}
    try:
        with open(MULTICHAIN_CACHE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(data):
    try:
        with open(MULTICHAIN_CACHE, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception:
        pass


def _cache_key(label):
    return hashlib.md5(label.encode()).hexdigest()[:12]


# ─── BridgeTracker ────────────────────────────────────────────────────────────

class BridgeTracker:
    """
    Track known bridge contracts and simulate bridge activity.
    """

    def __init__(self):
        self.bridges = list(_DEFAULT_BRIDGES)

    def register_bridge(self, from_chain, to_chain, bridge_name, contract):
        """Register a bridge between two chains."""
        self.bridges.append({
            "from_chain": from_chain,
            "to_chain": to_chain,
            "bridge_name": bridge_name,
            "contract": contract,
        })

    def check_bridge_activity(self):
        """
        Check if tokens have been bridged recently.
        Returns list of bridge activity dicts.
        """
        activity = []
        for b in self.bridges:
            activity.append({
                "bridge": b["bridge_name"],
                "from": b["from_chain"],
                "to": b["to_chain"],
                "contract": b["contract"],
                "last_seen": None,
                "volume_7d": 0,
                "status": "monitoring",
            })
        return activity

    def bridge_flow_summary(self):
        """
        Net flow between chains.
        Real implementation requires on-chain transaction data.
        Returns a dict of {chain: net_flow} (all zeros until on-chain data is wired in).
        """
        flows = {}
        for b in self.bridges:
            fc = b["from_chain"]
            tc = b["to_chain"]
            # Placeholder: actual flows require indexing bridge events on-chain
            flows.setdefault(fc, 0)
            flows.setdefault(tc, 0)
        return flows

    def list_bridges(self):
        return list(self.bridges)


# ─── MultiChainTracker ────────────────────────────────────────────────────────

class MultiChainTracker:
    """
    Core multi-chain tracking engine.

    Searches DexScreener for PCVR across all chains in the registry,
    aggregates liquidity and volume, compares prices, and produces
    a formatted cross-chain report.
    """

    CHAIN_CACHE_TTL  = 60   # seconds — DexScreener per-chain cache
    AGGR_CACHE_TTL   = 30   # seconds — aggregated data cache

    def __init__(self):
        self.pcvr_contract  = PCVR_CONTRACT
        self.bridge_contracts = {}    # chain → contract address
        self.chain_data     = {}      # chain → cached pair list
        self._chain_ts      = {}      # chain → last fetch timestamp
        self.aggregated     = {}      # cached aggregated data
        self._aggr_ts       = 0
        self.bridge_tracker = BridgeTracker()
        self._chain_registry = {k: dict(v) for k, v in CHAINS.items()}
        self._load_config()

    # ── Config management ────────────────────────────────────────────────────

    def save_config(self):
        """Persist chain registry + bridge contracts to MULTICHAIN_CONFIG."""
        data = {
            "chains": self._chain_registry,
            "bridge_contracts": self.bridge_contracts,
            "bridges": self.bridge_tracker.list_bridges(),
            "saved_at": datetime.datetime.utcnow().isoformat(),
        }
        try:
            with open(MULTICHAIN_CONFIG, "w") as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception:
            return False

    def _load_config(self):
        """Load chain + bridge settings from MULTICHAIN_CONFIG if it exists."""
        if not os.path.exists(MULTICHAIN_CONFIG):
            return
        try:
            with open(MULTICHAIN_CONFIG, "r") as f:
                data = json.load(f)
            if "chains" in data:
                for k, v in data["chains"].items():
                    if k not in self._chain_registry:
                        self._chain_registry[k] = v
                    else:
                        self._chain_registry[k].update(v)
            if "bridge_contracts" in data:
                self.bridge_contracts.update(data["bridge_contracts"])
            if "bridges" in data:
                for b in data["bridges"]:
                    if b not in self.bridge_tracker.bridges:
                        self.bridge_tracker.bridges.append(b)
        except Exception:
            pass

    def load_config(self):
        self._load_config()

    def add_chain(self, chain_id, name, symbol="?", explorer="", dex_screener_id="",
                  rpc="", color="#FFFFFF"):
        """Add a custom chain to the registry."""
        key = name.lower().replace(" ", "_")
        self._chain_registry[key] = {
            "chain_id": chain_id,
            "name": name,
            "symbol": symbol,
            "explorer": explorer,
            "dex_screener_id": dex_screener_id or key,
            "rpc": rpc,
            "color": color,
            "active": True,
        }
        return key

    def add_bridge_contract(self, chain, contract):
        """Register PCVR contract address on a given chain."""
        self.bridge_contracts[chain] = contract

    def enable_chain(self, chain):
        if chain in self._chain_registry:
            self._chain_registry[chain]["active"] = True

    def disable_chain(self, chain):
        if chain in self._chain_registry:
            self._chain_registry[chain]["active"] = False

    # ── Cache management ─────────────────────────────────────────────────────

    def clear_cache(self):
        self.chain_data = {}
        self._chain_ts  = {}
        self.aggregated = {}
        self._aggr_ts   = 0
        try:
            if os.path.exists(MULTICHAIN_CACHE):
                os.remove(MULTICHAIN_CACHE)
        except Exception:
            pass

    def cache_status(self):
        """Return dict describing cache state."""
        now = time.time()
        chains = {}
        for chain, ts in self._chain_ts.items():
            age = int(now - ts)
            chains[chain] = {
                "age_seconds": age,
                "fresh": age < self.CHAIN_CACHE_TTL,
                "pairs": len(self.chain_data.get(chain, [])),
            }
        aggr_age = int(now - self._aggr_ts) if self._aggr_ts else None
        return {
            "chains": chains,
            "aggregated_age_seconds": aggr_age,
            "aggregated_fresh": (aggr_age is not None and aggr_age < self.AGGR_CACHE_TTL),
        }

    # ── DexScreener API ──────────────────────────────────────────────────────

    def search_token_all_chains(self, query="PCVR"):
        """
        Search DexScreener for the token across ALL chains.
        Returns list of pair dicts found.
        """
        if not _REQUESTS_OK:
            return []
        try:
            url = DEXSCREENER_SEARCH_URL + query
            resp = _requests.get(url, timeout=10)
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("pairs") or []
        except Exception:
            return []

    def get_pair_data(self, chain, pair_address):
        """
        Get specific pair data on a given chain from DexScreener.
        Returns pair dict or {}.
        """
        if not _REQUESTS_OK:
            return {}
        chain_id = self._chain_registry.get(chain, {}).get("dex_screener_id", chain)
        try:
            url = DEXSCREENER_PAIRS_URL + chain_id + "/" + pair_address
            resp = _requests.get(url, timeout=10)
            if resp.status_code != 200:
                return {}
            data = resp.json()
            pairs = data.get("pairs") or []
            return pairs[0] if pairs else {}
        except Exception:
            return {}

    def scan_all_dexes(self):
        """
        Scan DexScreener for PCVR on every active chain in the registry.
        Returns {chain: [pairs]} for every chain where PCVR exists.
        """
        now   = time.time()
        pairs = self.search_token_all_chains("PCVR")

        # Group by chain
        by_chain = {}
        for pair in pairs:
            chain_id = (pair.get("chainId") or "").lower()
            # Map DexScreener chainId → our registry key
            reg_key = self._dexscreener_id_to_key(chain_id)
            by_chain.setdefault(reg_key, []).append(pair)

        # Update per-chain cache
        for chain, chain_pairs in by_chain.items():
            self.chain_data[chain] = chain_pairs
            self._chain_ts[chain]  = now

        # Mark chains with no results
        for key, cfg in self._chain_registry.items():
            if cfg.get("active") and key not in by_chain:
                if key not in self.chain_data or (now - self._chain_ts.get(key, 0)) > self.CHAIN_CACHE_TTL:
                    self.chain_data[key] = []
                    self._chain_ts[key]  = now

        return {k: v for k, v in self.chain_data.items() if v}

    def _dexscreener_id_to_key(self, dex_id):
        """Map a DexScreener chainId string to our registry key."""
        for key, cfg in self._chain_registry.items():
            if cfg.get("dex_screener_id", "").lower() == dex_id:
                return key
        return dex_id

    def _get_chain_data(self, chain):
        """Return cached pair list for a chain, refreshing if stale."""
        now = time.time()
        if (now - self._chain_ts.get(chain, 0)) > self.CHAIN_CACHE_TTL:
            self.scan_all_dexes()
        return self.chain_data.get(chain, [])

    # ── Cross-chain liquidity ────────────────────────────────────────────────

    def aggregate_liquidity(self):
        """
        Combine liquidity and volume across all chains.
        Returns aggregated dict.
        """
        now = time.time()
        if self.aggregated and (now - self._aggr_ts) < self.AGGR_CACHE_TTL:
            return self.aggregated

        # Ensure we have fresh data
        by_chain = self.scan_all_dexes()

        chains   = {}
        total_liq = 0.0
        total_vol = 0.0

        for chain, pairs in by_chain.items():
            liq = sum(float(p.get("liquidity", {}).get("usd") or 0) for p in pairs)
            vol = sum(float(p.get("volume", {}).get("h24") or 0) for p in pairs)
            chains[chain] = {
                "liquidity": liq,
                "volume":    vol,
                "pairs":     len(pairs),
            }
            total_liq += liq
            total_vol += vol

        dominant = max(chains, key=lambda c: chains[c]["liquidity"]) if chains else "cronos"
        diversity = self.chain_diversity_score(chains_data=chains, total=total_liq)

        self.aggregated = {
            "total_liquidity_usd": total_liq,
            "total_volume_24h":    total_vol,
            "chains":              chains,
            "dominant_chain":      dominant,
            "diversity_score":     diversity,
        }
        self._aggr_ts = now
        return self.aggregated

    def liquidity_distribution(self):
        """
        Return dict of {chain: pct_of_total_liquidity}.
        """
        aggr  = self.aggregate_liquidity()
        total = aggr.get("total_liquidity_usd") or 0
        if total == 0:
            return {}
        return {
            c: round(v["liquidity"] / total * 100, 2)
            for c, v in aggr.get("chains", {}).items()
        }

    def volume_distribution(self):
        """
        Return dict of {chain: pct_of_total_volume}.
        """
        aggr  = self.aggregate_liquidity()
        total = aggr.get("total_volume_24h") or 0
        if total == 0:
            return {}
        return {
            c: round(v["volume"] / total * 100, 2)
            for c, v in aggr.get("chains", {}).items()
        }

    def chain_diversity_score(self, chains_data=None, total=None):
        """
        0-1 score: 0 = all liquidity on one chain, 1 = perfectly even.
        Uses the complement of the Herfindahl-Hirschman Index normalised to [0, 1].
        """
        if chains_data is None:
            aggr        = self.aggregate_liquidity()
            chains_data = aggr.get("chains", {})
            total       = aggr.get("total_liquidity_usd") or 0

        if not chains_data or not total:
            return 0.0

        n     = len(chains_data)
        hhi   = sum((v["liquidity"] / total) ** 2 for v in chains_data.values() if total)
        # Normalize: perfect distribution → score 1, monopoly → score 0
        if n <= 1:
            return 0.0
        score = (1 - hhi) / (1 - 1 / n)
        return round(max(0.0, min(1.0, score)), 4)

    # ── Price comparison ─────────────────────────────────────────────────────

    def cross_chain_prices(self):
        """
        Get PCVR price on every chain where it exists.
        Returns {chain: price_usd}.
        """
        by_chain = self.scan_all_dexes()
        prices   = {}
        for chain, pairs in by_chain.items():
            if not pairs:
                continue
            # Use the highest-liquidity pair
            best = max(pairs,
                       key=lambda p: float(p.get("liquidity", {}).get("usd") or 0))
            raw = best.get("priceUsd") or best.get("priceNative") or "0"
            try:
                prices[chain] = float(raw)
            except (ValueError, TypeError):
                prices[chain] = 0.0
        return prices

    def price_discrepancy(self):
        """
        Find arbitrage opportunities across chains.
        If price differs > 2% → flag as opportunity.
        Returns list of dicts {chain_low, chain_high, price_low, price_high, spread_pct}.
        """
        prices = {c: p for c, p in self.cross_chain_prices().items() if p > 0}
        if len(prices) < 2:
            return []

        pairs  = []
        chains = list(prices.keys())
        for i in range(len(chains)):
            for j in range(i + 1, len(chains)):
                ca, cb = chains[i], chains[j]
                pa, pb = prices[ca], prices[cb]
                lo_chain, lo_price = (ca, pa) if pa <= pb else (cb, pb)
                hi_chain, hi_price = (ca, pa) if pa >= pb else (cb, pb)
                spread = (hi_price - lo_price) / lo_price * 100 if lo_price else 0
                if spread >= 2.0:
                    pairs.append({
                        "chain_low":   lo_chain,
                        "chain_high":  hi_chain,
                        "price_low":   lo_price,
                        "price_high":  hi_price,
                        "spread_pct":  round(spread, 2),
                    })
        pairs.sort(key=lambda x: x["spread_pct"], reverse=True)
        return pairs

    def best_price(self):
        """
        Return which chain has the best buy (lowest) and sell (highest) price.
        Returns dict {buy_chain, buy_price, sell_chain, sell_price}.
        """
        prices = {c: p for c, p in self.cross_chain_prices().items() if p > 0}
        if not prices:
            return {}
        buy_chain  = min(prices, key=prices.get)
        sell_chain = max(prices, key=prices.get)
        return {
            "buy_chain":  buy_chain,
            "buy_price":  prices[buy_chain],
            "sell_chain": sell_chain,
            "sell_price": prices[sell_chain],
        }

    # ── Recommendations ──────────────────────────────────────────────────────

    def generate_recommendations(self):
        """Return list of recommendation strings based on current data."""
        recs = []
        aggr = self.aggregate_liquidity()
        dist = self.liquidity_distribution()
        disc = self.price_discrepancy()
        div  = aggr.get("diversity_score", 0)

        if dist:
            dominant = max(dist, key=dist.get)
            pct      = dist[dominant]
            if pct > 60:
                recs.append(
                    f"Liquidity concentrated on {dominant.capitalize()} ({pct:.0f}%)"
                    " — consider bridging to diversify"
                )

        if disc:
            best = disc[0]
            recs.append(
                f"Price spread {best['spread_pct']:.1f}% between "
                f"{best['chain_low'].capitalize()} and {best['chain_high'].capitalize()}"
                " — arbitrage opportunity exists"
            )

        if div < 0.3 and len(aggr.get("chains", {})) > 1:
            recs.append("Low chain diversity — expand presence to additional chains")
        elif div > 0.6:
            recs.append("Good chain diversity — multi-chain strategy is working")

        total = aggr.get("total_liquidity_usd", 0)
        if total > 0 and total < 5000:
            recs.append(f"Total cross-chain liquidity is low (${total:,.0f}) — consider LP incentives")

        active_chains = [c for c, d in aggr.get("chains", {}).items() if d.get("volume", 0) > 0]
        for c in active_chains:
            cd = aggr["chains"][c]
            if c != "cronos" and cd.get("volume", 0) > 0:
                recs.append(
                    f"{c.capitalize()} volume growing (${cd['volume']:,.0f}) — monitor for organic adoption"
                )

        if not recs:
            recs.append("No cross-chain data available — run 'scan' to check all chains")
        return recs

    # ── Report ───────────────────────────────────────────────────────────────

    def multichain_report(self):
        """Print the full multi-chain formatted report."""
        W = 52

        def _box_top():  return "╔" + "═" * W + "╗"
        def _box_sep():  return "╠" + "═" * W + "╣"
        def _box_bot():  return "╚" + "═" * W + "╝"
        def _box_line(t=""): return "║" + t.center(W) + "║"

        print(_box_top())
        print(_box_line("🔗 V10 MULTI-CHAIN REPORT"))
        print(_box_line("PCVR Studios — One token. Every chain."))
        print(_box_sep())

        # Home chain
        print("\n🏠 HOME CHAIN: Cronos")
        home_pairs = self._get_chain_data("cronos")
        if home_pairs:
            best = max(home_pairs,
                       key=lambda p: float(p.get("liquidity", {}).get("usd") or 0))
            h_price = float(best.get("priceUsd") or 0)
            h_vol   = float(best.get("volume", {}).get("h24") or 0)
            h_liq   = float(best.get("liquidity", {}).get("usd") or 0)
            print(f"  Contract : {self.pcvr_contract[:10]}…")
            print(f"  Price    : ${h_price:.8f} | Vol: ${h_vol:,.0f} | Liq: ${h_liq:,.0f}")
        else:
            print(f"  Contract : {self.pcvr_contract[:10]}…")
            print("  No Cronos pair data available")

        # Cross-chain presence table
        print("\n🔗 CROSS-CHAIN PRESENCE")
        aggr   = self.aggregate_liquidity()
        chains = aggr.get("chains", {})
        prices = self.cross_chain_prices()

        all_active = [k for k, v in self._chain_registry.items() if v.get("active")]
        print(f"  {'Chain':<10} {'Price':>12} {'Volume':>10} {'Liquidity':>10}")
        print("  " + "─" * 46)
        for chain_key in all_active:
            name     = self._chain_registry[chain_key].get("name", chain_key)[:9]
            price    = prices.get(chain_key)
            cd       = chains.get(chain_key)
            if price is not None and price > 0:
                p_str = f"${price:.8f}"
            else:
                p_str = "—"
            vol = f"${cd['volume']:,.0f}" if cd and cd.get("volume") else "—"
            liq = f"${cd['liquidity']:,.0f}" if cd and cd.get("liquidity") else "—"
            print(f"  {name:<10} {p_str:>12} {vol:>10} {liq:>10}")

        # Aggregated totals
        print("\n📊 AGGREGATED TOTALS")
        n_chains = len(chains)
        print(f"  Total Liquidity : ${aggr['total_liquidity_usd']:,.0f}"
              f" (across {n_chains} chain{'s' if n_chains != 1 else ''})")
        print(f"  Total Volume    : ${aggr['total_volume_24h']:,.0f} (24h)")
        div   = aggr["diversity_score"]
        if div >= 0.7:
            div_label = "HIGH"
        elif div >= 0.4:
            div_label = "MODERATE"
        else:
            div_label = "LOW"
        print(f"  Chain Diversity : {div:.2f} ({div_label})")

        # Price comparison
        bp = self.best_price()
        if bp:
            print("\n💰 PRICE COMPARISON")
            print(f"  Best Buy  : {bp['buy_chain'].capitalize()} (${bp['buy_price']:.8f})")
            print(f"  Best Sell : {bp['sell_chain'].capitalize()} (${bp['sell_price']:.8f})")
            disc = self.price_discrepancy()
            if disc:
                best_disc = disc[0]
                spread = best_disc["spread_pct"]
                flag = " ⚠️ ARBITRAGE OPPORTUNITY" if spread >= 5 else ""
                print(f"  Spread    : {spread:.1f}%{flag}")
            else:
                print("  Spread    : <2% (within normal range)")

        # Liquidity distribution
        dist = self.liquidity_distribution()
        if dist:
            print("\n📈 LIQUIDITY DISTRIBUTION")
            for chain_key, pct in sorted(dist.items(), key=lambda x: x[1], reverse=True):
                name = self._chain_registry.get(chain_key, {}).get("name", chain_key)
                bar  = "█" * int(pct / 5)
                print(f"  {name:<18} {pct:>5.1f}% {bar}")

        # Bridge activity
        print("\n🌉 BRIDGE ACTIVITY")
        b_activity = self.bridge_tracker.check_bridge_activity()
        if b_activity:
            for b in b_activity[:4]:
                print(f"  [{b['bridge']}]  {b['from']} → {b['to']}  — {b['status']}")
        else:
            print("  No bridge contracts registered")

        # Recommendations
        print("\n🧠 RECOMMENDATIONS")
        for i, rec in enumerate(self.generate_recommendations(), 1):
            print(f"  {i}. {rec}")

        print()
        print(_box_bot())
        print(f"  Contract : {self.pcvr_contract}")
        print("  V10 Multi-Chain — One token. Every chain. Total visibility.")

    def summary_line(self):
        """Return a compact one-line summary string."""
        aggr     = self.aggregate_liquidity()
        n        = len(aggr.get("chains", {}))
        total    = aggr.get("total_liquidity_usd", 0)
        vol      = aggr.get("total_volume_24h", 0)
        dominant = aggr.get("dominant_chain", "cronos")
        disc     = self.price_discrepancy()
        arb      = f" | ⚠️ {disc[0]['spread_pct']:.1f}% spread" if disc else ""
        return (
            f"Multi-Chain: {n} chain(s) | "
            f"Liq ${total:,.0f} | Vol ${vol:,.0f} | "
            f"Dominant: {dominant}{arb}"
        )


# ─── Module-level helpers ─────────────────────────────────────────────────────

_tracker = None


def _get_tracker():
    global _tracker
    if _tracker is None:
        _tracker = MultiChainTracker()
    return _tracker


def scan():
    """Scan all chains — convenience wrapper."""
    return _get_tracker().scan_all_dexes()


def report():
    """Print full multi-chain report — convenience wrapper."""
    _get_tracker().multichain_report()


def liquidity():
    """Return aggregated liquidity — convenience wrapper."""
    return _get_tracker().aggregate_liquidity()


def prices():
    """Return cross-chain prices — convenience wrapper."""
    return _get_tracker().cross_chain_prices()


def arbitrage():
    """Return price discrepancies — convenience wrapper."""
    return _get_tracker().price_discrepancy()


def diversity():
    """Return chain diversity score — convenience wrapper."""
    return _get_tracker().chain_diversity_score()


def summary():
    """Return one-line multi-chain summary — convenience wrapper."""
    return _get_tracker().summary_line()


# ─── Interactive CLI ──────────────────────────────────────────────────────────

def _run_cli():
    W = 38

    def _box_top():  return "═" * W
    def _box_line(): return "─" * W

    print(_box_top())
    print("🔗 V10 MULTI-CHAIN TRACKER")
    print(_box_top())
    commands = [
        (" 1. scan",       "scan all chains for PCVR"),
        (" 2. report",     "full multi-chain report"),
        (" 3. liquidity",  "cross-chain liquidity"),
        (" 4. prices",     "price comparison"),
        (" 5. bridges",    "bridge activity"),
        (" 6. chains",     "list supported chains"),
        (" 7. add_chain",  "add custom chain"),
        (" 8. add_bridge", "register bridge contract"),
        (" 9. arbitrage",  "check arbitrage opportunities"),
        ("10. diversity",  "chain diversity score"),
        ("11. config",     "view/edit config"),
        ("12. cache",      "cache status"),
        ("13. exit",       ""),
    ]
    print("Commands:")
    for cmd, desc in commands:
        if desc:
            print(f"  {cmd:<14} → {desc}")
        else:
            print(f"  {cmd}")
    print(_box_line())

    tracker = MultiChainTracker()

    aliases = {
        "1": "scan",     "2": "report",   "3": "liquidity",
        "4": "prices",   "5": "bridges",  "6": "chains",
        "7": "add_chain","8": "add_bridge","9": "arbitrage",
        "10": "diversity","11": "config", "12": "cache",
        "13": "exit",
    }

    while True:
        try:
            raw = input("\nmultichain> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Multi-Chain Tracker shutting down.")
            break

        if not raw:
            continue

        cmd = aliases.get(raw, raw)

        if cmd == "scan":
            print("  🔍 Scanning all chains for PCVR …")
            found = tracker.scan_all_dexes()
            if found:
                for chain, pairs in found.items():
                    print(f"  ✅ {chain:<12} — {len(pairs)} pair(s) found")
            else:
                print("  No PCVR pairs found on any chain (or API unavailable)")

        elif cmd == "report":
            tracker.multichain_report()

        elif cmd == "liquidity":
            aggr = tracker.aggregate_liquidity()
            print(f"\n  Total Liquidity : ${aggr['total_liquidity_usd']:,.0f}")
            print(f"  Total Volume    : ${aggr['total_volume_24h']:,.0f} (24h)")
            print(f"  Dominant Chain  : {aggr['dominant_chain']}")
            print(f"  Diversity Score : {aggr['diversity_score']:.2f}")
            for chain, cd in aggr.get("chains", {}).items():
                print(f"  {chain:<12} liq=${cd['liquidity']:,.0f}  vol=${cd['volume']:,.0f}  pairs={cd['pairs']}")

        elif cmd == "prices":
            p = tracker.cross_chain_prices()
            if p:
                print("\n  Chain Prices:")
                for chain, price in sorted(p.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {chain:<12} ${price:.8f}")
            else:
                print("  No price data available")
            bp = tracker.best_price()
            if bp:
                print(f"\n  Best Buy  : {bp['buy_chain']} (${bp['buy_price']:.8f})")
                print(f"  Best Sell : {bp['sell_chain']} (${bp['sell_price']:.8f})")

        elif cmd == "bridges":
            activity = tracker.bridge_tracker.check_bridge_activity()
            print("\n  Bridge Activity:")
            for b in activity:
                print(f"  {b['bridge']:<25} {b['from']} → {b['to']}")

        elif cmd == "chains":
            print("\n  Supported Chains:")
            for key, cfg in tracker._chain_registry.items():
                status = "✅" if cfg.get("active") else "⛔"
                print(f"  {status} {key:<12} {cfg.get('name',''):<22} (chain_id={cfg.get('chain_id',0)})")

        elif cmd == "add_chain":
            try:
                name    = input("  Chain name: ").strip()
                cid     = int(input("  Chain ID: ").strip())
                symbol  = input("  Native symbol: ").strip() or "ETH"
                dex_id  = input("  DexScreener chain ID: ").strip() or name.lower()
                key = tracker.add_chain(cid, name, symbol=symbol, dex_screener_id=dex_id)
                print(f"  ✅ Chain '{name}' added as '{key}'")
                tracker.save_config()
            except (ValueError, EOFError):
                print("  ❌ Invalid input — cancelled")

        elif cmd == "add_bridge":
            try:
                chain    = input("  Chain key (e.g. bsc): ").strip().lower()
                contract = input("  Contract address: ").strip()
                tracker.add_bridge_contract(chain, contract)
                print(f"  ✅ Bridge contract registered for {chain}")
                tracker.save_config()
            except EOFError:
                print("  ❌ Cancelled")

        elif cmd == "arbitrage":
            disc = tracker.price_discrepancy()
            if disc:
                print("\n  ⚠️  Arbitrage Opportunities:")
                for d in disc:
                    print(f"  {d['chain_low']:<10} (${d['price_low']:.8f}) → "
                          f"{d['chain_high']:<10} (${d['price_high']:.8f}) "
                          f"spread {d['spread_pct']:.1f}%")
            else:
                print("  No arbitrage opportunities found (spread < 2%)")

        elif cmd == "diversity":
            score = tracker.chain_diversity_score()
            if score >= 0.7:
                label = "HIGH"
            elif score >= 0.4:
                label = "MODERATE"
            else:
                label = "LOW"
            print(f"\n  Chain Diversity Score: {score:.4f} ({label})")
            dist = tracker.liquidity_distribution()
            if dist:
                print("  Liquidity distribution:")
                for chain_key, pct in sorted(dist.items(), key=lambda x: x[1], reverse=True):
                    print(f"    {chain_key:<12} {pct:.1f}%")

        elif cmd == "config":
            print(f"\n  Config file: {MULTICHAIN_CONFIG}")
            print(f"  Registered chains : {len(tracker._chain_registry)}")
            print(f"  Bridge contracts  : {len(tracker.bridge_contracts)}")
            print(f"  Bridges registered: {len(tracker.bridge_tracker.bridges)}")
            save = input("  Save current config? [y/N]: ").strip().lower()
            if save == "y":
                ok = tracker.save_config()
                print("  ✅ Config saved" if ok else "  ❌ Could not save config")

        elif cmd == "cache":
            cs = tracker.cache_status()
            print(f"\n  Cache status:")
            for chain_key, info in cs.get("chains", {}).items():
                fresh = "fresh" if info["fresh"] else "stale"
                print(f"  {chain_key:<12} {info['pairs']} pair(s)  age={info['age_seconds']}s  [{fresh}]")
            if not cs.get("chains"):
                print("  Cache is empty — run 'scan' first")
            aggr_age = cs.get("aggregated_age_seconds")
            if aggr_age is not None:
                fresh = "fresh" if cs.get("aggregated_fresh") else "stale"
                print(f"  Aggregated        age={aggr_age}s  [{fresh}]")

        elif cmd in ("exit", "quit", "q"):
            print("👋 Multi-Chain Tracker shutting down.")
            break

        elif cmd == "help":
            print("Commands: scan report liquidity prices bridges chains "
                  "add_chain add_bridge arbitrage diversity config cache exit")

        else:
            print(f"  ❓ Unknown command: '{raw}'.  Type 'help' for the list.")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  PCVR Studios — Multi-Chain Tracker v1.0")
    print("  V10 Multi-Chain — One token. Every chain. Total visibility.")
    print("  © PCVR Studios 2026")
    print(f"  Contract: {PCVR_CONTRACT}\n")
    _run_cli()
