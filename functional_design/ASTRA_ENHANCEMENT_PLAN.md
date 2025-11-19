# ASTRA Enhancement Plan
## Advanced Stock Risk Analysis

**Project Evolution:** Stock RAVA → **ASTRA** (Advanced Stock Risk Analysis)

---

## ⚠️ CRITICAL: Implementation Rules

**DO NOT MODIFY EXISTING FILES:**
- ❌ **DO NOT** modify `Stock_RAVA.py`
- ❌ **DO NOT** modify `requirements_app.txt`
- ❌ **DO NOT** modify any existing shell scripts
- ❌ **DO NOT** modify `README_LINUX.md`

**CREATE NEW FILES IN SUBDIRECTORY:**
- ✅ **CREATE** `astra/` subdirectory
- ✅ **COPY** `Stock_RAVA.py` → `astra/ASTRA.py`
- ✅ **COPY** `requirements_app.txt` → `astra/requirements.txt`
- ✅ **MODIFY** only files in `astra/` directory

**Result:** Both Stock RAVA (original) and ASTRA (enhanced) coexist independently.

**⚠️ CODING STANDARDS:**
- ✅ **MUST FOLLOW** `standards/CODING_STANDARDS.md` - All ASTRA code must follow modular coding standards
- ✅ **REFERENCE** `ASTRA_MODULAR_APPROACH.md` - Detailed explanation of modular approach
- ❌ **FORBIDDEN:** Writing code that violates coding standards (see checklists in standards/CODING_STANDARDS.md)

---

## Overview

**Key Principles:**
- **DO NOT modify existing `Stock_RAVA.py`** - Keep original intact
- **Create new subdirectory** for ASTRA implementation
- **Copy and enhance** - Start from Stock_RAVA.py as base
- PyQuant News provides educational content and code patterns (not a library)

**Directory Structure:**
```
stock-rava/
├── Stock_RAVA.py              # ORIGINAL - DO NOT MODIFY
├── requirements_app.txt        # ORIGINAL - DO NOT MODIFY
├── astra/                     # ASTRA implementation & documentation
│   ├── ASTRA.py               # Enhanced version (copy of Stock_RAVA.py)
│   ├── requirements.txt       # ASTRA-specific requirements
│   ├── ASTRA_ENHANCEMENT_PLAN.md   # This planning document
│   ├── README.md              # ASTRA documentation
│   └── *.drawio               # Architecture diagrams
└── ... (other existing files)
```

**Related Documentation:**
- **`standards/CODING_STANDARDS.md`** - ⚠️ **MANDATORY** - Coding standards all implementations must follow
- **`ASTRA_MODULAR_APPROACH.md`** - Detailed explanation of modular coding philosophy
- **`standards/AUDIT_GUIDE.md`** - How to verify compliance with coding standards
- **`standards/VARIATIONS.md`** - Documented variations from standards (with justification)
- **`README.md`** - Overview and quick start guide
- Architecture diagrams are in `.drawio` files (open with draw.io)

---

## Current State: Stock RAVA

### Existing Features
- ✅ Risk metrics calculation (Sharpe, Sortino, CAGR, volatility, max drawdown)
- ✅ Historical volatility analysis (30, 60, 252-day rolling)
- ✅ Drawdown analysis and recovery time calculations
- ✅ Comprehensive visualization dashboard
- ✅ Data download from Yahoo Finance (yfinance)
- ✅ Single-page Streamlit interface

### Current Dependencies
- `streamlit` - Web interface
- `yfinance` - Stock data
- `ffn` - Drawdown calculations
- `quantstats` - Risk metrics
- `pandas`, `numpy` - Data processing
- `matplotlib` - Visualization

### Limitations
- ❌ No strategy backtesting capabilities
- ❌ Limited technical indicators
- ❌ No forward-looking risk analysis (Monte Carlo)
- ❌ Single-page UI (long scroll)
- ❌ No benchmark comparison
- ❌ Monolithic code structure

---

## Enhancement Roadmap

