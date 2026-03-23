# ============================================================
# PCVR Studios — wkapp_ui.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# V10 Pythonista UI — Native iOS. One tap. Total control.
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# WKApp Pythonista UI — wraps the existing dashboard using
# the WKApp framework pattern from M4nw3l/pythonista-wkapp.
# Falls back gracefully if not running in Pythonista.
# ============================================================

import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Detect Pythonista environment ─────────────────────────────────────────────

def _is_pythonista():
    """Return True if running inside Pythonista 3 on iOS."""
    try:
        import console  # noqa: F401 — Pythonista-only module
        return True
    except ImportError:
        return False


_PYTHONISTA = _is_pythonista()

# ── Graceful module imports ───────────────────────────────────────────────────

def _try_import(name):
    """Import a module from project_dont_die, return (module, None) or (None, err)."""
    if _DIR not in sys.path:
        sys.path.insert(0, _DIR)
    try:
        import importlib
        mod = importlib.import_module(name)
        return mod, None
    except Exception as exc:
        return None, str(exc)


def _mod(name):
    """Return module or None."""
    mod, _ = _try_import(name)
    return mod


# ── PCVRToolbar ───────────────────────────────────────────────────────────────

class PCVRToolbar:
    """
    Native iOS toolbar with quick-action buttons.
    Renders as native ui.View in Pythonista, or prints a text menu otherwise.
    Buttons: 🌐 Dashboard | 🚨 Risk | 📊 Market | 🐋 Whale | 🤖 Auto | ⚙️ Settings
    """

    BUTTONS = [
        ("🌐", "Dashboard", "dashboard"),
        ("🚨", "Risk",      "risk"),
        ("📊", "Market",    "market"),
        ("🐋", "Whale",     "whale"),
        ("🤖", "Auto",      "auto"),
        ("⚙️", "Settings",  "settings"),
    ]

    def __init__(self, app_ref=None):
        self.app = app_ref
        self._view = None

    def _on_tap(self, action):
        """Handle toolbar button tap."""
        omega = _mod("atlas_omega")
        if omega:
            engine = omega.OmegaEngine()
        else:
            engine = None

        if action == "dashboard":
            self._open_dashboard()
        elif action == "risk":
            if engine:
                engine.quick_risk()
            else:
                print("  🚨 Risk module not available.")
        elif action == "market":
            if engine:
                engine.quick_market()
            else:
                print("  📊 Market module not available.")
        elif action == "whale":
            if engine:
                engine.quick_whale()
            else:
                print("  🐋 Whale module not available.")
        elif action == "auto":
            auto_mod = _mod("automation")
            if auto_mod:
                ae = auto_mod.AutomationEngine()
                print(f"  🤖 Automation: {ae.status_summary()}")
            else:
                print("  🤖 Automation module not available.")
        elif action == "settings":
            print("  ⚙️  Settings: run atlas_omega.py for full configuration.")

    def _open_dashboard(self):
        """Open the visual dashboard."""
        dash = _mod("dashboard")
        if dash:
            try:
                ds = dash.DashboardServer()
                ds.start()
                import webbrowser
                webbrowser.open("http://localhost:8080")
                print("  🌐 Dashboard opened at http://localhost:8080")
            except Exception as exc:
                print(f"  ❌ Dashboard error: {exc}")
        else:
            print("  ⚠️  dashboard module not available — run dashboard.py directly.")

    def build_native(self):
        """Build a Pythonista native ui.View toolbar. Returns the view."""
        if not _PYTHONISTA:
            return None
        try:
            import ui  # noqa: F401
            toolbar = ui.View()
            toolbar.name        = "PCVR Toolbar"
            toolbar.frame       = (0, 0, 375, 50)
            toolbar.background_color = "#1a1a2e"

            btn_width = 375 // len(self.BUTTONS)
            for i, (emoji, label, action) in enumerate(self.BUTTONS):
                btn = ui.Button()
                btn.frame           = (i * btn_width, 0, btn_width, 50)
                btn.title           = f"{emoji}\n{label}"
                btn.tint_color      = "#00d4aa"
                btn.font            = ("<system>", 9)
                btn.background_color = "#1a1a2e"

                # Capture action in closure
                def _make_handler(act):
                    def _handler(sender):
                        sender.background_color = "#00d4aa"
                        import time as _time
                        _time.sleep(0.1)
                        sender.background_color = "#1a1a2e"
                        self._on_tap(act)
                    return _handler

                btn.action = _make_handler(action)
                toolbar.add_subview(btn)

            self._view = toolbar
            return toolbar
        except Exception as exc:
            print(f"  ⚠️  Could not build native toolbar: {exc}")
            return None

    def print_text_menu(self):
        """Fallback text menu for non-Pythonista environments."""
        print("\n  ── PCVR Quick Actions ──")
        for emoji, label, action in self.BUTTONS:
            print(f"    {emoji}  {label}")
        print()


# ── PCVRQuickPanel ────────────────────────────────────────────────────────────

