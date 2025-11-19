# ASTRA Code Audit Guide
## How to Verify Compliance with Coding Standards

**Purpose:** This document provides tools and processes to audit ASTRA code and ensure it complies with `standards/CODING_STANDARDS.md`.

**When to Audit:**
- Before committing code
- During code review
- Before merging pull requests
- Periodically (weekly/monthly) for existing codebase

---

## Audit Methods

### Method 1: Automated Checks (Fast, Objective)

### Method 2: Manual Review (Thorough, Context-Aware)

### Method 3: Hybrid Approach (Recommended)

---

## Method 1: Automated Checks

### Setup Automated Tools

Create `astra/scripts/audit_code.py` to run automated checks:

```python
#!/usr/bin/env python3
"""
Automated code audit script for ASTRA.

Checks compliance with standards/CODING_STANDARDS.md

Usage:
    python scripts/audit_code.py
    python scripts/audit_code.py --file astra/data/loader.py
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class AuditIssue:
    file: str
    line: int
    rule: str
    severity: str  # "ERROR", "WARNING", "INFO"
    message: str

class CodeAuditor:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.issues: List[AuditIssue] = []
    
    def audit_file(self, file_path: Path) -> List[AuditIssue]:
        """Audit a single Python file."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                issues.append(AuditIssue(
                    file=str(file_path),
                    line=e.lineno or 0,
                    rule="SYNTAX_ERROR",
                    severity="ERROR",
                    message=f"Syntax error: {e.msg}"
                ))
                return issues
            
            # Run all checks
            issues.extend(self._check_type_hints(file_path, tree, lines))
            issues.extend(self._check_docstrings(file_path, tree, lines))
            issues.extend(self._check_function_length(file_path, tree, lines))
            issues.extend(self._check_global_state(file_path, tree, lines))
            issues.extend(self._check_module_structure(file_path, lines))
            issues.extend(self._check_error_handling(file_path, tree, lines))
            
        except Exception as e:
            issues.append(AuditIssue(
                file=str(file_path),
                line=0,
                rule="AUDIT_ERROR",
                severity="ERROR",
                message=f"Failed to audit file: {str(e)}"
            ))
        
        return issues
    
    def _check_type_hints(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[AuditIssue]:
        """Check: All functions have type hints (Rule #11)."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has return type hint
                if node.returns is None:
                    issues.append(AuditIssue(
                        file=str(file_path),
                        line=node.lineno,
                        rule="TYPE_HINTS",
                        severity="ERROR",
                        message=f"Function '{node.name}' missing return type hint"
                    ))
                
                # Check if all parameters have type hints
                for arg in node.args.args:
                    if arg.annotation is None:
                        issues.append(AuditIssue(
                            file=str(file_path),
                            line=node.lineno,
                            rule="TYPE_HINTS",
                            severity="ERROR",
                            message=f"Function '{node.name}' parameter '{arg.arg}' missing type hint"
                        ))
        
        return issues
    
    def _check_docstrings(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[AuditIssue]:
        """Check: All functions have docstrings (Rule #12)."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for docstring
                docstring = ast.get_docstring(node)
                if not docstring:
                    issues.append(AuditIssue(
                        file=str(file_path),
                        line=node.lineno,
                        rule="DOCSTRINGS",
                        severity="ERROR",
                        message=f"Function '{node.name}' missing docstring"
                    ))
                elif "Contract:" not in docstring:
                    issues.append(AuditIssue(
                        file=str(file_path),
                        line=node.lineno,
                        rule="DOCSTRINGS",
                        severity="WARNING",
                        message=f"Function '{node.name}' docstring missing 'Contract:' section"
                    ))
        
        return issues
    
    def _check_function_length(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[AuditIssue]:
        """Check: Functions < 50 lines (Rule #10)."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate function length (excluding docstring)
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                length = end_line - start_line
                
                if length > 50:
                    issues.append(AuditIssue(
                        file=str(file_path),
                        line=node.lineno,
                        rule="FUNCTION_LENGTH",
                        severity="WARNING",
                        message=f"Function '{node.name}' is {length} lines (limit: 50). Consider breaking it down."
                    ))
        
        return issues
    
    def _check_global_state(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[AuditIssue]:
        """Check: No global state for function inputs (Rule #4, Forbidden Pattern #1)."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for global statements
                for child in ast.walk(node):
                    if isinstance(child, ast.Global):
                        issues.append(AuditIssue(
                            file=str(file_path),
                            line=child.lineno,
                            rule="GLOBAL_STATE",
                            severity="ERROR",
                            message=f"Function '{node.name}' uses 'global' statement (forbidden pattern)"
                        ))
        
        return issues
    
    def _check_module_structure(self, file_path: Path, lines: List[str]) -> List[AuditIssue]:
        """Check: Module structure compliance (Rule #1)."""
        issues = []
        
        file_str = str(file_path)
        
        # Check if ASTRA.py has business logic (should only have UI wiring)
        if file_path.name == "ASTRA.py":
            # Look for calculation functions (heuristic: functions with "calculate" in name)
            for i, line in enumerate(lines, 1):
                if re.search(r'def\s+calculate_\w+', line):
                    issues.append(AuditIssue(
                        file=str(file_path),
                        line=i,
                        rule="MODULE_STRUCTURE",
                        severity="ERROR",
                        message="ASTRA.py should only contain UI wiring, not business logic"
                    ))
        
        # Check module size (Rule #10)
        if len(lines) > 1000:
            issues.append(AuditIssue(
                file=str(file_path),
                line=1,
                rule="MODULE_SIZE",
                severity="ERROR",
                message=f"File is {len(lines)} lines (limit: 1000). Refactor immediately."
            ))
        elif len(lines) > 500:
            issues.append(AuditIssue(
                file=str(file_path),
                line=1,
                rule="MODULE_SIZE",
                severity="WARNING",
                message=f"File is {len(lines)} lines (limit: 500). Consider splitting."
            ))
        
        return issues
    
    def _check_error_handling(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[AuditIssue]:
        """Check: Error handling patterns (Rule #8)."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for bare except clauses (forbidden)
                for child in ast.walk(node):
                    if isinstance(child, ast.ExceptHandler):
                        if child.type is None:  # bare except:
                            issues.append(AuditIssue(
                                file=str(file_path),
                                line=child.lineno,
                                rule="ERROR_HANDLING",
                                severity="WARNING",
                                message=f"Function '{node.name}' has bare 'except:' clause. Should specify exception type."
                            ))
        
        return issues
    
    def audit_directory(self, directory: Path) -> List[AuditIssue]:
        """Audit all Python files in directory."""
        all_issues = []
        
        for py_file in directory.rglob("*.py"):
            # Skip test files and scripts
            if "test_" in py_file.name or "scripts" in str(py_file):
                continue
            
            issues = self.audit_file(py_file)
            all_issues.extend(issues)
        
        return all_issues
    
    def print_report(self, issues: List[AuditIssue]):
        """Print audit report."""
        if not issues:
            print("✅ No issues found. Code complies with standards.")
            return
        
        # Group by severity
        errors = [i for i in issues if i.severity == "ERROR"]
        warnings = [i for i in issues if i.severity == "WARNING"]
        info = [i for i in issues if i.severity == "INFO"]
        
        print(f"\n📊 Audit Report")
        print(f"{'='*60}")
        print(f"Total Issues: {len(issues)}")
        print(f"  ❌ Errors: {len(errors)}")
        print(f"  ⚠️  Warnings: {len(warnings)}")
        print(f"  ℹ️  Info: {len(info)}")
        print(f"{'='*60}\n")
        
        # Print errors
        if errors:
            print("❌ ERRORS (Must Fix):")
            for issue in errors:
                print(f"  {issue.file}:{issue.line} - {issue.rule}")
                print(f"    {issue.message}\n")
        
        # Print warnings
        if warnings:
            print("⚠️  WARNINGS (Should Fix):")
            for issue in warnings:
                print(f"  {issue.file}:{issue.line} - {issue.rule}")
                print(f"    {issue.message}\n")
        
        # Exit with error code if errors found
        if errors:
            sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit ASTRA code for standards compliance")
    parser.add_argument("--file", help="Audit specific file")
    parser.add_argument("--dir", default="astra", help="Directory to audit (default: astra)")
    
    args = parser.parse_args()
    
    root_dir = Path(args.dir)
    auditor = CodeAuditor(root_dir)
    
    if args.file:
        issues = auditor.audit_file(Path(args.file))
    else:
        issues = auditor.audit_directory(root_dir)
    
    auditor.print_report(issues)

if __name__ == "__main__":
    main()
```

