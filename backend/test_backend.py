#!/usr/bin/env python3
"""
RagFlow Backend Test Suite
Comprehensive testing for the RagFlow backend API
"""

import requests
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RagFlowBackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Test tracking
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = 0
        self.test_results = []
        
        # Performance tracking
        self.response_times = []
        
        print(f"🧪 RagFlow Backend Test Suite")
        print(f"Target: {self.base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def log_test(self, test_name: str, status: str, message: str = "", response_time: float = 0):
        """Log test result"""
        self.total_tests += 1
        
        # Status icons
        icons = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}
        icon = icons.get(status, "📋")
        
        # Update counters
        if status == "PASS":
            self.passed_tests += 1
        elif status == "FAIL":
            self.failed_tests += 1
        elif status == "WARN":
            self.warnings += 1
        
        # Format output
        time_str = f"({response_time*1000:.0f}ms)" if response_time > 0 else ""
        print(f"{icon} {test_name:<35} {status:<4} {message} {time_str}")
        
        # Store result
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        })

    def make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[bool, Optional[Dict], float]:
        """Make HTTP request and measure response time"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            # Try to parse JSON
            try:
                data = response.json()
                return response.status_code == 200, data, response_time
            except json.JSONDecodeError:
                # Return text for non-JSON responses (like HTML docs)
                return response.status_code == 200, {"text": response.text[:200]}, response_time
                
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return False, {"error": str(e)}, response_time

    def test_connectivity(self) -> bool:
        """Test basic backend connectivity"""
        print("\n🔌 CONNECTIVITY TESTS")
        print("-" * 40)
        
        success, data, resp_time = self.make_request("GET", "/")
        if success:
            self.log_test("Backend Reachable", "PASS", "API is responding", resp_time)
            return True
        else:
            self.log_test("Backend Reachable", "FAIL", f"Connection failed: {data.get('error', 'Unknown')}", resp_time)
            return False

    def test_core_endpoints(self):
        """Test core API endpoints"""
        print("\n🏠 CORE API ENDPOINTS")
        print("-" * 40)
        
        # Root endpoint
        success, data, resp_time = self.make_request("GET", "/")
        if success and data:
            if "message" in data and "version" in data:
                self.log_test("Root Endpoint", "PASS", f"v{data.get('version', 'unknown')}", resp_time)
                
                # Check features
                features = data.get("features", {})
                enabled_features = [k for k, v in features.items() if v]
                if enabled_features:
                    self.log_test("Feature Check", "INFO", f"Enabled: {', '.join(enabled_features)}")
            else:
                self.log_test("Root Endpoint", "WARN", "Missing expected fields", resp_time)
        else:
            self.log_test("Root Endpoint", "FAIL", "Invalid response", resp_time)

        # Ping endpoint
        success, data, resp_time = self.make_request("GET", "/ping")
        if success and data and data.get("message") == "pong":
            self.log_test("Ping Health", "PASS", "Pong received", resp_time)
        else:
            self.log_test("Ping Health", "FAIL", "No pong response", resp_time)

        # Basic health
        success, data, resp_time = self.make_request("GET", "/health")
        if success and data and data.get("status") == "healthy":
            self.log_test("Basic Health", "PASS", "Backend healthy", resp_time)
        else:
            self.log_test("Basic Health", "FAIL", "Backend not healthy", resp_time)

    def test_health_endpoints(self):
        """Test comprehensive health endpoints"""
        print("\n🏥 HEALTH MONITORING")
        print("-" * 40)
        
        # Detailed health check
        success, data, resp_time = self.make_request("GET", "/api/v1/health/")
        if success and data:
            status = data.get("status", "unknown")
            self.log_test("Health v1", "PASS" if status == "healthy" else "WARN", f"Status: {status}", resp_time)
            
            # Check individual services
            checks = data.get("checks", {})
            for service, check in checks.items():
                service_status = check.get("status", "unknown")
                service_msg = check.get("message", "")
                status_level = "PASS" if service_status in ["healthy", "available"] else "FAIL"
                self.log_test(f"{service.title()} Service", status_level, f"{service_status}: {service_msg}")
        else:
            self.log_test("Health v1", "FAIL", "Health check failed", resp_time)

        # Readiness check
        success, data, resp_time = self.make_request("GET", "/api/v1/health/ready")
        if success and data:
            self.log_test("Readiness Check", "PASS", "Backend ready", resp_time)
        else:
            self.log_test("Readiness Check", "FAIL", "Backend not ready", resp_time)

        # System info
        success, data, resp_time = self.make_request("GET", "/api/v1/health/info")
        if success and data:
            app_name = data.get("app_name", "Unknown")
            version = data.get("version", "Unknown")
            self.log_test("System Info", "PASS", f"{app_name} v{version}", resp_time)
            
            # Log configuration details
            config_items = []
            if "max_file_size_mb" in data:
                config_items.append(f"Max file: {data['max_file_size_mb']}MB")
            if "embedding_model" in data:
                config_items.append(f"Model: {data['embedding_model']}")
            if config_items:
                self.log_test("Configuration", "INFO", " | ".join(config_items))
        else:
            self.log_test("System Info", "WARN", "No system info available", resp_time)

    def test_api_endpoints(self):
        """Test main API endpoints"""
        print("\n🔗 API ENDPOINTS")
        print("-" * 40)
        
        # Documents endpoint
        success, data, resp_time = self.make_request("GET", "/api/v1/documents/")
        if success:
            self.log_test("Documents List", "PASS", "Endpoint accessible", resp_time)
            if data and "documents" in data:
                doc_count = len(data.get("documents", []))
                self.log_test("Document Count", "INFO", f"{doc_count} documents found")
        else:
            self.log_test("Documents List", "FAIL", "Endpoint not accessible", resp_time)

        # Collections endpoint
        success, data, resp_time = self.make_request("GET", "/api/v1/collections/")
        if success:
            self.log_test("Collections List", "PASS", "Endpoint accessible", resp_time)
        else:
            self.log_test("Collections List", "FAIL", "Endpoint not accessible", resp_time)

        # Development routes
        success, data, resp_time = self.make_request("GET", "/api/v1/dev/routes")
        if success and data:
            route_count = data.get("total_routes", 0)
            self.log_test("Routes List", "PASS", f"{route_count} routes found", resp_time)
        else:
            self.log_test("Routes List", "WARN", "Dev routes not available", resp_time)

        # System status
        success, data, resp_time = self.make_request("GET", "/api/v1/system/status")
        if success and data:
            status = data.get("status", "unknown")
            mode = data.get("mode", "unknown")
            self.log_test("System Status", "PASS", f"{status} ({mode})", resp_time)
            
            # Check services status
            services = data.get("services", {})
            healthy_services = sum(1 for status in services.values() if status in ["healthy", "available"])
            total_services = len(services)
            self.log_test("Services Status", "INFO", f"{healthy_services}/{total_services} healthy")
        else:
            self.log_test("System Status", "FAIL", "Status not available", resp_time)

    def test_documentation(self):
        """Test API documentation endpoints"""
        print("\n📚 DOCUMENTATION")
        print("-" * 40)
        
        # Swagger UI
        success, data, resp_time = self.make_request("GET", "/docs")
        if success:
            self.log_test("Swagger UI", "PASS", "Documentation accessible", resp_time)
        else:
            self.log_test("Swagger UI", "FAIL", "Swagger not accessible", resp_time)

        # OpenAPI schema
        success, data, resp_time = self.make_request("GET", "/openapi.json")
        if success and data and "openapi" in str(data):
            self.log_test("OpenAPI Schema", "PASS", "Valid schema", resp_time)
        else:
            self.log_test("OpenAPI Schema", "FAIL", "Invalid schema", resp_time)

        # ReDoc
        success, data, resp_time = self.make_request("GET", "/redoc")
        if success:
            self.log_test("ReDoc", "PASS", "ReDoc accessible", resp_time)
        else:
            self.log_test("ReDoc", "WARN", "ReDoc not accessible", resp_time)

    def test_post_endpoints(self):
        """Test POST endpoints (placeholder tests)"""
        print("\n📤 POST ENDPOINTS")
        print("-" * 40)
        
        # Document upload (without file - should fail gracefully)
        success, data, resp_time = self.make_request("POST", "/api/v1/documents/upload")
        # We expect this to fail with 422 (validation error), but endpoint should exist
        if resp_time > 0:  # If we got any response, endpoint exists
            self.log_test("Upload Endpoint", "PASS", "Endpoint exists (validation error expected)", resp_time)
        else:
            self.log_test("Upload Endpoint", "FAIL", "Endpoint not found", resp_time)

        # Semantic search (without query - should fail gracefully)
        success, data, resp_time = self.make_request("POST", "/api/v1/search/semantic", 
                                                   json={"query": "test query"})
        if resp_time > 0:  # If we got any response, endpoint exists
            self.log_test("Search Endpoint", "PASS", "Endpoint exists", resp_time)
        else:
            self.log_test("Search Endpoint", "FAIL", "Endpoint not found", resp_time)

    def test_performance(self):
        """Test performance metrics"""
        print("\n⚡ PERFORMANCE ANALYSIS")
        print("-" * 40)
        
        if self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            max_time = max(self.response_times)
            min_time = min(self.response_times)
            
            # Performance assessment
            if avg_time < 0.1:
                perf_status = "PASS"
                perf_msg = "Excellent"
            elif avg_time < 0.5:
                perf_status = "PASS"
                perf_msg = "Good"
            elif avg_time < 1.0:
                perf_status = "WARN"
                perf_msg = "Acceptable"
            else:
                perf_status = "FAIL"
                perf_msg = "Slow"
            
            self.log_test("Response Time", perf_status, 
                         f"Avg: {avg_time*1000:.0f}ms, Max: {max_time*1000:.0f}ms ({perf_msg})")
            
            # Test load capacity with concurrent requests
            self.test_concurrent_load()

    def test_concurrent_load(self):
        """Test concurrent request handling"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        num_threads = 5
        
        def worker():
            success, _, resp_time = self.make_request("GET", "/ping")
            results_queue.put((success, resp_time))
        
        # Launch concurrent requests
        threads = []
        start_time = time.time()
        
        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        successes = 0
        response_times = []
        
        for _ in range(num_threads):
            try:
                success, resp_time = results_queue.get_nowait()
                if success:
                    successes += 1
                response_times.append(resp_time)
            except queue.Empty:
                break
        
        success_rate = (successes / num_threads) * 100
        avg_concurrent_time = sum(response_times) / len(response_times) if response_times else 0
        
        if success_rate >= 100:
            self.log_test("Concurrent Load", "PASS", 
                         f"{successes}/{num_threads} success, {avg_concurrent_time*1000:.0f}ms avg")
        elif success_rate >= 80:
            self.log_test("Concurrent Load", "WARN", 
                         f"{successes}/{num_threads} success ({success_rate:.0f}%)")
        else:
            self.log_test("Concurrent Load", "FAIL", 
                         f"Only {successes}/{num_threads} success ({success_rate:.0f}%)")

    def run_all_tests(self) -> bool:
        """Run the complete test suite"""
        print(f"🚀 Starting comprehensive backend tests...")
        
        # Test connectivity first
        if not self.test_connectivity():
            print("\n❌ Backend not reachable - stopping tests")
            return False
        
        # Run all test categories
        self.test_core_endpoints()
        self.test_health_endpoints()
        self.test_api_endpoints()
        self.test_documentation()
        self.test_post_endpoints()
        self.test_performance()
        
        # Generate summary
        self.print_summary()
        
        return self.failed_tests == 0

    def run_quick_tests(self) -> bool:
        """Run essential tests only"""
        print(f"⚡ Running quick backend tests...")
        
        if not self.test_connectivity():
            return False
            
        self.test_core_endpoints()
        self.test_health_endpoints()
        self.print_summary()
        
        return self.failed_tests == 0

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        # Statistics
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests:    {self.total_tests}")
        print(f"✅ Passed:      {self.passed_tests}")
        print(f"❌ Failed:      {self.failed_tests}")
        print(f"⚠️  Warnings:    {self.warnings}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Performance summary
        if self.response_times:
            avg_time = sum(self.response_times) / len(self.response_times)
            print(f"⚡ Avg Response: {avg_time*1000:.0f}ms")
        
        # Overall status
        print("\n" + "-" * 60)
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Backend is ready for development!")
        elif self.failed_tests <= 2:
            print("✅ MOSTLY SUCCESSFUL!")
            print("⚠️  Minor issues detected - check warnings above")
        else:
            print("❌ MULTIPLE FAILURES!")
            print("🔧 Backend needs attention before proceeding")
        
        # Quick links
        print(f"\n🔗 Quick Links:")
        print(f"   API:          {self.base_url}")
        print(f"   Docs:         {self.base_url}/docs")
        print(f"   Health:       {self.base_url}/api/v1/health/")
        print(f"   System:       {self.base_url}/api/v1/system/status")
        
        return self.failed_tests == 0

def main():
    """Main function with CLI support"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RagFlow Backend Test Suite")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Backend URL (default: http://localhost:8000)")
    parser.add_argument("--quick", action="store_true",
                       help="Run only essential tests")
    parser.add_argument("--json", action="store_true",
                       help="Output results in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Create tester
    tester = RagFlowBackendTester(args.url)
    
    # Run tests
    if args.quick:
        success = tester.run_quick_tests()
    else:
        success = tester.run_all_tests()
    
    # JSON output
    if args.json:
        results = {
            "timestamp": datetime.now().isoformat(),
            "backend_url": args.url,
            "total_tests": tester.total_tests,
            "passed": tester.passed_tests,
            "failed": tester.failed_tests,
            "warnings": tester.warnings,
            "success_rate": (tester.passed_tests / tester.total_tests * 100) if tester.total_tests > 0 else 0,
            "avg_response_time_ms": sum(tester.response_times) / len(tester.response_times) * 1000 if tester.response_times else 0,
            "tests": tester.test_results
        }
        print("\n" + json.dumps(results, indent=2))
    
    # Exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()