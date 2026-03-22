# PCVR STUDIOS — Atlas Graph Core v2
# Pythonista-compatible graph analysis engine
# Analyzes codebases AND token economy flow
#
# Token: PCVR Coin | Chain: Cronos
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# © PCVR STUDIOS 2026

import os
import ast
import json
import random
from datetime import datetime

# -------------------------
# CONSTANTS
# -------------------------
DATA_FILE = "atlas_graph.json"
ECONOMY_FILE = "atlas_economy.json"

PCVR_CONTRACT = "0x05c870C5C6E7AF4298976886471c69Fc722107e4"
PCVR_CHAIN = "Cronos"

# Try to import values from existing toolkit; fall back to built-in defaults
try:
    import economy as _econ
    DEFAULT_DAILY_CAP = _econ.cap
    DEFAULT_SUPPLY = _econ.supply
    DEFAULT_CIRC = _econ.circ
except Exception:
    DEFAULT_DAILY_CAP = 50_000
    DEFAULT_SUPPLY = 1_000_000_000
    DEFAULT_CIRC = 100_000_000

try:
    import vault as _vault
    DEFAULT_LOCK_DAYS = 90
except Exception:
    DEFAULT_LOCK_DAYS = 90

try:
    import detector as _detector
    _DETECTOR_AVAILABLE = True
except Exception:
    _DETECTOR_AVAILABLE = False

DEFAULT_BURN_RATE_MIN = 0.15
DEFAULT_BURN_RATE_MAX = 0.35
DEFAULT_LOCK_PCT = 0.10


# -------------------------
# STORAGE
# -------------------------
def save_graph(data, filepath=DATA_FILE):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_graph(filepath=DATA_FILE):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {"nodes": [], "edges": []}


# -------------------------
# GRAPH BUILDER (Code Mode)
# -------------------------
class GraphBuilder:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, name, ntype):
        if not any(n["id"] == name for n in self.nodes):
            self.nodes.append({"id": name, "type": ntype})

    def add_edge(self, source, target, etype):
        self.edges.append({"source": source, "target": target, "type": etype})

    def scan_file(self, filepath):
        try:
            with open(filepath, "r") as f:
                tree = ast.parse(f.read())
        except Exception:
            return

        filename = os.path.basename(filepath)
        self.add_node(filename, "file")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                fname = f"{filename}:{node.name}"
                self.add_node(fname, "function")
                self.add_edge(filename, fname, "defines")

            if isinstance(node, ast.ClassDef):
                cname = f"{filename}:{node.name}"
                self.add_node(cname, "class")
                self.add_edge(filename, cname, "defines")

            if isinstance(node, ast.Import):
                for n in node.names:
                    self.add_edge(filename, n.name, "imports")

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                self.add_edge(filename, module, "imports")

    def scan_folder(self, folder):
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".py"):
                    self.scan_file(os.path.join(root, file))

        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "timestamp": str(datetime.now()),
        }


# -------------------------
# ECONOMY GRAPH BUILDER (Economy Mode)
# -------------------------
class EconomyGraphBuilder:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_wallet(self, wallet_id, wallet_type):
        if not any(n["id"] == wallet_id for n in self.nodes):
            self.nodes.append({"id": wallet_id, "type": wallet_type})

    def add_transaction(self, source, target, tx_type, amount):
        self.edges.append({
            "source": source,
            "target": target,
            "type": tx_type,
            "amount": amount,
        })

    def simulate_economy(self, num_players=5, num_days=7):
        random.seed(42)

        # Create wallets
        player_ids = [f"player_{i+1}" for i in range(num_players)]
        for pid in player_ids:
            self.add_wallet(pid, "player")
        self.add_wallet("store", "store")
        self.add_wallet("vault", "vault")
        self.add_wallet("burn_address", "burn")
        self.add_wallet("emission_pool", "pool")

        total_emitted = 0.0
        total_spent = 0.0
        total_burned = 0.0
        total_locked = 0.0

        player_cap = DEFAULT_DAILY_CAP / num_players

        for day in range(num_days):
            day_emitted = 0.0
            for pid in player_ids:
                # Earn (capped at daily emission cap per player)
                earned = random.uniform(player_cap * 0.3, player_cap)
                self.add_transaction("emission_pool", pid, "earn", round(earned, 2))
                total_emitted += earned
                day_emitted += earned

                # Spend at store
                if random.random() > 0.3:
                    spend_amt = random.uniform(earned * 0.1, earned * 0.5)
                    burn_rate = random.uniform(DEFAULT_BURN_RATE_MIN, DEFAULT_BURN_RATE_MAX)
                    burn_amt = spend_amt * burn_rate
                    lock_amt = spend_amt * DEFAULT_LOCK_PCT

                    self.add_transaction(pid, "store", "spend", round(spend_amt, 2))
                    self.add_transaction("store", "burn_address", "burn", round(burn_amt, 2))
                    self.add_transaction("store", "vault", "lock", round(lock_amt, 2))

                    total_spent += spend_amt
                    total_burned += burn_amt
                    total_locked += lock_amt

        summary = {
            "total_emitted": round(total_emitted, 2),
            "total_spent": round(total_spent, 2),
            "total_burned": round(total_burned, 2),
            "total_locked": round(total_locked, 2),
        }

        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "timestamp": str(datetime.now()),
            "summary": summary,
        }


