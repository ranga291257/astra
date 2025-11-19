# ASTRA Modular Coding Approach
## How to Build Maintainable, Testable, and Debuggable Code

**Purpose:** This document explains the coding philosophy and implementation strategy to avoid "code spaghetti" and ensure human testers/debuggers can easily understand, test, and maintain the codebase.

---

## Core Principles

### 1. **One Responsibility Per Module**
Each module has ONE clear job. If you can't describe a module's purpose in one sentence, it's doing too much.

### 2. **Explicit Interfaces, Not Hidden Dependencies**
Functions clearly declare what they need (parameters) and what they return. No hidden global state or side effects.

### 3. **Data Flow is Visible**
You can trace data from input → processing → output without jumping through hoops.

### 4. **Incremental Implementation**
Build one module at a time, test it, then connect it. Don't build everything at once.

### 5. **Fail Fast, Fail Clearly**
Errors happen at boundaries with clear messages. No silent failures or mysterious bugs.

---

## Module Architecture

### Module Structure (Simple & Clear)

```
astra/
├── ASTRA.py              # Main Streamlit app (UI wiring only)
├── data/                 # Data layer
│   └── loader.py         # download_data, clean_data
├── risk/                 # Risk calculations
│   └── metrics.py        # returns, volatility, drawdown, risk_metrics
├── analysis/             # Analysis features
│   ├── indicators.py     # Technical indicators (MA, momentum)
│   ├── backtest.py       # Strategy backtesting
│   └── monte_carlo.py    # Monte Carlo simulation
└── ui/                   # UI components
    └── components.py      # Reusable UI widgets
```

