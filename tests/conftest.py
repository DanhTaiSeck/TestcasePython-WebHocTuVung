"""
Pytest configuration and shared fixtures
"""

import pytest
import requests
import json
import time
from typing import Dict, List, Any, Generator
from faker import Faker
from rich.console import Console
from tests.factories.vocabulary_factory import VocabularyFactory
from tests.utils.test_helpers import TestHelpers

# Initialize console for rich output
console = Console()
fake = Faker(['en_US', 'vi_VN'])

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:3000",
    "api_base": "http://localhost:3000/api",
    "timeout": 30,
    "max_retries": 3,
    "test_data_size": 10
}

@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """Global test configuration"""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def console_output():
    """Rich console for formatted output"""
    return console

@pytest.fixture(scope="session")
def api_client(config):
    """HTTP client for API testing"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'VocabularyApp-TestSuite/1.0'
    })
    
    class APIClient:
        def __init__(self, base_url: str, session: requests.Session):
            self.base_url = base_url
            self.session = session
            
        def get(self, endpoint: str, **kwargs):
            return self.session.get(f"{self.base_url}{endpoint}", **kwargs)
            
        def post(self, endpoint: str, **kwargs):
            return self.session.post(f"{self.base_url}{endpoint}", **kwargs)
            
        def put(self, endpoint: str, **kwargs):
            return self.session.put(f"{self.base_url}{endpoint}", **kwargs)
            
        def delete(self, endpoint: str, **kwargs):
            return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)
    
    return APIClient(config["api_base"], session)

@pytest.fixture(scope="function")
def vocabulary_factory():
    """Factory for creating test vocabulary data"""
    return VocabularyFactory()

@pytest.fixture(scope="function")
def test_helpers():
    """Helper utilities for tests"""
    return TestHelpers()

@pytest.fixture(scope="function")
def clean_vocabulary_data(api_client, console_output):
    """Clean up vocabulary data before and after tests"""
    def cleanup():
        try:
            response = api_client.get("/vocabulary")
            if response.status_code == 200:
                vocabularies = response.json()
                for vocab in vocabularies:
                    if 'id' in vocab:
                        api_client.delete(f"/vocabulary/{vocab['id']}")
            console_output.print("[green]✓ Cleaned up test vocabulary data[/green]")
        except Exception as e:
            console_output.print(f"[yellow]⚠ Warning: Could not clean vocabulary data: {e}[/yellow]")
    
    # Cleanup before test
    cleanup()
    yield
    # Cleanup after test
    cleanup()

@pytest.fixture(scope="function")
def sample_vocabulary_data(vocabulary_factory):
    """Generate sample vocabulary data for testing"""
    return vocabulary_factory.create_batch(5)

@pytest.fixture(scope="function")
def large_vocabulary_dataset(vocabulary_factory):
    """Generate large dataset for performance testing"""
    return vocabulary_factory.create_batch(100)

@pytest.fixture(scope="function")
def quiz_data():
    """Sample quiz data for testing"""
    return [
        {"word": "hello", "meaning": "xin chào", "difficulty": "easy"},
        {"word": "beautiful", "meaning": "đẹp", "difficulty": "medium"},
        {"word": "extraordinary", "meaning": "phi thường", "difficulty": "hard"},
        {"word": "serendipity", "meaning": "may mắn bất ngờ", "difficulty": "hard"},
        {"word": "book", "meaning": "sách", "difficulty": "easy"}
    ]

@pytest.fixture(scope="function")
def performance_monitor():
    """Monitor for performance testing"""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.metrics = {}
            
        def start(self):
            self.start_time = time.time()
            
        def stop(self):
            self.end_time = time.time()
            
        def get_duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
            
        def add_metric(self, name: str, value: Any):
            self.metrics[name] = value
            
        def get_metrics(self):
            return self.metrics
    
    return PerformanceMonitor()

@pytest.fixture(autouse=True)
def test_environment_check(console_output):
    """Check if test environment is ready"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code != 200:
            console_output.print("[red]❌ Test server not accessible[/red]")
            pytest.skip("Test server not available")
    except requests.exceptions.RequestException:
        console_output.print("[red]❌ Test server not running on localhost:3000[/red]")
        pytest.skip("Test server not running")

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )

def pytest_runtest_setup(item):
    """Setup for each test"""
    console.print(f"[blue]🧪 Running: {item.name}[/blue]")

def pytest_runtest_teardown(item):
    """Teardown for each test"""
    console.print(f"[green]✅ Completed: {item.name}[/green]")
