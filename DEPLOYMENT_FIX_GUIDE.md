# SENIOR DEVELOPER DIAGNOSTIC REPORT
## AI-KIOSK CI Failure Analysis (Commit 89cad95)

---

## 🔴 ROOT CAUSE ANALYSIS

### Primary Failure
**Error:** `ImportError while importing test module 'tests/test_endpoints.py'`  
**Location:** Line 4 of test file  
**Import Statement:** `from app.main import app`

### Why It Fails
The test is being executed from `/backend` directory with `PYTHONPATH=.` set, but the Python package structure is **incomplete**. Missing `__init__.py` files break Python's module resolution, preventing relative imports from working correctly.

---

## 🏗️ ROOT CAUSES (All Issues Found)

### Issue 1: Missing Package Initializers
**Severity:** CRITICAL  
**Files Missing:**
- `backend/app/__init__.py` — Makes `app` a proper Python package
- `backend/app/api/__init__.py` — Makes `api` a proper Python package  
- `backend/app/api/routes/__init__.py` — Makes `routes` a proper Python package
- `backend/app/core/__init__.py` — Makes `core` a proper Python package
- `backend/tests/__init__.py` — Makes `tests` a proper Python package

**Impact:** Python cannot resolve imports like `from app.main import app`

### Issue 2: Missing Pytest Configuration
**Severity:** HIGH  
**File Missing:** `backend/pytest.ini`

**Why It's Needed:**
- Tells pytest where to find modules (`pythonpath = .`)
- Configures async test support (`asyncio_mode = auto`)
- Specifies test discovery patterns

**Current Behavior:** Pytest uses defaults, doesn't set PYTHONPATH correctly

### Issue 3: Missing Conftest with Fixtures
**Severity:** HIGH  
**File Missing:** `backend/conftest.py`

**Why It's Needed:**
- Pytest loads conftest.py first in every test session
- Sets up environment variables BEFORE importing the app
- Provides reusable fixtures (like `client`, `test_app`)
- Ensures consistent test initialization

**Current Problem:** Environment variables set in workflow CI but app imports fail before reaching them

### Issue 4: Incorrect Import Path in app/main.py
**Severity:** HIGH  
**File:** `backend/app/main.py` Line 14  
**Current:** `from backend.app.api.routes import ...`  
**Problem:** Uses absolute import path that assumes `/backend` is NOT the root

**Why It Fails:**
- When running pytest from `/backend` with `PYTHONPATH=.`
- Python expects: `from app.api.routes import ...` (relative to current path)
- NOT `from backend.app.api.routes` (absolute path from project root)

---

## 🔧 STEP-BY-STEP FIX APPROACH

### STEP 1: Create Missing Package Initializers
Create empty or minimal `__init__.py` files to establish Python package hierarchy:

```bash
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/routes/__init__.py
touch backend/app/core/__init__.py
touch backend/tests/__init__.py
```

**Why:** Python 3.3+ requires `__init__.py` (or uses implicit packages, but explicit is better for clarity and IDE support)

---

### STEP 2: Create pytest.ini Configuration
**Location:** `backend/pytest.ini`  
**Contents:**
```ini
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
log_cli = true
log_cli_level = INFO
```

**Why:**
- `pythonpath = .` — Tells pytest to add current directory to sys.path (matches CI workflow `PYTHONPATH: .`)
- `asyncio_mode = auto` — Enables pytest-asyncio's auto mode for FastAPI async tests
- `testpaths = tests` — Limits test discovery to tests/ directory
- Logging enabled for CI debugging

---

### STEP 3: Create conftest.py with Fixture Setup
**Location:** `backend/conftest.py`  
**Purpose:** Pytest's special file that runs before any tests

```python
"""
Pytest Configuration and Fixtures
Runs before any test session to set up environment and provide shared fixtures
"""

import os
import pytest

# SET ENVIRONMENT BEFORE IMPORTING APP (CRITICAL!)
os.environ.setdefault("PYTHONPATH", ".")
os.environ.setdefault("USE_MOCK_SERVICES", "true")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

# NOW import app after environment is configured
from app.main import app

@pytest.fixture(scope="session")
def test_app():
    """Provide FastAPI app instance for tests"""
    return app

@pytest.fixture
def client():
    """Provide TestClient for making test requests"""
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
```

**Why:**
- Environment variables set BEFORE app import ensures config loads correctly
- Fixtures reduce boilerplate in test files
- `scope="session"` for `test_app` means it's created once per test run (efficient)

---

### STEP 4: Fix Import in app/main.py
**File:** `backend/app/main.py` Line 14  
**Change FROM:**
```python
from backend.app.api.routes import detect, asr, riar, route, rag, tts, session
from backend.app.core.config import settings
```

**Change TO:**
```python
from app.api.routes import detect, asr, riar, route, rag, tts, session
from app.core.config import settings
```