**Note:** This section uses "Phase 1/2" terminology from the original plan. The **REVISED** section below (see "Implementation Priority") uses "Phase A/B/C" which is the current active plan. Phase 1/2 information is kept for reference but Phase A/B/C should be followed for implementation.

### Phase 1: Quick Wins (Low Complexity, High Impact) [REFERENCE - See Phase A/B/C below]

#### 1.1 UI Improvements with Tabs
**Goal:** Better user experience with organized interface

**Implementation:**
- Replace long vertical scroll with `st.tabs`
- Organize content into logical sections:
  - **Risk Dashboard** - Current main view
  - **Detailed Metrics** - Expanded metrics table
  - **Drawdowns** - Major drawdown events
  - **Recovery Analysis** - Recovery time analysis
  - **Data Export** - Download options

**Files to Create/Modify:**
- `astra/ASTRA.py` - Copy from `Stock_RAVA.py`, then modify main function (reorganize UI)
- **DO NOT modify:** `Stock_RAVA.py` (keep original intact)

**Impact:** Better UX, easier navigation, less scrolling

---

#### 1.2 Basic Technical Indicators
**Goal:** Add fundamental technical analysis tools

**Implementation:**
- Moving Averages (20-day, 100-day)
- 20-day Momentum
- Simple price/MA overlays in dashboard

**New Function:**
```python
def calculate_factors(df):
    """Calculate technical indicators"""
    # 20-day momentum (%)
    df["Mom_20d"] = df["Close"].pct_change(20) * 100
    
    # Moving averages
    df["MA_20"] = df["Close"].rolling(20).mean()
    df["MA_100"] = df["Close"].rolling(100).mean()
    
    return df
```

**Files to Create/Modify:**
- `astra/ASTRA.py` - Add `calculate_factors()`, update `create_dashboard()`
- **DO NOT modify:** `Stock_RAVA.py` (keep original intact)

**Dependencies:** None (use pandas/numpy)

**Impact:** More comprehensive analysis, professional indicators

---

### Phase 2: Medium Complexity Features [REFERENCE - See Phase A/B/C below]

#### 2.1 Strategy Backtesting Tab
**Goal:** Enable users to test simple trading strategies

**Implementation:**
- Add new tab: "Simple Strategies"
- Moving Average Crossover backtest:
  - Short MA (default: 20 days)
  - Long MA (default: 100 days)
  - Generate buy/sell signals
  - Calculate strategy returns
  - Compare with buy-and-hold

**Features:**
- Interactive sliders for MA windows
- Equity curve comparison (Strategy vs Buy & Hold)
- Performance metrics comparison
- Signal visualization

**Example Implementation (FIXED):**
```python
with strategy_tab:
    st.subheader("Simple Moving Average Strategy")
    
    short_win = st.slider("Short MA window", 5, 50, 20)
    long_win = st.slider("Long MA window", 20, 250, 100)
    
    prices = df.set_index("Date")["Close"]
    short_ma = prices.rolling(short_win).mean()
    long_ma = prices.rolling(long_win).mean()
    
    signal = (short_ma > long_ma).astype(int)
    strategy_ret = signal.shift(1) * df["Daily_Return"]
    
    # Normalize both to starting value of 1 for fair comparison
    strategy_equity = (1 + strategy_ret).cumprod()
    buyhold_equity = prices / prices.iloc[0]
    
    # Align indices
    common_idx = strategy_equity.index.intersection(buyhold_equity.index)
    strategy_equity = strategy_equity.loc[common_idx]
    buyhold_equity = buyhold_equity.loc[common_idx]
    
    # Calculate stats on normalized equity series
    strat_stats = ffn.calc_stats(strategy_equity)
    bench_stats = ffn.calc_stats(buyhold_equity)
    
    # Display comparison
    col1, col2 = st.columns(2)
    col1.metric("Strategy CAGR", f"{strat_stats.cagr*100:.2f}%")
    col2.metric("Buy & Hold CAGR", f"{bench_stats.cagr*100:.2f}%")
    
    # Equity curve chart
    comparison_df = pd.DataFrame({
        "Strategy": strategy_equity,
        "Buy & Hold": buyhold_equity
    })
    st.line_chart(comparison_df)
```