class PCVRQuickPanel:
    """
    Swipe-up panel showing quick_status() output.
    In Pythonista: native scrollable ui.View with pull-to-refresh feel.
    Elsewhere: prints quick status to console.
    """

    def __init__(self):
        self._view   = None
        self._label  = None

    def get_status_text(self):
        """Fetch current status text from atlas_omega."""
        omega = _mod("atlas_omega")
        if omega:
            try:
                engine = omega.OmegaEngine()
                # Capture print output
                import io
                old_stdout = sys.stdout
                sys.stdout = buf = io.StringIO()
                engine.quick_status()
                sys.stdout = old_stdout
                return buf.getvalue().strip()
            except Exception as exc:
                return f"Status unavailable: {exc}"
        return "Atlas Omega not available — run atlas_omega.py for full status."

    def refresh(self):
        """Reload status data and update display."""
        text = self.get_status_text()
        if self._label is not None:
            try:
                self._label.text = text
            except Exception:
                pass
        return text

    def build_native(self):
        """Build a Pythonista native scrollable panel. Returns the view."""
        if not _PYTHONISTA:
            return None
        try:
            import ui
            panel = ui.View()
            panel.name             = "PCVR Quick Panel"
            panel.frame            = (0, 0, 375, 200)
            panel.background_color = "#0d0d1a"

            label = ui.Label()
            label.frame            = (10, 10, 355, 180)
            label.text             = self.get_status_text()
            label.font             = ("<monospace>", 11)
            label.text_color       = "#00d4aa"
            label.number_of_lines  = 0
            label.alignment        = ui.ALIGN_LEFT
            panel.add_subview(label)

            self._label = label
            self._view  = panel
            return panel
        except Exception as exc:
            print(f"  ⚠️  Could not build native panel: {exc}")
            return None

    def show(self):
        """Show the quick panel (native or text)."""
        if _PYTHONISTA:
            view = self.build_native()
            if view:
                try:
                    import ui
                    view.present("sheet")
                    return
                except Exception:
                    pass
        # Fallback: print to console
        print("\n" + "=" * 52)
        print("  📊 PCVR QUICK STATUS")
        print("=" * 52)
        print(f"  {self.get_status_text()}")
        print("=" * 52 + "\n")


# ── PCVRApp ────────────────────────────────────────────────────────────────────

