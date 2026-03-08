# Code Review: Global Energy Market Analysis

**Reviewed:** 2026-03-08
**Scope:** Full codebase — security, performance, and coding standards
**Files reviewed:** `src/api.py`, `src/data_loader.py`, `src/analysis.py`, `src/report.py`, `dashboard.html`, `tests/`, `requirements.txt`

---

## Security Vulnerabilities

### SEC-1: Path Traversal in `load_market_data` — **HIGH**

**File:** `src/data_loader.py:12-15`

The `filename` parameter is joined directly to `DATA_DIR` with no sanitization. If any caller passes user-controlled input (e.g., via a future endpoint), an attacker could read arbitrary files on the server.

```python
# Current (vulnerable)
def load_market_data(filename="global_energy_market.csv"):
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(filepath)
```

**Fix:** Validate the filename and ensure it stays within the data directory.

```python
def load_market_data(filename="global_energy_market.csv"):
    if os.sep in filename or filename.startswith("."):
        raise ValueError(f"Invalid filename: {filename}")
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.realpath(filepath).startswith(os.path.realpath(DATA_DIR)):
        raise ValueError(f"Path traversal detected: {filename}")
    df = pd.read_csv(filepath)
    return df
```

---

### SEC-2: No CORS Configuration — **MEDIUM**

**File:** `src/api.py`

The FastAPI app has no CORS middleware. If `dashboard.html` (or any browser client) attempts to call the API from a different origin, requests will fail — or worse, if CORS is later added too permissively (`allow_origins=["*"]`) it could expose the API to cross-origin attacks.

**Fix:** Add explicit CORS middleware with a specific allowed origin list.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

---

### SEC-3: No Authentication or Rate Limiting — **MEDIUM**

**File:** `src/api.py`

All API endpoints are publicly accessible with no authentication, authorization, or rate limiting. This makes the API vulnerable to abuse and data scraping.

**Fix:** Add API key authentication and rate limiting middleware (e.g., `slowapi` for rate limiting).

---

### SEC-4: User Input Reflected in Error Responses — **LOW**

**File:** `src/api.py:66-68, 84-86`

User-supplied sector names and company names are reflected directly in error messages. While FastAPI returns JSON (not HTML), this is still a minor information disclosure concern and a bad practice.

```python
# Current
detail=f"Sector '{sector}' not found. Valid sectors: {valid_sectors}"
```

**Fix:** Return a generic message without listing all valid sectors.

```python
detail=f"Sector not found"
```

---

### SEC-5: Outdated Pinned Dependencies — **LOW**

**File:** `requirements.txt`

All dependencies are pinned to versions from late 2023. These likely contain known security vulnerabilities that have since been patched (e.g., FastAPI 0.104.1, uvicorn 0.24.0).

**Fix:** Update all dependencies to their latest versions and set up Dependabot or Renovate for automated updates.

---

## Performance Issues

### PERF-1: CSV Re-read on Every API Request — **HIGH**

**File:** `src/api.py:28-56` (all endpoints)

Every single API request calls `load_market_data()`, which reads and parses the CSV from disk. For a web API, this is extremely inefficient — disk I/O and CSV parsing on every request adds unnecessary latency.

```python
# Current — every endpoint does this:
@app.get("/api/market-size")
def get_market_size():
    df = load_market_data()  # Reads CSV from disk every time
    ...
```

**Fix:** Cache the data at startup using a module-level variable or `@lru_cache`, or use a FastAPI lifespan event.

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_market_data(filename="global_energy_market.csv"):
    filepath = os.path.join(DATA_DIR, filename)
    return pd.read_csv(filepath)