**Note:** This is simplified backtesting for demo purposes. Real backtesting would include:
- Transaction costs
- Slippage
- Position sizing
- Risk management rules
- Proper signal timing and execution delays

**Keep this disclaimer visible in the UI** so users understand it's educational/demo quality, not production-grade.

**Files to Create/Modify:**
- `astra/ASTRA.py` - Add `strategy_tab`, backtest functions
- **DO NOT modify:** `Stock_RAVA.py` (keep original intact)

**Dependencies:** None (use existing ffn, pandas)

**Impact:** Users can test strategies, adds significant value

**Reference:** Based on PyQuant News "Creating and Backtesting Trading Strategies" and "Basic Trading Algorithms in Python"

---

#### 2.2 Monte Carlo Simulation Tab
**Goal:** Forward-looking risk analysis using historical data

**Implementation:**
- Add new tab: "Monte Carlo Simulation"
- Simulate future price paths using historical return distribution
- Calculate forward risk metrics:
  - Value at Risk (VaR)
  - Expected shortfall
  - Price distribution percentiles
- Visualize multiple simulation paths

**Features:**
- Configurable simulation horizon (30-252 days)
- Adjustable number of simulations (100-2000)
- Distribution analysis
- Risk metrics at different confidence levels

**Example Implementation (FIXED):**
```python
with sim_tab:
    st.subheader("Monte Carlo Price Path Simulation")
    
    horizon_days = st.slider("Horizon (trading days)", 30, 252, 126)
    n_sims = st.slider("Number of simulations", 100, 2000, 500, step=100)
    
    mu = df["Daily_Return"].mean()
    sigma = df["Daily_Return"].std()
    last_price = df["Close"].iloc[-1]
    
    # Generate simulation paths (log-normal process)
    sim_paths = np.zeros((horizon_days, n_sims))
    for i in range(n_sims):
        shocks = np.random.normal(mu, sigma, horizon_days)
        sim_paths[:, i] = last_price * np.exp(np.cumsum(shocks))
    
    # Calculate VaR (5th percentile of final prices)
    final_prices = sim_paths[-1, :]
    var_5_price = np.percentile(final_prices, 5)
    var_5_loss_pct = (last_price - var_5_price) / last_price * 100
    
    # Display metrics
    st.metric("5% Worst-Case Loss (VaR)", f"{var_5_loss_pct:.2f}%")
    st.metric("5th Percentile Price", f"${var_5_price:.2f}")
    
    # Show sample of paths (e.g., first 50 for performance)
    sample_paths = sim_paths[:, :min(50, n_sims)]
    st.line_chart(pd.DataFrame(sample_paths.T, columns=range(sample_paths.shape[0])))
```

**Note:** This is simplified Monte Carlo for demo purposes. Real risk modeling would include:
- More sophisticated return distributions
- Volatility clustering (GARCH models)
- Correlation with market factors
- Multiple scenarios and stress testing

**Files to Create/Modify:**
- `astra/ASTRA.py` - Add `sim_tab`, `monte_carlo_simulation()` function
- **DO NOT modify:** `Stock_RAVA.py` (keep original intact)

**Dependencies:** None (use numpy)

**Impact:** Forward-looking risk analysis, professional feature

**Reference:** Based on PyQuant News "Power of Monte Carlo Simulations in Finance"

---

---

### Phase C: Light Refactor (Only If Needed) [REFERENCE - See Phase A/B/C below]

**Philosophy:** Simple structure, not enterprise architecture. Refactor only when code becomes hard to maintain.

#### Light Modular Structure
**Goal:** Better organization without over-engineering

