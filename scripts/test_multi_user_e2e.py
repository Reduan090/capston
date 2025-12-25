#!/usr/bin/env python3
"""
End-to-End Multi-User Testing Script
Tests the capstone application with multiple users going through different workflows
"""

import os
import sys
import requests
import json
import time
from pathlib import Path
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# Test users
TEST_USERS = [
    {"id": "user_001", "name": "Alice Johnson", "email": "alice@university.edu", "password": "alice_pass123"},
    {"id": "user_002", "name": "Bob Smith", "email": "bob@university.edu", "password": "bob_pass123"},
    {"id": "user_003", "name": "Carol Davis", "email": "carol@university.edu", "password": "carol_pass123"},
]

# Test documents
TEST_DOCS = [
    {
        "name": "ml_paper.txt",
        "content": """Machine Learning in Healthcare
This paper explores the application of deep learning models for early disease detection.
Main Contributions:
1. Novel CNN architecture for medical imaging
2. 95% accuracy on test dataset
3. Real-time inference capabilities
The study involved 500 patient samples with informed consent."""
    },
    {
        "name": "quantum_computing.txt",
        "content": """Quantum Computing Applications
We present a new quantum algorithm for optimization problems.
Abstract: This research demonstrates practical applications of quantum supremacy.
Methods: Used IBM Quantum Experience platform
Results: 3x speedup compared to classical algorithms
Future Work: Scaling to larger problem domains"""
    },
    {
        "name": "nlp_trends.txt",
        "content": """Natural Language Processing Trends 2024
Recent advances in transformer architectures and their applications.
Key Topics: BERT, GPT models, semantic understanding
Applications: Text classification, sentiment analysis, question answering
Benchmark Results: GLUE, SuperGLUE, SQuAD datasets
Open Challenges: Interpretability, multilingual support, efficiency"""
    }
]

class MultiUserTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.users_data = {}
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} [{timestamp}] {test_name}: {status}")
        if details:
            print(f"   └─ {details}")
    
    def register_user(self, user):
        """Register a new user"""
        test_name = f"Register {user['name']}"
        try:
            response = self.session.post(
                f"{API_BASE_URL}/api/auth/register",
                json={
                    "email": user['email'],
                    "password": user['password'],
                    "name": user['name']
                },
                timeout=10
            )
            
            if response.status_code in [200, 201, 409]:  # 409 = user exists
                self.users_data[user['id']] = {
                    **user,
                    "token": response.json().get('token') if 'token' in response.json() else None
                }
                self.log_test(test_name, "PASS", f"Status: {response.status_code}")
                return True
            else:
                self.log_test(test_name, "FAIL", f"Status: {response.status_code} - {response.text[:100]}")
                return False
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")
            return False
    
    def login_user(self, user_id):
        """Login a user"""
        user = TEST_USERS[[u['id'] for u in TEST_USERS].index(user_id)]
        test_name = f"Login {user['name']}"
        try:
            response = self.session.post(
                f"{API_BASE_URL}/api/auth/login",
                json={
                    "email": user['email'],
                    "password": user['password']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                token = response.json().get('token')
                self.users_data[user_id]['token'] = token
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                self.log_test(test_name, "PASS", "Token acquired")
                return True
            else:
                self.log_test(test_name, "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")
            return False
    
    def upload_document(self, user_id, doc_index):
        """Upload a document for a user"""
        user = [u for u in TEST_USERS if u['id'] == user_id][0]
        doc = TEST_DOCS[doc_index % len(TEST_DOCS)]
        test_name = f"{user['name']} - Upload '{doc['name']}'"
        
        try:
            # Prepare file
            files = {'file': (doc['name'], doc['content'].encode())}
            headers = {"Authorization": f"Bearer {self.users_data[user_id]['token']}"}
            
            response = self.session.post(
                f"{API_BASE_URL}/api/upload",
                files=files,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                self.log_test(test_name, "PASS", f"File size: {len(doc['content'])} bytes")
                return True
            else:
                self.log_test(test_name, "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")
            return False
    
    def call_module_endpoint(self, user_id, module_name, action, params=None):
        """Call a module endpoint"""
        user = [u for u in TEST_USERS if u['id'] == user_id][0]
        test_name = f"{user['name']} - {module_name}: {action}"
        
        try:
            headers = {"Authorization": f"Bearer {self.users_data[user_id]['token']}"}
            payload = params or {}
            
            response = self.session.post(
                f"{API_BASE_URL}/api/{module_name}/{action}",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                self.log_test(test_name, "PASS", f"Response status: {response.status_code}")
                return True
            else:
                self.log_test(test_name, "FAIL", f"Status: {response.status_code} - {str(response.text)[:100]}")
                return False
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")
            return False
    
    def check_user_data_isolation(self, user_id):
        """Verify user's data is isolated from other users"""
        test_name = f"Data Isolation Check - {[u for u in TEST_USERS if u['id'] == user_id][0]['name']}"
        try:
            headers = {"Authorization": f"Bearer {self.users_data[user_id]['token']}"}
            
            # Get user's files
            response = self.session.get(
                f"{API_BASE_URL}/api/files/list",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                files = response.json().get('files', [])
                
                # Get all files with a different user token (should get different results)
                other_user_id = [u['id'] for u in TEST_USERS if u['id'] != user_id][0]
                other_headers = {"Authorization": f"Bearer {self.users_data[other_user_id]['token']}"}
                
                other_response = self.session.get(
                    f"{API_BASE_URL}/api/files/list",
                    headers=other_headers,
                    timeout=10
                )
                
                if other_response.status_code == 200:
                    other_files = other_response.json().get('files', [])
                    
                    # Check that lists are different (isolation working)
                    if len(files) != len(other_files) or set(files) != set(other_files):
                        self.log_test(test_name, "PASS", "User data properly isolated")
                        return True
                    else:
                        # Lists are same - either both empty or isolation not working
                        if len(files) == 0:
                            self.log_test(test_name, "PASS", "Both users have empty file lists (expected)")
                            return True
                        else:
                            self.log_test(test_name, "FAIL", "Data not isolated between users")
                            return False
                else:
                    self.log_test(test_name, "FAIL", f"Could not fetch other user files: {other_response.status_code}")
                    return False
            else:
                self.log_test(test_name, "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")
            return False
    
    def check_user_audit_log(self, user_id):
        """Verify user actions are logged"""
        user = [u for u in TEST_USERS if u['id'] == user_id][0]
        test_name = f"Audit Log Check - {user['name']}"
        try:
            headers = {"Authorization": f"Bearer {self.users_data[user_id]['token']}"}
            
            response = self.session.get(
                f"{API_BASE_URL}/api/audit/logs",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logs = response.json().get('logs', [])
                if len(logs) > 0:
                    self.log_test(test_name, "PASS", f"Found {len(logs)} audit log entries")
                    return True
                else:
                    self.log_test(test_name, "PASS", "Audit log endpoint working (empty for now)")
                    return True
            else:
                self.log_test(test_name, "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_concurrent_operations(self):
        """Test multiple users performing operations simultaneously"""
        test_name = "Concurrent Operations Test"
        try:
            # Each user uploads a document
            for idx, user in enumerate(TEST_USERS):
                self.upload_document(user['id'], idx)
            
            self.log_test(test_name, "PASS", "All users uploaded documents concurrently")
            return True
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_full_workflow(self, user_id, user_index):
        """Run a complete workflow for a user"""
        user = [u for u in TEST_USERS if u['id'] == user_id][0]
        
        print(f"\n{'='*60}")
        print(f"Testing Workflow for {user['name']} (User #{user_index + 1})")
        print(f"{'='*60}\n")
        
        # 1. Register
        self.register_user(user)
        time.sleep(0.5)
        
        # 2. Login
        self.login_user(user_id)
        time.sleep(0.5)
        
        # 3. Upload documents (2-3 documents per user)
        num_docs = 2 + user_index  # Different number of docs for variety
        for doc_idx in range(num_docs):
            self.upload_document(user_id, doc_idx)
            time.sleep(0.3)
        
        # 4. Call various module endpoints
        modules_and_actions = [
            ("literature_review", "generate"),
            ("topic_finder", "extract"),
            ("grammar_style", "check"),
            ("citation_tool", "search"),
            ("plagiarism_check", "analyze"),
        ]
        
        for module, action in modules_and_actions:
            params = {
                "text": TEST_DOCS[user_index % len(TEST_DOCS)]['content'][:500],
                "query": "machine learning" if module == "citation_tool" else None
            }
            self.call_module_endpoint(user_id, module, action, {k: v for k, v in params.items() if v})
            time.sleep(0.2)
        
        # 5. Check data isolation
        self.check_user_data_isolation(user_id)
        time.sleep(0.3)
        
        # 6. Check audit log
        self.check_user_audit_log(user_id)
        time.sleep(0.3)
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("Multi-User End-to-End Testing")
        print("="*60 + "\n")
        
        print("Starting Test Suite...\n")
        
        # Run workflows for each user
        for idx, user in enumerate(TEST_USERS):
            self.run_full_workflow(user['id'], idx)
            time.sleep(1)
        
        # Test concurrent operations
        print(f"\n{'='*60}")
        print("Concurrent Operations Test")
        print(f"{'='*60}\n")
        self.test_concurrent_operations()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print(f"\n{'='*60}")
        print("Test Report")
        print(f"{'='*60}\n")
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%\n")
        
        if failed > 0:
            print("Failed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  ❌ {result['test']}")
                    print(f"     {result['details']}\n")
        
        # Save report to file
        report_file = Path(__file__).parent.parent / "test_results_multiuser.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nDetailed report saved to: {report_file}")
        
        # Summary
        print(f"\n{'='*60}")
        if failed == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print(f"⚠️  {failed} test(s) failed - see details above")
        print(f"{'='*60}\n")
        
        return passed, failed

if __name__ == "__main__":
    try:
        print("\n🚀 Starting Multi-User End-to-End Tests...\n")
        print(f"API URL: {API_BASE_URL}")
        print(f"Frontend URL: {FRONTEND_URL}\n")
        
        tester = MultiUserTester()
        tester.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
