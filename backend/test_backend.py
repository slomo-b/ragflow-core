#!/usr/bin/env python3
"""
RagFlow Backend Test Suite
Comprehensive testing of all backend endpoints and functionality
"""

import requests
import time
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile
import os

class BackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, status: str, message: str = "", response_time: float = 0):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            icon = "✅"
        elif status == "FAIL":
            self.failed_tests += 1
            icon = "❌"
        else:
            icon = "⚠️"
        
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "response_time": response_time
        }
        self.test_results.append(result)
        
        print(f"{icon} {test_name}: {status}" + (f" - {message}" if message else ""))
        if response_time > 0:
            print(f"   Response time: {response_time:.3f}s")

    def test_request(self, method: str, endpoint: str, test_name: str, 
                    expected_status: int = 200, **kwargs) -> Tuple[bool, Optional[Dict]]:
        """Make HTTP request and test response"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response_time = time.time() - start_time
            
            if response.status_code == expected_status:
                try:
                    json_data = response.json()
                    self.log_test(test_name, "PASS", f"Status: {response.status_code}", response_time)
                    return True, json_data
                except ValueError:
                    # Non-JSON response
                    self.log_test(test_name, "PASS", f"Status: {response.status_code} (non-JSON)", response_time)
                    return True, {"text": response.text}
            else:
                self.log_test(test_name, "FAIL", f"Expected {expected_status}, got {response.status_code}", response_time)
                return False, None
                
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Request failed: {str(e)}", response_time)
            return False, None

    def test_connectivity(self):
        """Test basic connectivity"""
        print("\n🔌 CONNECTIVITY TESTS")
        print("=" * 40)
        
        # Test backend is reachable
        success, _ = self.test_request("GET", "/", "Backend Connectivity")
        if not success:
            print("❌ Backend not reachable - stopping tests")
            return False
        return True

    def test_core_endpoints(self):
        """Test core API endpoints"""
        print("\n🏠 CORE ENDPOINT TESTS")
        print("=" * 40)
        
        # Root endpoint
        success, data = self.test_request("GET", "/", "Root Endpoint")
        if success and data:
            if "message" in data and "version" in data:
                self.log_test("Root Data Structure", "PASS", "Contains message and version")
            else:
                self.log_test("Root Data Structure", "FAIL", "Missing required fields")

        # Ping endpoint
        success, data = self.test_request("GET", "/ping", "Ping Endpoint")
        if success and data:
            if data.get("message") == "pong":
                self.log_test("Ping Response", "PASS", "Correct pong response")
            else:
                self.log_test("Ping Response", "FAIL", f"Expected 'pong', got {data.get('message')}")

        # Health endpoint
        success, data = self.test_request("GET", "/health", "Health Endpoint")
        if success and data:
            if data.get("status") == "healthy":
                self.log_test("Health Status", "PASS", "Backend reports healthy")
            else:
                self.log_test("Health Status", "FAIL", f"Status: {data.get('status')}")

    def test_api_v1_endpoints(self):
        """Test API v1 endpoints"""
        print("\n🔗 API v1 ENDPOINT TESTS")
        print("=" * 40)
        
        # Health v1
        success, data = self.test_request("GET", "/api/v1/health/", "Health v1 Endpoint")
        if success and data:
            if data.get("status") == "healthy" and "checks" in data:
                self.log_test("Health v1 Structure", "PASS", "Contains status and checks")
            else:
                self.log_test("Health v1 Structure", "FAIL", "Missing required fields")

        # Ready endpoint
        success, data = self.test_request("GET", "/api/v1/health/ready", "Ready Endpoint")
        
        # Documents list (should be placeholder)
        success, data = self.test_request("GET", "/api/v1/documents/", "Documents List")
        if success and data:
            if "message" in data and "documents" in data:
                self.log_test("Documents Structure", "PASS", "Placeholder response correct")
            else:
                self.log_test("Documents Structure", "FAIL", "Unexpected response structure")

        # Collections list (should be placeholder)
        success, data = self.test_request("GET", "/api/v1/collections/", "Collections List")

    def test_api_documentation(self):
        """Test API documentation endpoints"""
        print("\n📚 DOCUMENTATION TESTS")
        print("=" * 40)
        
        # OpenAPI docs
        success, _ = self.test_request("GET", "/docs", "Swagger UI")
        
        # OpenAPI JSON
        success, data = self.test_request("GET", "/openapi.json", "OpenAPI Schema")
        if success and data:
            if "openapi" in data and "info" in data:
                self.log_test("OpenAPI Structure", "PASS", "Valid OpenAPI schema")
            else:
                self.log_test("OpenAPI Structure", "FAIL", "Invalid OpenAPI schema")

        # ReDoc
        success, _ = self.test_request("GET", "/redoc", "ReDoc Documentation")

    def test_post_endpoints(self):
        """Test POST endpoints (placeholders)"""
        print("\n📤 POST ENDPOINT TESTS")
        print("=" * 40)
        
        # Search endpoint
        search_data = {
            "query": "test query",
            "top_k": 5
        }
        success, data = self.test_request("POST", "/api/v1/search/semantic", 
                                        "Search Endpoint", 
                                        json=search_data)
        
        # Upload endpoint (without file for now)
        success, data = self.test_request("POST", "/api/v1/documents/upload", 
                                        "Upload Endpoint (no file)", 
                                        expected_status=422)  # Expect validation error

    def test_error_handling(self):
        """Test error handling"""
        print("\n🚨 ERROR HANDLING TESTS")
        print("=" * 40)
        
        # 404 endpoint
        success, _ = self.test_request("GET", "/nonexistent", "404 Error Handling", 
                                     expected_status=404)
        
        # Invalid method
        success, _ = self.test_request("DELETE", "/", "Invalid Method", 
                                     expected_status=405)

    def test_cors_headers(self):
        """Test CORS configuration"""
        print("\n🌐 CORS TESTS")
        print("=" * 40)
        
        try:
            response = self.session.options(f"{self.base_url}/", headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            })
            
            if "Access-Control-Allow-Origin" in response.headers:
                self.log_test("CORS Headers", "PASS", "CORS headers present")
            else:
                self.log_test("CORS Headers", "FAIL", "CORS headers missing")
                
        except Exception as e:
            self.log_test("CORS Headers", "FAIL", f"CORS test failed: {e}")

    def test_performance(self):
        """Test basic performance"""
        print("\n⚡ PERFORMANCE TESTS")
        print("=" * 40)
        
        # Test multiple requests
        times = []
        for i in range(5):
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/ping")
            end_time = time.time()
            if response.status_code == 200:
                times.append(end_time - start_time)
        
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            if avg_time < 1.0:
                self.log_test("Response Time", "PASS", f"Avg: {avg_time:.3f}s (Max: {max_time:.3f}s)")
            else:
                self.log_test("Response Time", "WARN", f"Slow response: {avg_time:.3f}s")

    def test_database_services(self):
        """Test database service connectivity"""
        print("\n🗄️ DATABASE SERVICE TESTS")
        print("=" * 40)
        
        # Test if backend can reach databases (through health endpoint)
        success, data = self.test_request("GET", "/api/v1/health/", "Database Health Check")
        if success and data and "checks" in data:
            checks = data["checks"]
            
            for service in ["database", "vector_db"]:
                if service in checks:
                    status = checks[service].get("status", "unknown")
                    if status in ["healthy", "available", "ready"]:
                        self.log_test(f"{service.title()} Status", "PASS", f"Status: {status}")
                    else:
                        self.log_test(f"{service.title()} Status", "FAIL", f"Status: {status}")
                else:
                    self.log_test(f"{service.title()} Status", "WARN", "No status reported")

    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        print("\n🔄 CONCURRENCY TESTS")
        print("=" * 40)
        
        import threading
        
        results = []
        
        def make_request():
            try:
                response = self.session.get(f"{self.base_url}/ping", timeout=5)
                results.append(response.status_code == 200)
            except:
                results.append(False)
        
        # Create 10 concurrent threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        success_count = sum(results)
        if success_count == 10:
            self.log_test("Concurrent Requests", "PASS", 
                         f"10/10 successful in {end_time - start_time:.3f}s")
        else:
            self.log_test("Concurrent Requests", "FAIL", 
                         f"Only {success_count}/10 successful")

    def run_all_tests(self):
        """Run all test suites"""
        print("🧪 RagFlow Backend Test Suite")
        print("="*50)
        print(f"Testing backend at: {self.base_url}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        # Run test suites
        if not self.test_connectivity():
            return self.print_summary()
        
        self.test_core_endpoints()
        self.test_api_v1_endpoints()
        self.test_api_documentation()
        self.test_post_endpoints()
        self.test_error_handling()
        self.test_cors_headers()
        self.test_performance()
        self.test_database_services()
        self.test_concurrent_requests()
        
        total_time = time.time() - start_time
        
        self.print_summary(total_time)

    def print_summary(self, total_time: float = 0):
        """Print test summary"""
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"⚠️  Warnings: {self.total_tests - self.passed_tests - self.failed_tests}")
        
        if total_time > 0:
            print(f"⏱️  Total Time: {total_time:.3f}s")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("Backend is ready for Phase 2 development!")
        elif self.failed_tests <= 2:
            print("\n✅ MOSTLY SUCCESSFUL!")
            print("Backend is functional with minor issues.")
        else:
            print("\n⚠️ MULTIPLE ISSUES DETECTED!")
            print("Backend needs attention before proceeding.")
        
        # Print failed tests
        if self.failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   - {result['test']}: {result['message']}")
        
        print("\n🔗 Quick Links:")
        print(f"   Backend API: {self.base_url}")
        print(f"   API Docs: {self.base_url}/docs")
        print(f"   Health Check: {self.base_url}/api/v1/health/")
        
        return self.failed_tests == 0

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RagFlow Backend Test Suite")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Backend URL (default: http://localhost:8000)")
    parser.add_argument("--json", action="store_true", 
                       help="Output results in JSON format")
    parser.add_argument("--quick", action="store_true",
                       help="Run only essential tests")
    
    args = parser.parse_args()
    
    tester = BackendTester(args.url)
    
    if args.quick:
        # Quick test mode
        print("🚀 Quick Test Mode")
        tester.test_connectivity()
        tester.test_core_endpoints()
        tester.test_api_v1_endpoints()
    else:
        # Full test suite
        tester.run_all_tests()
    
    if args.json:
        # Output JSON results
        results = {
            "total_tests": tester.total_tests,
            "passed": tester.passed_tests,
            "failed": tester.failed_tests,
            "success_rate": tester.passed_tests / tester.total_tests * 100 if tester.total_tests > 0 else 0,
            "tests": tester.test_results
        }
        print("\n" + json.dumps(results, indent=2))
    
    # Exit code based on results
    sys.exit(0 if tester.failed_tests == 0 else 1)

if __name__ == "__main__":
    main()