**Proposed Structure (Simple):**
```
stock-rava/
├── Stock_RAVA.py          # ORIGINAL - DO NOT MODIFY
├── requirements_app.txt    # ORIGINAL - DO NOT MODIFY
├── astra/                 # NEW - ASTRA enhanced version
│   ├── ASTRA.py           # Main Streamlit app
│   ├── core_data.py       # download_data, clean_data
│   ├── core_risk.py       # returns, volatility, drawdown, risk_metrics
│   ├── core_factors.py    # indicators, strategies, Monte Carlo
│   ├── requirements.txt   # ASTRA-specific requirements
│   └── README.md          # ASTRA documentation
└── ... (other existing files)
```

**Benefits:**
- Simple to navigate (only 3 helper modules)
- Easy to maintain
- Enough structure for reuse
- Not over-engineered

**When to Refactor:**
- Only if `ASTRA.py` becomes > 800 lines
- Only if you find yourself scrolling too much
- Only if you need to reuse functions elsewhere

**Files to Create (Only if refactoring):**
- `astra/core_data.py`
- `astra/core_risk.py`
- `astra/core_factors.py`

**Files to Reference (DO NOT MODIFY):**
- `Stock_RAVA.py` - Use as reference/base for ASTRA
- `requirements_app.txt` - Use as base for astra/requirements.txt

**Impact:** Cleaner code without unnecessary complexity

---

#### Add Tests Early (Not in Phase 4)

**Goal:** Catch bugs before they compound

**Critical Functions to Test First:**
- `find_major_drawdowns` - Complex logic, easy to break
- `calculate_recovery` - Complex logic, easy to break
- New feature (Strategy or Monte Carlo) - Verify correctness

**Simple Test Structure (Concrete Example):**
```python
# Option 1: Inline in ASTRA.py (simplest)
if __name__ == "__main__":
    # Quick smoke tests
    import pandas as pd
    import numpy as np
    
    # Create simple test data
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    prices = 100 * (1 + np.random.randn(100).cumsum() * 0.01)
    test_df = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Daily_Return': np.diff(prices, prepend=prices[0]) / prices
    })
    
    # Test find_major_drawdowns
    drawdowns = find_major_drawdowns(test_df, threshold=20)
    assert len(drawdowns) >= 0, "Should return list (may be empty)"
    if len(drawdowns) > 0:
        assert all('start_date' in d for d in drawdowns), "Drawdowns should have start_date"
    
    # Test calculate_recovery
    if len(drawdowns) > 0:
        recovery = calculate_recovery(test_df, drawdowns)
        assert len(recovery) == len(drawdowns), "Recovery count should match drawdowns"
    
    print("✓ Basic tests passed")

# Option 2: Separate test file (if you want pytest later)
# astra/test_core.py
# Same code, but can run with: pytest astra/test_core.py
```

**Dependencies:** None (use simple assert statements) or `pytest` (optional, only if you want test infrastructure)

**Impact:** Catch bugs early, ensure reliability

**Timing:** Add tests when implementing Phase B, not at the end

---

## Implementation Priority (REVISED - Based on Client Feedback)

### Realistic, Focused Approach

**Key Principle:** Build a clean showcase tool, not an enterprise framework. Focus on visible value, not perfect architecture.

**Note on Phase Names:** These are action-oriented phases focused on shipping. Some prefer "Sprint 1/2/3" terminology for time-boxing, but "Phase A/B/C" works fine - the important part is executing, not naming.

### Phase A: Minimal but Real v2 (ASTRA) - START HERE

**Goal:** Create a cleaner, richer version with low effort. Good enough for demo/showcase.

1. **Create `astra/ASTRA.py`** - Copy from `Stock_RAVA.py`, update titles
2. **Add `st.tabs`** - Reorganize UI into tabs:
   - `["Risk Dashboard", "Metrics", "Drawdowns", "Recovery", "Data"]`
   - Immediate visible improvement
3. **Add `calculate_factors()`** - Basic indicators:
   - MA20, MA100 (moving averages)
   - 20-day momentum
   - Plot in main chart or dedicated subplot
   - No new dependencies

