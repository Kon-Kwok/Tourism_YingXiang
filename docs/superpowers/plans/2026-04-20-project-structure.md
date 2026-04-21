# Project Structure Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the collectors into a unified `src/tourism_automation/` package, add a single CLI entrypoint, and keep current `sycm` and `fliggy_home` collection behavior intact.

**Architecture:** Extract Chrome cookie/session and JSON request code into shared modules, split each collector into focused modules under `collectors/`, and route all commands through `tourism_automation.cli.main`. Keep repository-local execution working by auto-injecting `src/` onto `sys.path`.

**Tech Stack:** Python 3, `unittest`, `requests`, `secretstorage`, `cryptography`

---

### Task 1: Add failing tests for the new package and unified CLI

**Files:**
- Create: `tests/cli/test_main.py`
- Modify: `tests/test_sycm.py`
- Modify: `tests/test_fliggy_home.py`

- [ ] **Step 1: Write the failing tests**

```python
import unittest

from tourism_automation.cli.main import build_parser


class UnifiedCliTests(unittest.TestCase):
    def test_build_parser_registers_collectors(self):
        parser = build_parser()
        self.assertIsNotNone(parser)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.cli.test_main -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tourism_automation'`

- [ ] **Step 3: Update collector tests to import through new package paths**

Replace old imports with:

```python
from tourism_automation.collectors.sycm.normalize import normalize_home_payloads
from tourism_automation.shared.chrome.session import _decrypt_cookie_value
from tourism_automation.collectors.fliggy_home.collector import collect_home
```

- [ ] **Step 4: Run the focused tests again**

Run: `python3 -m unittest tests.cli.test_main -v`
Expected: still FAIL until package structure exists

### Task 2: Create the new package skeleton and shared runtime path setup

**Files:**
- Create: `sitecustomize.py`
- Create: `src/tourism_automation/__init__.py`
- Create: `src/tourism_automation/cli/__init__.py`
- Create: `src/tourism_automation/collectors/__init__.py`
- Create: `src/tourism_automation/shared/__init__.py`

- [ ] **Step 1: Write minimal runtime path setup**

```python
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))
```

- [ ] **Step 2: Create empty package markers**

```python
"""tourism_automation package."""
```

- [ ] **Step 3: Run the CLI test**

Run: `python3 -m unittest tests.cli.test_main -v`
Expected: FAIL moves from package import to missing `build_parser`

### Task 3: Extract shared Chrome and HTTP helpers

**Files:**
- Create: `src/tourism_automation/shared/chrome/__init__.py`
- Create: `src/tourism_automation/shared/chrome/session.py`
- Create: `src/tourism_automation/shared/http/__init__.py`
- Create: `src/tourism_automation/shared/http/json_client.py`

- [ ] **Step 1: Copy the current Chrome cookie/session implementation into `shared/chrome/session.py`**
- [ ] **Step 2: Wrap `requests.Session` JSON GET behavior in `shared/http/json_client.py`**
- [ ] **Step 3: Export a `ChromeHttpClient` compatible API from the shared layer**
- [ ] **Step 4: Run `python3 -m unittest tests.test_sycm -v` and fix imports until green**

### Task 4: Move and split the SYCM collector into the new layout

**Files:**
- Create: `src/tourism_automation/collectors/sycm/__init__.py`
- Create: `src/tourism_automation/collectors/sycm/client.py`
- Create: `src/tourism_automation/collectors/sycm/normalize.py`
- Create: `src/tourism_automation/collectors/sycm/collector.py`
- Create: `src/tourism_automation/collectors/sycm/cli.py`
- Create: `src/tourism_automation/collectors/sycm/storage.py`
- Create: `src/tourism_automation/collectors/sycm/discovery.py`

- [ ] **Step 1: Move SYCM request-path building and fetching into `client.py`**
- [ ] **Step 2: Move normalization helpers into `normalize.py`**
- [ ] **Step 3: Keep `HomePageCollector` in `collector.py`**
- [ ] **Step 4: Recreate SYCM command registration in `cli.py`**
- [ ] **Step 5: Run `python3 -m unittest tests.test_sycm -v`**

### Task 5: Move and split the Fliggy home collector into the new layout

**Files:**
- Create: `src/tourism_automation/collectors/fliggy_home/__init__.py`
- Create: `src/tourism_automation/collectors/fliggy_home/client.py`
- Create: `src/tourism_automation/collectors/fliggy_home/normalize.py`
- Create: `src/tourism_automation/collectors/fliggy_home/collector.py`
- Create: `src/tourism_automation/collectors/fliggy_home/cli.py`
- Create: `src/tourism_automation/shared/result/__init__.py`
- Create: `src/tourism_automation/shared/result/module_result.py`

- [ ] **Step 1: Move Fliggy request specs/client into `client.py`**
- [ ] **Step 2: Move module normalizers into `normalize.py`**
- [ ] **Step 3: Move orchestration and aggregate-result code into `collector.py`**
- [ ] **Step 4: Put shared module-summary/result helpers in `shared/result/module_result.py`**
- [ ] **Step 5: Run `python3 -m unittest tests.test_fliggy_home -v`**

### Task 6: Implement the unified CLI and update tests/docs

**Files:**
- Create: `src/tourism_automation/cli/main.py`
- Create: `docs/architecture/project-structure.md`
- Create: `docs/collectors/sycm.md`
- Create: `docs/collectors/fliggy-home.md`
- Modify: `tests/cli/test_main.py`

- [ ] **Step 1: Register `sycm` and `fliggy-home` subcommands in `main.py`**
- [ ] **Step 2: Add a parser test that checks both collector names are present**
- [ ] **Step 3: Write short runtime docs for the new commands**
- [ ] **Step 4: Run `python3 -m unittest discover -s tests -v`**

### Task 7: Remove obsolete root-level collector packages after verification

**Files:**
- Delete: `sycm/`
- Delete: `fliggy_home/`

- [ ] **Step 1: Re-run all tests before deleting old roots**
- [ ] **Step 2: Delete the old packages once new imports are green**
- [ ] **Step 3: Run live commands**

Run:

```bash
python3 -m tourism_automation.cli.main sycm healthcheck
python3 -m tourism_automation.cli.main sycm collect-home --date 2026-04-19 --shop-name "皇家加勒比国际游轮旗舰店"
python3 -m tourism_automation.cli.main fliggy-home collect-home --date 2026-04-19 --shop-name "皇家加勒比国际游轮旗舰店"
```

Expected: all commands succeed and return the same JSON shape as before
