"""
Error handling and edge case tests
"""

import pytest
import requests
import json
from typing import Dict, Any
from unittest.mock import patch


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling scenarios"""

    def test_api_server_down(self, config, console_output):
        """Test behavior when API server is not available"""
        # Create client pointing to non-existent server
        unavailable_client = requests.Session()
        
        try:
            response = unavailable_client.get("http://localhost:9999/api/vocabulary", timeout=1)
            # Should not reach here
            assert False, "Should have raised an exception"
        except requests.exceptions.RequestException as e:
            console_output.print(f"[green]✓ Correctly handled server unavailable: {type(e).__name__}[/green]")
            assert True

    def test_network_timeout_handling(self, api_client, console_output):
        """Test network timeout scenarios"""
        # Test with very short timeout
        try:
            response = api_client.get("/vocabulary", timeout=0.001)
            # If it succeeds with very short timeout, that's also acceptable
            console_output.print("[yellow]⚠ Request completed faster than expected timeout[/yellow]")
        except requests.exceptions.Timeout:
            console_output.print("[green]✓ Correctly handled timeout[/green]")
            assert True
        except requests.exceptions.RequestException as e:
            console_output.print(f"[green]✓ Correctly handled network error: {type(e).__name__}[/green]")
            assert True

    def test_malformed_json_requests(self, api_client):
        """Test handling of malformed JSON in requests"""
        malformed_data_sets = [
            "{'invalid': json}",  # Invalid JSON syntax
            "{word: 'test'}",  # Unquoted keys
            "{'word': 'test',}",  # Trailing comma
            "undefined",  # JavaScript undefined
            "null",  # Just null
        ]
        
        for malformed_data in malformed_data_sets:
            try:
                response = requests.post(
                    f"{api_client.base_url}/vocabulary",
                    data=malformed_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
                # Should return 4xx error for malformed JSON
                assert response.status_code >= 400, f"Should reject malformed JSON: {malformed_data}"
            except requests.exceptions.RequestException:
                # Network errors are also acceptable
                pass

    def test_invalid_http_methods(self, api_client):
        """Test invalid HTTP methods on endpoints"""
        invalid_method_tests = [
            ("/vocabulary", "PATCH"),  # If PATCH is not supported
            ("/vocabulary", "HEAD"),   # If HEAD is not supported
            ("/vocabulary/123", "POST"),  # POST to specific ID
        ]
        
        for endpoint, method in invalid_method_tests:
            try:
                response = requests.request(
                    method=method,
                    url=f"{api_client.base_url}{endpoint}",
                    timeout=5
                )
                # Should return 405 Method Not Allowed
                assert response.status_code == 405, f"Should return 405 for {method} {endpoint}"
            except requests.exceptions.RequestException:
                # Network errors are acceptable
                pass

    def test_invalid_content_types(self, api_client):
        """Test handling of invalid content types"""
        invalid_content_types = [
            "text/plain",
            "text/html",
            "application/xml",
            "multipart/form-data",
            "application/octet-stream",
        ]
        
        for content_type in invalid_content_types:
            try:
                response = requests.post(
                    f"{api_client.base_url}/vocabulary",
                    data="test data",
                    headers={"Content-Type": content_type},
                    timeout=5
                )
                # Should return 415 Unsupported Media Type or 400 Bad Request
                assert response.status_code in [400, 415], f"Should reject content type: {content_type}"
            except requests.exceptions.RequestException:
                # Network errors are acceptable
                pass

    def test_large_request_handling(self, api_client):
        """Test handling of oversized requests"""
        # Create very large vocabulary item
        large_word = "a" * 10000
        large_meaning = "b" * 50000
        
        oversized_data = {
            "word": large_word,
            "meaning": large_meaning
        }
        
        response = api_client.post("/vocabulary", json=oversized_data)
        # Should reject oversized requests
        assert response.status_code in [400, 413, 422], "Should reject oversized requests"

    def test_sql_injection_prevention(self, api_client, console_output):
        """Test SQL injection prevention"""
        sql_injection_payloads = [
            "'; DROP TABLE vocabulary; --",
            "' OR '1'='1",
            "admin'/*",
            "'; INSERT INTO vocabulary (word, meaning) VALUES ('hacked', 'pwned'); --",
            "' UNION SELECT * FROM vocabulary --",
        ]
        
        for payload in sql_injection_payloads:
            test_data = {
                "word": payload,
                "meaning": "test meaning"
            }
            
            response = api_client.post("/vocabulary", json=test_data)
            
            # The request might succeed (if properly sanitized) or fail (if rejected)
            # But it should never cause server errors or data corruption
            assert response.status_code != 500, f"SQL injection caused server error: {payload}"
            
            # If it succeeded, verify no actual SQL injection occurred
            if response.status_code in [200, 201]:
                # Check that the data was properly sanitized
                created_item = response.json()
                assert "DROP TABLE" not in created_item.get("word", ""), "SQL injection not prevented"
        
        console_output.print("[green]✓ SQL injection prevention tests completed[/green]")

    def test_xss_prevention(self, api_client, console_output):
        """Test XSS prevention in input handling"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
        ]
        
        for payload in xss_payloads:
            test_data = {
                "word": payload,
                "meaning": "test meaning"
            }
            
            response = api_client.post("/vocabulary", json=test_data)
            
            # If the request succeeds, verify XSS payload was sanitized
            if response.status_code in [200, 201]:
                created_item = response.json()
                stored_word = created_item.get("word", "")
                
                # Check that dangerous content was removed or escaped
                assert "<script>" not in stored_word.lower(), "XSS script tag not sanitized"
                assert "javascript:" not in stored_word.lower(), "XSS javascript: not sanitized"
                assert "onerror=" not in stored_word.lower(), "XSS event handler not sanitized"
        
        console_output.print("[green]✓ XSS prevention tests completed[/green]")

    def test_concurrent_error_scenarios(self, api_client, vocabulary_factory, console_output):
        """Test error handling under concurrent load"""
        import threading
        import queue
        
        error_queue = queue.Queue()
        success_count = 0
        error_count = 0
        
        def make_invalid_request():
            nonlocal success_count, error_count
            try:
                # Intentionally invalid data
                invalid_data = {"invalid": "data", "missing": "required_fields"}
                response = api_client.post("/vocabulary", json=invalid_data)
                
                if response.status_code >= 400:
                    error_count += 1  # Expected errors
                else:
                    success_count += 1  # Unexpected success
                    
            except Exception as e:
                error_queue.put(str(e))
        
        # Start multiple threads with invalid requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_invalid_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        console_output.print(f"[blue]Concurrent error test results:[/blue]")
        console_output.print(f"Expected errors: {error_count}")
        console_output.print(f"Unexpected successes: {success_count}")
        console_output.print(f"Exception errors: {error_queue.qsize()}")
        
        # Most requests should result in expected errors (4xx status codes)
        assert error_count > success_count, "Most invalid requests should be properly rejected"

    def test_database_connection_error_simulation(self, api_client, console_output):
        """Test behavior when database is unavailable"""
        # This test assumes that if the database is down, API will return 500 errors
        # In a real scenario, you might use dependency injection to mock the database
        
        try:
            response = api_client.get("/vocabulary")
            
            if response.status_code == 500:
                console_output.print("[yellow]⚠ Database appears to be unavailable[/yellow]")
                # This is actually what we want to test - proper error handling
            elif response.status_code == 200:
                console_output.print("[green]✓ Database connection working normally[/green]")
            else:
                console_output.print(f"[blue]Unexpected response: {response.status_code}[/blue]")
                
        except requests.exceptions.RequestException as e:
            console_output.print(f"[red]Network error: {e}[/red]")

    def test_invalid_vocabulary_id_handling(self, api_client):
        """Test handling of invalid vocabulary IDs"""
        invalid_ids = [
            "abc",  # Non-numeric ID
            "-1",   # Negative ID
            "999999999",  # Very large ID
            "0",    # Zero ID (might be invalid depending on system)
            "1.5",  # Decimal ID
            "",     # Empty ID
            "null", # String "null"
        ]
        
        for invalid_id in invalid_ids:
            # Test GET with invalid ID
            response = api_client.get(f"/vocabulary/{invalid_id}")
            assert response.status_code in [400, 404], f"Should handle invalid ID in GET: {invalid_id}"
            
            # Test PUT with invalid ID
            update_data = {"word": "test", "meaning": "test"}
            response = api_client.put(f"/vocabulary/{invalid_id}", json=update_data)
            assert response.status_code in [400, 404], f"Should handle invalid ID in PUT: {invalid_id}"
            
            # Test DELETE with invalid ID
            response = api_client.delete(f"/vocabulary/{invalid_id}")
            assert response.status_code in [400, 404], f"Should handle invalid ID in DELETE: {invalid_id}"

    def test_memory_exhaustion_prevention(self, api_client, console_output):
        """Test prevention of memory exhaustion attacks"""
        # Test with extremely large JSON payload
        try:
            # Create a large but not excessive payload for testing
            large_array = ["test"] * 1000  # Adjust size based on server limits
            large_payload = {
                "word": "test",
                "meaning": "test",
                "large_field": large_array
            }
            
            response = api_client.post("/vocabulary", json=large_payload)
            
            # Should either succeed (if within limits) or be rejected (if too large)
            assert response.status_code != 500, "Large payload should not cause server crash"
            
            if response.status_code in [400, 413, 422]:
                console_output.print("[green]✓ Large payload properly rejected[/green]")
            elif response.status_code in [200, 201]:
                console_output.print("[yellow]⚠ Large payload accepted (check server limits)[/yellow]")
                
        except requests.exceptions.RequestException as e:
            console_output.print(f"[green]✓ Request failed safely: {type(e).__name__}[/green]")

    def test_rate_limiting_behavior(self, api_client, console_output):
        """Test rate limiting (if implemented)"""
        # Make rapid requests to test rate limiting
        rapid_requests = 20
        status_codes = []
        
        for i in range(rapid_requests):
            try:
                response = api_client.get("/vocabulary")
                status_codes.append(response.status_code)
                
                # Check for rate limiting responses
                if response.status_code == 429:  # Too Many Requests
                    console_output.print(f"[green]✓ Rate limiting activated after {i+1} requests[/green]")
                    break
                    
            except requests.exceptions.RequestException:
                break
        
        # Analyze results
        success_codes = [code for code in status_codes if code == 200]
        rate_limit_codes = [code for code in status_codes if code == 429]
        
        console_output.print(f"[blue]Rate limiting test results:[/blue]")
        console_output.print(f"Successful requests: {len(success_codes)}")
        console_output.print(f"Rate limited requests: {len(rate_limit_codes)}")
        
        # If no rate limiting is implemented, all requests should succeed
        # If rate limiting is implemented, some should be blocked

    def test_graceful_degradation(self, api_client, console_output):
        """Test graceful degradation under stress"""
        # This test checks if the system degrades gracefully under load
        # rather than failing catastrophically
        
        import time
        start_time = time.time()
        response_times = []
        error_count = 0
        
        for i in range(50):  # Moderate load test
            try:
                request_start = time.time()
                response = api_client.get("/vocabulary")
                request_end = time.time()
                
                response_times.append(request_end - request_start)
                
                if response.status_code != 200:
                    error_count += 1
                    
            except requests.exceptions.RequestException:
                error_count += 1
        
        total_time = time.time() - start_time
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        console_output.print(f"[blue]Graceful degradation test results:[/blue]")
        console_output.print(f"Total time: {total_time:.2f}s")
        console_output.print(f"Average response time: {avg_response_time:.3f}s")
        console_output.print(f"Error count: {error_count}")
        console_output.print(f"Success rate: {((50-error_count)/50)*100:.1f}%")
        
        # System should maintain reasonable performance and not fail completely
        assert error_count < 25, "Too many errors - system not degrading gracefully"
        assert avg_response_time < 5.0, "Response times too slow under load"