**Time Estimate:** 4-6 hours  
**Result:** ASTRA is visibly better than Stock RAVA with minimal effort

---

### Phase B: Pick ONE Big Feature

**Decision:** Choose ONE, not both:
- **Strategy Backtesting** (if audience is traders/quants)
- **Monte Carlo Simulation** (if audience is risk/portfolio/educational)

**While implementing:**
- Write 2-3 small tests for critical functions:
  - `find_major_drawdowns`
  - `calculate_recovery`
  - New feature correctness
- Don't need full pytest infrastructure yet - simple test block is fine

**Time Estimate:** 8-12 hours per feature  
**Result:** One substantial feature that adds real value

---

### Phase C: Light Refactor (If Needed)

**Instead of full package structure, use simple modules:**

```
astra/
  ASTRA.py          # Main Streamlit wiring
  core_data.py      # download_data, clean_data
  core_risk.py      # returns, vol, drawdowns, risk_metrics
  core_factors.py   # indicators, strategies, Monte Carlo helpers
```

**Only 3 helper modules** - enough structure, not over-engineered.

**Time Estimate:** 4-6 hours (only if codebase becomes unwieldy)

---

### What to SKIP (For Now)

**These are NOT in the current plan - they're backlog/future ideas:**

- ❌ Advanced indicators (RSI, MACD, ATR, Bollinger Bands) - Future enhancement
- ❌ Benchmark comparison - Future enhancement
- ❌ Save/Load presets - Future enhancement
- ❌ Full modular package structure - Only refactor if code becomes unwieldy
- ❌ Full unit test suite - Add tests incrementally with features

**Rationale:** Focus on features that deliver visible value. Don't start Phase 3 until Phase A + Phase B are complete and proven.

---

## Dependencies Assessment

### No New Dependencies Needed For:
- ✅ UI tabs (Streamlit built-in)
- ✅ Basic indicators (pandas/numpy)
- ✅ Strategy backtesting (use existing ffn)
- ✅ Monte Carlo (numpy)
- ✅ Benchmark comparison (use existing yfinance)
- ✅ Presets (json built-in)

### Optional Dependencies:
- `ta` or `ta-lib` - For advanced technical indicators (RSI, MACD)
  - `ta` is lightweight and pure Python
  - `ta-lib` requires C library compilation
  - Recommendation: Use `ta` for easier installation
- `pytest` - For unit tests (development dependency)

---

## Files Impact Summary

### Files to Create (New ASTRA Implementation)
- `astra/ASTRA.py` - Copy from `Stock_RAVA.py`, then enhance incrementally
- `astra/requirements.txt` - Copy from `requirements_app.txt`, add optional dependencies
- `astra/README.md` - ASTRA-specific documentation
- `ASTRA_ENHANCEMENT_PLAN.md` - This planning document (already created)

### Files to Keep Intact (DO NOT MODIFY)
- `Stock_RAVA.py` - Original version, keep untouched
- `requirements_app.txt` - Original requirements, keep untouched
- All existing shell scripts - Keep as-is for Stock RAVA
- `README_LINUX.md` - Keep for Stock RAVA documentation

### Optional: Docker Version for ASTRA
- `astra_docker/` - New Docker setup for ASTRA (parallel to stock_rava_docker/)

### Files to Create (If Refactoring - Phase C Only)
- `astra/core_data.py` - Data loading and cleaning
- `astra/core_risk.py` - Risk calculations
- `astra/core_factors.py` - Indicators, strategies, simulations
- `astra/test_core.py` - Simple tests (or inline in ASTRA.py)
- `astra/requirements.txt` - ASTRA requirements
- `astra/README.md` - ASTRA documentation

**Note:** Only create these if code becomes unwieldy. Start with single `ASTRA.py` file.

---

## Success Criteria

### Functional
- ✅ All existing functionality maintained
- ✅ New features work correctly
- ✅ Performance remains acceptable
- ✅ No breaking changes to existing workflows

