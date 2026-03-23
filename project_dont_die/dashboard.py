# © PCVR Studios 2025 — Dashboard Server v1.0
# V10 Phase 2 — Visual Web Dashboard for PCVR Command Center
#
# See everything. Control everything. From any browser.
# Earn → Hold → Spend → Buy → Earn.
#
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
# Runs in Pythonista 3 on iOS — standard library only

import json
import os
import datetime
import threading

_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Module loader ────────────────────────────────────────────────────────────

def _try_import(name):
    """Import a module from project_dont_die, return (module, error_str)."""
    import sys
    if _DIR not in sys.path:
        sys.path.insert(0, _DIR)
    try:
        import importlib
        mod = importlib.import_module(name)
        return mod, None
    except Exception as exc:
        return None, str(exc)


# ─── DashboardServer ─────────────────────────────────────────────────────────

class DashboardServer:
    """
    HTTP server that serves the PCVR visual dashboard and JSON API endpoints.
    Runs in a background thread so it doesn't block the main programme.
    """

    host = "0.0.0.0"
    port = 8080

    # Template path
    _TEMPLATE = os.path.join(_DIR, "dashboard_template.html")

    def __init__(self, host=None, port=None):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        self._server  = None
        self._thread  = None
        self._running = False
        self._modules = {}
        self._load_modules()

    # ── Module loading ────────────────────────────────────────────────────────

    def _load_modules(self):
        """Gracefully import all toolkit modules."""
        names = [
            "token_data", "economy", "vault", "detector",
            "atlas_graph_core", "store", "history", "whale_tracker",
            "scenario", "alert", "live_data", "validate",
            "github_sync", "smart_integrations",
        ]
        for name in names:
            mod, _ = _try_import(name)
            if mod is not None:
                self._modules[name] = mod

    # ── Data collection ───────────────────────────────────────────────────────

    def get_dashboard_data(self):
        """Collect data from ALL modules into one JSON-serialisable payload."""
        data = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "contract":  "0x05c870C5C6E7AF4298976886471c69Fc722107e4",
        }

        # Market data
        data["market"]  = self._market_data()
        # Economy
        data["economy"] = self._economy_data()
        # Vault
        data["vault"]   = self._vault_data()
        # Whale tracker + Gini
        data["whale"]   = self._whale_data()
        # Risk score + alerts
        data["risk"]    = self._risk_data()
        data["alerts"]  = self._alerts_data()
        # Scenario results
        data["scenario"] = self._scenario_data()
        # Sentiment / intelligence
        data["sentiment"] = self._sentiment_data()
        # System health
        health, loaded, total = self._health_data()
        data["health"]                 = health
        data["system_modules_loaded"]  = loaded
        data["system_modules_total"]   = total
        # Sync status
        data["sync"]    = self._sync_data()
        # Ledger / history
        data["ledger"]  = self._ledger_data()
        # Store stats
        data["store"]   = self._store_data()
        # Recommendations
        data["recommendations"] = self._recommendations(data)

        return data

    # ── Per-module data helpers ───────────────────────────────────────────────

    def _market_data(self):
        ld = self._modules.get("live_data")
        if not ld:
            return {}
        try:
            return ld.get_data(force_refresh=False) or {}
        except Exception:
            return {}

    def _economy_data(self):
        ec = self._modules.get("economy")
        if not ec:
            return {}
        try:
            return {
                "supply":  getattr(ec, "supply",  1_000_000_000),
                "circ":    getattr(ec, "circ",    100_000_000),
                "cap":     getattr(ec, "cap",       50_000),
                "emitted": getattr(ec, "emitted",       0),
                "burned":  getattr(ec, "burned",        0),
                "locked":  getattr(ec, "locked",        0),
                "spent":   getattr(ec, "spent",         0),
                "today":   getattr(ec, "today",         0),
            }
        except Exception:
            return {}

    def _vault_data(self):
        vt = self._modules.get("vault")
        if not vt:
            return {}
        try:
            return {
                "balance": getattr(vt, "vault_balance", 0),
                "locked":  getattr(vt, "total_locked",  0),
                "lockers": getattr(vt, "lockers",       []),
                "apy":     vt.vault_apy() if hasattr(vt, "vault_apy") else 0,
            }
        except Exception:
            return {}

    def _whale_data(self):
        wt = self._modules.get("whale_tracker")
        if not wt:
            return {}
        try:
            wallets = wt.load_wallets() if hasattr(wt, "load_wallets") else []
            top     = wt.top_holders(1) if hasattr(wt, "top_holders") else []
            gini_v, gini_l = (wt.gini_coefficient()
                              if hasattr(wt, "gini_coefficient") else (0, "N/A"))
            circ, _ = (wt.get_supply() if hasattr(wt, "get_supply") else (1, 1))
            effective = max(circ, sum(w.get("balance", 0) for w in wallets)) or 1
            top_pct   = (top[0]["balance"] / effective * 100) if top else 0
            return {
                "total_wallets":   len(wallets),
                "gini":            gini_v,
                "gini_label":      gini_l,
                "top_holder_pct":  top_pct,
                "top_holder_id":   top[0]["wallet_id"] if top else "N/A",
            }
        except Exception:
            return {}

    def _risk_data(self):
        al = self._modules.get("alert")
        if not al:
            return {}
        try:
            score, interp = (al.risk_score()
                             if hasattr(al, "risk_score") else (0, "N/A"))
            counts = (al.count_by_severity()
                      if hasattr(al, "count_by_severity") else {})
            active = al.get_active() if hasattr(al, "get_active") else []
            return {
                "score":    score,
                "interp":   interp,
                "active":   len(active),
                "critical": counts.get("critical", 0),
                "danger":   counts.get("danger",   0),
                "warning":  counts.get("warning",  0),
            }
        except Exception:
            return {}

    def _alerts_data(self):
        al = self._modules.get("alert")
        if not al:
            return []
        try:
            return al.get_active() if hasattr(al, "get_active") else []
        except Exception:
            return []

    def _scenario_data(self):
        sc = self._modules.get("scenario")
        if not sc:
            return {}
        try:
            results = {}
            for name in ("baseline", "utopia", "death_spiral"):
                preset = (sc.get_scenario(name)
                          if hasattr(sc, "get_scenario") else None)
                if preset is None:
                    continue
                r = sc.run_scenario(preset) if hasattr(sc, "run_scenario") else {}
                results[name] = r.get("summary", r)
            return results
        except Exception:
            return {}

    def _sentiment_data(self):
        si = self._modules.get("smart_integrations")
        if not si:
            return {}
        try:
            if hasattr(si, "sentiment_report"):
                return si.sentiment_report()
            return {}
        except Exception:
            return {}

    def _health_data(self):
        vl = self._modules.get("validate")
        loaded = len(self._modules)
        total  = 14  # known module count
        if not vl:
            return {"status": "validate module not loaded"}, loaded, total
        try:
            report = (vl.run_validation()
                      if hasattr(vl, "run_validation") else {})
            return report, loaded, total
        except Exception:
            return {}, loaded, total

    def _sync_data(self):
        gs = self._modules.get("github_sync")
        if not gs:
            return {}
        try:
            last = gs.last_sync_time() if hasattr(gs, "last_sync_time") else None
            return {
                "last_sync": last,
                "status":    "synced" if last else "never synced",
            }
        except Exception:
            return {}

    def _ledger_data(self):
        hi = self._modules.get("history")
        if not hi:
            return {}
        try:
            events = hi.load_events() if hasattr(hi, "load_events") else []
            return {"count": len(events), "recent": events[-5:] if events else []}
        except Exception:
            return {}

    def _store_data(self):
        st = self._modules.get("store")
        if not st:
            return {}
        try:
            items = st.load_catalog() if hasattr(st, "load_catalog") else []
            return {
                "total_items": len(items),
                "item_count":  len(items),
            }
        except Exception:
            return {}

    def _recommendations(self, data):
        """Generate simple recommendations from the collected data."""
        recs = []
        risk = data.get("risk", {})
        eco  = data.get("economy", {})
        mkt  = data.get("market", {})
        sent = data.get("sentiment", {})

        score = risk.get("score", 0)
        if score < 30:
            recs.append("Risk score is low — system operating normally.")
        elif score < 60:
            recs.append(f"Moderate risk (score {score}) — review active alerts.")
        else:
            recs.append(f"⚠️ High risk score ({score}) — immediate review required.")

        vol = mkt.get("volume_24h", 0)
        if vol and vol < 1000:
            recs.append("Volume is low — consider a marketing push or community event.")

        burned = eco.get("burned", 0)
        emitted = eco.get("emitted", 1) or 1
        if burned / emitted > 0.05:
            recs.append("Burn rate healthy — deflation mechanism active.")
        else:
            recs.append("Burn rate low — review economy parameters.")

        comb = (sent.get("combined") or {}).get("score", 0)
        if comb > 0.3:
            recs.append("Sentiment is BULLISH — good time for community engagement.")
        elif comb < -0.3:
            recs.append("Sentiment is BEARISH — monitor closely, prepare comms.")

        recs.append("Run scenario.py before any parameter changes.")
        return recs

    # ── HTTP server ───────────────────────────────────────────────────────────

    def _make_handler(self):
        """Return a request handler class bound to this DashboardServer instance."""
        server_ref = self

        from http.server import BaseHTTPRequestHandler

        class _Handler(BaseHTTPRequestHandler):

            def log_message(self, fmt, *args):  # silence default access log
                pass

            def _send_json(self, payload, status=200):
                body = json.dumps(payload, default=str).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type",  "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin",  "*")
                self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                self.wfile.write(body)

            def _send_html(self, body_bytes, status=200):
                self.send_response(status)
                self.send_header("Content-Type",  "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body_bytes)))
                self.end_headers()
                self.wfile.write(body_bytes)

            def do_OPTIONS(self):
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin",  "*")
                self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
                self.end_headers()

            def do_GET(self):
                path = self.path.split("?")[0].rstrip("/") or "/"

                if path == "/":
                    # Serve HTML dashboard
                    tmpl = server_ref._TEMPLATE
                    if os.path.isfile(tmpl):
                        with open(tmpl, "rb") as fh:
                            self._send_html(fh.read())
                    else:
                        self._send_html(b"<h1>Dashboard template not found</h1>", 404)

                elif path == "/api/data":
                    self._send_json(server_ref.get_dashboard_data())

                elif path == "/api/market":
                    self._send_json(server_ref._market_data())

                elif path == "/api/economy":
                    self._send_json(server_ref._economy_data())

                elif path == "/api/risk":
                    d = server_ref._risk_data()
                    d["alerts"] = server_ref._alerts_data()
                    self._send_json(d)

                elif path == "/api/whale":
                    self._send_json(server_ref._whale_data())

                elif path == "/api/sentiment":
                    self._send_json(server_ref._sentiment_data())

                elif path == "/api/health":
                    h, loaded, total = server_ref._health_data()
                    h["modules_loaded"] = loaded
                    h["modules_total"]  = total
                    self._send_json(h)

                else:
                    self._send_json({"error": "not found", "path": path}, 404)

        return _Handler

    # ── Start / stop ──────────────────────────────────────────────────────────

    def start(self):
        """Start the dashboard server in a background thread."""
        if self._running:
            print(f"  ⚠️  Dashboard already running at http://{self.host}:{self.port}/")
            return

        from http.server import HTTPServer
        handler = self._make_handler()
        try:
            self._server  = HTTPServer((self.host, self.port), handler)
            self._running = True
            self._thread  = threading.Thread(
                target=self._server.serve_forever,
                daemon=True,
                name="DashboardServer",
            )
            self._thread.start()
            display_host = "localhost" if self.host in ("0.0.0.0", "") else self.host
            print(f"\n  🌐 PCVR Dashboard running at http://{display_host}:{self.port}/")
            print(f"  📡 API endpoint : http://{display_host}:{self.port}/api/data")
            print(f"  🛑 Stop with    : dashboard.stop()\n")
        except OSError as exc:
            self._running = False
            print(f"  ❌ Could not start dashboard: {exc}")

    def stop(self):
        """Gracefully shut down the server."""
        if not self._running:
            print("  ℹ️  Dashboard is not running.")
            return
        self._running = False
        if self._server:
            self._server.shutdown()
            self._server = None
        print("  🛑 Dashboard server stopped.")

    @property
    def running(self):
        return self._running

    def status(self):
        """Print current server status."""
        if self._running:
            display_host = "localhost" if self.host in ("0.0.0.0", "") else self.host
            print(f"  🟢 Dashboard running → http://{display_host}:{self.port}/")
        else:
            print("  🔴 Dashboard not running")

    def open_browser(self):
        """Try to open the dashboard in the default browser."""
        import webbrowser
        url = f"http://localhost:{self.port}/"
        try:
            webbrowser.open(url)
            print(f"  🌐 Opening {url}")
        except Exception:
            print(f"  ℹ️  Open manually: {url}")

    def preview_data(self):
        """Print a JSON preview of the current dashboard data."""
        data = self.get_dashboard_data()
        print(json.dumps(data, indent=2, default=str))


# ─── Interactive CLI ──────────────────────────────────────────────────────────

def _print_dashboard_menu():
    W = 50
    print("╔" + "═" * W + "╗")
    print("║" + "📊 PCVR DASHBOARD SERVER".center(W) + "║")
    print("║" + "V10 Phase 2 — Visual Command Center".center(W) + "║")
    print("╠" + "═" * W + "╣")
    cmds = [
        ("1. start",  "start dashboard server"),
        ("2. stop",   "stop server"),
        ("3. status", "server status"),
        ("4. open",   "open in browser"),
        ("5. port",   "change port"),
        ("6. data",   "preview JSON data"),
        ("7. exit",   ""),
    ]
    print("║" + " Commands:".ljust(W) + "║")
    for cmd, desc in cmds:
        line = f"  {cmd:<10}" + (f" → {desc}" if desc else "")
        print("║" + line.ljust(W) + "║")
    print("╚" + "═" * W + "╝")


def _run_dashboard_cli(server):
    _print_dashboard_menu()
    while True:
        try:
            raw = input("\ndashboard> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Dashboard CLI shutting down.")
            if server.running:
                server.stop()
            break

        if not raw:
            continue

        aliases = {
            "1": "start", "2": "stop", "3": "status",
            "4": "open",  "5": "port", "6": "data", "7": "exit",
        }
        cmd = aliases.get(raw, raw)

        if cmd == "start":
            server.start()
        elif cmd == "stop":
            server.stop()
        elif cmd == "status":
            server.status()
        elif cmd == "open":
            server.open_browser()
        elif cmd == "port":
            try:
                new_port = int(input("  New port [8080]: ").strip() or 8080)
                if server.running:
                    print("  ⚠️  Stop the server first before changing port.")
                else:
                    server.port = new_port
                    print(f"  ✅ Port set to {new_port}")
            except (ValueError, EOFError):
                print("  ❌ Invalid port number.")
        elif cmd == "data":
            server.preview_data()
        elif cmd in ("exit", "quit", "q"):
            print("👋 Dashboard CLI shutting down.")
            if server.running:
                server.stop()
            break
        elif cmd == "help":
            _print_dashboard_menu()
        else:
            print(f"  ❓ Unknown command: '{raw}'.  Type 'help' for the menu.")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  PCVR Dashboard Server v1.0 — V10 Phase 2")
    print("  © PCVR Studios 2025")
    print("  Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4")
    print("  V10 Dashboard — See everything. Control everything. From any browser.\n")

    _server = DashboardServer()
    _run_dashboard_cli(_server)
