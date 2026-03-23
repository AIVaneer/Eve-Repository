# 📦 Project Don't Die — Module Reference

> Detailed documentation for every module in the `project_dont_die/` toolkit.

**Contract:** `0x05c870C5C6E7AF4298976886471c69Fc722107e4` (Cronos)  
**Philosophy:** Earn → Hold → Spend → Buy → Earn

---

## Table of Contents

- [atlas\_omega.py](#atlas_omegapy--v9)
- [live\_data.py](#live_datapy--v1)
- [economy.py](#economypy--v2)
- [vault.py](#vaultpy--v3)
- [alert.py](#alertpy--v4)
- [whale\_tracker.py](#whale_trackerpy--v5)
- [scenario.py](#scenariopy--v6)
- [detector.py](#detectorpy--v6)
- [store.py](#storepy--v7)
- [history.py](#historypy--v7)
- [token\_data.py](#token_datapy--v7)
- [github\_sync.py](#github_syncpy--v8)
- [validate.py](#validatepy--v8)
- [atlas\_graph\_core.py](#atlas_graph_corepy--v9)
- [smart\_integrations.py](#smart_integrationspy--v10)
- [dashboard.py](#dashboardpy--v10)
- [automation.py](#automationpy--v10)
- [wkapp\_ui.py](#wkapp_uipy--v10)
- [multichain.py](#multichainpy--v10)
- [run\_all.py](#run_allpy)

---

## `atlas_omega.py` — V9

**Unified Command Center.** One entry point for all 20+ modules.

### CLI Commands

Run with `python atlas_omega.py` and enter a command name or number.

| # | Command | Description |
|---|---------|-------------|
| 1 | `omega` | Full omega report — every subsystem in one view |
| 2 | `quick` | One-line status summary |
| 3 | `market` | Market data panel (live price, volume, liquidity) |
| 4 | `economy` | Economy status (supply, burn, health ratio) |
| 5 | `risk` | Risk assessment with severity scoring |
| 6 | `whale` | Whale tracker (concentration, Gini coefficient) |
| 7 | `scenario` | Scenario outlook (baseline, utopia, death spiral) |
| 8 | `graph` | System graph visualization (V9) |
| 9 | `recommend` | AI-generated recommendations |
| 10 | `watch` | Continuous monitoring mode (configurable interval) |
| 11 | `modules` | Module load status |
| 12 | `trends` | History & activity trends |
| 13 | `intel` | V10 intelligence report (Tavily/Firecrawl/sentiment) |
| 14 | `save` | Save full report to `omega_reports/` |
| 15 | `dashboard` | Launch the web dashboard (`dashboard.py`) |
| 16 | `auto` | Start/stop the automation engine |
| 17 | `ios` | Launch Pythonista iOS UI (`wkapp_ui.py`) |
| 18 | `multichain` | Multi-chain tracker overview |
| 19 | `exit` | Quit |

### Key Class: `OmegaEngine`

```python
engine = OmegaEngine()
engine.omega_report()        # Print full unified report
engine.quick_status()        # One-line status string
engine.quick_market()        # Market data section
engine.quick_economy()       # Economy section
engine.quick_risk()          # Risk section
engine.quick_whale()         # Whale section
engine.generate_recommendations()  # List of AI recommendations
engine.watch(interval=60)    # Continuous monitoring loop
engine.module_status()       # Which modules loaded
engine.trend_summary()       # History events and trends
engine.save_report()         # Save report JSON to disk
engine.all_data()            # Dict of all data sections
```

### Integration

Atlas Omega loads all other modules dynamically via `_try_import()`. Add a module to `_MODULE_META` to register it:

```python
_MODULE_META = {
    "your_module": "V11",
    ...
}
```

---

## `live_data.py` — V1

**Real-time market data.** Fetches price, volume, and liquidity from DexScreener and Binance.

### Key Functions

```python
from live_data import *

# Fetch data
fetch_dexscreener()       # Raw DexScreener response dict
fetch_binance_btc()       # BTC/USDT price from Binance

# Cached data
get_data()                # Fetch or load cached snapshot
get_data(force_refresh=True)  # Force fresh fetch

# Analysis
price_to_pcvr(1.00)       # Convert USD → PCVR token amount
pcvr_to_usd(1000)         # Convert PCVR → USD
liquidity_ratio()         # Liquidity / market cap ratio
volume_ratio()            # 24h volume / market cap ratio
market_status()           # "bullish" / "bearish" / "neutral" string
supply_pressure()         # Buy/sell pressure analysis string

# Reports
wallet_report()           # Current wallet value report
market_report()           # Full market data report (prints to console)
```

### Data Sources

- **DexScreener** — `https://api.dexscreener.com/latest/dex/tokens/{contract}`
- **Binance** — `https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT`

### Cached Data File

`pcvr_market_data.json` — snapshot saved after each fetch. Cache expires after 5 minutes.

---

## `economy.py` — V2

**Tokenomics engine.** Tracks emissions, burns, spending, and the overall economic health ratio.

### State Variables

```python
import economy

economy.emitted    # Total tokens emitted (earned by players)
economy.spent      # Total tokens spent in-game
economy.burned     # Total tokens permanently burned
economy.locked     # Total tokens locked in vault
economy.circ       # Circulating supply
economy.supply     # Max supply
economy.cap        # Market cap (USD)
economy.today      # Daily counters dict
```

### Key Functions

```python
economy.earn(100)          # Record 100 tokens earned
economy.spend(50)          # Record 50 tokens spent
economy.burn(10)           # Permanently burn 10 tokens
economy.lock(25)           # Lock 25 tokens in vault
economy.buy(100, burn_pct=15)  # Buy: 15% burned, rest circulates

economy.health()           # Health ratio (0.0–1.0)
economy.burn_ratio()       # Burned / emitted ratio
economy.net()              # Net change today

economy.new_day()          # Reset daily counters
economy.report()           # Print full economy status
```

### Health Ratio

The health ratio measures token sustainability:
- `1.0` = perfect balance (spending == earning)
- `> 1.0` = deflationary (more spending/burning than earning)
- `< 0.5` = danger zone (more emission than burn)

---

## `vault.py` — V3

**Staking vault.** Players lock tokens to earn APY rewards.

### Key Functions

```python
from vault import *

deposit_revenue(1000, source="store")  # Add revenue to vault balance
lock_tokens("player_1", 500)           # Player locks 500 tokens
advance_day()                          # Process one day (apply rewards)
check_unlocks()                        # Check and process unlocks
vault_apy()                            # Current APY rate (float)
report()                               # Print vault status
```

### State Variables

```python
import vault

vault.vault_balance    # Available vault balance
vault.total_locked     # Total tokens currently locked
vault.lockers          # List of {player, amount, days_locked, unlock_day}
```

---

## `alert.py` — V4

**Risk engine.** Multi-level alert system with risk scoring.

### Alert Severities

| Severity | Use Case |
|----------|----------|
| `CRITICAL` | Immediate threat to token survival |
| `HIGH` | Serious risk requiring attention |
| `MEDIUM` | Moderate concern |
| `LOW` | Informational warning |
| `INFO` | Status update |

### Key Functions

```python
from alert import *

# Fire alerts
fire("HIGH", "WHALE", "Large wallet dumped 2% supply", source="whale_tracker")
fire("CRITICAL", "LIQUIDITY", "Liquidity below $5k", data={"liquidity": 4800})

# Query alerts
get_all()                   # All alerts (list of dicts)
get_active()                # Unacknowledged alerts
get_by_severity("HIGH")     # Filter by severity
get_by_category("WHALE")    # Filter by category

# Manage alerts
acknowledge(alert_id)       # Mark alert as acknowledged
acknowledge_all()           # Acknowledge all active alerts
clear_old(days=7)           # Remove alerts older than 7 days

# Analytics
count_by_severity()         # Dict: {"HIGH": 3, "CRITICAL": 1, ...}
risk_score()                # Returns (score: int, interpretation: str)
health_check()              # Full system health check

# Reports
dashboard()                 # Print alert dashboard
```

### Risk Score

`risk_score()` returns a tuple `(score, interpretation)`:
- Score 0–25: LOW risk
- Score 26–50: MEDIUM risk
- Score 51–75: HIGH risk
- Score 76–100: CRITICAL risk

---

## `whale_tracker.py` — V5

**Whale analysis.** Tracks large wallet holders and measures token concentration.

### Key Functions

```python
from whale_tracker import *

# Wallet management
add_wallet("wallet_123", "whale", balance=500000)
update_balance("wallet_123", 450000)
transfer("wallet_123", "wallet_456", 50000)

# Analysis
get_all_wallets()           # List of all tracked wallets
top_holders(n=10)           # Top N wallets by balance
get_by_type("whale")        # Filter by wallet type: "whale", "fund", "team", "retail"
concentration_report()      # Print concentration analysis
gini_coefficient()          # Gini coefficient (0 = equal, 1 = one wallet holds all)

# Movements
log_movement("wallet_123", 50000, "sell", details="Whale exit")
get_supply()                # Total tracked supply
```

### Wallet Types

| Type | Description |
|------|-------------|
| `whale` | Large holder (>1% supply) |
| `fund` | Investment fund or institutional |
| `team` | Core team allocation |
| `retail` | Standard retail holder |

### Gini Coefficient

The Gini coefficient measures wealth concentration:
- `0.0` = perfectly equal distribution
- `0.5` = moderate concentration
- `0.8+` = high concentration (danger zone)

---

## `scenario.py` — V6

**Simulation engine.** Runs economic scenarios to model token survival outcomes.

### Built-in Scenarios

| Scenario | Description |
|----------|-------------|
| `death_spiral` | Aggressive sell pressure + liquidity drain |
| `slow_bleed` | Gradual decline over 30 days |
| `baseline` | Current trajectory continues unchanged |
| `recovery` | Moderate improvement in buy pressure |
| `bull_run` | Strong buying + positive sentiment |
| `utopia` | Best-case scenario with burn acceleration |
| `whale_exit` | Single large whale exits |

### Key Functions

```python
from scenario import *

# Run scenarios
run_scenario(get_scenario("death_spiral"))
run_all_scenarios()                        # Run all 7 scenarios

# Compare scenarios
compare("baseline", "bull_run")
comparison_report(results1, results2)

# Reports
scenario_report(results)                  # Print scenario results
list_scenarios()                          # List available scenarios

# Save / load
save_results(results, filename="my_run")
```

### Custom Scenarios

```python
custom = {
    "name": "my_scenario",
    "days": 30,
    "daily_buy_pressure": 0.05,     # 5% daily buy pressure
    "daily_sell_pressure": 0.02,    # 2% daily sell pressure
    "burn_multiplier": 1.5,         # 1.5× normal burn rate
}
run_scenario(custom)
```

---

## `detector.py` — V6

**Pattern detection.** Identifies dangerous on-chain patterns from economic data.

### Key Function

```python
from detector import check

patterns = check(
    emitted=10000,    # Tokens emitted today
    spent=3000,       # Tokens spent today
    burned=500,       # Tokens burned today
    locked=2000,      # Tokens locked today
    circ=1000000,     # Circulating supply
    supply=10000000,  # Max supply
    cap=50000,        # Market cap (USD)
    today={}          # Today's economy counters
)
# Returns list of detected pattern strings
```

### Detected Patterns

| Pattern | Trigger |
|---------|---------|
| `HEAVY DUMP` | Spend-to-earn ratio critically low |
| `ACCUMULATION` | Large lock + low spend |
| `DISTRIBUTION` | High emit + low spend + low burn |
| `HEALTHY` | Balanced economy signals |
| `CRITICAL: LOW LIQUIDITY` | Market cap below warning threshold |

---

## `store.py` — V7

**In-game store.** Manages items, purchases, and revenue.

### Key Functions

```python
from store import *

# Purchases
purchase("player_1", "Speed Boost")    # Returns (success, message)

# Analytics
top_sellers(n=5)                       # Top 5 items by units sold
dead_items()                           # Items with zero sales
revenue_report()                       # Full revenue breakdown
category_breakdown()                   # Revenue by category

# Display
browse()                               # Print store catalog
print_revenue_report()                 # Print revenue report
print_category_breakdown()             # Print category breakdown
```

### Data Files

- `store_catalog.json` — item definitions (gitignored)
- `store_transactions.json` — purchase history (gitignored)

---

## `history.py` — V7

**Event history.** Timestamped log of all toolkit events.

### Key Functions

```python
from history import *

# Log events
log_event("EARN", 100, details="Daily reward", source="economy")
log_event("BURN", 50, details="Store burn", source="store")

# Query
get_all()                              # All events
get_by_type("EARN")                    # Filter by type
get_by_date("2026-03-23")             # Events on a date
get_range("2026-03-01", "2026-03-31") # Date range
get_last(n=10)                         # Last N events

# Analytics
total_by_type("EARN")                  # Total amount for event type
daily_summary("2026-03-23")           # Summary for a day
weekly_summary()                       # Last 7 days summary
trend("EARN", days=7)                 # Trend data for event type
```

### Event Types

Common event types: `EARN`, `SPEND`, `BURN`, `LOCK`, `BUY`, `UNLOCK`, `PURCHASE`, `ALERT`, `SYNC`

---

## `token_data.py` — V7

**Token constants.** Core token metadata and chain information.

### Key Function

```python
from token_data import show
show()    # Print token summary (contract, chain, supply, etc.)
```

---

## `github_sync.py` — V8

**GitHub integration.** Push and pull module files to/from GitHub.

### Key Functions

```python
from github_sync import *

# Auth
setup_auth()                           # Interactive token setup
load_token()                           # Load saved token
get_headers()                          # Auth headers dict

# File operations
list_remote_files()                    # Files in GitHub repo
get_remote_file("economy.py")         # Download remote file
push_file("economy.py", content, message="Update economy")
delete_remote_file("old_module.py")

# Sync
compare()                              # Compare local vs remote
local_files()                          # List local module files
remote_files()                         # List remote module files
```

### Auth File

`github_token.txt` — personal access token. Gitignored, never committed.

---

## `validate.py` — V8

**System health.** Validates all modules, functions, data files, and integrations.

### Key Functions

```python
from validate import *

validate_imports()             # Check all modules import (returns passed, failed counts)
validate_functions()           # Check required functions exist
validate_data_files()          # Check data file integrity
validate_integrations()        # Check API connectivity
validate_config()              # Validate configuration files
full_validation()              # Run all checks, print full report
```

### Validation Report

Results saved to `pcvr_validation_report.json` after each run.

---

## `atlas_graph_core.py` — V9

**Economy graph engine.** Builds and analyzes a graph representation of the token economy.

### Key Classes

```python
from atlas_graph_core import AtlasGraphCore, GraphBuilder, GraphAnalyzer

# High-level interface
core = AtlasGraphCore()
core.build()                  # Build graph from current economy state
core.analyze()                # Run graph analysis
core.summary()                # Summary dict

# Graph building
builder = GraphBuilder()
builder.add_node("economy", data={})
builder.add_edge("economy", "vault", weight=1.0)
graph = builder.build()

# Economy graph (pre-configured)
econ_builder = EconomyGraphBuilder()
econ_graph = econ_builder.build()

# Analysis
analyzer = GraphAnalyzer(graph)
analyzer.centrality()         # Node centrality scores
analyzer.critical_paths()     # Most critical economic paths
```

---

## `smart_integrations.py` — V10

**AI intelligence layer.** Connects to Tavily search and Firecrawl for off-chain intelligence.

### Key Functions

```python
from smart_integrations import *

# Setup
setup_keys()                          # Interactive API key setup
get_key("tavily")                     # Get stored key
load_keys()                           # Load keys from file

# Search
tavily_search("PCVR token cronos")   # AI web search, returns results list
pcvr_news()                           # Search for recent PCVR news
crypto_sentiment()                    # Search crypto market sentiment
competitor_scan()                     # Scan competitor tokens
regulatory_check()                    # Search for regulatory news

# Cache
cache_result("key", data, ttl=300)   # Cache data for 300 seconds
get_cached("key")                     # Get cached data or None
cache_status()                        # Print cache statistics
```

### API Keys Configuration

Create `integration_keys.json` in the `project_dont_die/` directory:

```json
{
  "tavily": "tvly-YOUR_KEY_HERE",
  "firecrawl": "fc-YOUR_KEY_HERE"
}
```

Or run `setup_keys()` for interactive setup.

- [Tavily API](https://app.tavily.com) — AI-powered web search
- [Firecrawl API](https://firecrawl.dev) — structured web scraping

---

## `dashboard.py` — V10

**Web dashboard server.** Serves a dark-theme Chart.js dashboard on `localhost:8080`.

### Key Class: `DashboardServer`

```python
from dashboard import DashboardServer

server = DashboardServer(host="localhost", port=8080)
server.start()                # Start in background thread
server.stop()                 # Stop server
server.status()               # Server status string
```

### API Endpoints

| Endpoint | Returns |
|----------|---------|
| `GET /` | HTML dashboard page |
| `GET /api/data` | Full JSON payload (all subsystems) |
| `GET /api/market` | Market data |
| `GET /api/economy` | Economy data |
| `GET /api/risk` | Risk and alert data |
| `GET /api/whale` | Whale tracker data |
| `GET /api/sentiment` | Sentiment analysis data |
| `GET /api/health` | System health status |

### Run via CLI

```bash
python dashboard.py
# → Select "Start server" from the menu
# → Open http://localhost:8080 in your browser
```

---

## `automation.py` — V10

**Rule-based automation engine.** Evaluates rules in a background thread and fires actions.

### Key Class: `AutomationEngine`

```python
from automation import AutomationEngine

engine = AutomationEngine()
engine.start()                         # Start background thread
engine.stop()                          # Stop background thread
engine.status()                        # Status string
engine.run_once()                      # Evaluate all rules once
engine.set_dry_run(True)              # Enable dry-run (no real actions)
engine.get_history(n=20)              # Last N actions taken
engine.clear_history()                 # Clear action log
```

### Built-in Rules

| Rule | Trigger | Action |
|------|---------|--------|
| `dump_alert` | Price drop > 15% in 1h | Fire CRITICAL alert |
| `low_liquidity` | Liquidity < $10,000 | Fire HIGH alert |
| `whale_dump` | Single wallet sells > 2% supply | Fire HIGH alert |
| `high_concentration` | Top 10 wallets > 80% supply | Fire MEDIUM alert |
| `volume_spike` | Volume > 5× 24h average | Fire INFO alert |
| `burn_milestone` | Burn crosses threshold | Log event |
| `vault_unlock` | Large vault unlock approaching | Fire WARNING |
| `scenario_death_spiral` | Multiple risk factors active | Fire CRITICAL |
| `arbitrage_opportunity` | Price gap > 3% across chains | Log opportunity |
| `sentiment_crash` | Sentiment score < -0.5 | Fire WARNING |

### Custom Rules

Custom rules can be added to `automation_rules_custom.json`. Each rule defines:
- `name` — unique rule identifier
- `condition` — Python expression evaluated against engine data
- `action` — action to take when condition is true
- `cooldown` — seconds between triggers (prevents spam)

### Run via CLI

```bash
python automation.py
# → Select "Start background engine" from the menu
```

---

## `wkapp_ui.py` — V10

**Native iOS UI for Pythonista 3.** Uses WKWebView to render the dashboard inside a native iOS interface.

### Key Classes

```python
from wkapp_ui import PCVRApp, PCVRToolbar, PCVRQuickPanel

# Full app
app = PCVRApp()
app.launch()                  # Launch the WKWebView app

# Toolbar only
toolbar = PCVRToolbar()
toolbar.show()

# Quick panel (key metrics without full dashboard)
panel = PCVRQuickPanel()
panel.show()
```

### Helper Functions

```python
from wkapp_ui import _is_pythonista

_is_pythonista()    # True if running in Pythonista 3, False otherwise
```

### Pythonista Detection

The module detects whether it's running in Pythonista 3 at import time. On desktop Python, it falls back to CLI mode gracefully. The `PCVRApp.launch()` method opens the dashboard URL in Pythonista's built-in WKWebView.

### Run via CLI

```bash
python wkapp_ui.py
# On iOS Pythonista 3: launches native UI
# On desktop: shows CLI menu
```

---

## `multichain.py` — V10

**Multi-chain tracker.** Monitors PCVR price and liquidity across 8 blockchain networks.

### Supported Chains

| Chain | Network | Explorer |
|-------|---------|----------|
| Cronos | CRO | cronoscan.com |
| Ethereum | ETH | etherscan.io |
| BSC | BNB | bscscan.com |
| Polygon | MATIC | polygonscan.com |
| Arbitrum | ARB | arbiscan.io |
| Optimism | OP | optimistic.etherscan.io |
| Avalanche | AVAX | snowtrace.io |
| Base | BASE | basescan.org |

### Key Functions

```python
from multichain import *

scan()            # Scan all chains (prints results)
report()          # Full multi-chain report
liquidity()       # Liquidity summary across all chains
prices()          # Price comparison across chains
arbitrage()       # Flag price discrepancies (arbitrage opportunities)
diversity()       # Chain diversity score
summary()         # One-line summary dict
```

### Key Classes

```python
from multichain import MultiChainTracker, BridgeTracker

# Full tracker
tracker = MultiChainTracker()
tracker.scan_all()            # Fetch data from all chains
tracker.get_chain("cronos")   # Data for a specific chain
tracker.total_liquidity()     # Aggregated liquidity

# Bridge tracker
bridges = BridgeTracker()
bridges.scan()                # Check bridge routes
bridges.active_routes()       # Active bridge routes with status
```

### Run via CLI

```bash
python multichain.py
# → Select "Scan all chains" from the menu
```

---

## `run_all.py`

**Full system runner.** Imports and runs all modules in dependency order.

### Usage

```bash
python run_all.py
```

Or in Pythonista 3:

```python
import run_all
```

### What it does

1. Validates all module imports via `validate.py`
2. Runs `token_data.show()`
3. Runs the economy simulation cycle
4. Runs vault operations
5. Fetches live market data
6. Runs pattern detection
7. Runs whale tracker
8. Runs alert risk check
9. Runs scenario analysis
10. Runs store and ledger reports
11. Runs history summary
12. Runs Atlas Omega quick status
13. Reports V10 module availability (smart_integrations, automation, multichain, wkapp_ui)

All V10 module imports are graceful — `run_all.py` continues even if optional modules are unavailable.

---

*© PCVR STUDIOS · 2026 — Contract: `0x05c870C5C6E7AF4298976886471c69Fc722107e4`*
