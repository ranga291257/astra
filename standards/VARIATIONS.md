# Documented Variations from Coding Standards

**Purpose:** This file documents any code that deviates from `standards/CODING_STANDARDS.md` with justification and approval.

**Rule:** All variations must be:
1. Documented here
2. Reviewed and approved
3. Have clear justification
4. Have plan to fix (if temporary)

---

## Variation Template

```markdown
## Variation #N: [Brief Description]

**Date:** [YYYY-MM-DD]
**File:** `[path/to/file.py]`
**Function/Module:** `[function_name or module_name]`
**Standard Violated:** Rule #[N] - [Rule Name]
**Severity:** ERROR / WARNING
**Status:** PENDING / ACCEPTED / FIXED / REJECTED

**Description:**
[What is the variation? What code violates the standard?]

**Justification:**
[Why is this variation necessary? What makes the standard not applicable here?]

**Impact:**
[What is the impact of this variation? Does it affect maintainability, testability, etc.?]

**Plan to Fix (if temporary):**
[If this is a temporary variation, what is the plan to fix it? Timeline?]

**Reviewer:** [Name]
**Approved Date:** [YYYY-MM-DD]
**Review Notes:**
[Any additional notes from the review]
```

---

## Variations Log

*No variations documented yet. All code should comply with standards.*

---

## How to Add a Variation

1. **Identify the violation** during audit or code review
2. **Determine if variation is justified** (see criteria below)
3. **Add entry** to this file using the template above
4. **Get review/approval** from team lead or code reviewer
5. **Update status** as variation is addressed

## When Variations Are Acceptable

- **Temporary** - Fix planned and documented with timeline
- **Justified** - Clear technical reason why standard doesn't apply
- **Reviewed** - Approved by team/reviewer
- **Documented** - Fully documented here

## When Variations Are NOT Acceptable

- **Silent** - Not documented
- **Systemic** - Pattern repeated across codebase
- **Unjustified** - No clear reason
- **Permanent** - No plan to fix

---

**Last Updated:** 2025-11-16  
**Status:** Active - Track all variations here