### Using Automated Checks

```bash
# Audit entire astra/ directory
python astra/scripts/audit_code.py

# Audit specific file
python astra/scripts/audit_code.py --file astra/data/loader.py

# Exit code: 0 if no errors, 1 if errors found (for CI/CD)
```

---

## Method 2: Manual Review Checklist

### Pre-Commit Review Checklist

**Before committing code, manually verify:**

#### Module Structure (Rule #1)
- [ ] Code is in correct module (data/risk/analysis/ui)
- [ ] ASTRA.py contains only UI wiring (no business logic)
- [ ] No circular dependencies between modules
- [ ] Module has one clear responsibility

#### Function Contracts (Rule #2)
- [ ] Every function has type hints for all parameters
- [ ] Every function has return type hint
- [ ] Every function has docstring with "Contract:" section
- [ ] Docstring explains inputs, outputs, errors, side effects

#### Code Size (Rule #10)
- [ ] No function > 50 lines
- [ ] No module > 500 lines
- [ ] No file > 1000 lines

#### Dependencies (Rule #4)
- [ ] No global variables used as function inputs
- [ ] All dependencies passed as parameters
- [ ] No hidden side effects

#### Error Handling (Rule #8)
- [ ] Functions return errors explicitly (tuple pattern)
- [ ] No bare `except:` clauses
- [ ] Errors are descriptive

