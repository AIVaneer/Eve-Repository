# ============================================================
# PCVR Studios — github_sync.py
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# "Earn → Hold → Spend → Buy → Earn.
#  If any link breaks, the token dies."
#
# PCVR GitHub Auto-Sync Engine
# Code on the phone. Push to the cloud. Never lose a line.
# ============================================================

import json
import os
import datetime
import base64
import hashlib

# ── optional requests import ──────────────────────────────
try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# ── optional toolkit integrations ─────────────────────────
try:
    import history as _history
    _HISTORY_AVAILABLE = True
except Exception:
    _HISTORY_AVAILABLE = False

try:
    import alert as _alert
    _ALERT_AVAILABLE = True
except Exception:
    _ALERT_AVAILABLE = False

# ──────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────

GITHUB_OWNER  = "AIVaneer"
GITHUB_REPO   = "Eve-Repository"
GITHUB_BRANCH = "main"
GITHUB_API    = "https://api.github.com"

_DIR       = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(_DIR, "github_token.txt")
SYNC_DIR   = _DIR                                         # project_dont_die/
SYNC_LOG   = os.path.join(_DIR, "pcvr_sync_log.json")

# Files and patterns that must never be pushed
_SKIP_FILES = {
    "github_token.txt",
    "pcvr_sync_log.json",
}
_SKIP_SUFFIXES = (".pyc", ".bak")
_SKIP_DIRS    = {"__pycache__"}

# ──────────────────────────────────────────────────────────
# AUTHENTICATION
# ──────────────────────────────────────────────────────────