**Why This Structure?**
- **data/** - "Get me stock data" - one job
- **risk/** - "Calculate risk metrics" - one job
- **analysis/** - "Run analysis features" - one job
- **ui/** - "Display things" - one job
- **ASTRA.py** - "Wire everything together" - one job

---

## Module Contracts (Interfaces)

### What is a "Contract"?
A contract is a clear agreement: "Give me X, I'll give you Y, and here's what can go wrong."

### Example: Data Loader Contract

```python
# data/loader.py

def download_data(ticker: str, start_date: str | None = None) -> tuple[pd.DataFrame | None, str, str | None]:
    """
    Download stock data from Yahoo Finance.
    
    Contract:
    - Input: ticker (str), optional start_date (str)
    - Output: (dataframe, actual_ticker, error_message)
      - If success: (DataFrame, ticker, None)
      - If failure: (None, ticker, "error message")
    - Side effects: None (pure function)
    - Raises: Nothing (returns error in tuple)
    
    Example:
        df, ticker, err = download_data("AAPL")
        if err:
            print(f"Error: {err}")
        else:
            print(f"Got {len(df)} rows for {ticker}")
    """
    # Implementation here
    pass
```

**Why This Matters:**
- Tester knows exactly what to expect
- Debugger knows where errors come from
- No surprises, no hidden behavior

---

## Data Flow Diagram

### How Data Moves Through the System

```
User Input (ticker)
    ↓
[data/loader.py]
    ├─→ download_data() → (raw_data, ticker, error)
    └─→ clean_data() → (clean_df)
    ↓
[risk/metrics.py]
    ├─→ calculate_returns() → (df with returns)
    ├─→ calculate_volatility() → (df with volatility)
    ├─→ calculate_drawdown() → (df with drawdown)
    ├─→ find_major_drawdowns() → (drawdowns_df)
    ├─→ calculate_recovery() → (recovery_df)
    └─→ calculate_risk_metrics() → (metrics_dict)
    ↓
[analysis/indicators.py] (optional)
    └─→ calculate_factors() → (df with indicators)
    ↓
[ui/components.py]
    └─→ render_dashboard() → (Streamlit widgets)
    ↓
User sees results
```

**Key Points:**
- Each step is a function call with clear inputs/outputs
- No circular dependencies
- Easy to trace: "Where did this number come from?"

---

## Implementation Strategy: One Module at a Time

**Note:** The "Phase 1/2/3" here refers to implementation steps (how to build), not project phases. For project phases (what to build), see `ASTRA_ENHANCEMENT_PLAN.md` which uses "Phase A/B/C".

### Phase 1: Data Layer (Foundation)

**Goal:** Get data loading working and tested.

**Steps:**
1. Create `astra/data/loader.py`
2. Copy `download_data()` and `clean_data()` from Stock_RAVA.py
3. Add type hints and docstrings
4. Write simple test:
   ```python
   # Test: Can we download data?
   df, ticker, err = download_data("AAPL")
   assert err is None, "Should succeed for valid ticker"
   assert df is not None, "Should return data"
   assert len(df) > 0, "Should have rows"
   ```
5. **Verify:** Run test, fix if broken
6. **Move on:** Only proceed when data layer works

**Why This Works:**
- Small, focused task
- Easy to test
- Clear success criteria
- No dependencies on other modules

---

### Phase 2: Risk Layer (Core Functionality)

**Goal:** Get risk calculations working and tested.

**Steps:**
1. Create `astra/risk/metrics.py`
2. Copy risk functions from Stock_RAVA.py:
   - `calculate_returns()`
   - `calculate_volatility()`
   - `calculate_drawdown()`
   - `find_major_drawdowns()`
   - `calculate_recovery()`
   - `calculate_risk_metrics()`
3. Add type hints and docstrings
4. Write tests for each function:
   ```python
   # Test: Can we calculate returns?
   test_df = pd.DataFrame({
       'Close': [100, 110, 105, 120],
       'Date': pd.date_range('2024-01-01', periods=4)
   })
   result = calculate_returns(test_df)
   assert 'Daily_Return' in result.columns
   assert result['Daily_Return'].iloc[0] == 0.0  # First row should be 0
   ```
5. **Verify:** Each function tested independently
6. **Move on:** Only proceed when risk layer works

**Why This Works:**
- Each function is testable in isolation
- Can debug one function at a time
- Clear boundaries

---

### Phase 3: UI Layer (Presentation)

**Goal:** Wire UI to display results.

**Steps:**
1. Create `astra/ui/components.py`
2. Extract UI rendering functions:
   - `render_metrics_table()`
   - `render_charts()`
   - `render_drawdowns()`
3. Create `astra/ASTRA.py` (main app):
   ```python
   # ASTRA.py - ONLY UI wiring, no business logic
   import streamlit as st
   from data.loader import download_data, clean_data
   from risk.metrics import (
       calculate_returns, calculate_volatility,
       calculate_drawdown, find_major_drawdowns,
       calculate_recovery, calculate_risk_metrics
   )
   from ui.components import render_dashboard
   
   def main():
       # UI input
       ticker = st.text_input("Ticker")
       
       if st.button("Analyze"):
           # Data layer
           raw_data, actual_ticker, error = download_data(ticker)
           if error:
               st.error(error)
               return
           
           df = clean_data(raw_data)
           
           # Risk layer
           df = calculate_returns(df)
           df = calculate_volatility(df)
           df = calculate_drawdown(df)
           drawdowns = find_major_drawdowns(df)
           recovery = calculate_recovery(df, drawdowns)
           metrics = calculate_risk_metrics(df, actual_ticker)
           
           # UI layer
           render_dashboard(df, metrics, actual_ticker, recovery)
   ```
4. **Verify:** Run app, check it works
5. **Move on:** Only proceed when UI works

**Why This Works:**
- Main file is just "wiring" - easy to read
- Business logic is in modules - easy to test
- Clear separation of concerns

---

### Phase 4: Analysis Features (Incremental)

**Goal:** Add one feature at a time.

**Example: Adding Technical Indicators**

1. Create `astra/analysis/indicators.py`
2. Add `calculate_factors()` function:
   ```python
   def calculate_factors(df: pd.DataFrame) -> pd.DataFrame:
       """
       Add technical indicators to dataframe.
       
       Contract:
       - Input: df with 'Close' column
       - Output: df with added columns: 'MA_20', 'MA_100', 'Mom_20d'
       - Side effects: None
       """
       df = df.copy()  # Don't modify input
       df['MA_20'] = df['Close'].rolling(20).mean()
       df['MA_100'] = df['Close'].rolling(100).mean()
       df['Mom_20d'] = df['Close'].pct_change(20) * 100
       return df
   ```
3. Write test:
   ```python
   test_df = create_test_dataframe()
   result = calculate_factors(test_df)
   assert 'MA_20' in result.columns
   assert 'MA_100' in result.columns
   assert 'Mom_20d' in result.columns
   ```
4. Wire into `ASTRA.py`:
   ```python
   from analysis.indicators import calculate_factors
   
   # In main():
   df = calculate_factors(df)  # Add after risk calculations
   ```
5. **Verify:** Test function, then test in app
6. **Move on:** Only proceed when feature works

**Why This Works:**
- One feature = one module = one test
- Easy to add/remove features
- No "big bang" integration

---

## Testing Strategy

### Test Structure

```
astra/
├── tests/
│   ├── test_data_loader.py      # Test data/loader.py
│   ├── test_risk_metrics.py     # Test risk/metrics.py
│   ├── test_indicators.py       # Test analysis/indicators.py
│   └── test_integration.py      # Test full flow
```

### Test Philosophy

**Rule:** Test at the boundary where data enters/leaves a module.

**Example: Testing Data Loader**

```python
# tests/test_data_loader.py

def test_download_data_success():
    """Test: Can download valid ticker?"""
    df, ticker, err = download_data("AAPL")
    assert err is None
    assert df is not None
    assert len(df) > 0
    assert 'Close' in df.columns

def test_download_data_invalid_ticker():
    """Test: Does it handle invalid ticker gracefully?"""
    df, ticker, err = download_data("INVALID_TICKER_XYZ")
    assert err is not None  # Should return error
    assert df is None  # Should return None for data

def test_clean_data():
    """Test: Does cleaning work?"""
    raw_data = create_mock_raw_data()
    cleaned = clean_data(raw_data)
    assert 'Date' in cleaned.columns
    assert 'Close' in cleaned.columns
    assert cleaned['Close'].isna().sum() == 0  # No NaN values
```

**Why This Works:**
- Each test is small and focused
- Easy to understand what's being tested
- Easy to debug when test fails

---

## Debugging Strategy

### How to Debug Modular Code

**Scenario:** "The Sharpe ratio is wrong!"

**Step 1: Identify the Module**
- Sharpe ratio comes from `risk/metrics.py` → `calculate_risk_metrics()`

**Step 2: Check the Input**
```python
# In ASTRA.py, add debug print:
metrics = calculate_risk_metrics(df, ticker)
st.write("DEBUG: Input to calculate_risk_metrics:")
st.write(f"  - DataFrame shape: {df.shape}")
st.write(f"  - Has Daily_Return: {'Daily_Return' in df.columns}")
st.write(f"  - Daily_Return stats: {df['Daily_Return'].describe()}")
```

**Step 3: Check the Function**
```python
# In risk/metrics.py, add debug print:
def calculate_risk_metrics(df, ticker):
    returns = df['Daily_Return']
    mean_return = returns.mean()
    std_return = returns.std()
    sharpe = (mean_return * 252) / (std_return * np.sqrt(252))
    
    # DEBUG: Print intermediate values
    print(f"DEBUG calculate_risk_metrics:")
    print(f"  - mean_return: {mean_return}")
    print(f"  - std_return: {std_return}")
    print(f"  - sharpe: {sharpe}")
    
    return {'sharpe': sharpe, ...}
```

**Step 4: Trace Backwards**
- If Sharpe is wrong, check if `returns` is correct
- If `returns` is wrong, check `calculate_returns()`
- If `calculate_returns()` is wrong, check input `df`

**Why This Works:**
- Clear boundaries = clear debugging path
- Each module can be tested in isolation
- No need to understand entire codebase to fix one bug

---

## Code Organization Rules

### Rule 1: No Circular Dependencies

**Bad:**
```python
# data/loader.py
from risk.metrics import calculate_returns  # ❌ Data depends on risk

# risk/metrics.py
from data.loader import clean_data  # ❌ Risk depends on data
```

**Good:**
```python
# data/loader.py
# No imports from risk/ or analysis/  # ✅ Data is independent

# risk/metrics.py
# No imports from data/ or analysis/  # ✅ Risk only needs pandas/numpy

# ASTRA.py
from data.loader import download_data  # ✅ Main app imports everything
from risk.metrics import calculate_returns
```

**Why:** Circular dependencies create "spaghetti" - you can't understand one module without understanding the other.

---

### Rule 2: Functions Are Pure (When Possible)

**Pure Function:** Same input → same output, no side effects.

**Bad:**
```python
# Global state - unpredictable
current_ticker = None

def calculate_metrics():
    global current_ticker  # ❌ Hidden dependency
    # ...
```

**Good:**
```python
def calculate_metrics(df, ticker):
    # ✅ All inputs are explicit
    # ✅ No global state
    # ✅ Same (df, ticker) → same result
    pass
```

**Why:** Pure functions are easy to test and debug. You know exactly what they need.

---

### Rule 3: One Function, One Job

**Bad:**
```python
def process_and_display(ticker):
    # Downloads data
    data = download_data(ticker)
    # Calculates metrics
    metrics = calculate_metrics(data)
    # Displays results
    st.write(metrics)
    # ❌ Does three things - hard to test, hard to debug
```

**Good:**
```python
def download_data(ticker):  # ✅ One job: download
    pass

def calculate_metrics(df):  # ✅ One job: calculate
    pass

def display_metrics(metrics):  # ✅ One job: display
    st.write(metrics)

# In main():
data = download_data(ticker)
metrics = calculate_metrics(data)
display_metrics(metrics)
```

**Why:** Small functions are easy to understand, test, and fix.

---

### Rule 4: Type Hints Everywhere

**Bad:**
```python
def calculate_returns(df):
    # ❌ What is df? What does this return?
    return df
```

**Good:**
```python
def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily returns from price data.
    
    Args:
        df: DataFrame with 'Close' column
    
    Returns:
        DataFrame with added 'Daily_Return' column
    """
    return df
```

**Why:** Type hints are documentation. They tell testers/debuggers what to expect.

---

## Implementation Checklist

### Before Writing Code

- [ ] Identify which module this belongs to
- [ ] Write the function signature (name, inputs, outputs)
- [ ] Write a docstring explaining the contract
- [ ] Write a simple test case

### While Writing Code

- [ ] Keep function small (< 50 lines if possible)
- [ ] No global state (pass everything as parameters)
- [ ] Add type hints
- [ ] Add error handling (return errors, don't crash silently)

### After Writing Code

- [ ] Run the test
- [ ] Fix any issues
- [ ] Check: Can I explain this function in one sentence?
- [ ] Check: Can I test this function without running the whole app?

---

## Example: Complete Module Implementation

### Module: `data/loader.py`

```python
"""
Data loading and cleaning module.

This module handles:
- Downloading stock data from Yahoo Finance
- Cleaning and preparing data for analysis
"""

import pandas as pd
import yfinance as yf
from typing import Tuple, Optional

@st.cache_data(ttl=3600)
def download_data(
    ticker: str,
    start_date: Optional[str] = None
) -> Tuple[Optional[pd.DataFrame], str, Optional[str]]:
    """
    Download historical stock data from Yahoo Finance.
    
    Contract:
    - Input: ticker (str), optional start_date (str 'YYYY-MM-DD')
    - Output: (dataframe, actual_ticker, error_message)
      - Success: (DataFrame, ticker, None)
      - Failure: (None, ticker, "error message")
    - Side effects: None (cached by Streamlit)
    
    Example:
        df, ticker, err = download_data("AAPL")
        if err:
            st.error(err)
        else:
            st.success(f"Downloaded {len(df)} rows")
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        if start_date:
            hist = ticker_obj.history(start=start_date)
        else:
            hist = ticker_obj.history(period="max")
        
        if hist.empty:
            return None, ticker, f"No data available for {ticker}"
        
        return hist, ticker, None
    
    except Exception as e:
        return None, ticker, f"Error downloading {ticker}: {str(e)}"


def clean_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare raw stock data for analysis.
    
    Contract:
    - Input: DataFrame from download_data() (yfinance format)
    - Output: DataFrame with columns: ['Date', 'Close', ...]
    - Side effects: None (returns new DataFrame)
    - Raises: ValueError if required columns missing
    
    Example:
        df = clean_data(raw_data)
        assert 'Date' in df.columns
        assert 'Close' in df.columns
    """
    if raw_data.empty:
        raise ValueError("Input dataframe is empty")
    
    df = raw_data.copy()
    df.reset_index(inplace=True)
    
    # Ensure Date column exists
    if 'Date' not in df.columns:
        raise ValueError("Input dataframe missing 'Date' column")
    
    # Ensure Close column exists
    if 'Close' not in df.columns:
        raise ValueError("Input dataframe missing 'Close' column")
    
    # Remove NaN values
    df = df.dropna(subset=['Close'])
    
    # Sort by date
    df = df.sort_values('Date')
    
    return df
```

**Why This is Good:**
- Clear contracts (what goes in, what comes out)
- Type hints everywhere
- Error handling (returns errors, doesn't crash)
- Docstrings explain usage
- Easy to test (pure functions)

---

## Summary: The Modular Approach

### What Makes Code "Modular"?

1. **Clear Boundaries** - Each module has one job
2. **Explicit Contracts** - Functions declare inputs/outputs clearly
3. **No Hidden Dependencies** - Everything is passed as parameters
4. **Testable in Isolation** - Can test one module without others
5. **Easy to Debug** - Can trace data flow step by step

### What Makes Code "Spaghetti"?

1. **Unclear Boundaries** - Functions do multiple things
2. **Hidden Dependencies** - Global state, side effects
3. **Circular Dependencies** - Module A needs B, B needs A
4. **Hard to Test** - Need entire app running to test one function
5. **Hard to Debug** - Can't trace where data comes from

### The Golden Rule

**If a human tester/debugger can't understand a module in 5 minutes, it's too complex.**

Break it down. Make it smaller. Make it clearer.

---

## Next Steps

1. **Start with data/loader.py** - Get data loading working
2. **Test it** - Write simple tests
3. **Move to risk/metrics.py** - Get risk calculations working
4. **Test it** - Write simple tests
5. **Wire it in ASTRA.py** - Connect modules together
6. **Test the full flow** - Integration test
7. **Add features incrementally** - One module at a time

**Remember:** Small, focused modules are easier to write, test, debug, and maintain than one giant file.

---

**Last Updated:** 2025-11-16  
**Status:** Implementation Guide  
**Related:** See `ASTRA_ENHANCEMENT_PLAN.md` for project phases (Phase A/B/C), this document covers implementation steps (Phase 1/2/3)  
**Purpose:** Ensure code is maintainable, testable, and debuggable