# -------------------------
# GRAPH ANALYZER (Both Modes)
# -------------------------
class GraphAnalyzer:
    def __init__(self, graph, mode="code"):
        self.graph = graph
        self.mode = mode

    def find_orphans(self):
        used = set(e["target"] for e in self.graph["edges"])
        all_nodes = set(n["id"] for n in self.graph["nodes"])
        return list(all_nodes - used)

    def find_heavy_dependencies(self):
        count = {}
        for e in self.graph["edges"]:
            tgt = e["target"]
            count[tgt] = count.get(tgt, 0) + 1
        return sorted(count.items(), key=lambda x: x[1], reverse=True)[:5]

    def system_health(self):
        if self.mode == "economy":
            return self._economy_health()
        return self._code_health()

    def _code_health(self):
        edges = len(self.graph["edges"])
        nodes = len(self.graph["nodes"])
        if nodes == 0:
            return "EMPTY"
        ratio = edges / nodes
        if ratio > 2:
            return "HIGHLY CONNECTED 🔥"
        elif ratio > 1:
            return "STABLE ⚖️"
        else:
            return "FRAGILE ⚠️"

    def _economy_health(self):
        s = self.graph.get("summary", {})
        emitted = s.get("total_emitted", 0)
        spent = s.get("total_spent", 0)
        burned = s.get("total_burned", 0)
        locked = s.get("total_locked", 0)

        if emitted == 0:
            return "NO DATA"

        circ = emitted - burned
        health_ratio = spent / emitted
        burn_ratio = burned / emitted
        lock_ratio = locked / circ if circ > 0 else 0
        net_emission = emitted - spent - burned

        lines = [
            f"  Health Ratio  (spent/emitted):   {health_ratio:.4f}  "
            + ("✅ >= 1.0" if health_ratio >= 1.0 else "⚠️  target >= 1.0"),
            f"  Burn Ratio    (burned/emitted):   {burn_ratio:.1%}  "
            + ("✅ >= 15%" if burn_ratio >= 0.15 else "⚠️  target >= 15%"),
            f"  Lock Ratio    (locked/circ):      {lock_ratio:.1%}  "
            + ("✅ 20-40%" if 0.20 <= lock_ratio <= 0.40 else "⚠️  target 20-40%"),
            f"  Net Emission  (emitted-spent-burned): {net_emission:,.0f}  "
            + ("✅ <= 0" if net_emission <= 0 else "⚠️  target <= 0"),
        ]

        # Overall status
        if health_ratio >= 1.0 and burn_ratio >= 0.15 and 0.20 <= lock_ratio <= 0.40 and net_emission <= 0:
            status = "🟢 GREEN — Economy is healthy"
        elif health_ratio >= 0.7 and burn_ratio >= 0.10:
            status = "🟡 YELLOW — Caution, monitor closely"
        elif health_ratio >= 0.2:
            status = "🔴 RED — Intervention needed"
        else:
            status = "💀 SKULL — Token in critical danger"

        return "\n".join([status] + lines)