### Code Quality
- ✅ Code follows PyQuant "framework" philosophy
- ✅ Functions are reusable and testable
- ✅ Type hints and documentation added
- ✅ Modular structure (if refactored)

### User Experience
- ✅ UI is more organized and user-friendly
- ✅ Features are intuitive and well-documented
- ✅ Better navigation with tabs
- ✅ Professional appearance

### Documentation
- ✅ README updated with new features
- ✅ Code comments and docstrings enhanced
- ✅ Usage examples provided

---

## Implementation Approach (REVISED - Practical Steps)

### Step 1: Create ASTRA Directory Structure
```bash
mkdir -p astra
cp Stock_RAVA.py astra/ASTRA.py
cp requirements_app.txt astra/requirements.txt
```

### Step 2: Phase A - Minimal v2 (4-6 hours)
- Update page title to "ASTRA - Advanced Stock Risk Analysis"
- Reorganize UI with `st.tabs`:
  ```python
  risk_tab, metrics_tab, drawdown_tab, recovery_tab, data_tab = st.tabs([
      "Risk Dashboard", "Metrics", "Drawdowns", "Recovery", "Data"
  ])
  ```
- Add `calculate_factors()` function (MA20, MA100, momentum)
- Update dashboard to show indicators
- **Test:** Run ASTRA, verify all tabs work, indicators display correctly

### Step 3: Phase B - Pick ONE Feature (8-12 hours)
**Option 1: Strategy Backtesting**
- Add "Strategies" tab
- Implement MA crossover backtest
- Fix backtest calculation issues (normalize equity series, handle returns correctly)
- Add simple tests for backtest logic

**Option 2: Monte Carlo Simulation**
- Add "Monte Carlo" tab
- Implement price path simulation
- Calculate VaR and percentiles
- Add simple tests for simulation logic

**Decision:** Choose based on audience (traders → Strategy, risk/education → Monte Carlo)

### Step 4: Add Tests Early (2-3 hours)
- Write tests for `find_major_drawdowns` (critical, fragile function)
- Write tests for `calculate_recovery` (critical, fragile function)
- Test new feature (Strategy or Monte Carlo)
- Simple test structure - no need for full pytest setup yet

### Step 5: Phase C - Light Refactor (Only if needed, 4-6 hours)
- Only if code becomes hard to navigate
- Split into 3 simple modules: `core_data.py`, `core_risk.py`, `core_factors.py`
- Keep `ASTRA.py` as main Streamlit app
- Don't over-engineer with full package structure

## Next Steps (REVISED - Clear Action Plan)

### Immediate Actions (This Week)

1. **Create ASTRA structure** (30 minutes)
   ```bash
   mkdir -p astra
   cp Stock_RAVA.py astra/ASTRA.py
   cp requirements_app.txt astra/requirements.txt
   ```

2. **Phase A: Minimal v2** (4-6 hours)
   - Add tabs to reorganize UI
   - Add basic indicators (MA20, MA100, momentum)
   - Test and verify
   - **Result:** Working ASTRA v2 ready for demo

3. **Decide on Phase B feature** (5 minutes)
   - **If audience = traders/quants:** → Strategy Backtesting
   - **If audience = risk/portfolio/education:** → Monte Carlo Simulation
   - **Pick ONE, commit to it**

### Short-term (Next 1-2 Weeks)

4. **Phase B: Implement chosen feature** (8-12 hours)
   - Strategy Backtesting OR Monte Carlo (not both)
   - Fix any calculation issues
   - Add simple tests
   - **Result:** One substantial feature complete

5. **Add critical tests** (2-3 hours)
   - Test `find_major_drawdowns`
   - Test `calculate_recovery`
   - Test new feature

### Long-term (Only if needed)

6. **Phase C: Light refactor** (4-6 hours, only if code becomes unwieldy)
   - Split into 3 simple modules
   - Don't over-engineer

### What NOT to Do

- ❌ Don't try to implement everything at once
- ❌ Don't build full package structure yet
- ❌ Don't maintain two codebases long-term (eventually consolidate)
- ❌ Don't add features nobody asked for