#### Testing (Rule #9)
- [ ] Test file exists for module (test_*.py)
- [ ] Success case tested
- [ ] Error case tested
- [ ] Function can be tested in isolation

#### Documentation (Rule #12)
- [ ] Module has docstring explaining purpose
- [ ] Functions have docstrings with contracts
- [ ] Complex logic has inline comments

---

## Method 3: Hybrid Approach (Recommended)

### Step 1: Run Automated Checks

```bash
# Run automated audit
python astra/scripts/audit_code.py > audit_report.txt

# Review report
cat audit_report.txt
```

**Action:** Fix all ERRORS. Review WARNINGS.

### Step 2: Manual Review for Context

Automated checks can't catch everything. Manually review:

#### Check Data Flow (Rule #5)
- [ ] Can trace data from input → processing → output
- [ ] No circular dependencies
- [ ] Linear flow (A → B → C)

#### Check One Responsibility (Rule #3)
- [ ] Can describe module purpose in one sentence
- [ ] Can describe function purpose in one sentence
- [ ] Module doesn't do multiple unrelated things

#### Check Testability (Rule #9)
- [ ] Can test function without running entire app
- [ ] No hard dependencies on Streamlit in business logic
- [ ] Functions are pure (when possible)

#### Check Incremental Implementation (Rule #6)
- [ ] Module was built and tested incrementally
- [ ] Each function tested before moving on
- [ ] Not a "big bang" implementation

### Step 3: Document Variations

If code deviates from standards, document why:

**Create `standards/VARIATIONS.md`:**

```markdown
# Documented Variations from Coding Standards

## Variation #1: [Date]

**File:** `astra/analysis/monte_carlo.py`
**Function:** `run_simulation()`
**Standard Violated:** Rule #10 (Function length > 50 lines)
**Reason:** Monte Carlo simulation requires 65 lines of setup/validation logic. Breaking it down further would reduce readability.
**Status:** ACCEPTED (with review)
**Reviewer:** [Name]
**Date:** [Date]

## Variation #2: [Date]

**File:** `astra/data/loader.py`
**Function:** `download_data()`
**Standard Violated:** Rule #8 (Uses exception instead of error return)
**Reason:** yfinance library raises exceptions. Wrapping in try/except and converting to error return pattern.
**Status:** FIXED
**Date:** [Date]
```

**Rule:** All variations must be:
1. Documented in `standards/VARIATIONS.md`
2. Reviewed and approved
3. Have clear justification
4. Have plan to fix (if temporary)

---

## Audit Workflow

### Daily Workflow (Before Committing)

1. **Run automated checks:**
   ```bash
   python astra/scripts/audit_code.py
   ```

2. **Fix all ERRORS**

3. **Review WARNINGS** - Fix if quick, document if justified

4. **Manual review** - Use Pre-Commit Review Checklist

5. **Run tests:**
   ```bash
   pytest astra/tests/
   ```

6. **Commit only if:**
   - ✅ No ERRORS from automated checks
   - ✅ All tests pass
   - ✅ Manual checklist complete
   - ✅ Variations documented (if any)

### Weekly Audit (Code Review)

1. **Run full audit:**
   ```bash
   python astra/scripts/audit_code.py --dir astra > weekly_audit.txt
   ```

2. **Review variations:**
   ```bash
   cat standards/VARIATIONS.md
   ```

3. **Check for new violations:**
   - Compare with previous audit
   - Identify trends
   - Address systemic issues

4. **Update standards if needed:**
   - If pattern keeps appearing, consider if standard needs adjustment
   - Document decision in `standards/VARIATIONS.md`

### Pre-Merge Audit (Pull Requests)

**Required checks before merging:**

1. ✅ Automated audit passes (no ERRORS)
2. ✅ All tests pass
3. ✅ Code review completed
4. ✅ Manual checklist verified
5. ✅ Variations documented (if any)
6. ✅ Documentation updated

---

## Identifying Variations

### How to Identify Variations

#### 1. Automated Detection

The audit script will flag:
- Missing type hints
- Missing docstrings
- Functions > 50 lines
- Files > 500/1000 lines
- Global state usage
- Bare except clauses

#### 2. Manual Detection

Look for these patterns:

**Pattern: Business Logic in ASTRA.py**
```python
# ❌ VIOLATION
# astra/ASTRA.py
def main():
    # ... 200 lines of calculation logic
```

