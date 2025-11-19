#!/usr/bin/env python3
"""
Automated code audit script for ASTRA.

Checks compliance with standards/CODING_STANDARDS.md

Usage:
    python scripts/audit_code.py
    python scripts/audit_code.py --file astra/data/loader.py
    python scripts/audit_code.py --dir astra
"""

import ast
import re
import sys
from pathlib import Path
from typing import List
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
                # Skip private methods and dunder methods
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                
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
                    if arg.annotation is None and arg.arg != 'self':
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
                # Skip private methods
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                
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
                elif "Contract:" not in docstring and "Args:" not in docstring:
                    # Allow alternative docstring formats (Google/NumPy style)
                    if "Parameters" not in docstring and "Returns" not in docstring:
                        issues.append(AuditIssue(
                            file=str(file_path),
                            line=node.lineno,
                            rule="DOCSTRINGS",
                            severity="WARNING",
                            message=f"Function '{node.name}' docstring missing contract section (Contract:/Args:/Parameters:)"
                        ))
        
        return issues
    
    def _check_function_length(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[AuditIssue]:
        """Check: Functions < 50 lines (Rule #10)."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private methods
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                
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
                # Skip private methods
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                
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
                        message="ASTRA.py should only contain UI wiring, not business logic (found calculate_* function)"
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
                # Skip private methods
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                
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
        
        # Patterns to exclude
        exclude_patterns = [
            "test_",
            "__pycache__",
            ".pyc",
            "scripts/audit_code.py",  # Don't audit the auditor
        ]
        
        for py_file in directory.rglob("*.py"):
            # Skip excluded files
            if any(pattern in str(py_file) for pattern in exclude_patterns):
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
        
        print(f"\n📊 ASTRA Code Audit Report")
        print(f"{'='*70}")
        print(f"Total Issues: {len(issues)}")
        print(f"  ❌ Errors: {len(errors)} (Must Fix)")
        print(f"  ⚠️  Warnings: {len(warnings)} (Should Fix)")
        print(f"  ℹ️  Info: {len(info)}")
        print(f"{'='*70}\n")
        
        # Print errors
        if errors:
            print("❌ ERRORS (Must Fix):")
            print("-" * 70)
            for issue in errors:
                print(f"  {issue.file}:{issue.line}")
                print(f"    Rule: {issue.rule}")
                print(f"    {issue.message}\n")
        
        # Print warnings
        if warnings:
            print("⚠️  WARNINGS (Should Fix):")
            print("-" * 70)
            for issue in warnings:
                print(f"  {issue.file}:{issue.line}")
                print(f"    Rule: {issue.rule}")
                print(f"    {issue.message}\n")
        
        # Print info
        if info:
            print("ℹ️  INFO:")
            print("-" * 70)
            for issue in info:
                print(f"  {issue.file}:{issue.line}")
                print(f"    Rule: {issue.rule}")
                print(f"    {issue.message}\n")
        
        # Summary
        print(f"{'='*70}")
        if errors:
            print(f"❌ Audit FAILED: {len(errors)} error(s) must be fixed.")
        elif warnings:
            print(f"⚠️  Audit PASSED with {len(warnings)} warning(s) to review.")
        else:
            print(f"✅ Audit PASSED: All checks passed.")
        print(f"{'='*70}\n")
        
        # Exit with error code if errors found
        if errors:
            sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Audit ASTRA code for standards compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/audit_code.py                    # Audit entire astra/ directory
  python scripts/audit_code.py --file astra/data/loader.py  # Audit specific file
  python scripts/audit_code.py --dir astra/data   # Audit specific directory
        """
    )
    parser.add_argument("--file", help="Audit specific file")
    parser.add_argument("--dir", default="astra", help="Directory to audit (default: astra)")
    
    args = parser.parse_args()
    
    root_dir = Path(args.dir)
    
    if not root_dir.exists():
        print(f"❌ Error: Directory '{root_dir}' does not exist.")
        sys.exit(1)
    
    auditor = CodeAuditor(root_dir)
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ Error: File '{file_path}' does not exist.")
            sys.exit(1)
        issues = auditor.audit_file(file_path)
    else:
        issues = auditor.audit_directory(root_dir)
    
    auditor.print_report(issues)

if __name__ == "__main__":
    main()