### Realistic Timeline

- **Week 1:** Phase A complete (tabs + indicators)
- **Week 2-3:** Phase B complete (one big feature)
- **Week 4:** Tests + polish
- **Total:** ~20-25 hours of focused work

### Success Metrics

- ✅ ASTRA runs independently on different port
- ✅ UI is cleaner and more organized
- ✅ One substantial new feature works correctly
- ✅ Critical functions have tests
- ✅ Ready for demo/showcase

---

## References

- [PyQuant News - Free Python Resources](https://www.pyquantnews.com/free-python-resources)
- [Creating and Backtesting Trading Strategies](https://www.pyquantnews.com/free-python-resources)
- [Monte Carlo Simulations in Finance](https://www.pyquantnews.com/free-python-resources)
- [Implementing Technical Indicators in Python](https://www.pyquantnews.com/free-python-resources)

---

## Important Notes (REVISED)

### Critical Principles
- **DO NOT modify `Stock_RAVA.py`** - Keep original intact (frozen/legacy)
- **ASTRA is the future** - All new development happens in `astra/`
- **Create new `astra/` subdirectory** for all ASTRA work
- **Copy, don't move** - Start from copy of Stock_RAVA.py
- **Test independently** - ASTRA should run separately from Stock RAVA
- **Focus on visible value** - Build showcase tool, not enterprise framework
- **One feature at a time** - Don't try to do everything at once
- **Accept duplication** - Stock_RAVA is frozen, bugs fixed in ASTRA won't auto-fix RAVA

### Realistic Constraints
- **Time:** Plan for 20-25 hours total (not 40-80)
- **Scope:** Phase A + Phase B (one feature) is enough for v2
- **Architecture:** Keep it simple - refactor only if needed
- **Maintenance:** Long-term, consider consolidating to one codebase

### Technical Notes
- PyQuant News is educational content, not a library to import
- We're implementing industry-standard techniques
- Focus on practical, value-adding features
- Keep dependencies minimal (no new deps for core features)
- ASTRA can run on different port (e.g., 8502) to coexist with Stock RAVA
- Add tests early, not at the end

### File Naming & Versioning
- Original: `Stock_RAVA.py` (unchanged, becomes legacy/frozen)
- Enhanced: `astra/ASTRA.py` (new file, all future development)
- Both can coexist in same repository
- **Naming Decision:** Using "ASTRA" branding for now to clearly separate from original. Long-term, may consolidate to "Stock RAVA v2.0" or deprecate original, but starting separate is pragmatic for risk-free experimentation.

### Honest Assessment
- **This is a showcase/demo tool** - optimize for that, not enterprise architecture
- **Start simple** - single file is fine, refactor only when needed
- **Ship fast** - Phase A + Phase B is a complete v2
- **Iterate based on feedback** - Don't build features nobody asked for

---

## Future Ideas / Backlog (NOT in Current Plan)

**These are potential future enhancements, NOT part of Phase A/B/C. Don't start these until Phase A + Phase B are complete and proven.**

### Advanced Technical Indicators
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- ATR (Average True Range)
- Bollinger Bands
- **When:** Only after Phase A + Phase B are complete and you've used ASTRA for a while

### Benchmark Comparison
- Compare ticker with benchmark (^GSPC, etc.)
- Side-by-side metrics
- Correlation analysis
- **When:** Only if users request it

### Save/Load Presets
- Save analysis settings to JSON
- Load presets for quick analysis
- **When:** Only if workflow efficiency becomes an issue

**Decision Rule:** Don't start any of these until Phase A + Phase B are done, tested, and you've used ASTRA for a while. Focus on shipping, not feature creep.

---

**Last Updated:** 2025-11-16  
**Status:** Ready for Implementation - Phase A  
**Project:** Stock RAVA → ASTRA (Advanced Stock Risk Analysis)  
**Next Step:** `mkdir astra && cp Stock_RAVA.py astra/ASTRA.py` then implement Phase A