# -------------------------
# ATLAS GRAPH CORE (Main Controller)
# -------------------------
class AtlasGraphCore:
    def __init__(self):
        self.graph = load_graph(DATA_FILE)
        self.economy_graph = load_graph(ECONOMY_FILE)

    def build(self, folder):
        print("\n🔍 Scanning codebase...")
        builder = GraphBuilder()
        self.graph = builder.scan_folder(folder)
        save_graph(self.graph, DATA_FILE)
        print("✅ Code graph built and saved.")

    def build_economy(self, num_players=5, num_days=7):
        print("\n💹 Simulating token economy...")
        builder = EconomyGraphBuilder()
        self.economy_graph = builder.simulate_economy(num_players, num_days)
        save_graph(self.economy_graph, ECONOMY_FILE)
        print("✅ Economy graph built and saved.")

    def analyze(self, mode="code"):
        graph = self.economy_graph if mode == "economy" else self.graph

        if not graph["nodes"]:
            print(f"\n⚠️  No {mode} graph data. Run build first.")
            return

        analyzer = GraphAnalyzer(graph, mode=mode)

        print(f"\n🧠 ATLAS ANALYSIS REPORT — {mode.upper()} MODE\n")
        print("📊 System Health:")
        print(" ", analyzer.system_health())

        label_orphan = (
            "wallets that earn but never spend (farmers)"
            if mode == "economy"
            else "unused files/functions (dead code)"
        )
        print(f"\n⚠️  Orphan Nodes ({label_orphan}):")
        orphans = analyzer.find_orphans()
        if not orphans:
            print("  None")
        else:
            for o in orphans[:10]:
                print(f"  - {o}")

        label_heavy = (
            "most-transacted wallets"
            if mode == "economy"
            else "most-imported modules"
        )
        print(f"\n🔥 Heavy Dependencies ({label_heavy}):")
        heavy = analyzer.find_heavy_dependencies()
        if not heavy:
            print("  None")
        else:
            for name, cnt in heavy:
                print(f"  - {name}: {cnt} links")

    def show_summary(self, mode="code"):
        graph = self.economy_graph if mode == "economy" else self.graph
        label = "ECONOMY" if mode == "economy" else "CODE"
        print(f"\n📊 GRAPH SUMMARY — {label}")
        print(f"  Nodes:     {len(graph['nodes'])}")
        print(f"  Edges:     {len(graph['edges'])}")
        print(f"  Last Scan: {graph.get('timestamp', 'N/A')}")
        if mode == "economy" and "summary" in graph:
            s = graph["summary"]
            print(f"  Emitted:   {s.get('total_emitted', 0):,.2f}")
            print(f"  Spent:     {s.get('total_spent', 0):,.2f}")
            print(f"  Burned:    {s.get('total_burned', 0):,.2f}")
            print(f"  Locked:    {s.get('total_locked', 0):,.2f}")

    def quick_economy_health(self):
        """Return a one-line economy health status (used by run_all.py)."""
        if not self.economy_graph.get("nodes"):
            self.build_economy()
        analyzer = GraphAnalyzer(self.economy_graph, mode="economy")
        status = analyzer.system_health()
        # Return just the first line (the emoji status)
        return status.split("\n")[0]


# -------------------------
# INTERACTIVE CLI RUNNER
# -------------------------
if __name__ == "__main__":
    atlas = AtlasGraphCore()

    print("""
==================================
🧠 ATLAS GRAPH CORE v2
PCVR SYSTEM ANALYZER + ECONOMY ENGINE
==================================
© PCVR STUDIOS 2026
Token: PCVR Coin | Chain: Cronos
Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4

"Earn → Hold → Spend → Buy → Earn.
 If any link breaks, the token dies."
==================================
Commands:
1. build        → scan code folder
2. economy      → simulate token economy
3. analyze      → code analysis report
4. econ-report  → economy health report
5. summary      → quick stats
6. quick        → scan current folder + analyze
7. exit
""")

    while True:
        try:
            cmd = input("atlas_graph> ").lower().strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Atlas shutting down.")
            break

        if cmd in ["1", "build"]:
            path = input("Enter folder path (or press Enter for current): ").strip()
            if not path:
                path = os.getcwd()
            atlas.build(path)

        elif cmd in ["2", "economy"]:
            try:
                p = int(input("Number of players (default 5): ").strip() or "5")
                d = int(input("Number of days (default 7): ").strip() or "7")
            except ValueError:
                p, d = 5, 7
            atlas.build_economy(p, d)

        elif cmd in ["3", "analyze"]:
            atlas.analyze(mode="code")

        elif cmd in ["4", "econ-report"]:
            atlas.analyze(mode="economy")

        elif cmd in ["5", "summary"]:
            atlas.show_summary(mode="code")
            atlas.show_summary(mode="economy")

        elif cmd in ["6", "quick"]:
            print("⚡ Quick scan running...")
            atlas.build(os.getcwd())
            atlas.analyze(mode="code")

        elif cmd in ["7", "exit"]:
            print("👋 Atlas shutting down.")
            break

        else:
            print("❌ Unknown command. Use 1–7 or type command name.")