def load_token():
    """Load GitHub PAT from TOKEN_FILE. Returns token string or None."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as fh:
                tok = fh.read().strip()
            return tok if tok else None
        except IOError:
            return None
    return None


def save_token(token):
    """Save GitHub PAT to TOKEN_FILE."""
    with open(TOKEN_FILE, "w") as fh:
        fh.write(token.strip())
    print(f"  ✅ Token saved to {TOKEN_FILE}")


def get_headers():
    """Return auth headers dict for GitHub API calls."""
    tok = load_token()
    if not tok:
        return {"Accept": "application/vnd.github+json"}
    return {
        "Authorization": f"token {tok}",
        "Accept": "application/vnd.github+json",
    }


def _validate_token(token):
    """Test a token against the GitHub API. Returns (ok, message)."""
    if not _REQUESTS_AVAILABLE:
        return False, "requests library not available"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    try:
        resp = requests.get(f"{GITHUB_API}/user", headers=headers, timeout=10)
        if resp.status_code == 200:
            username = resp.json().get("login", "unknown")
            return True, f"Authenticated as {username}"
        return False, f"HTTP {resp.status_code}: {resp.json().get('message', 'unknown error')}"
    except Exception as exc:
        return False, str(exc)


def setup_auth():
    """Interactive: prompt for GitHub PAT, validate, and save if valid."""
    print("\n── GitHub Token Setup ────────────────────────────────")
    print("  Enter your GitHub Personal Access Token.")
    print("  Create one at: https://github.com/settings/tokens")
    print("  Required scopes: repo (full)")
    tok = input("  Token: ").strip()
    if not tok:
        print("  ❌ No token entered.")
        return False
    ok, msg = _validate_token(tok)
    if ok:
        save_token(tok)
        print(f"  ✅ {msg}")
        return True
    print(f"  ❌ Token validation failed: {msg}")
    return False


# ──────────────────────────────────────────────────────────
# GITHUB FILE OPERATIONS
# ──────────────────────────────────────────────────────────

def _remote_path(filename):
    """Build the remote path for a filename inside project_dont_die/."""
    return f"project_dont_die/{filename}"


def list_remote_files():
    """
    GET /repos/{owner}/{repo}/contents/project_dont_die/
    Returns list of dicts with keys: name, sha, size, download_url.
    """
    if not _REQUESTS_AVAILABLE:
        print("  ❌ requests not available — cannot contact GitHub API")
        return []
    url = (f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
           f"/contents/project_dont_die?ref={GITHUB_BRANCH}")
    resp = requests.get(url, headers=get_headers(), timeout=15)
    if resp.status_code == 200:
        return resp.json()
    print(f"  ❌ list_remote_files failed: HTTP {resp.status_code}")
    return []


def get_remote_file(filename):
    """
    GET file content + sha from GitHub.
    Returns (content_str, sha) or (None, None) on failure.
    """
    if not _REQUESTS_AVAILABLE:
        return None, None
    url = (f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
           f"/contents/{_remote_path(filename)}?ref={GITHUB_BRANCH}")
    resp = requests.get(url, headers=get_headers(), timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content, data["sha"]
    return None, None


def push_file(filename, content, message=None):
    """
    PUT to create or update a file on GitHub.
    content : str — file text content
    Returns (ok, commit_sha_or_error)
    """
    if not _REQUESTS_AVAILABLE:
        return False, "requests not available"
    if message is None:
        message = f"sync: update {filename} from Pythonista"

    # Check if the file exists to get its sha
    _, existing_sha = get_remote_file(filename)

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": message,
        "content": encoded,
        "branch":  GITHUB_BRANCH,
    }
    if existing_sha:
        payload["sha"] = existing_sha

    url = (f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
           f"/contents/{_remote_path(filename)}")
    resp = requests.put(url, headers=get_headers(),
                        data=json.dumps(payload), timeout=20)
    if resp.status_code in (200, 201):
        commit_sha = resp.json().get("commit", {}).get("sha", "")
        return True, commit_sha
    return False, f"HTTP {resp.status_code}: {resp.json().get('message', '')}"


def delete_remote_file(filename, message=None):
    """
    DELETE a file from GitHub.
    Returns (ok, message_str)
    """
    if not _REQUESTS_AVAILABLE:
        return False, "requests not available"
    if message is None:
        message = f"sync: delete {filename} via Pythonista"

    _, existing_sha = get_remote_file(filename)
    if not existing_sha:
        return False, f"{filename} not found on remote"

    payload = {
        "message": message,
        "sha":     existing_sha,
        "branch":  GITHUB_BRANCH,
    }
    url = (f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
           f"/contents/{_remote_path(filename)}")
    resp = requests.delete(url, headers=get_headers(),
                           data=json.dumps(payload), timeout=20)
    if resp.status_code == 200:
        return True, "deleted"
    return False, f"HTTP {resp.status_code}: {resp.json().get('message', '')}"


# ──────────────────────────────────────────────────────────
# SYNC ENGINE
# ──────────────────────────────────────────────────────────

def _should_skip(filename):
    """Return True if this filename should never be synced."""
    if filename in _SKIP_FILES:
        return True
    for suf in _SKIP_SUFFIXES:
        if filename.endswith(suf):
            return True
    return False


def local_files():
    """List all .py files in SYNC_DIR (excluding skip list)."""
    result = []
    for entry in os.listdir(SYNC_DIR):
        if not entry.endswith(".py"):
            continue
        if _should_skip(entry):
            continue
        if os.path.isfile(os.path.join(SYNC_DIR, entry)):
            result.append(entry)
    return sorted(result)


def remote_files():
    """List all .py files on GitHub (as {name: sha} dict)."""
    items = list_remote_files()
    return {
        item["name"]: item["sha"]
        for item in items
        if item.get("type") == "file"
        and item["name"].endswith(".py")
        and not _should_skip(item["name"])
    }


def file_hash(filepath):
    """SHA256 hash of local file content."""
    h = hashlib.sha256()
    with open(filepath, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def compare():
    """
    Compare local vs remote files.

    Returns dict with keys:
        local_only   : [filename, ...]   — needs push
        remote_only  : [filename, ...]   — needs pull
        modified     : [filename, ...]   — on both, content differs
        in_sync      : [filename, ...]   — on both, identical
    """
    local  = set(local_files())
    remote = remote_files()  # {name: github_sha}

    local_only  = sorted(local - set(remote))
    remote_only = sorted(set(remote) - local)

    modified = []
    in_sync  = []

    for fname in sorted(local & set(remote)):
        local_path = os.path.join(SYNC_DIR, fname)
        remote_content, _ = get_remote_file(fname)
        if remote_content is None:
            modified.append(fname)
            continue
        with open(local_path, "r", encoding="utf-8") as fh:
            local_content = fh.read()
        if local_content == remote_content:
            in_sync.append(fname)
        else:
            modified.append(fname)

    return {
        "local_only":  local_only,
        "remote_only": remote_only,
        "modified":    modified,
        "in_sync":     in_sync,
    }


def sync_report():
    """Print a visual comparison of local vs remote files."""
    if not _REQUESTS_AVAILABLE:
        print("  ❌ requests not available — cannot contact GitHub")
        return

    tok = load_token()
    if not tok:
        print("  ⚠️  No GitHub token — run 'setup' first")

    print("\n── PCVR Sync Status ──────────────────────────────────")
    result = compare()

    for f in result["in_sync"]:
        print(f"  ✅ {f}")
    for f in result["local_only"]:
        print(f"  📤 {f}  (local only — needs push)")
    for f in result["remote_only"]:
        print(f"  📥 {f}  (remote only — needs pull)")
    for f in result["modified"]:
        print(f"  ⚠️  {f}  (modified — needs resolution)")

    total = (len(result["in_sync"]) + len(result["local_only"])
             + len(result["remote_only"]) + len(result["modified"]))
    print(f"\n  {total} files checked  |  "
          f"{len(result['in_sync'])} in sync  |  "
          f"{len(result['local_only'])} to push  |  "
          f"{len(result['remote_only'])} to pull  |  "
          f"{len(result['modified'])} conflicts")


# ──────────────────────────────────────────────────────────
# PUSH & PULL
# ──────────────────────────────────────────────────────────

def push_all():
    """Push all local files that are new or modified to GitHub."""
    if not _REQUESTS_AVAILABLE:
        print("  ❌ requests not available")
        return

    tok = load_token()
    if not tok:
        print("  ⚠️  No GitHub token — run 'setup' first")
        return

    result = compare()
    to_push = result["local_only"] + result["modified"]

    if not to_push:
        print("  ✅ Nothing to push — already in sync")
        return

    for fname in to_push:
        print(f"  📤 Pushing {fname}...")
        local_path = os.path.join(SYNC_DIR, fname)
        try:
            with open(local_path, "r", encoding="utf-8") as fh:
                content = fh.read()
            ok, commit_sha = push_file(fname, content)
            if ok:
                print(f"     ✅ {fname} pushed (commit {commit_sha[:7]})")
                log_sync("push", fname, "success", commit_sha)
            else:
                print(f"     ❌ {fname} failed: {commit_sha}")
                log_sync("push", fname, "fail")
        except Exception as exc:
            print(f"     ❌ {fname} error: {exc}")
            log_sync("push", fname, "fail")


def pull_all():
    """Pull all remote files that are new or modified to local."""
    if not _REQUESTS_AVAILABLE:
        print("  ❌ requests not available")
        return

    tok = load_token()
    if not tok:
        print("  ⚠️  No GitHub token — run 'setup' first")
        return

    result = compare()
    to_pull = result["remote_only"] + result["modified"]

    if not to_pull:
        print("  ✅ Nothing to pull — already in sync")
        return

    for fname in to_pull:
        print(f"  📥 Pulling {fname}...")
        local_path = os.path.join(SYNC_DIR, fname)
        try:
            content, _ = get_remote_file(fname)
            if content is None:
                print(f"     ❌ {fname} — could not retrieve from GitHub")
                log_sync("pull", fname, "fail")
                continue
            # Backup local if it exists
            if os.path.exists(local_path):
                bak = local_path + ".bak"
                with open(local_path, "r", encoding="utf-8") as src:
                    orig = src.read()
                with open(bak, "w", encoding="utf-8") as dst:
                    dst.write(orig)
                print(f"     💾 Backup saved as {os.path.basename(bak)}")
            with open(local_path, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(f"     ✅ {fname} pulled")
            log_sync("pull", fname, "success")
        except Exception as exc:
            print(f"     ❌ {fname} error: {exc}")
            log_sync("pull", fname, "fail")


def push_file_interactive(filename):
    """Push a single file with confirmation."""
    if not _REQUESTS_AVAILABLE:
        print("  ❌ requests not available")
        return
    if _should_skip(filename):
        print(f"  ⛔ {filename} is on the skip list — not pushed")
        return
    local_path = os.path.join(SYNC_DIR, filename)
    if not os.path.exists(local_path):
        print(f"  ❌ {filename} not found locally")
        return
    confirm = input(f"  Push {filename} to GitHub? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return
    print(f"  📤 Pushing {filename}...")
    try:
        with open(local_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        ok, commit_sha = push_file(filename, content)
        if ok:
            print(f"  ✅ {filename} pushed (commit {commit_sha[:7]})")
            log_sync("push", filename, "success", commit_sha)
        else:
            print(f"  ❌ Push failed: {commit_sha}")
            log_sync("push", filename, "fail")
    except Exception as exc:
        print(f"  ❌ Error: {exc}")
        log_sync("push", filename, "fail")


def pull_file_interactive(filename):
    """Pull a single file with confirmation."""
    if not _REQUESTS_AVAILABLE:
        print("  ❌ requests not available")
        return
    content, sha = get_remote_file(filename)
    if content is None:
        print(f"  ❌ {filename} not found on remote")
        return
    local_path = os.path.join(SYNC_DIR, filename)
    confirm = input(f"  Pull {filename} from GitHub? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return
    try:
        if os.path.exists(local_path):
            bak = local_path + ".bak"
            with open(local_path, "r", encoding="utf-8") as src:
                orig = src.read()
            with open(bak, "w", encoding="utf-8") as dst:
                dst.write(orig)
            print(f"  💾 Backup saved as {os.path.basename(bak)}")
        with open(local_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"  ✅ {filename} pulled")
        log_sync("pull", filename, "success", sha)
    except Exception as exc:
        print(f"  ❌ Error: {exc}")
        log_sync("pull", filename, "fail")


def full_sync():
    """
    Smart sync:
    - Push local-only files
    - Pull remote-only files
    - For modified files: ask user which version to keep
    """
    if not _REQUESTS_AVAILABLE:
        print("  ❌ requests not available")
        return

    tok = load_token()
    if not tok:
        print("  ⚠️  No GitHub token — run 'setup' first")
        return

    print("\n── Full Smart Sync ───────────────────────────────────")
    result = compare()

    # Push local-only
    for fname in result["local_only"]:
        print(f"\n  📤 Local-only: {fname}")
        confirm = input(f"     Push to GitHub? (y/n): ").strip().lower()
        if confirm == "y":
            local_path = os.path.join(SYNC_DIR, fname)
            with open(local_path, "r", encoding="utf-8") as fh:
                content = fh.read()
            ok, commit_sha = push_file(fname, content)
            if ok:
                print(f"     ✅ Pushed (commit {commit_sha[:7]})")
                log_sync("push", fname, "success", commit_sha)
            else:
                print(f"     ❌ Failed: {commit_sha}")
                log_sync("push", fname, "fail")

    # Pull remote-only
    for fname in result["remote_only"]:
        print(f"\n  📥 Remote-only: {fname}")
        confirm = input(f"     Pull to local? (y/n): ").strip().lower()
        if confirm == "y":
            content, sha = get_remote_file(fname)
            local_path = os.path.join(SYNC_DIR, fname)
            with open(local_path, "w", encoding="utf-8") as fh:
                fh.write(content)
            print(f"     ✅ Pulled")
            log_sync("pull", fname, "success", sha)

    # Handle modified — ask user
    for fname in result["modified"]:
        print(f"\n  ⚠️  Modified: {fname}")
        local_path = os.path.join(SYNC_DIR, fname)
        with open(local_path, "r", encoding="utf-8") as fh:
            local_content = fh.read()
        remote_content, sha = get_remote_file(fname)

        local_lines  = local_content.splitlines()
        remote_lines = (remote_content or "").splitlines()
        print(f"     Local:  {len(local_lines)} lines")
        print(f"     Remote: {len(remote_lines)} lines")

        choice = input("     Keep which? (l=local/r=remote/s=skip): ").strip().lower()
        if choice == "l":
            ok, commit_sha = push_file(fname, local_content)
            if ok:
                print(f"     ✅ Local version pushed (commit {commit_sha[:7]})")
                log_sync("push", fname, "success", commit_sha)
            else:
                print(f"     ❌ Push failed: {commit_sha}")
                log_sync("push", fname, "fail")
        elif choice == "r" and remote_content:
            bak = local_path + ".bak"
            with open(bak, "w", encoding="utf-8") as fh:
                fh.write(local_content)
            print(f"     💾 Local backed up as {os.path.basename(bak)}")
            with open(local_path, "w", encoding="utf-8") as fh:
                fh.write(remote_content)
            print(f"     ✅ Remote version pulled")
            log_sync("pull", fname, "success", sha)
        else:
            print(f"     ⏭  Skipped")
            log_sync("push", fname, "skipped")

    if not result["local_only"] and not result["remote_only"] and not result["modified"]:
        print("  ✅ Everything is already in sync!")

    # Notify via alert module
    if _ALERT_AVAILABLE:
        try:
            _alert.fire("sync", "info", "Full sync complete",
                        "github_sync")
        except Exception:
            pass

    # Log to history ledger
    if _HISTORY_AVAILABLE:
        try:
            _history.log_event("vault_deposit", 0,
                               details="GitHub full_sync complete",
                               source="github_sync")
        except Exception:
            pass


# ──────────────────────────────────────────────────────────
# SYNC HISTORY
# ──────────────────────────────────────────────────────────

def log_sync(action, filename, status, commit_sha=""):
    """Append one sync event to SYNC_LOG."""
    entry = {
        "timestamp":  datetime.datetime.utcnow().isoformat() + "Z",
        "action":     action,
        "filename":   filename,
        "status":     status,
        "commit_sha": commit_sha,
    }
    log = []
    if os.path.exists(SYNC_LOG):
        try:
            with open(SYNC_LOG, "r") as fh:
                log = json.load(fh)
        except (json.JSONDecodeError, IOError):
            log = []
    log.append(entry)
    try:
        with open(SYNC_LOG, "w") as fh:
            json.dump(log, fh, indent=2)
    except IOError:
        pass  # Non-fatal — sync still happened


def sync_history():
    """Print last 20 sync operations."""
    print("\n── Sync History (last 20) ────────────────────────────")
    if not os.path.exists(SYNC_LOG):
        print("  No sync history found.")
        return
    try:
        with open(SYNC_LOG, "r") as fh:
            log = json.load(fh)
    except (json.JSONDecodeError, IOError):
        print("  Could not read sync log.")
        return

    recent = log[-20:]
    for entry in reversed(recent):
        ts  = entry.get("timestamp", "?")[:19].replace("T", " ")
        act = entry.get("action", "?")
        fn  = entry.get("filename", "?")
        st  = entry.get("status", "?")
        sha = entry.get("commit_sha", "")[:7]
        icon = "📤" if act == "push" else "📥"
        ok   = "✅" if st == "success" else ("⏭" if st == "skipped" else "❌")
        sha_part = f"  [{sha}]" if sha else ""
        print(f"  {ok} {icon} {act:<6} {fn:<30} {ts}{sha_part}")


def last_sync_time():
    """Return ISO timestamp of the last successful sync, or None."""
    if not os.path.exists(SYNC_LOG):
        return None
    try:
        with open(SYNC_LOG, "r") as fh:
            log = json.load(fh)
        successes = [e for e in log if e.get("status") == "success"]
        if successes:
            return successes[-1]["timestamp"]
    except (json.JSONDecodeError, IOError):
        pass
    return None


# ──────────────────────────────────────────────────────────
# INTERACTIVE CLI
# ──────────────────────────────────────────────────────────

_MENU = """
==================================
🔄 PCVR GITHUB SYNC ENGINE
==================================
Commands:
1. setup     → configure GitHub token
2. status    → compare local vs remote
3. push      → push all changes to GitHub
4. pull      → pull all changes from GitHub
5. sync      → full smart sync
6. push_one  → push a single file
7. pull_one  → pull a single file
8. history   → sync history
9. exit
==================================
"""


def _run_cli():
    if not _REQUESTS_AVAILABLE:
        print("  ⚠️  'requests' library not available.")
        print("  Install it with: pip install requests")
        return

    print(_MENU)

    _dispatch = {
        "1":        setup_auth,
        "setup":    setup_auth,
        "2":        sync_report,
        "status":   sync_report,
        "3":        push_all,
        "push":     push_all,
        "4":        pull_all,
        "pull":     pull_all,
        "5":        full_sync,
        "sync":     full_sync,
        "8":        sync_history,
        "history":  sync_history,
    }

    while True:
        try:
            cmd = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if cmd in ("9", "exit", "quit", "q"):
            print("  Goodbye!")
            break

        elif cmd in ("6", "push_one"):
            fname = input("  Filename to push: ").strip()
            push_file_interactive(fname)

        elif cmd in ("7", "pull_one"):
            fname = input("  Filename to pull: ").strip()
            pull_file_interactive(fname)

        elif cmd in _dispatch:
            try:
                _dispatch[cmd]()
            except Exception as exc:
                print(f"  ❌ Error: {exc}")

        else:
            print("  Unknown command. Try: setup / status / push / pull / sync / history / exit")


if __name__ == "__main__":
    _run_cli()
