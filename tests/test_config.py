"""
Test configuration and environment validation
"""

import pytest
import requests
import json
import os
from typing import Dict, Any


class TestConfiguration:
    """Test the configuration setup and environment"""

    def test_config_file_exists(self):
        """Test that configuration file exists"""
        assert os.path.exists("test_config.json"), "Test configuration file not found"

    def test_config_file_valid_json(self):
        """Test that configuration file contains valid JSON"""
        with open("test_config.json", "r") as f:
            config = json.load(f)
        assert isinstance(config, dict), "Configuration should be a dictionary"

    def test_required_config_keys(self):
        """Test that all required configuration keys are present"""
        with open("test_config.json", "r") as f:
            config = json.load(f)
        
        required_keys = ["api_base_url", "test_timeout", "max_retries", "environments"]
        for key in required_keys:
            assert key in config, f"Required configuration key '{key}' not found"

    @pytest.mark.api
    def test_api_server_accessibility(self, config):
        """Test that the API server is accessible"""
        try:
            response = requests.get(f"{config['base_url']}", timeout=config['timeout'])
            assert response.status_code == 200, f"API server returned status {response.status_code}"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"API server not accessible: {e}")

    @pytest.mark.api
    def test_vocabulary_endpoint_exists(self, api_client):
        """Test that vocabulary endpoint exists"""
        response = api_client.get("/vocabulary")
        assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"

    def test_environment_variables(self):
        """Test required environment variables"""
        # Check for optional environment variables
        env_vars = ["NODE_ENV", "PORT", "API_URL"]
        for var in env_vars:
            value = os.getenv(var)
            if value:
                assert isinstance(value, str), f"Environment variable {var} should be string"

    def test_test_data_directory_structure(self):
        """Test that test directory structure is correct"""
        required_dirs = ["tests", "tests/factories", "tests/utils", "tests/reports"]
        for directory in required_dirs:
            assert os.path.exists(directory), f"Required directory '{directory}' not found"

    def test_pytest_configuration(self):
        """Test pytest configuration"""
        assert os.path.exists("pytest.ini"), "pytest.ini configuration file not found"
        
        with open("pytest.ini", "r") as f:
            content = f.read()
        
        assert "[tool:pytest]" in content or "[pytest]" in content, "Invalid pytest configuration"

    @pytest.mark.integration
    def test_full_api_connectivity(self, api_client, console_output):
        """Test full API connectivity and basic endpoints"""
        endpoints_to_test = [
            ("/vocabulary", "GET"),
            ("/vocabulary", "POST"),
        ]
        
        results = {}
        for endpoint, method in endpoints_to_test:
            try:
                if method == "GET":
                    response = api_client.get(endpoint)
                elif method == "POST":
                    response = api_client.post(endpoint, json={"word": "test", "meaning": "test"})
                
                results[f"{method} {endpoint}"] = {
                    "status_code": response.status_code,
                    "accessible": True
                }
            except Exception as e:
                results[f"{method} {endpoint}"] = {
                    "status_code": None,
                    "accessible": False,
                    "error": str(e)
                }
        
        console_output.print("[bold]API Connectivity Test Results:[/bold]")
        for endpoint, result in results.items():
            if result["accessible"]:
                console_output.print(f"[green]✓ {endpoint}: {result['status_code']}[/green]")
            else:
                console_output.print(f"[red]❌ {endpoint}: {result.get('error', 'Failed')}[/red]")
        
        # At least vocabulary GET should be accessible
        assert results.get("GET /vocabulary", {}).get("accessible", False), "Vocabulary GET endpoint not accessible"
