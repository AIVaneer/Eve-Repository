# 🎮 PCVR Studios — Project Don't Die Toolkit

> The most advanced token survival toolkit ever built. 20+ Python modules monitoring, analyzing, and protecting PCVR on Cronos and beyond.

**Contract:** `0x05c870C5C6E7AF4298976886471c69Fc722107e4` (Cronos)  
**Philosophy:** Earn → Hold → Spend → Buy → Earn

[![Modules](https://img.shields.io/badge/Modules-20%2B-blue)]()
[![Chains](https://img.shields.io/badge/Chains-8-green)]()
[![Platform](https://img.shields.io/badge/Platform-Pythonista%203%20%7C%20Desktop-orange)]()

---

## 📋 Table of Contents

- [What is this?](#-what-is-this)
- [Quick Start](#-quick-start)
- [Module Overview](#-module-overview)
- [Architecture](#-architecture)
- [V10 Features](#-v10-features)
- [Setup Guide — Desktop](#-setup-guide--desktop)
- [Setup Guide — Pythonista 3 / iOS](#-setup-guide--pythonista-3--ios)
- [API Reference — Dashboard Endpoints](#-api-reference--dashboard-endpoints)
- [Dashboard](#-dashboard)
- [Automation](#-automation)
- [Multi-Chain](#-multi-chain)
- [Configuration Files](#-configuration-files)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [Games Library](#-games-library)
- [License](#-license)

---

## 🧠 What is this?

**PCVR** is a token on the Cronos blockchain. **Project Don't Die** is the philosophy — and the toolkit — built to keep it alive.

The toolkit is a comprehensive Python-based system for monitoring, analyzing, and automating every aspect of the PCVR token ecosystem. It runs on both desktop Python and **Pythonista 3 on iOS**, making it portable and always accessible.

### The "Don't Die" Philosophy

Every token has a lifecycle. Most die from neglect, manipulation, or economic collapse. Project Don't Die exists to prevent exactly that. The toolkit watches the chain 24/7, spots danger before it becomes a crisis, and automates the responses that humans would be too slow — or too distracted — to execute.

```
Earn → Hold → Spend → Buy → Earn
```

If any link in that chain breaks, the token dies. The toolkit exists to ensure it never does.

### What it does

- **Monitors** price, liquidity, volume, and wallet concentration in real time
- **Analyzes** tokenomics, risk, sentiment, and on-chain patterns
- **Simulates** economic scenarios from death spiral to utopia
- **Automates** alerts, responses, and governance actions
- **Tracks** PCVR across 8 blockchain networks and bridge routes
- **Visualizes** everything in a dark-theme web dashboard
- **Runs natively** on iOS via Pythonista 3 and a WKWebView dashboard

---

## 🚀 Quick Start

### Desktop

```bash
cd project_dont_die
python run_all.py          # Full system check
python atlas_omega.py      # Command center (19 commands)
python dashboard.py        # Web dashboard at localhost:8080
python automation.py       # Start automation engine
```

### Pythonista 3 (iOS)

```python
import run_all             # Full system check
import atlas_omega         # Command center
import wkapp_ui            # Native iOS interface
```

---

## 📦 Module Overview

| Module | Version | Description | Key Features |
|--------|---------|-------------|--------------|
| `atlas_omega.py` | V9 | Unified Command Center | 19 commands, omega report, quick status |
| `live_data.py` | V1 | Market Data | DexScreener, Binance APIs |
| `economy.py` | V2 | Tokenomics Engine | Supply, emission, burn, health ratio |
| `vault.py` | V3 | Staking Vault | Lock, unlock, APY, rewards |
| `alert.py` | V4 | Risk Engine | Risk scoring, pattern alerts, multi-level |
| `whale_tracker.py` | V5 | Whale Analysis | Gini coefficient, concentration tracking |
| `scenario.py` | V6 | Simulation Engine | 7 scenarios: death spiral to utopia |
| `detector.py` | V6 | Pattern Detection | HEAVY DUMP, accumulation, distribution |
| `store.py` | V7 | In-Game Store | Items, purchases, revenue |
| `ledger.py` | V7 | Transaction Ledger | Full audit trail |
| `history.py` | V7 | Event History | Timestamped event log |
| `github_sync.py` | V8 | GitHub Integration | Push/pull code, auto-sync |
| `validate.py` | V8 | System Health | Module validation, integrity checks |
| `token_data.py` | V7 | Token Constants | Supply, contract, chain metadata |
| `atlas_graph_core.py` | V9 | Graph Engine | Economy graph, analysis, visualization |
| `smart_integrations.py` | V10 | AI Intelligence | Tavily search, Firecrawl, sentiment |
| `dashboard.py` | V10 | Web Dashboard | Chart.js, dark theme, 7 API endpoints |
| `automation.py` | V10 | Automation Engine | 10 rules, background thread, dry-run |
| `wkapp_ui.py` | V10 | iOS Native UI | WKWebView, native toolbar, Pythonista |
| `multichain.py` | V10 | Multi-Chain Tracker | 8 chains, bridges, arbitrage detection |
| `run_all.py` | — | System Runner | Runs all modules, full status report |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ATLAS OMEGA (V9)                          │
│               Unified Command Center                         │
│          19 commands │ omega_report │ quick_status           │
├────────┬────────┬────────┬────────┬────────┬────────────────┤
│ Market │ Economy│ Risk   │ Whale  │ Scenario│ Intelligence  │
│ V1     │ V2-V3  │ V4     │ V5     │ V6     │ V10           │
├────────┴────────┴────────┴────────┴────────┴────────────────┤
│ Store V7 │ Ledger V7 │ History V7 │ Sync V8 │ Validate V8  │
├─────────────────────────────────────────────────────────────┤
│ Dashboard V10 │ Automation V10 │ iOS UI V10 │ MultiChain V10│
└─────────────────────────────────────────────────────────────┘
```

All modules follow the same pattern:
- **Graceful imports** — every module loads with `try/except`; failures are logged, not fatal
- **Standard library preferred** — only `requests` is an external dependency
- **Pythonista compatible** — every module runs on iOS Pythonista 3
- **Self-contained** — each module can be imported and used independently

---

## ⚡ V10 Features

### 🔍 Smart Integrations (`smart_integrations.py`)

The intelligence layer. Connects the toolkit to the real world.

- **Tavily Search** — AI-powered web search for PCVR news, sentiment, and market context
- **Firecrawl** — Structured web scraping of DexScreener, CronosScan, and competitor pages
- **Built-in sentiment analysis** — keyword-based NLP scoring without external ML libraries
- **Data enrichment** — augments on-chain data with off-chain intelligence
- **Caching** — all results cached with configurable TTL to avoid rate limits

### 📊 Dashboard (`dashboard.py` + `dashboard_template.html`)

A full dark-theme web dashboard with real-time data visualization.

- **Chart.js charts** — price history, volume, liquidity, and risk gauge
- **7 JSON API endpoints** — structured data for every subsystem
- **Auto-refresh** — configurable polling interval
- **Dark theme** — professional dark UI optimized for monitoring
- **Run locally** — `python dashboard.py` → open `http://localhost:8080`

### 🤖 Automation (`automation.py`)

A rule-based automation engine with a background thread.

- **10 pre-built rules** — covering dump detection, liquidity drops, whale moves, and more
- **Background thread** — runs continuously, evaluating rules on every tick
- **Cooldowns** — per-rule cooldowns prevent alert spam
- **Dry-run mode** — test automation logic without triggering real actions
- **Safety caps** — maximum actions per hour to prevent runaway automation
- **Action history** — full log of every triggered rule and action taken

### 📱 iOS UI (`wkapp_ui.py`)

Native iOS interface for Pythonista 3.

- **WKWebView wrapper** — renders the dashboard inside a native iOS web view
- **Native toolbar** — iOS-native navigation and action buttons
- **Pythonista detection** — graceful fallback to CLI mode on desktop
- **Quick panel** — native iOS panel for key metrics without opening the dashboard

### 🌐 Multi-Chain (`multichain.py`)

Tracks PCVR liquidity and price across 8 blockchain networks.

- **8 chains** — Cronos, Ethereum, BSC, Polygon, Arbitrum, Optimism, Avalanche, Base
- **DexScreener multi-chain scan** — real-time prices and liquidity per chain
- **Liquidity aggregation** — total liquidity across all chains in one view
- **Bridge tracker** — monitors assets moving between chains
- **Arbitrage detection** — flags price discrepancies across chains

---

## 💻 Setup Guide — Desktop

### Requirements

- Python 3.7+
- `requests` library (the only external dependency)

### Install

```bash
git clone https://github.com/AIVaneer/Eve-Repository.git
cd Eve-Repository/project_dont_die
pip install requests
python run_all.py
```

### API Keys (optional — for Smart Integrations)

Create `project_dont_die/integration_keys.json`:

```json
{
  "tavily": "tvly-YOUR_KEY_HERE",
  "firecrawl": "fc-YOUR_KEY_HERE"
}
```

- **Tavily API** — [app.tavily.com](https://app.tavily.com) — AI web search
- **Firecrawl API** — [firecrawl.dev](https://firecrawl.dev) — structured web scraping

Keys file is gitignored and never committed.

### Run the Dashboard

```bash
python dashboard.py
# Open http://localhost:8080 in your browser
```

### Run the Automation Engine

```bash
python automation.py
# Select "Start background engine" from the menu
```

---

## 📱 Setup Guide — Pythonista 3 / iOS

### Install Pythonista 3

[Pythonista 3](https://omz-software.com/pythonista/) is available on the iOS App Store. It provides a full Python 3 environment on iPhone and iPad.

For additional tools and community resources, see [Pythonista-Tools](https://github.com/Pythonista-Tools/Pythonista-Tools).

### Get the Code

Use one of these methods to get the toolkit onto your device:

- **[Working Copy](https://workingcopyapp.com/)** — Git client for iOS; clone the repo and open files in Pythonista
- **[StaSh](https://github.com/ywangd/stash)** — Bash-like shell for Pythonista; run `git clone` directly

```bash
# In StaSh:
git clone https://github.com/AIVaneer/Eve-Repository.git
```

### Run

```python
# In Pythonista 3:
import sys
sys.path.insert(0, 'Eve-Repository/project_dont_die')

import run_all        # Full system check
import atlas_omega    # Command center
import wkapp_ui       # Native iOS interface
```

### Notes

- `requests` is pre-installed in Pythonista 3 — no `pip install` needed
- The WKWebView dashboard renders inside Pythonista's built-in web view
- `wkapp_ui.py` provides the native iOS toolbar and quick panel
- The [pythonista-wkapp](https://github.com/M4nw3l/pythonista-wkapp) framework pattern is used for WKWebView integration

---

## 🔌 API Reference — Dashboard Endpoints

When `dashboard.py` is running, the following JSON endpoints are available at `http://localhost:8080`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | HTML dashboard with Chart.js visualization |
| `/api/data` | GET | Full JSON payload — all subsystems |
| `/api/market` | GET | Market data (price, volume, liquidity) |
| `/api/economy` | GET | Economy data (supply, burn, emissions) |
| `/api/risk` | GET | Risk and alert data |
| `/api/whale` | GET | Whale tracker data |
| `/api/sentiment` | GET | Sentiment analysis data |
| `/api/health` | GET | System health and module status |

All endpoints return `Content-Type: application/json`. The `/api/data` endpoint aggregates all other endpoints into a single payload.

---

## 📊 Dashboard

The dashboard is a self-contained HTTP server with a dark-theme frontend.

```bash
python dashboard.py
# → Server running at http://localhost:8080
```

Features:
- Real-time price, volume, and liquidity charts (Chart.js)
- Risk gauge with color-coded severity
- Whale concentration heatmap
- Automation rule status panel
- Multi-chain liquidity table
- Auto-refresh every 30 seconds

---

## 🤖 Automation

The automation engine evaluates 10 built-in rules on every tick:

| Rule | Trigger | Action |
|------|---------|--------|
| `dump_alert` | Price drop > 15% in 1h | Fire CRITICAL alert |
| `low_liquidity` | Liquidity < $10,000 | Fire HIGH alert |
| `whale_dump` | Single wallet sells > 2% supply | Fire HIGH alert |
| `high_concentration` | Top 10 wallets > 80% supply | Fire MEDIUM alert |
| `volume_spike` | Volume > 5× 24h average | Fire INFO alert |
| `burn_milestone` | Burn crosses threshold | Log event + celebrate |
| `vault_unlock` | Large vault unlock approaching | Fire WARNING |
| `scenario_death_spiral` | Multiple risk factors active | Fire CRITICAL + escalate |
| `arbitrage_opportunity` | Price gap > 3% across chains | Log opportunity |
| `sentiment_crash` | Sentiment score < -0.5 | Fire WARNING |

Run with `python automation.py` and select **Start background engine** from the menu. Use **dry-run mode** to test rules without triggering real actions.

---

## 🌐 Multi-Chain

PCVR is tracked across 8 chains simultaneously:

| Chain | Explorer | Status |
|-------|----------|--------|
| Cronos | cronoscan.com | Primary chain |
| Ethereum | etherscan.io | Bridge target |
| BSC | bscscan.com | Bridge target |
| Polygon | polygonscan.com | Bridge target |
| Arbitrum | arbiscan.io | Bridge target |
| Optimism | optimistic.etherscan.io | Bridge target |
| Avalanche | snowtrace.io | Bridge target |
| Base | basescan.org | Bridge target |

Run `python multichain.py` and select **Scan all chains** for a live multi-chain liquidity snapshot.

---

## 📁 Configuration Files

These files are generated at runtime and are **gitignored** — never committed.

| File | Description |
|------|-------------|
| `integration_keys.json` | API keys for Tavily and Firecrawl |
| `automation_log.json` | Full history of automation rule triggers |
| `automation_rules_custom.json` | Custom user-defined rules |
| `multichain_config.json` | Chain and bridge configuration |
| `multichain_cache.json` | Cached multi-chain scan results |
| `intelligence_cache.json` | Cached Tavily/Firecrawl responses |
| `dashboard_cache/` | Dashboard data cache directory |
| `omega_reports/` | Saved Atlas Omega reports |
| `scenario_results/` | Saved simulation results |
| `atlas_graph.json` | Economy graph data |
| `atlas_economy.json` | Economy state |
| `pcvr_ledger.json` / `.csv` | Transaction ledger |
| `pcvr_wallets.json` | Wallet registry |
| `pcvr_whale_movements.json` | Whale movement log |
| `pcvr_alerts.json` | Alert history |
| `pcvr_market_data.json` | Cached market data snapshot |
| `pcvr_validation_report.json` | Last validation run report |
| `github_token.txt` | GitHub personal access token |
| `pcvr_sync_log.json` | GitHub sync log |

---

## 🤝 Contributing

### How to Add a New Module

1. Create `project_dont_die/your_module.py`
2. Follow the graceful import pattern:

```python
# © PCVR Studios 2026 — Your Module v1.0
# VX Description — one line purpose

import os

_DIR = os.path.dirname(os.path.abspath(__file__))

# Your module code here

def report():
    """Standard report function — called by atlas_omega and run_all."""
    pass
```

3. Register in `atlas_omega.py` — add to `_MODULE_META`:

```python
_MODULE_META = {
    ...
    "your_module": "V11",
}
```

4. Add a command to `OmegaEngine` in `atlas_omega.py`
5. Add import to `run_all.py` with graceful fallback:

```python
try:
    import your_module as _your_module
    _YOUR_MODULE_AVAILABLE = True
except Exception:
    _YOUR_MODULE_AVAILABLE = False
```

### Code Style

- **Pythonista compatible** — standard library preferred; no C extensions
- **Graceful imports** — all cross-module imports use `try/except`
- **`requests` is the only allowed external dependency**
- **No type hints required** — keep it readable on a phone screen
- **`_DIR`-relative file paths** — all data files saved relative to the module's directory
- **CLI interface** — every module should have a `_cli()` or `_run_cli()` function

### Naming Conventions

- Module files: `snake_case.py`
- Data files: `pcvr_<name>.json`
- Config files: `<module>_config.json` or `<module>_keys.json`
- Cache files: `<module>_cache.json`

---

## 🗺️ Roadmap

| Version | Status | Features |
|---------|--------|----------|
| V1–V3 | ✅ Complete | Market data, tokenomics, staking vault |
| V4–V6 | ✅ Complete | Risk engine, whale tracking, scenario simulation, pattern detection |
| V7 | ✅ Complete | In-game store, transaction ledger, event history |
| V8 | ✅ Complete | GitHub sync, system validation, live market data |
| V9 | ✅ Complete | Atlas Omega command center, graph engine |
| V10 | ✅ Complete | AI intelligence, web dashboard, automation engine, iOS UI, multi-chain |
| V11 | 🔮 Future | Advanced AI predictions, social media monitoring, predictive analytics |
| V12 | 🔮 Future | DAO integration, on-chain governance, community tools |

---

## 🎮 Games Library

PCVR Studios also builds games. All powered by custom in-house engines.

| Game | Platform | Description | Repository |
|------|----------|-------------|------------|
| 🚀 **SkyBurner Ultimate** | Pythonista 3 / iOS | 100% Python arcade space-shooter. Atlas Nexus Engine. 4 weapon tiers, multi-phase bosses, ×8 combo system. | [View Repo](https://github.com/AIVaneer/SkyBurner-Ultimate-pythonista-game-) |
| 🌀 **Warp Protocol** | Pythonista 3 / iOS | Fast-paced arcade shooter with dynamic starfield, enemy archetypes, power-ups, and progressive difficulty. | [View Repo](https://github.com/AIVaneer/Eve-Repository) |
| 🎮 **PCVR Game Shell** | Oculus Quest 3 | Foundational 2D VR game framework. Open-source under MIT License. | [View Repo](https://github.com/AIVaneer/PCVR-game-shell-) |

### 📥 Downloads

> 💬 Downloads are hosted on our Discord server — [join free](https://discord.gg/E7bW3Zh4x) to access them.

- **SkyBurner Ultimate**: [Game](https://discord.com/channels/1316937801995911198/1484003872178573495/1484552464639332605) · [Music](https://discord.com/channels/1316937801995911198/1484003872178573495/1484595490828845229)
- **Warp Protocol**: [Game](https://discord.com/channels/1316937801995911198/1484003872178573495/1484175284419690687) · [Music](https://discord.com/channels/1316937801995911198/1484003872178573495/1484175284419690687)

### 🔗 Community

- **Twitter/X**: [PCVR Studios](https://x.com/pcvr2024?s=21)
- **Discord**: [Join our Discord](https://discord.gg/E7bW3Zh4x)

---

## 📄 License

See [LICENSE](LICENSE) for details.

---

*© PCVR STUDIOS · 2026 — Contract: `0x05c870C5C6E7AF4298976886471c69Fc722107e4`*