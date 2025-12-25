#!/usr/bin/env python3
"""
Integration Verification Script
Validates that all 7 modules have been properly integrated with user isolation
"""

import re
from pathlib import Path
from typing import List, Tuple

# Configuration
MODULES_DIR = Path(__file__).parent.parent / "modules"
REQUIRED_PATTERNS = {
    "require_authentication": r"@require_authentication",
    "user_data_import": r"from utils\.user_data import",
    "get_current_user_id": r"get_current_user_id",
    "log_user_action": r"log_user_action",
}

MODULES_TO_CHECK = [
    "ask_paper.py",
    "ai_writer.py",
    "upload_pdf.py",
    "literature_review.py",
    "topic_finder.py",
    "grammar_style.py",
    "citation_tool.py",
    "plagiarism_check.py",
]

class IntegrationVerifier:
    def __init__(self):
        self.results = []
        self.modules_ok = 0
        self.modules_issues = 0
    
    def check_module(self, module_name: str) -> Tuple[bool, List[str]]:
        """Check if a module is properly integrated"""
        module_path = MODULES_DIR / module_name
        
        if not module_path.exists():
            return False, [f"File not found: {module_path}"]
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return False, [f"Error reading file: {str(e)}"]
        
        issues = []
        
        # Check for required patterns
        for pattern_name, pattern in REQUIRED_PATTERNS.items():
            if not re.search(pattern, content):
                issues.append(f"Missing: {pattern_name}")
        
        # Special check: ensure @require_authentication is not duplicated
        decorator_count = len(re.findall(r"@require_authentication", content))
        if decorator_count > 1:
            # Count unique lines with decorator
            lines_with_decorator = [i for i, line in enumerate(content.split('\n')) 
                                   if '@require_authentication' in line]
            # It's OK if same line has multiple (was a paste error), but check structure
            if len(lines_with_decorator) > 1:
                issues.append(f"Duplicate decorators found ({decorator_count} occurrences)")
        
        # Check that main() has decorator
        main_pattern = r"@require_authentication\s+def main\(\):"
        if not re.search(main_pattern, content):
            issues.append("main() function not decorated with @require_authentication")
        
        # Check for old UPLOAD_DIR/EXPORT_DIR (global) references
        old_refs = []
        if re.search(r"UPLOAD_DIR\s*(?!.*from)", content):
            # Check if it's a direct UPLOAD_DIR usage (not in import)
            for match in re.finditer(r"(UPLOAD_DIR|EXPORT_DIR)\s*(?!=)", content):
                if "from config import" not in content[max(0, match.start()-100):match.start()]:
                    old_refs.append("UPLOAD_DIR")
                    break
        
        if old_refs:
            issues.append(f"Found unhandled global directory references: {', '.join(set(old_refs))}")
        
        return len(issues) == 0, issues
    
    def run_verification(self):
        """Run verification on all modules"""
        print("\n" + "="*70)
        print("Integration Verification - Multi-User Module Check")
        print("="*70 + "\n")
        
        for module_name in MODULES_TO_CHECK:
            ok, issues = self.check_module(module_name)
            
            if ok:
                print(f"✅ {module_name:<30} - OK")
                self.modules_ok += 1
            else:
                print(f"❌ {module_name:<30} - ISSUES FOUND:")
                for issue in issues:
                    print(f"   ├─ {issue}")
                self.modules_issues += 1
            
            self.results.append({
                "module": module_name,
                "status": "OK" if ok else "ISSUES",
                "issues": issues
            })
        
        print("\n" + "="*70)
        print("Summary")
        print("="*70 + "\n")
        
        total = len(MODULES_TO_CHECK)
        print(f"Total Modules: {total}")
        print(f"✅ Properly Integrated: {self.modules_ok}")
        print(f"❌ Issues Found: {self.modules_issues}")
        print(f"Success Rate: {(self.modules_ok/total*100):.1f}%")
        
        if self.modules_issues > 0:
            print("\n⚠️  Issues to resolve:")
            for result in self.results:
                if result['status'] == 'ISSUES':
                    print(f"\n{result['module']}:")
                    for issue in result['issues']:
                        print(f"  - {issue}")
        
        print("\n" + "="*70)
        if self.modules_issues == 0:
            print("✅ ALL MODULES PROPERLY INTEGRATED!")
            print("✅ Ready for multi-user testing")
        else:
            print("⚠️  Some modules need attention")
        print("="*70 + "\n")
        
        return self.modules_issues == 0

    def verify_helper_functions(self):
        """Verify that utils/user_data.py has required functions"""
        print("\n" + "="*70)
        print("Verifying Helper Functions")
        print("="*70 + "\n")
        
        user_data_path = Path(__file__).parent.parent / "utils" / "user_data.py"
        
        if not user_data_path.exists():
            print(f"❌ {user_data_path} not found!")
            return False
        
        required_functions = [
            "require_authentication",
            "get_current_user_id",
            "get_user_upload_dir",
            "get_user_export_dir",
            "get_user_db_dir",
            "log_user_action",
            "get_user_audit_logs",
        ]
        
        try:
            with open(user_data_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
        
        all_found = True
        for func_name in required_functions:
            if f"def {func_name}" in content or f"class {func_name}" in content:
                print(f"✅ {func_name}")
            else:
                print(f"❌ {func_name} - NOT FOUND")
                all_found = False
        
        print("\n" + "="*70)
        if all_found:
            print("✅ All required helper functions found!")
        else:
            print("❌ Some helper functions missing!")
        print("="*70 + "\n")
        
        return all_found

if __name__ == "__main__":
    verifier = IntegrationVerifier()
    
    # Verify helper functions first
    helpers_ok = verifier.verify_helper_functions()
    
    # Verify all modules
    modules_ok = verifier.run_verification()
    
    # Exit with appropriate code
    exit(0 if (helpers_ok and modules_ok) else 1)
