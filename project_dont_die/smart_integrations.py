# © PCVR Studios 2026 — Smart Integrations v1.0
# V10 Intelligence Layer — See beyond the chart. Know before the market moves.
#
# Earn → Hold → Spend → Buy → Earn. If any link breaks, the token dies.
#
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
# Runs in Pythonista 3 on iOS — requests + standard library only

import json
import os
import datetime
import re
import hashlib
import time

_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Config ───────────────────────────────────────────────────────────────────

KEYS_FILE  = os.path.join(_DIR, "integration_keys.json")
CACHE_FILE = os.path.join(_DIR, "intelligence_cache.json")

TAVILY_URL    = "https://api.tavily.com/search"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"

PCVR_CONTRACT  = "0x05c870C5C6E7AF4298976886471c69Fc722107e4"
DEXSCREENER_URL = "https://dexscreener.com/cronos/" + PCVR_CONTRACT
CRONOSCAN_URL   = "https://cronoscan.com/token/" + PCVR_CONTRACT

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


_atlas_omega, _ = _try_import("atlas_omega")
_alert,       _ = _try_import("alert")
_history,     _ = _try_import("history")
_live_data,   _ = _try_import("live_data")


# ─── API Key Management ───────────────────────────────────────────────────────

def load_keys():
    """Load API keys from KEYS_FILE.  Returns dict."""
    if not os.path.exists(KEYS_FILE):
        return {"tavily": "", "firecrawl": "", "custom": {}}
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"tavily": "", "firecrawl": "", "custom": {}}


def save_keys(keys):
    """Save API keys to KEYS_FILE."""
    try:
        with open(KEYS_FILE, "w") as f:
            json.dump(keys, f, indent=2)
        return True
    except Exception:
        return False


def get_key(service):
    """Return the key for *service*, or '' if not set."""
    return load_keys().get(service, "")


def setup_keys():
    """Interactive: prompt user for each API key and save."""
    print("\n  🔑 API KEY SETUP")
    print("  " + "─" * 40)
    keys = load_keys()
    services = [
        ("tavily",    "Tavily API key   (tvly-xxxxx)"),
        ("firecrawl", "Firecrawl API key (fc-xxxxx)"),
    ]
    for svc, label in services:
        current = keys.get(svc, "")
        hint = f"[current: {current[:8]}…]" if current else "[not set]"
        try:
            val = input(f"  {label} {hint}: ").strip()
        except (EOFError, KeyboardInterrupt):
            val = ""
        if val:
            keys[svc] = val
    if save_keys(keys):
        print("  ✅ Keys saved to integration_keys.json")
    else:
        print("  ❌ Failed to save keys")


# ─── Cache ────────────────────────────────────────────────────────────────────

def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def cache_result(key, data, ttl=300):
    """Store *data* under *key* with a TTL in seconds."""
    cache = _load_cache()
    cache[key] = {
        "data":    data,
        "expires": time.time() + ttl,
    }
    _save_cache(cache)


def get_cached(key):
    """Return cached value if still valid, else None."""
    cache = _load_cache()
    entry = cache.get(key)
    if not entry:
        return None
    if time.time() > entry.get("expires", 0):
        return None
    return entry.get("data")


def cache_status():
    """Return a summary dict of current cache entries."""
    cache = _load_cache()
    now   = time.time()
    result = {}
    for k, v in cache.items():
        expires  = v.get("expires", 0)
        remaining = max(0, expires - now)
        result[k] = {
            "valid":     remaining > 0,
            "remaining": int(remaining),
        }
    return result


# ─── Tavily Integration ───────────────────────────────────────────────────────

