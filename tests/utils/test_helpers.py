"""
Helper utilities for testing
"""

import json
import time
import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import requests


class TestHelpers:
    """Collection of helper methods for testing"""
    
    @staticmethod
    def wait_for_api_availability(base_url: str, timeout: int = 30, interval: int = 1) -> bool:
        """Wait for API to become available"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(base_url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(interval)
        
        return False
    
    @staticmethod
    def create_test_file(content: str, suffix: str = ".json") -> str:
        """Create a temporary test file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            return f.name
    
    @staticmethod
    def cleanup_test_file(file_path: str):
        """Remove test file"""
        try:
            os.unlink(file_path)
        except OSError:
            pass
    
    @staticmethod
    def create_test_directory() -> str:
        """Create a temporary test directory"""
        return tempfile.mkdtemp()
    
    @staticmethod
    def cleanup_test_directory(dir_path: str):
        """Remove test directory and all contents"""
        try:
            shutil.rmtree(dir_path)
        except OSError:
            pass
    
    @staticmethod
    def assert_api_response_structure(response_data: Dict[str, Any], required_fields: List[str]):
        """Assert that API response has required structure"""
        for field in required_fields:
            assert field in response_data, f"Missing required field: {field}"
    
    @staticmethod
    def assert_vocabulary_item_valid(vocab_item: Dict[str, Any]):
        """Assert that vocabulary item has valid structure"""
        required_fields = ["word", "meaning"]
        TestHelpers.assert_api_response_structure(vocab_item, required_fields)
        
        assert isinstance(vocab_item["word"], str), "Word must be string"
        assert isinstance(vocab_item["meaning"], str), "Meaning must be string"
        assert len(vocab_item["word"].strip()) > 0, "Word cannot be empty"
        assert len(vocab_item["meaning"].strip()) > 0, "Meaning cannot be empty"
    
    @staticmethod
    def measure_response_time(func, *args, **kwargs) -> tuple:
        """Measure function execution time and return (result, duration)"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        return result, duration
    
    @staticmethod
    def retry_operation(func, max_retries: int = 3, delay: float = 1.0, *args, **kwargs):
        """Retry operation with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay * (2 ** attempt))
    
    @staticmethod
    def compare_vocabulary_items(item1: Dict[str, Any], item2: Dict[str, Any], 
                                ignore_fields: List[str] = None) -> bool:
        """Compare two vocabulary items, optionally ignoring certain fields"""
        if ignore_fields is None:
            ignore_fields = ["id", "created_at", "updated_at"]
        
        for key in item1:
            if key not in ignore_fields:
                if key not in item2 or item1[key] != item2[key]:
                    return False
        
        for key in item2:
            if key not in ignore_fields:
                if key not in item1:
                    return False
        
        return True
    
    @staticmethod
    def generate_test_report(test_results: Dict[str, Any], output_file: str = None) -> str:
        """Generate HTML test report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Vocabulary App Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
                .warning {{ color: orange; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Vocabulary App Test Report</h1>
                <p>Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Test Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Tests</td><td>{test_results.get('total_tests', 0)}</td></tr>
                    <tr><td>Passed</td><td class="success">{test_results.get('passed', 0)}</td></tr>
                    <tr><td>Failed</td><td class="error">{test_results.get('failed', 0)}</td></tr>
                    <tr><td>Skipped</td><td class="warning">{test_results.get('skipped', 0)}</td></tr>
                    <tr><td>Success Rate</td><td>{test_results.get('success_rate', 0)}%</td></tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Performance Metrics</h2>
                <table>
                    <tr><th>Operation</th><th>Average Time (s)</th><th>Max Time (s)</th></tr>
        """
        
        performance_metrics = test_results.get('performance_metrics', {})
        for operation, metrics in performance_metrics.items():
            html_content += f"""
                    <tr>
                        <td>{operation}</td>
                        <td>{metrics.get('avg_time', 'N/A')}</td>
                        <td>{metrics.get('max_time', 'N/A')}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content
    
    @staticmethod
    def log_test_step(step_name: str, details: str = ""):
        """Log test step with timestamp"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] {step_name}: {details}")
    
    @staticmethod
    def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Basic JSON schema validation"""
        try:
            # This is a simplified schema validator
            # In a real project, you might use jsonschema library
            
            for field, field_type in schema.items():
                if field not in data:
                    return False
                
                if field_type == "string" and not isinstance(data[field], str):
                    return False
                elif field_type == "integer" and not isinstance(data[field], int):
                    return False
                elif field_type == "array" and not isinstance(data[field], list):
                    return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def create_mock_api_response(status_code: int = 200, data: Any = None, headers: Dict[str, str] = None):
        """Create mock API response for testing"""
        class MockResponse:
            def __init__(self, status_code: int, data: Any, headers: Dict[str, str]):
                self.status_code = status_code
                self._data = data
                self.headers = headers or {}
            
            def json(self):
                return self._data
            
            def text(self):
                return json.dumps(self._data) if self._data else ""
        
        return MockResponse(status_code, data, headers)
    
    @staticmethod
    def extract_test_metrics(test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract metrics from test results"""
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result.get('status') == 'passed')
        failed_tests = sum(1 for result in test_results if result.get('status') == 'failed')
        skipped_tests = sum(1 for result in test_results if result.get('status') == 'skipped')
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Extract timing information
        execution_times = [result.get('duration', 0) for result in test_results if result.get('duration')]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'skipped': skipped_tests,
            'success_rate': round(success_rate, 2),
            'avg_execution_time': round(avg_execution_time, 3),
            'total_execution_time': round(sum(execution_times), 3)
        }
    
    @staticmethod
    def backup_test_data(data: Any, backup_file: str):
        """Backup test data to file"""
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Failed to backup test data: {e}")
            return False
    
    @staticmethod
    def restore_test_data(backup_file: str) -> Any:
        """Restore test data from file"""
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to restore test data: {e}")
            return None
    
    @staticmethod
    def check_test_environment() -> Dict[str, bool]:
        """Check test environment readiness"""
        checks = {
            'api_server': False,
            'database': False,
            'network': False
        }
        
        # Check API server
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            checks['api_server'] = response.status_code == 200
        except:
            pass
        
        # Check database (indirect through API)
        try:
            response = requests.get("http://localhost:3000/api/vocabulary", timeout=5)
            checks['database'] = response.status_code in [200, 404]  # 404 is okay (empty database)
        except:
            pass
        
        # Check network connectivity
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            checks['network'] = True
        except:
            pass
        
        return checks
    
    @staticmethod
    def generate_test_data_summary(test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of test data"""
        if not test_data:
            return {'total_items': 0}
        
        total_items = len(test_data)
        
        # Count by difficulty if available
        difficulties = {}
        categories = {}
        
        for item in test_data:
            if 'difficulty' in item:
                difficulty = item['difficulty']
                difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
            
            if 'category' in item:
                category = item['category']
                categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_items': total_items,
            'difficulties': difficulties,
            'categories': categories,
            'has_difficulty_field': bool(difficulties),
            'has_category_field': bool(categories)
        }