class PCVRApp:
    """
    Main PCVR Pythonista application.
    - In Pythonista: native iOS UI with WKWebView wrapping dashboard_template.html
    - Elsewhere: falls back to dashboard.py HTTP server with browser launch
    """

    def __init__(self):
        self.toolbar    = PCVRToolbar(app_ref=self)
        self.quick_panel = PCVRQuickPanel()
        self._main_view  = None

    # ── Notifications (Pythonista-specific) ──────────────────────────────────

    def notify(self, title, body, delay=1):
        """Schedule an iOS notification (Pythonista only)."""
        if _PYTHONISTA:
            try:
                import notification
                notification.schedule(body, title=title, delay=delay)
                print(f"  🔔 Notification scheduled: [{title}] {body}")
                return True
            except Exception as exc:
                print(f"  ⚠️  Notification failed: {exc}")
        else:
            print(f"  🔔 [NOTIFICATION] {title}: {body}")
        return False

    def alert_critical(self, message):
        """Show a native iOS alert dialog for critical notifications."""
        if _PYTHONISTA:
            try:
                import console
                console.alert("⚠️ PCVR Critical Alert", message, "OK",
                              hide_cancel_button=True)
                return True
            except Exception as exc:
                print(f"  ⚠️  Alert dialog failed: {exc}")
        print(f"\n  🚨 CRITICAL ALERT: {message}\n")
        return False

    def copy_to_clipboard(self, text):
        """Copy text to iOS clipboard."""
        if _PYTHONISTA:
            try:
                import clipboard
                clipboard.set(text)
                print(f"  📋 Copied to clipboard: {text[:40]}…" if len(text) > 40 else
                      f"  📋 Copied to clipboard: {text}")
                return True
            except Exception as exc:
                print(f"  ⚠️  Clipboard failed: {exc}")
        else:
            print(f"  📋 [CLIPBOARD] {text}")
        return False

    def play_alert_sound(self):
        """Play alert sound effect (Pythonista only)."""
        if _PYTHONISTA:
            try:
                import sound
                sound.play_effect("ui:Tink")
                return True
            except Exception:
                pass
        return False

    def open_url(self, url):
        """Open an external URL in the browser."""
        try:
            import webbrowser
            webbrowser.open(url)
            print(f"  🌐 Opening: {url}")
            return True
        except Exception as exc:
            print(f"  ❌ Could not open URL: {exc}")
            return False

    # ── Dashboard integration ────────────────────────────────────────────────

    def _get_template_path(self):
        """Return path to dashboard_template.html."""
        return os.path.join(_DIR, "dashboard_template.html")

    def launch_webview(self):
        """
        Launch dashboard in WKWebView (Pythonista) or HTTP server (fallback).
        """
        if _PYTHONISTA:
            template = self._get_template_path()
            if os.path.exists(template):
                try:
                    import ui
                    wv = ui.WebView()
                    wv.name            = "PCVR Dashboard"
                    wv.frame           = (0, 0, 375, 667)
                    with open(template, "r") as fh:
                        html_content = fh.read()
                    wv.load_html(html_content, base_url="")
                    wv.present("fullscreen")
                    print("  🌐 Dashboard opened in WKWebView (Pythonista native).")
                    return True
                except Exception as exc:
                    print(f"  ⚠️  WKWebView failed: {exc}")
            else:
                print("  ⚠️  dashboard_template.html not found — run dashboard.py first.")

        # Fallback: use HTTP server
        return self._launch_http_server()

    def _launch_http_server(self):
        """Start the dashboard HTTP server and open browser."""
        dash = _mod("dashboard")
        if dash:
            try:
                ds = dash.DashboardServer()
                ds.start()
                import webbrowser
                webbrowser.open("http://localhost:8080")
                print("  🌐 Dashboard started at http://localhost:8080")
                print("  Press Ctrl-C or call ds.stop() to stop the server.")
                return True
            except Exception as exc:
                print(f"  ❌ Dashboard server error: {exc}")
        else:
            print("  ⚠️  dashboard module not available — run dashboard.py directly.")
        return False

    # ── Main launch ──────────────────────────────────────────────────────────

    def launch(self):
        """Launch the full PCVR iOS application."""
        if _PYTHONISTA:
            self._launch_native()
        else:
            print(
                "\n  ℹ️  Full native UI requires Pythonista 3 on iOS.\n"
                "     Falling back to dashboard.py HTTP server.\n"
                "     Install Pythonista 3 from the App Store for native iOS UI.\n"
            )
            self._launch_http_server()

    def _launch_native(self):
        """Build and present the full native Pythonista UI."""
        try:
            import ui

            # Root view
            root = ui.View()
            root.name             = "PCVR Studios"
            root.frame            = (0, 0, 375, 667)
            root.background_color = "#0d0d1a"

            # Title label
            title = ui.Label()
            title.frame      = (0, 20, 375, 44)
            title.text       = "🌐 PCVR STUDIOS"
            title.font       = ("<system-bold>", 18)
            title.text_color = "#00d4aa"
            title.alignment  = ui.ALIGN_CENTER
            root.add_subview(title)

            # Quick panel (status)
            panel = self.quick_panel.build_native()
            if panel:
                panel.frame = (0, 70, 375, 200)
                root.add_subview(panel)

            # Toolbar at bottom
            toolbar = self.toolbar.build_native()
            if toolbar:
                toolbar.frame = (0, 617, 375, 50)
                root.add_subview(toolbar)

            self._main_view = root
            root.present("fullscreen")
            print("  📱 PCVR native iOS UI launched.")

        except Exception as exc:
            print(f"  ❌ Native UI launch failed: {exc}")
            print("     Falling back to HTTP server mode.")
            self._launch_http_server()

    def dashboard_only(self):
        """Open dashboard only (without full app shell)."""
        self.launch_webview()

    def quick_status(self):
        """Show quick status panel."""
        self.quick_panel.show()


# ── Interactive CLI ───────────────────────────────────────────────────────────

def _print_menu():
    print("""
==================================
📱 PCVR PYTHONISTA UI
==================================
Commands:
 1. launch     → launch full UI
 2. dashboard  → open dashboard only
 3. quick      → quick status panel
 4. notify     → test notification
 5. exit
==================================
""")
    if not _PYTHONISTA:
        print("  ℹ️  Pythonista 3 not detected.")
        print("     Commands will use fallback (HTTP server / console output).")
        print()


def _run_cli(app):
    _print_menu()
    while True:
        try:
            raw = input("\nwkapp_ui> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 PCVR UI shutting down.")
            break

        if not raw:
            continue

        aliases = {
            "1": "launch", "2": "dashboard", "3": "quick",
            "4": "notify",  "5": "exit",
        }
        cmd = aliases.get(raw, raw)

        if cmd == "launch":
            app.launch()

        elif cmd == "dashboard":
            app.dashboard_only()

        elif cmd == "quick":
            app.quick_status()

        elif cmd == "notify":
            title = input("  Notification title [PCVR Alert]: ").strip() or "PCVR Alert"
            body  = input("  Message body: ").strip() or "Test notification from PCVR Studios."
            app.notify(title, body)

        elif cmd in ("exit", "quit", "q", "5"):
            print("  👋 Bye.")
            break

        elif cmd == "help":
            _print_menu()

        else:
            print(f"  ❓ Unknown command: '{raw}'.  Type 'help' for the menu.\n")


if __name__ == "__main__":
    print("\n  © PCVR Studios 2026")
    print("  Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4")
    print("  V10 Pythonista UI — Native iOS. One tap. Total control.\n")
    _app = PCVRApp()
    _run_cli(_app)