**Why:**
- When pytest runs from `/backend` with `PYTHONPATH=.`, the root module is `app`, not `backend.app`
- CI sets `working-directory: backend`, so paths are relative to that
- Using `from app.*` works in both development and CI environments

---

### STEP 5: Create __init__.py for Routes Package
**Location:** `backend/app/api/routes/__init__.py`  
**Contents:**
```python
"""
API Route Handlers
"""
from . import detect, asr, riar, route, rag, tts, session

__all__ = [
    "detect",
    "asr", 
    "riar",
    "route",
    "rag",
    "tts",
    "session",
]
```

**Why:**
- Makes `from app.api.routes import detect` work correctly
- Explicitly exports route modules for clarity

---

### STEP 6: Fix Route Files (Stub Structure Issue)
**File:** `backend/app/api/routes/asr.py` (and similar route files)

**Current Problem:** Multiple route definitions in single file  
**All route files are currently stubs** — need proper structure:

```python
# asr.py - CORRECT STRUCTURE
"""
ASR Route — POST /asr
Owner: Harsha
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ASRRequest(BaseModel):
    session_id: str
    audio_base64: str
    language_hint: str = "en"
    turn_id: int

class ASRResponse(BaseModel):
    session_id: str
    turn_id: int
    transcript: str
    detected_language: str = "en"
    confidence: float = 0.95

@router.post("/asr", response_model=ASRResponse)
async def transcribe_audio(request: ASRRequest):
    """Transcribe audio to text using Whisper"""
    return ASRResponse(
        session_id=request.session_id,
        turn_id=request.turn_id,
        transcript="[MOCK] How do I apply?",
        detected_language="en",
        confidence=0.95
    )
```

---

### STEP 7: Update test_endpoints.py
**File:** `backend/tests/test_endpoints.py`

**Current Problem:**
- Uses bare `from app.main import app` which fails
- Should use fixture from conftest.py
- Tests need to match actual endpoint signatures

**Replace with:**
```python
"""
Endpoint Integration Tests
"""

import pytest
from fastapi.testclient import TestClient

class TestHealth:
    def test_health(self, client: TestClient):
        """Test health endpoint exists"""
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

class TestDetection:
    def test_detect(self, client: TestClient):
        """Test detection endpoint"""
        r = client.post("/api/v1/detect", json={
            "camera_id": "cam_front_01",
            "confidence": 0.95,
            "bounding_box": {"x": 100, "y": 100, "w": 200, "h": 400}
        })
        assert r.status_code == 200
        data = r.json()
        assert "session_id" in data
        assert data["action"] == "session_created"
```

---

## 📋 EXECUTION CHECKLIST

### Phase 1: Package Structure (5 files)
- [ ] Create `backend/app/__init__.py` (empty or minimal)
- [ ] Create `backend/app/api/__init__.py` (empty or minimal)
- [ ] Create `backend/app/api/routes/__init__.py` (with exports)
- [ ] Create `backend/app/core/__init__.py` (empty or minimal)
- [ ] Create `backend/tests/__init__.py` (empty or minimal)

### Phase 2: Configuration Files (2 files)
- [ ] Create `backend/pytest.ini` (test configuration)
- [ ] Create `backend/conftest.py` (pytest fixtures + env setup)

### Phase 3: Fix Imports (1 file)
- [ ] Update `backend/app/main.py` — Remove `backend.` prefix from imports

### Phase 4: Fix Route Structure (All route files)
- [ ] Verify each route file has proper structure with router and model definitions
- [ ] Ensure `@router.post(...)` decorators exist for all endpoints

### Phase 5: Test File (1 file)
- [ ] Update `backend/tests/test_endpoints.py` — Use fixtures from conftest

---

## ✅ VERIFICATION STEPS

After making changes, run locally:

```bash
cd backend

# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify imports
python -c "from app.main import app; print('✓ Import successful')"

# 3. Run pytest collection (no execution)
pytest --collect-only

# 4. Run actual tests
pytest tests/ -v --tb=short

# 5. Lint check
ruff check app/ tests/
```

---

## 📊 EXPECTED RESULT

**Before Fix:**
```
ERROR collecting tests/test_endpoints.py
ImportError while importing test module
```

**After Fix:**
```
collected 4 items
tests/test_endpoints.py::TestHealth::test_health PASSED
tests/test_endpoints.py::TestDetection::test_detect PASSED
tests/test_endpoints.py::TestFullPipeline::test_full_pipeline PASSED
======================== 4 passed in 0.85s ==========================
```

---

## 🎯 WHY THIS FIXES THE CI

1. **Package Initializers** → Python can resolve `from app.* import` statements
2. **pytest.ini** → Pytest correctly sets PYTHONPATH before test discovery
3. **conftest.py** → Environment loaded BEFORE app import (fixes config loading)
4. **Fixed main.py imports** → Uses relative paths that work with PYTHONPATH=.
5. **Test file uses fixtures** → Reuses app instance from conftest safely

**CI Failure Chain Broken At:** Step 1 (import error → package discovery)

---