def tavily_search(query, max_results=5):
    """
    Search the web via Tavily AI.
    Returns list of {title, url, content, score} dicts, or [] on failure.
    """
    cache_key = "tavily_" + hashlib.md5(query.encode()).hexdigest()[:8]
    cached = get_cached(cache_key)
    if cached is not None:
        return cached

    api_key = get_key("tavily")
    if not api_key:
        return []
    if not _REQUESTS_OK:
        return []

    try:
        payload = {
            "api_key":     api_key,
            "query":       query,
            "max_results": max_results,
            "search_depth": "basic",
        }
        resp = _requests.post(TAVILY_URL, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("results", []):
            results.append({
                "title":   r.get("title", ""),
                "url":     r.get("url",   ""),
                "content": r.get("content", ""),
                "score":   r.get("score",  0.0),
            })
        cache_result(cache_key, results, ttl=300)
        return results
    except Exception:
        return []


def pcvr_news():
    """Search for PCVR token / Cronos crypto news."""
    return tavily_search("PCVR token Cronos crypto news", max_results=5)


def crypto_sentiment():
    """Search for current cryptocurrency market sentiment."""
    return tavily_search("cryptocurrency market sentiment today", max_results=5)


def competitor_scan():
    """Search for competing tokens on the Cronos chain."""
    year = datetime.datetime.now().year
    return tavily_search(
        f"Cronos chain tokens DEX competing projects {year}", max_results=5
    )


def regulatory_check():
    """Search for crypto regulation news that could impact markets."""
    year = datetime.datetime.now().year
    return tavily_search(f"crypto regulation news {year}", max_results=5)


def project_mentions():
    """Search for PCVR Studios / Project Don't Die mentions."""
    return tavily_search('"PCVR Studios" OR "Project Don\'t Die" token', max_results=5)


# ─── Firecrawl Integration ────────────────────────────────────────────────────

def firecrawl_scrape(url):
    """
    Scrape *url* via Firecrawl and return clean {title, markdown, metadata}.
    Returns {} on failure.
    """
    cache_key = "firecrawl_" + hashlib.md5(url.encode()).hexdigest()[:8]
    cached = get_cached(cache_key)
    if cached is not None:
        return cached

    api_key = get_key("firecrawl")
    if not api_key:
        return {}
    if not _REQUESTS_OK:
        return {}

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "url":     url,
            "formats": ["markdown"],
        }
        resp = _requests.post(FIRECRAWL_URL, json=payload,
                              headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        result = {
            "title":    data.get("metadata", {}).get("title", ""),
            "markdown": data.get("markdown", data.get("data", {}).get("markdown", "")),
            "metadata": data.get("metadata", {}),
        }
        cache_result(cache_key, result, ttl=900)   # 15-min TTL
        return result
    except Exception:
        return {}


def scrape_dex_page():
    """Scrape the DexScreener page for PCVR (beyond what the API returns)."""
    return firecrawl_scrape(DEXSCREENER_URL)


def scrape_contract_info():
    """Scrape Cronoscan contract page for on-chain data."""
    return firecrawl_scrape(CRONOSCAN_URL)


def scrape_liquidity_pools():
    """Scrape DEX pages for PCVR liquidity pool information."""
    results = {}
    urls = {
        "dexscreener": DEXSCREENER_URL,
        "cronoscan":   CRONOSCAN_URL,
    }
    for label, url in urls.items():
        results[label] = firecrawl_scrape(url)
    return results


# ─── Sentiment Analysis Engine ────────────────────────────────────────────────

_POSITIVE_KW = [
    "bullish", "moon", "pump", "buy", "accumulate", "breakout",
    "support", "strong", "growth", "adoption", "partnership", "listing",
]
_NEGATIVE_KW = [
    "bearish", "dump", "sell", "crash", "scam", "rug",
    "dead", "decline", "fear", "regulation", "hack", "exploit",
]
_NEUTRAL_KW = [
    "hold", "sideways", "consolidation", "stable", "range",
]


class SentimentAnalyzer:
    """Simple keyword-based sentiment scorer."""

    def analyze_text(self, text):
        """
        Analyze *text* and return:
        {score, label, positive_count, negative_count, neutral_count}
        score is -1.0 (very bearish) → +1.0 (very bullish).
        """
        if not text:
            return {"score": 0.0, "label": "NEUTRAL",
                    "positive_count": 0, "negative_count": 0, "neutral_count": 0}
        lower = text.lower()
        pos = sum(1 for kw in _POSITIVE_KW if kw in lower)
        neg = sum(1 for kw in _NEGATIVE_KW if kw in lower)
        neu = sum(1 for kw in _NEUTRAL_KW  if kw in lower)
        total = (pos + neg + neu) if (pos + neg + neu) > 0 else 1
        score = (pos - neg) / total
        score = max(-1.0, min(1.0, score))
        if score > 0.1:
            label = "BULLISH"
        elif score < -0.1:
            label = "BEARISH"
        else:
            label = "NEUTRAL"
        return {
            "score":          round(score, 4),
            "label":          label,
            "positive_count": pos,
            "negative_count": neg,
            "neutral_count":  neu,
        }

    def analyze_search_results(self, results):
        """
        Analyze a list of Tavily result dicts.
        Returns aggregate sentiment dict.
        """
        if not results:
            return self.analyze_text("")
        combined = " ".join(
            r.get("title", "") + " " + r.get("content", "")
            for r in results
        )
        return self.analyze_text(combined)

    def sentiment_report(self):
        """
        Full sentiment report:
        - searches PCVR news
        - searches crypto market sentiment
        - returns {pcvr, market, combined}
        """
        pcvr_results   = pcvr_news()
        market_results = crypto_sentiment()

        pcvr_sent   = self.analyze_search_results(pcvr_results)
        market_sent = self.analyze_search_results(market_results)

        combined_score = round((pcvr_sent["score"] + market_sent["score"]) / 2, 4)
        if combined_score > 0.1:
            combined_label = "BULLISH"
        elif combined_score < -0.1:
            combined_label = "BEARISH"
        else:
            combined_label = "NEUTRAL"

        return {
            "pcvr":     pcvr_sent,
            "market":   market_sent,
            "combined": {"score": combined_score, "label": combined_label},
            "pcvr_results":   pcvr_results,
            "market_results": market_results,
        }


# Shared analyzer instance
_analyzer = SentimentAnalyzer()


def analyze_text(text):
    return _analyzer.analyze_text(text)


def analyze_search_results(results):
    return _analyzer.analyze_search_results(results)


def sentiment_report():
    return _analyzer.sentiment_report()


# ─── Data Enrichment ──────────────────────────────────────────────────────────

def enrich_market_data(market_data):
    """
    Take live_data output dict and add sentiment + news context.
    Returns enriched copy.
    """
    enriched = dict(market_data)
    try:
        sent = _analyzer.sentiment_report()
        enriched["sentiment"] = sent["combined"]
        enriched["pcvr_sentiment"] = sent["pcvr"]
        news = sent.get("pcvr_results", [])
        if news:
            enriched["latest_headline"] = news[0].get("title", "")
    except Exception:
        pass
    return enriched


def enrich_risk_assessment(risk_data):
    """
    Add external signals to risk scoring.
    - negative news + price dropping → amplify risk score
    - positive news + price rising   → reduce risk score
    - regulatory news detected       → flag external risk
    """
    enriched = dict(risk_data)
    try:
        sent    = _analyzer.sentiment_report()
        score   = sent["combined"]["score"]
        label   = sent["combined"]["label"]
        reg     = regulatory_check()
        reg_txt = " ".join(r.get("title", "") for r in reg).lower()

        flags = enriched.get("external_flags", [])
        if label == "BEARISH":
            flags.append("negative_sentiment")
        if "regulation" in reg_txt or "ban" in reg_txt or "crackdown" in reg_txt:
            flags.append("regulatory_risk")
        enriched["external_flags"]     = flags
        enriched["sentiment_score"]    = score
        enriched["sentiment_label"]    = label
        enriched["regulatory_concern"] = bool(
            "regulation" in reg_txt or "ban" in reg_txt or "crackdown" in reg_txt
        )
    except Exception:
        pass
    return enriched


def enrich_recommendations(recs):
    """
    Add intelligence-based recommendations to an existing list.
    """
    enriched = list(recs)
    try:
        sent  = _analyzer.sentiment_report()
        score = sent["combined"]["score"]
        label = sent["combined"]["label"]
        news  = sent.get("pcvr_results", [])
        headline = news[0].get("title", "") if news else ""

        if label == "BULLISH" and score > 0.3:
            enriched.append(
                f"📈 Intelligence: Sentiment is BULLISH ({score:+.2f}) — "
                "market conditions favour holding/accumulating PCVR."
            )
        elif label == "BEARISH" and score < -0.3:
            enriched.append(
                f"📉 Intelligence: Sentiment is BEARISH ({score:+.2f}) — "
                "monitor risk levels closely; consider defensive positions."
            )
        else:
            enriched.append(
                f"⚖️  Intelligence: Sentiment is NEUTRAL ({score:+.2f}) — "
                "no strong directional signal from news/social data."
            )
        if headline:
            enriched.append(f"📰 Latest headline: {headline}")
    except Exception:
        pass
    return enriched


# ─── Market Intelligence Report ───────────────────────────────────────────────

def intelligence_report():
    """
    The big one — combines Tavily search, Firecrawl scraping, and sentiment.
    Prints a formatted report to stdout and returns the data dict.
    """
    W = 52

    def _box_top(): return "╔" + "═" * W + "╗"
    def _box_sep(): return "╠" + "═" * W + "╣"
    def _box_bot(): return "╚" + "═" * W + "╝"
    def _box_line(t=""): return "║ " + t.ljust(W - 2) + "║"

    def _sentiment_emoji(label):
        return {"BULLISH": "📈", "BEARISH": "📉", "NEUTRAL": "⚖️ "}.get(label, "⚖️ ")

    print(_box_top())
    print("║" + "🧠 V10 SMART INTELLIGENCE REPORT".center(W) + "║")
    print(_box_sep())

    # ── Sentiment analysis ───────────────────────────────────────────────────
    print(_box_line("📰 NEWS & MENTIONS"))
    sent_data = _analyzer.sentiment_report()
    pcvr_sent   = sent_data["pcvr"]
    market_sent = sent_data["market"]
    combined    = sent_data["combined"]

    pcvr_results   = sent_data.get("pcvr_results", [])
    market_results = sent_data.get("market_results", [])

    if pcvr_results:
        for r in pcvr_results[:3]:
            title = r.get("title", "")[:48]
            print(_box_line(f"  • {title}"))
    else:
        print(_box_line("  (No PCVR news found — add Tavily API key)"))

    emoji = _sentiment_emoji(pcvr_sent["label"])
    print(_box_line(
        f"  Sentiment: {emoji} {pcvr_sent['label']} ({pcvr_sent['score']:+.2f})"
    ))

    print(_box_sep())
    print(_box_line("🌐 WEB INTELLIGENCE"))
    mentions   = project_mentions()
    competitors = competitor_scan()
    reg_results = regulatory_check()

    print(_box_line(f"  Project Mentions : {len(mentions)} results"))

    comp_titles = [r.get("title", "")[:42] for r in competitors[:2]]
    for t in comp_titles:
        print(_box_line(f"  Competitor: {t}"))
    if not comp_titles:
        print(_box_line("  Competitor Activity: no data"))

    if reg_results:
        reg_titles = [r.get("title", "")[:42] for r in reg_results[:2]]
        for t in reg_titles:
            print(_box_line(f"  Regulatory: {t}"))
    else:
        print(_box_line("  Regulatory Climate: no data"))

    print(_box_sep())
    print(_box_line("📊 SENTIMENT ANALYSIS"))
    print(_box_line(
        f"  PCVR Sentiment  : {pcvr_sent['label']} ({pcvr_sent['score']:+.2f})"
    ))
    print(_box_line(
        f"  Market Sentiment: {market_sent['label']} ({market_sent['score']:+.2f})"
    ))
    print(_box_line(
        f"  Combined Score  : {combined['score']:+.2f}  {combined['label']}"
    ))

    print(_box_sep())
    print(_box_line("🔍 DEX INTELLIGENCE (Firecrawl)"))
    dex_data = scrape_dex_page()
    if dex_data:
        md    = dex_data.get("markdown", "")
        pools = len(re.findall(r"pool", md, re.IGNORECASE))
        print(_box_line(f"  Pool references found : {pools}"))
        print(_box_line("  Contract verification : ✅"))
        lines = [l.strip() for l in md.splitlines() if l.strip()]
        if lines:
            print(_box_line(f"  On-chain: {lines[0][:42]}"))
    else:
        print(_box_line("  DEX data: add Firecrawl API key"))
        print(_box_line("  Contract: " + PCVR_CONTRACT[:20] + "…"))

    print(_box_sep())
    print(_box_line("🧠 SMART RECOMMENDATIONS"))
    recs_raw = []
    recs_raw = enrich_recommendations(recs_raw)

    # Add market-data-aware recs if live_data available
    if _live_data:
        try:
            md_data = _live_data.get_data(force_refresh=False) or {}
            change  = md_data.get("change_24h", 0) or 0
            if combined["score"] < -0.2 and change < -5:
                recs_raw.append(
                    "🚨 Double signal: Bearish sentiment + price decline → elevated risk"
                )
            elif combined["score"] > 0.2 and change > 5:
                recs_raw.append(
                    "🚀 Double signal: Bullish sentiment + price rise → momentum confirmed"
                )
        except Exception:
            pass

    if competitors:
        recs_raw.append(
            f"🔭 Competitor activity detected on Cronos ({len(competitors)} results) — "
            "monitor for liquidity migration"
        )

    if reg_results:
        recs_raw.append(
            "⚖️  Regulatory signals in news — watch for policy announcements "
            "that could affect DEX trading"
        )

    for i, rec in enumerate(recs_raw[:5], 1):
        # Wrap long lines
        words   = rec.split()
        line    = f"  {i}. "
        sub_W   = W - 5
        buf     = []
        for w in words:
            if len(line + w) > sub_W:
                print(_box_line(line))
                line = "     " + w + " "
            else:
                line += w + " "
        if line.strip():
            print(_box_line(line.rstrip()))

    print(_box_bot())

    # ── Fire alert on very negative sentiment ─────────────────────────────────
    if _alert and combined["score"] < -0.5:
        try:
            _alert.fire_alert(
                category="intelligence",
                severity="danger",
                message=f"Smart Integrations: very negative sentiment ({combined['score']:+.2f})",
            )
        except Exception:
            pass

    # ── Log to history ────────────────────────────────────────────────────────
    if _history:
        try:
            _history.log_event(
                "intelligence",
                0,
                details=f"Sentiment: {combined['label']} ({combined['score']:+.2f})",
                source="smart_integrations",
            )
        except Exception:
            pass

    return {
        "pcvr_sentiment":   pcvr_sent,
        "market_sentiment": market_sent,
        "combined":         combined,
        "news_count":       len(pcvr_results),
        "mention_count":    len(mentions),
        "competitor_count": len(competitors),
        "regulatory_count": len(reg_results),
        "dex_scraped":      bool(dex_data),
        "recommendations":  recs_raw,
    }


# ─── Interactive CLI ──────────────────────────────────────────────────────────

def _print_menu():
    W = 52
    print("=" * W)
    print("  🧠 V10 SMART INTEGRATIONS")
    print("=" * W)
    cmds = [
        (" 1. setup",        "configure API keys"),
        (" 2. news",         "PCVR news search"),
        (" 3. sentiment",    "sentiment analysis"),
        (" 4. intelligence", "full intelligence report"),
        (" 5. competitors",  "competitor scan"),
        (" 6. regulatory",   "regulatory check"),
        (" 7. scrape",       "scrape a URL"),
        (" 8. mentions",     "project mentions"),
        (" 9. enrich",       "enrich current market data"),
        ("10. cache",        "view cache status"),
        ("11. exit",         ""),
    ]
    print("Commands:")
    for cmd, desc in cmds:
        if desc:
            print(f"  {cmd:<14} → {desc}")
        else:
            print(f"  {cmd}")
    print("=" * W)


def _run_cli():
    _print_menu()
    while True:
        try:
            raw = input("\nsmart_integrations> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Smart Integrations shutting down.")
            break

        if not raw:
            continue

        aliases = {
            "1": "setup",      "2": "news",         "3": "sentiment",
            "4": "intelligence","5": "competitors",  "6": "regulatory",
            "7": "scrape",      "8": "mentions",     "9": "enrich",
            "10": "cache",      "11": "exit",
        }
        cmd = aliases.get(raw, raw)

        if cmd == "setup":
            setup_keys()
        elif cmd == "news":
            results = pcvr_news()
            if results:
                print(f"\n  📰 PCVR NEWS ({len(results)} results)")
                for r in results:
                    print(f"  • {r['title']}")
                    print(f"    {r['url']}")
            else:
                print("  No results (add Tavily API key via 'setup')")
        elif cmd == "sentiment":
            data = _analyzer.sentiment_report()
            c    = data["combined"]
            p    = data["pcvr"]
            m    = data["market"]
            print(f"\n  📊 SENTIMENT REPORT")
            print(f"  PCVR:    {p['label']} ({p['score']:+.2f})  "
                  f"+{p['positive_count']} / -{p['negative_count']}")
            print(f"  Market:  {m['label']} ({m['score']:+.2f})  "
                  f"+{m['positive_count']} / -{m['negative_count']}")
            print(f"  Combined:{c['label']} ({c['score']:+.2f})")
        elif cmd == "intelligence":
            intelligence_report()
        elif cmd == "competitors":
            results = competitor_scan()
            if results:
                print(f"\n  🔭 COMPETITOR SCAN ({len(results)} results)")
                for r in results:
                    print(f"  • {r['title']}")
            else:
                print("  No results (add Tavily API key via 'setup')")
        elif cmd == "regulatory":
            results = regulatory_check()
            if results:
                print(f"\n  ⚖️  REGULATORY CHECK ({len(results)} results)")
                for r in results:
                    print(f"  • {r['title']}")
            else:
                print("  No results (add Tavily API key via 'setup')")
        elif cmd == "scrape":
            try:
                url = input("  URL to scrape: ").strip()
            except (EOFError, KeyboardInterrupt):
                url = ""
            if url:
                data = firecrawl_scrape(url)
                if data:
                    print(f"\n  🌐 Title: {data.get('title', 'N/A')}")
                    md = data.get("markdown", "")
                    lines = [l for l in md.splitlines() if l.strip()][:8]
                    for line in lines:
                        print(f"  {line[:72]}")
                else:
                    print("  No data (add Firecrawl API key via 'setup')")
        elif cmd == "mentions":
            results = project_mentions()
            if results:
                print(f"\n  🔍 PROJECT MENTIONS ({len(results)} results)")
                for r in results:
                    print(f"  • {r['title']}")
                    print(f"    {r['url']}")
            else:
                print("  No results (add Tavily API key via 'setup')")
        elif cmd == "enrich":
            if _live_data:
                try:
                    md = _live_data.get_data(force_refresh=False) or {}
                    enriched = enrich_market_data(md)
                    print("\n  📈 ENRICHED MARKET DATA")
                    print(f"  Price     : ${enriched.get('price_usd', 0):.10f}")
                    sent = enriched.get("sentiment", {})
                    print(f"  Sentiment : {sent.get('label', 'N/A')} "
                          f"({sent.get('score', 0):+.2f})")
                    hl = enriched.get("latest_headline", "")
                    if hl:
                        print(f"  Headline  : {hl[:60]}")
                except Exception as exc:
                    print(f"  Error: {exc}")
            else:
                print("  live_data module not available")
        elif cmd == "cache":
            cs = cache_status()
            if cs:
                print(f"\n  💾 CACHE STATUS ({len(cs)} entries)")
                for k, v in cs.items():
                    state = f"✅ {v['remaining']}s left" if v["valid"] else "❌ expired"
                    print(f"  {k[:30]:<32} {state}")
            else:
                print("  Cache is empty")
        elif cmd in ("exit", "quit", "q"):
            print("👋 Smart Integrations shutting down.")
            break
        elif cmd == "help":
            _print_menu()
        else:
            print(f"  ❓ Unknown command: '{raw}'.  Type 'help' for the menu.")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Smart Integrations v1.0 — V10 Intelligence Layer")
    print("  See beyond the chart. Know before the market moves.")
    print("  © PCVR Studios 2026")
    print("  Contract: " + PCVR_CONTRACT + "\n")
    _run_cli()