```

**Note:** If using `lru_cache`, be aware that the returned DataFrame should not be mutated by callers (callers already use `.copy()` in most places, but not all).

---

### PERF-2: Redundant Growth Calculation — **LOW**

**Files:** `src/data_loader.py:60-62` and `src/analysis.py:41-43`

Revenue growth percentage is calculated identically in both `clean_data()` and `growth_leaders()`. This is duplicated work that also creates a maintenance risk (if the formula changes in one place but not the other).

**Fix:** Have `growth_leaders()` call `clean_data()` and use its `revenue_growth_pct` column, or extract the calculation into a shared helper.

---

### PERF-3: No Pagination on List Endpoints — **LOW**

**File:** `src/api.py:51-56`

Endpoints like `/api/sustainability` and `/api/market-size` return all records with no pagination. While the current dataset has only 20 rows, this will not scale.

**Fix:** Add `skip` and `limit` query parameters to list endpoints.

---

## Coding Standards Violations

### CODE-1: Division by Zero Risk — **HIGH**

**Files:** `src/data_loader.py:61`, `src/analysis.py:42,59,61`

Multiple locations divide by values that could be zero without any guard:

- `revenue_2022_bn` could be 0 → ZeroDivisionError in growth calculation
- `carbon_intensity.max()` could be 0 → ZeroDivisionError in sustainability score
- `rd_intensity.max()` could be 0 → ZeroDivisionError in sustainability score
- `revenue_2023_bn.sum()` could be 0 → ZeroDivisionError in competitive positioning

```python
# data_loader.py:61 — no guard against revenue_2022_bn == 0
df["revenue_growth_pct"] = (
    (df["revenue_2023_bn"] - df["revenue_2022_bn"]) / df["revenue_2022_bn"] * 100
)
```

**Fix:** Add zero-division guards using `replace` or conditional logic.

```python
df["revenue_growth_pct"] = np.where(
    df["revenue_2022_bn"] != 0,
    (df["revenue_2023_bn"] - df["revenue_2022_bn"]) / df["revenue_2022_bn"] * 100,
    0.0,
)
```

---

### CODE-2: Inconsistent Null Return vs Exception — **MEDIUM**

**File:** `src/analysis.py:79` vs `src/api.py:64-69`

`competitive_positioning()` returns `None` for an invalid sector, but the API endpoint pre-checks validity and raises `HTTPException`. If anyone calls the analysis function directly with an invalid sector, `None.to_dict()` would raise an `AttributeError` — a confusing error.

**Fix:** Either have the function raise a `ValueError` for invalid sectors, or document the `None` return and ensure all callers handle it.

---

### CODE-3: Dashboard Uses Hardcoded Data — **MEDIUM**

**File:** `dashboard.html:135-170`

All dashboard data is hardcoded in JavaScript arrays rather than fetched from the API. This means the dashboard and API can drift out of sync whenever the CSV data changes.

**Fix:** Have the dashboard `fetch()` data from the API endpoints, or generate the HTML from a template that reads the data.

---

### CODE-4: Missing Query Parameter Validation on `/api/compare` — **LOW**

**File:** `src/api.py:92`

The `compare_sectors` endpoint takes `sector_a` and `sector_b` as bare string parameters without using `Query()` for validation. Unlike `growth_leaders` which properly uses `Query(default=5, ge=1, le=20)`, these parameters have no defaults, descriptions, or constraints.

**Fix:** Use `Query()` with explicit annotations.

```python
def compare_sectors(
    sector_a: str = Query(..., description="First sector to compare"),
    sector_b: str = Query(..., description="Second sector to compare"),
):
```

---

### CODE-5: `validate_data()` Is Never Called — **LOW**

**File:** `src/data_loader.py:19-41`

The `validate_data()` function exists but is never called in the pipeline — not in the API, not in the report generator, and not in `clean_data()`. Data enters the system unvalidated.

**Fix:** Call `validate_data()` inside `load_market_data()` or at the start of `clean_data()`, and raise on critical issues.

---

### CODE-6: Tests Depend on Live Data File — **LOW**

**Files:** `tests/test_analysis.py:18-19`, `tests/test_api.py`

All tests load the real CSV file via `load_market_data()`. This means tests are not isolated — they depend on the exact contents of `global_energy_market.csv`. If the data file changes, tests will break in non-obvious ways.

**Fix:** Use synthetic test fixtures with known data rather than the production CSV, at least for unit tests.

---

## Summary

| ID | Category | Severity | File | Issue |
|---|---|---|---|---|
| SEC-1 | Security | **HIGH** | `data_loader.py:12` | Path traversal via unsanitized filename |
| SEC-2 | Security | MEDIUM | `api.py` | No CORS configuration |
| SEC-3 | Security | MEDIUM | `api.py` | No auth or rate limiting |
| SEC-4 | Security | LOW | `api.py:66` | User input in error messages |
| SEC-5 | Security | LOW | `requirements.txt` | Outdated dependencies |
| PERF-1 | Performance | **HIGH** | `api.py` (all endpoints) | CSV re-read on every request |
| PERF-2 | Performance | LOW | `data_loader.py`, `analysis.py` | Duplicated growth calculation |
| PERF-3 | Performance | LOW | `api.py` | No pagination |
| CODE-1 | Standards | **HIGH** | `data_loader.py:61`, `analysis.py:42` | Division by zero risk |
| CODE-2 | Standards | MEDIUM | `analysis.py:79` | Inconsistent None vs exception |
| CODE-3 | Standards | MEDIUM | `dashboard.html` | Hardcoded data, not fetched from API |
| CODE-4 | Standards | LOW | `api.py:92` | Missing Query() validation |
| CODE-5 | Standards | LOW | `data_loader.py:19` | validate_data() never called |
| CODE-6 | Standards | LOW | `tests/` | Tests depend on live data |

**High priority items to address first:** SEC-1, PERF-1, CODE-1