**Pattern: Circular Dependency**
```python
# ❌ VIOLATION
# data/loader.py
from risk.metrics import calculate_returns

# risk/metrics.py
from data.loader import clean_data
```

**Pattern: Hard to Test**
```python
# ❌ VIOLATION
def calculate_metrics():
    ticker = st.text_input("Ticker")  # Can't test without Streamlit
    # ...
```

**Pattern: Multiple Responsibilities**
```python
# ❌ VIOLATION
def process_everything(ticker):
    # Downloads data
    data = download_data(ticker)
    # Calculates metrics
    metrics = calculate_metrics(data)
    # Displays UI
    st.write(metrics)
    # Does 3 things - violates Rule #3
```

#### 3. Review Process

**When reviewing code, ask:**

1. **"Can I understand this module in 5 minutes?"**
   - If NO → Variation (too complex)

2. **"Can I test this function without running the app?"**
   - If NO → Variation (not testable)

3. **"Does this module do one thing?"**
   - If NO → Variation (multiple responsibilities)

4. **"Can I trace the data flow?"**
   - If NO → Variation (unclear flow)

---

## Variation Management

### When Variations Are Acceptable

**Acceptable variations:**
1. **Temporary** - Fix planned and documented
2. **Justified** - Clear reason why standard doesn't apply
3. **Reviewed** - Approved by team/reviewer
4. **Documented** - Recorded in `standards/VARIATIONS.md`

### When Variations Are NOT Acceptable

**Unacceptable variations:**
1. **Silent** - Not documented
2. **Systemic** - Pattern repeated across codebase
3. **Unjustified** - No clear reason
4. **Permanent** - No plan to fix

### Variation Resolution Process

1. **Identify** - Found during audit
2. **Document** - Add to `standards/VARIATIONS.md`
3. **Justify** - Explain why variation is needed
4. **Review** - Get approval
5. **Plan** - Create fix plan (if temporary)
6. **Track** - Monitor until resolved

---

## Audit Tools Integration

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook to run audit

echo "Running ASTRA code audit..."
python astra/scripts/audit_code.py

if [ $? -ne 0 ]; then
    echo "❌ Audit failed. Fix errors before committing."
    exit 1
fi

echo "✅ Audit passed."
exit 0
```

### CI/CD Integration

Add to `.github/workflows/audit.yml` (or equivalent):

```yaml
name: Code Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r astra/requirements.txt
      - name: Run audit
        run: python astra/scripts/audit_code.py
      - name: Run tests
        run: pytest astra/tests/
```

---

## Audit Report Template

### Standard Audit Report

```
ASTRA Code Audit Report
Date: [Date]
Auditor: [Name]
Scope: [Files/Directory]

Summary:
- Total Files Audited: [N]
- Total Issues Found: [N]
  - Errors: [N] (Must Fix)
  - Warnings: [N] (Should Fix)
  - Info: [N] (Consider)

Errors (Must Fix):
1. [File]:[Line] - [Rule] - [Message]
2. ...

Warnings (Should Fix):
1. [File]:[Line] - [Rule] - [Message]
2. ...

Variations Documented:
- [Variation #1] - [Status]
- [Variation #2] - [Status]

Recommendations:
1. [Action item]
2. [Action item]

Next Audit: [Date]
```

---

## Quick Reference

### Run Audit
```bash
# Full audit
python astra/scripts/audit_code.py

# Single file
python astra/scripts/audit_code.py --file astra/data/loader.py
```

### Check Variations
```bash
cat standards/VARIATIONS.md
```

### Manual Checklist
- Use Pre-Commit Review Checklist (above)
- Reference `standards/CODING_STANDARDS.md` for rules

### Document Variation
1. Add entry to `standards/VARIATIONS.md`
2. Include: File, Function, Rule, Reason, Status
3. Get review/approval

---

## Summary

**Three Methods:**
1. **Automated** - Fast, objective, catches syntax/structure issues
2. **Manual** - Thorough, catches logic/design issues
3. **Hybrid** - Best of both (recommended)

**Key Points:**
- Run automated checks before every commit
- Manual review for context and design
- Document all variations with justification
- Fix errors immediately, review warnings
- Track variations until resolved

**Goal:** Ensure code quality while allowing justified flexibility.

---

**Last Updated:** 2025-11-16  
**Status:** Active - Use for all ASTRA code audits  
**Related Documents:**
- **`standards/CODING_STANDARDS.md`** - Standards being audited
- **`functional_design/ASTRA_MODULAR_APPROACH.md`** - Detailed coding philosophy
- **`functional_design/ASTRA_ENHANCEMENT_PLAN.md`** - Implementation roadmap
- **`standards/VARIATIONS.md`** - Documented variations from standards
- **`README.md`** - Overview and quick start

