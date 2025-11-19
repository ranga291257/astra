# ASTRA - Advanced Stock Risk Analysis

This directory contains all ASTRA-related documentation, diagrams, and planning files.

## Contents

### Core Documentation
- **functional_design/ASTRA_ENHANCEMENT_PLAN.md** - Complete enhancement plan for evolving Stock RAVA into ASTRA
- **functional_design/ASTRA_MODULAR_APPROACH.md** - Detailed explanation of modular coding philosophy and implementation strategy
- **standards/CODING_STANDARDS.md** - ⚠️ **MANDATORY** - Coding standards all implementations must follow
- **standards/AUDIT_GUIDE.md** - How to verify compliance with coding standards
- **standards/VARIATIONS.md** - Documented variations from coding standards (with justification)

### Diagrams (draw.io format)
- **functional_design/ASTRA_Component_Diagram.drawio** - High-level component diagram
- **functional_design/ASTRA_Module_Diagram.drawio** - Module-level function diagram
- **functional_design/ASTRA_User_Flow.drawio** - User flow / activity diagram

### Tools
- **scripts/audit_code.py** - Automated code audit script

## Quick Start

### For Developers
1. **Read the plan:** Start with `functional_design/ASTRA_ENHANCEMENT_PLAN.md` to understand the roadmap
2. **Understand the approach:** Read `functional_design/ASTRA_MODULAR_APPROACH.md` for coding philosophy
3. **Follow standards:** Review `standards/CODING_STANDARDS.md` before writing code
4. **Audit your code:** Use `scripts/audit_code.py` to check compliance

### For Reviewers
1. **Review plan:** Check `functional_design/ASTRA_ENHANCEMENT_PLAN.md` for feature scope
2. **Check standards:** Verify code follows `standards/CODING_STANDARDS.md`
3. **Run audit:** Use `standards/AUDIT_GUIDE.md` for audit process
4. **Check variations:** Review `standards/VARIATIONS.md` for documented deviations

### For Everyone
- **View diagrams:** Open the `.drawio` files in draw.io to understand architecture

## Documentation Structure

```
astra/
├── README.md                      # This file - Overview and quick start
├── functional_design/             # Design documents and diagrams
│   ├── ASTRA_ENHANCEMENT_PLAN.md  # Feature roadmap and implementation plan
│   ├── ASTRA_MODULAR_APPROACH.md  # Coding philosophy and modular approach
│   └── *.drawio                   # Architecture diagrams
├── standards/                     # Code quality standards and process docs
│   ├── CODING_STANDARDS.md        # ⚠️ MANDATORY coding standards
│   ├── AUDIT_GUIDE.md             # How to audit code for compliance
│   ├── VARIATIONS.md              # Documented variations from standards
│   └── CONSISTENCY_REPORT.md      # Documentation consistency report
└── scripts/
    └── audit_code.py              # Automated audit tool
```

## Status

**Current Phase:** Planning Complete - Ready for Phase A Implementation

**Implementation Status:**
- ✅ Planning complete
- ✅ Coding standards defined
- ✅ Audit process established
- ⏳ Phase A: UI improvements + basic indicators (pending)
- ⏳ Phase B: One major feature (pending)
- ⏳ Phase C: Light refactor if needed (pending)

See `functional_design/ASTRA_ENHANCEMENT_PLAN.md` for detailed implementation phases and timeline.

## Important Notes

⚠️ **CRITICAL:** All ASTRA code MUST follow `standards/CODING_STANDARDS.md`

📋 **Before Coding:**
- Read `functional_design/ASTRA_MODULAR_APPROACH.md` to understand the philosophy
- Review `standards/CODING_STANDARDS.md` for mandatory rules
- Use `standards/AUDIT_GUIDE.md` to verify compliance

🔍 **Path Conventions:**
- References within `astra/` directory: Use relative paths (e.g., `data/loader.py`)
- References from outside `astra/`: Use `astra/` prefix (e.g., `astra/data/loader.py`)

---

**Last Updated:** 2025-11-16  
**Status:** Active Documentation

