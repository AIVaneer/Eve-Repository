# Contributing to PCVR Toolkit

Thank you for your interest in contributing to the PCVR Toolkit! This project is a 21-module, production-ready toolkit for PCVR token monitoring, analytics, and automation. We welcome contributions of all kinds — bug fixes, new modules, documentation improvements, and more.

> **Be respectful** — please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

## Getting Started

1. **Fork the repository** — click "Fork" on the top right of the repo page.
2. **Clone your fork locally:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Eve-Repository.git
   cd Eve-Repository/project_dont_die
   ```
3. **Install the only external dependency:**
   ```bash
   pip install requests
   ```
4. **Verify your setup:**
   ```bash
   python validate.py
   ```
5. **See the full system output:**
   ```bash
   python run_all.py
   ```

---

## Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-module
   ```
2. **Make your changes** (see Module Development Guide below).
3. **Validate nothing is broken:**
   ```bash
   python validate.py
   ```
4. **Run the full integration check:**
   ```bash
   python run_all.py
   ```
5. **Commit with a descriptive message:**
   ```bash
   git commit -m "feat: add your-module for X functionality"
   ```
6. **Open a Pull Request against `main`** with a clear title and body.

---

## Module Development Guide

### Creating a New Module

The toolkit uses a consistent module structure. Follow these conventions exactly so your module integrates cleanly with `atlas_omega.py` and `run_all.py`.

#### 1. File naming

Use `snake_case.py` — e.g., `my_feature.py`.

#### 2. Required structure

Every module must include:

```python
import os

_DIR = os.path.dirname(os.path.abspath(__file__))

# Graceful imports — REQUIRED for Pythonista 3 compatibility
try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

def report():
    """Return a formatted string report for this module."""
    lines = [
        "┌─────────────────────────────────┐",
        "│      YOUR MODULE REPORT         │",
        "└─────────────────────────────────┘",
    ]
    # ... populate lines
    return "\n".join(lines)

def _cli():
    """CLI entry point."""
    print(report())

if __name__ == "__main__":
    _cli()
```

Key requirements:
- **`_DIR` variable** — all data file paths must be relative to `_DIR`, never hardcoded or relative to `os.getcwd()`.
- **Graceful imports** — wrap every `import` in `try/except` so the module loads even when a dependency is missing (critical for Pythonista 3).
- **`report()` function** — returns a formatted string (box-style output consistent with existing modules).
- **`_cli()` or `_run_cli()`** — CLI entry point, called when the module is run directly.

#### 3. Register in `atlas_omega.py`

Add your module to `_MODULE_META` in `atlas_omega.py`:

```python
_MODULE_META = {
    # ... existing entries ...
    "your_module": {
        "file": "your_module.py",
        "description": "Short description of what it does",
        "report_fn": "report",
    },
}
```

#### 4. Wire into `run_all.py`

Add a `try/except` block in `run_all.py`:

```python
try:
    import your_module
    print(your_module.report())
except Exception as e:
    print(f"[your_module] skipped: {e}")
```

#### 5. Add data files to `.gitignore`

If your module reads/writes JSON, CSV, or config files, add them to `.gitignore`:

```
project_dont_die/your_module_data.json
```

#### 6. Document in `MODULES.md`

Add a full API reference section to `project_dont_die/MODULES.md` — include function signatures, usage examples, and a CLI command table.

---

## Code Standards

| Standard | Requirement |
|----------|-------------|
| **Python compatibility** | Pythonista 3 compatible — no C extensions, no compiled dependencies |
| **Type hints** | Not required (Pythonista compatibility) |
| **External dependencies** | `requests` is the **only** allowed external dependency |
| **Imports** | Always use `try/except` — graceful degradation required |
| **File paths** | Always use `_DIR`-relative paths for data files |
| **CLI interface** | Every module must have `_cli()` or `_run_cli()` |
| **Report output** | Box-style formatted output, consistent with existing modules |
| **File naming** | `snake_case.py` |

---

## Testing

There is no formal test framework (to maintain Pythonista 3 compatibility). Instead:

1. **Run `python validate.py`** — must pass all checks with no errors.
2. **Run `python run_all.py`** — must complete without exceptions.
3. **Test on both platforms if possible:**
   - Desktop Python 3.x
   - Pythonista 3 (iOS) — see [Pythonista-Tools](https://github.com/Pythonista-Tools/Pythonista-Tools) for iOS Python resources

---

## Documentation

When adding or modifying a module:

- Update the module table in `README.md` if you are adding a new module.
- Add a full API reference section in `project_dont_die/MODULES.md` — include:
  - Module overview
  - All public functions with signatures and descriptions
  - CLI command table
  - Usage examples
  - Data files used

---

## Pull Request Guidelines

- **One feature per PR** — keep PRs focused and reviewable.
- **Descriptive title and body** — explain what the change does and why.
- **Reference related issues** — use `Closes #123` or `Related to #123`.
- **`validate.py` must pass** — PRs that break validation will not be merged.
- **Include before/after** for any UI or output format changes.
- **Update docs** — README and MODULES.md must reflect your changes.

---

## Community

- 💬 **Discord:** https://discord.gg/E7bW3Zh4x
- 🐦 **Twitter/X:** https://x.com/pcvr2024
- 🐛 **Bug reports:** use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
- 💡 **Feature requests:** use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)

Be respectful in all interactions — see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## Recognition

All contributors are recognized in the project. Significant contributions may be credited in module headers and the project README.

**Philosophy:** *Earn → Hold → Spend → Buy → Earn*

---

*© PCVR STUDIOS · 2026 — Contract: `0x05c870C5C6E7AF4298976886471c69Fc722107e4`*
