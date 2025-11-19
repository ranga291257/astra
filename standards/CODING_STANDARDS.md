# ASTRA Coding Standards
## Project Standards for Modular, Maintainable Code

**Purpose:** This document defines the coding standards that ALL ASTRA code must follow. These are not suggestions—they are requirements.

**Reference:** See `ASTRA_MODULAR_APPROACH.md` for detailed explanations and examples.

---

## ⚠️ MANDATORY STANDARDS

### 1. Module Structure

**Rule:** Code MUST be organized into modules with clear boundaries:

```
astra/
├── ASTRA.py              # UI wiring ONLY (no business logic)
├── data/                 # Data operations ONLY
│   └── loader.py
├── risk/                 # Risk calculations ONLY
│   └── metrics.py
├── analysis/             # Analysis features ONLY
│   ├── indicators.py
│   ├── backtest.py
│   └── monte_carlo.py
└── ui/                   # UI components ONLY
    └── components.py
```

**Enforcement:**
- ❌ **FORBIDDEN:** Business logic in `ASTRA.py`
- ❌ **FORBIDDEN:** UI code in `risk/` or `data/` modules
- ✅ **REQUIRED:** One module = one responsibility

---

### 2. Function Contracts

**Rule:** Every function MUST have:
1. Type hints for all parameters and return value
2. Docstring explaining the contract (inputs, outputs, errors)
3. Clear error handling (return errors, don't crash silently)

**Template:**
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of what this function does.
    
    Contract:
    - Input: param1 (description), param2 (description)
    - Output: ReturnType (description)
    - Errors: Returns (None, error_message) on failure
    - Side effects: None (or describe if any)
    
    Example:
        result, err = function_name(value1, value2)
        if err:
            handle_error(err)
    """
    # Implementation
    pass
```

**Enforcement:**
- ❌ **FORBIDDEN:** Functions without type hints
- ❌ **FORBIDDEN:** Functions without docstrings
- ❌ **FORBIDDEN:** Silent failures (must return error explicitly)

---

### 3. One Responsibility Per Module

**Rule:** Each module MUST have ONE clear job that can be described in one sentence.

**Examples:**
- ✅ `data/loader.py` → "Downloads and cleans stock data"
- ✅ `risk/metrics.py` → "Calculates risk metrics (Sharpe, Sortino, drawdowns)"
- ✅ `analysis/indicators.py` → "Calculates technical indicators (MA, momentum)"
- ❌ **FORBIDDEN:** Module that does "Downloads data AND calculates metrics AND displays UI"

**Enforcement:**
- If you can't describe a module's purpose in one sentence, it's doing too much → **BREAK IT DOWN**

---

### 4. Explicit Interfaces, No Hidden Dependencies

**Rule:** Functions MUST declare all dependencies as parameters. No global state, no hidden side effects.

**Bad:**
```python
# ❌ FORBIDDEN
current_ticker = None

def calculate_metrics():
    global current_ticker  # Hidden dependency
    # ...
```

**Good:**
```python
# ✅ REQUIRED
def calculate_metrics(df: pd.DataFrame, ticker: str) -> dict:
    # All inputs explicit
    # No global state
    pass
```

**Enforcement:**
- ❌ **FORBIDDEN:** Global variables for function inputs
- ❌ **FORBIDDEN:** Functions that read from module-level state
- ✅ **REQUIRED:** All dependencies passed as parameters

---

### 5. Data Flow Must Be Visible

**Rule:** You MUST be able to trace data from input → processing → output without jumping through hoops.

**Pattern:**
```
User Input
    ↓
[data/loader.py] → (df, ticker, error)
    ↓
[risk/metrics.py] → (df_with_metrics)
    ↓
[analysis/indicators.py] → (df_with_indicators)
    ↓
[ui/components.py] → (displayed to user)
```

**Enforcement:**
- ❌ **FORBIDDEN:** Circular dependencies (Module A imports B, B imports A)
- ❌ **FORBIDDEN:** Data transformations that are hard to trace
- ✅ **REQUIRED:** Linear data flow (A → B → C, not A ↔ B)

---

### 6. Incremental Implementation

**Rule:** Build ONE module at a time. Test it. Then connect it. NEVER build everything at once.

**Process:**
1. Create module file
2. Implement ONE function
3. Write test for that function
4. Run test, fix if broken
5. Move to next function
6. Only proceed when module works

**Enforcement:**
- ❌ **FORBIDDEN:** Creating multiple modules without testing each one
- ❌ **FORBIDDEN:** Writing 500 lines of code before testing
- ✅ **REQUIRED:** Test each function before moving on

---

### 7. Pure Functions (When Possible)

**Rule:** Functions MUST be pure (same input → same output, no side effects) unless side effects are necessary (e.g., UI display).

**Pure Function (Good):**
```python
def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Same df → same result, no side effects"""
    result = df.copy()
    result['Daily_Return'] = result['Close'].pct_change()
    return result
```

**Side Effect Function (Only when necessary):**
```python
def display_metrics(metrics: dict) -> None:
    """UI display - side effect is intentional"""
    st.write(metrics)
```

**Enforcement:**
- ✅ **REQUIRED:** Business logic functions must be pure
- ✅ **ALLOWED:** UI functions can have side effects (displaying is the purpose)

---

### 8. Error Handling

**Rule:** Functions MUST return errors explicitly, not raise exceptions (unless exception is truly unexpected).

**Pattern:**
```python
def download_data(ticker: str) -> tuple[pd.DataFrame | None, str | None]:
    """
    Returns: (dataframe, error_message)
    - Success: (df, None)
    - Failure: (None, "error message")
    """
    try:
        # ... download logic
        return df, None
    except Exception as e:
        return None, f"Error: {str(e)}"
```

**Enforcement:**
- ❌ **FORBIDDEN:** Functions that crash on expected errors (invalid input, network failure)
- ✅ **REQUIRED:** Return error in tuple/result object
- ✅ **ALLOWED:** Raise exceptions only for truly unexpected errors (programming bugs)

---

### 9. Testing Requirements

**Rule:** Every module MUST have tests. Every function MUST be testable in isolation.

**Test Structure:**
```
astra/
├── data/
│   ├── loader.py
│   └── test_loader.py      # Tests for loader.py
├── risk/
│   ├── metrics.py
│   └── test_metrics.py     # Tests for metrics.py
```

**Test Template:**
```python
def test_function_name_success():
    """Test: Does function work with valid input?"""
    result = function_name(valid_input)
    assert result is not None
    # ... more assertions

def test_function_name_error_handling():
    """Test: Does function handle errors gracefully?"""
    result, err = function_name(invalid_input)
    assert err is not None
    assert result is None
```

**Enforcement:**
- ✅ **REQUIRED:** Test file for each module
- ✅ **REQUIRED:** Test for success case
- ✅ **REQUIRED:** Test for error case
- ❌ **FORBIDDEN:** Functions that can't be tested without running entire app

---

### 10. Code Size Limits

**Rule:** Functions and modules MUST stay within size limits.

**Limits:**
- Function: **< 50 lines** (if longer, break into smaller functions)
- Module: **< 500 lines** (if longer, split into multiple modules)
- File: **< 1000 lines** (if longer, refactor immediately)

**Enforcement:**
- If function > 50 lines → **BREAK IT DOWN**
- If module > 500 lines → **SPLIT IT UP**
- If file > 1000 lines → **REFACTOR NOW**

---

### 11. Type Hints Are Mandatory

**Rule:** ALL functions MUST have type hints for parameters and return values.

**Required:**
```python
def calculate_metrics(
    df: pd.DataFrame,
    ticker: str,
    risk_free_rate: float = 0.025
) -> dict[str, float]:
    """Type hints for all parameters and return"""
    pass
```

**Enforcement:**
- ❌ **FORBIDDEN:** Functions without type hints
- ✅ **REQUIRED:** Type hints for all parameters
- ✅ **REQUIRED:** Return type annotation

---

### 12. Documentation Requirements

**Rule:** Every module and function MUST have clear documentation.

**Module Documentation (top of file):**
```python
"""
Module: data/loader.py

Purpose: Downloads and cleans stock data from Yahoo Finance.

This module handles:
- Downloading historical stock data
- Cleaning and preparing data for analysis
- Error handling for network/data issues

Dependencies:
- yfinance (external)
- pandas (external)

No dependencies on other ASTRA modules (this is a foundation module).
"""
```

**Function Documentation (see Rule #2 for template)**

**Enforcement:**
- ✅ **REQUIRED:** Module docstring explaining purpose
- ✅ **REQUIRED:** Function docstring with contract
- ❌ **FORBIDDEN:** Undocumented functions

---

## 📋 Pre-Implementation Checklist

**Before writing ANY code, verify:**

- [ ] Which module does this belong to? (data/risk/analysis/ui)
- [ ] Does this module already exist, or do I need to create it?
- [ ] What is the function signature? (name, inputs, outputs)
- [ ] What is the contract? (what goes in, what comes out, what errors?)
- [ ] Can I write a test for this function?
- [ ] Does this follow the "one responsibility" rule?
- [ ] Are all dependencies explicit (no global state)?

**If any checkbox is unclear → STOP and clarify before coding.**

---

## 📋 During Implementation Checklist

**While writing code, verify:**

- [ ] Function has type hints for all parameters and return
- [ ] Function has docstring explaining contract
- [ ] Function is < 50 lines (if longer, break it down)
- [ ] No global state (everything passed as parameters)
- [ ] Error handling returns errors explicitly
- [ ] Function is pure (no side effects) unless side effect is intentional

**If any checkbox fails → FIX IT before moving on.**

---

## 📋 Post-Implementation Checklist

**After writing code, verify:**

- [ ] Test written and passing
- [ ] Function can be tested in isolation (without running entire app)
- [ ] Can explain function purpose in one sentence
- [ ] Data flow is clear (can trace input → output)
- [ ] No circular dependencies
- [ ] Documentation is complete

**If any checkbox fails → FIX IT before considering it done.**

---

## 🚫 FORBIDDEN PATTERNS

These patterns are **EXPLICITLY FORBIDDEN** in ASTRA code:

1. ❌ **Global state for function inputs**
   ```python
   # FORBIDDEN
   current_df = None
   def process_data():
       global current_df
   ```

2. ❌ **Circular dependencies**
   ```python
   # FORBIDDEN
   # data/loader.py imports from risk/metrics.py
   # risk/metrics.py imports from data/loader.py
   ```

3. ❌ **Functions > 50 lines without breaking down**
   ```python
   # FORBIDDEN - function is 200 lines
   def do_everything():
       # ... 200 lines of code
   ```

4. ❌ **Silent failures**
   ```python
   # FORBIDDEN
   def download_data(ticker):
       try:
           # ... download
       except:
           pass  # Silent failure
   ```

5. ❌ **Business logic in ASTRA.py**
   ```python
   # FORBIDDEN - ASTRA.py should only wire modules together
   def main():
       # ... 500 lines of calculation logic
   ```

6. ❌ **Undocumented functions**
   ```python
   # FORBIDDEN
   def calculate_metrics(df):
       # No docstring, no type hints
       pass
   ```

7. ❌ **Hard-to-test functions**
   ```python
   # FORBIDDEN - requires entire Streamlit app running
   def calculate_metrics():
       ticker = st.text_input("Ticker")  # Can't test without Streamlit
       # ...
   ```

---

## ✅ REQUIRED PATTERNS

These patterns are **REQUIRED** in ASTRA code:

1. ✅ **Explicit parameters**
   ```python
   # REQUIRED
   def calculate_metrics(df: pd.DataFrame, ticker: str) -> dict:
       pass
   ```

2. ✅ **Error return pattern**
   ```python
   # REQUIRED
   def download_data(ticker: str) -> tuple[pd.DataFrame | None, str | None]:
       try:
           return df, None
       except Exception as e:
           return None, str(e)
   ```

3. ✅ **Pure business logic functions**
   ```python
   # REQUIRED
   def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
       result = df.copy()
       result['Daily_Return'] = result['Close'].pct_change()
       return result
   ```

4. ✅ **Module separation**
   ```python
   # REQUIRED - data/loader.py
   def download_data(ticker: str) -> tuple[pd.DataFrame | None, str | None]:
       # Only data operations
       pass
   
   # REQUIRED - risk/metrics.py
   def calculate_risk_metrics(df: pd.DataFrame) -> dict:
       # Only risk calculations
       pass
   ```

5. ✅ **Testable functions**
   ```python
   # REQUIRED - can test without Streamlit
   def calculate_metrics(df: pd.DataFrame) -> dict:
       # No st.* calls, no global state
       return metrics
   ```

---

## 🔍 Code Review Checklist

**When reviewing code (self-review or peer review), check:**

- [ ] Follows module structure (data/risk/analysis/ui)
- [ ] Functions have type hints and docstrings
- [ ] One responsibility per module/function
- [ ] No circular dependencies
- [ ] Error handling is explicit
- [ ] Functions are testable in isolation
- [ ] Tests exist and pass
- [ ] Code size within limits (< 50 lines per function, < 500 per module)
- [ ] Data flow is clear and traceable
- [ ] No forbidden patterns

**If any item fails → REQUEST CHANGES before merging.**

---

## 📚 Reference Documents

- **This Document:** `standards/CODING_STANDARDS.md` - Enforceable rules (you are here)
- **Detailed Explanation:** `functional_design/ASTRA_MODULAR_APPROACH.md` - Full philosophy and examples
- **Implementation Plan:** `functional_design/ASTRA_ENHANCEMENT_PLAN.md` - Feature roadmap
- **Audit Guide:** `standards/AUDIT_GUIDE.md` - How to verify compliance with these standards
- **Variations:** `standards/VARIATIONS.md` - Documented deviations from standards
- **Overview:** `README.md` - Quick start and documentation structure

---

## 🎯 Golden Rule

**If a human tester/debugger can't understand a module in 5 minutes, it's too complex.**

**Action:** Break it down. Make it smaller. Make it clearer.

---

## ⚡ Quick Reference

**Before coding:**
1. Identify module (data/risk/analysis/ui)
2. Write function signature with type hints
3. Write docstring with contract
4. Write test case

**While coding:**
1. Keep function < 50 lines
2. No global state
3. Explicit error handling
4. Pure functions (when possible)

**After coding:**
1. Run tests
2. Verify can test in isolation
3. Check documentation complete
4. Verify one responsibility

---

**Last Updated:** 2025-11-16  
**Status:** Active Standards - All ASTRA code MUST follow these rules  
**Enforcement:** 
- Automated audit: `python astra/scripts/audit_code.py`
- Manual review: See `standards/AUDIT_GUIDE.md`
- Code reviews, pre-commit checks, team agreement
- Variations must be documented in `standards/VARIATIONS.md`

