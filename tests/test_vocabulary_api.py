"""
Comprehensive API tests for vocabulary endpoints
"""

import pytest
import json
import time
from typing import Dict, List, Any


@pytest.mark.api
class TestVocabularyAPI:
    """Test vocabulary CRUD operations via API"""

    def test_get_empty_vocabulary_list(self, api_client, clean_vocabulary_data):
        """Test getting vocabulary when list is empty"""
        response = api_client.get("/vocabulary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_single_vocabulary(self, api_client, clean_vocabulary_data, vocabulary_factory):
        """Test creating a single vocabulary item"""
        vocab_data = vocabulary_factory.create()
        
        response = api_client.post("/vocabulary", json=vocab_data)
        assert response.status_code in [200, 201], f"Failed to create vocabulary: {response.text}"
        
        created_vocab = response.json()
        assert "id" in created_vocab
        assert created_vocab["word"] == vocab_data["word"]
        assert created_vocab["meaning"] == vocab_data["meaning"]

    def test_create_vocabulary_with_invalid_data(self, api_client, clean_vocabulary_data):
        """Test creating vocabulary with invalid data"""
        invalid_data_sets = [
            {},  # Empty object
            {"word": ""},  # Empty word
            {"meaning": "test"},  # Missing word
            {"word": "test"},  # Missing meaning
            {"word": None, "meaning": "test"},  # None values
            {"word": "test", "meaning": None},
        ]
        
        for invalid_data in invalid_data_sets:
            response = api_client.post("/vocabulary", json=invalid_data)
            assert response.status_code in [400, 422], f"Should reject invalid data: {invalid_data}"

    def test_get_vocabulary_list_after_creation(self, api_client, clean_vocabulary_data, sample_vocabulary_data):
        """Test getting vocabulary list after creating items"""
        # Create multiple vocabulary items
        created_ids = []
        for vocab_data in sample_vocabulary_data:
            response = api_client.post("/vocabulary", json=vocab_data)
            assert response.status_code in [200, 201]
            created_vocab = response.json()
            created_ids.append(created_vocab["id"])
        
        # Get all vocabulary
        response = api_client.get("/vocabulary")
        assert response.status_code == 200
        
        vocabulary_list = response.json()
        assert len(vocabulary_list) >= len(sample_vocabulary_data)
        
        # Verify all created items are in the list
        returned_ids = [vocab["id"] for vocab in vocabulary_list]
        for created_id in created_ids:
            assert created_id in returned_ids

    def test_update_vocabulary_item(self, api_client, clean_vocabulary_data, vocabulary_factory):
        """Test updating an existing vocabulary item"""
        # Create a vocabulary item
        original_data = vocabulary_factory.create()
        response = api_client.post("/vocabulary", json=original_data)
        assert response.status_code in [200, 201]
        
        created_vocab = response.json()
        vocab_id = created_vocab["id"]
        
        # Update the item
        updated_data = vocabulary_factory.create()
        response = api_client.put(f"/vocabulary/{vocab_id}", json=updated_data)
        assert response.status_code in [200, 204]
        
        # Verify the update
        response = api_client.get("/vocabulary")
        assert response.status_code == 200
        
        vocabulary_list = response.json()
        updated_vocab = next((v for v in vocabulary_list if v["id"] == vocab_id), None)
        assert updated_vocab is not None
        assert updated_vocab["word"] == updated_data["word"]
        assert updated_vocab["meaning"] == updated_data["meaning"]

    def test_update_nonexistent_vocabulary(self, api_client, vocabulary_factory):
        """Test updating a vocabulary item that doesn't exist"""
        nonexistent_id = 99999
        update_data = vocabulary_factory.create()
        
        response = api_client.put(f"/vocabulary/{nonexistent_id}", json=update_data)
        assert response.status_code == 404

    def test_delete_vocabulary_item(self, api_client, clean_vocabulary_data, vocabulary_factory):
        """Test deleting a vocabulary item"""
        # Create a vocabulary item
        vocab_data = vocabulary_factory.create()
        response = api_client.post("/vocabulary", json=vocab_data)
        assert response.status_code in [200, 201]
        
        created_vocab = response.json()
        vocab_id = created_vocab["id"]
        
        # Delete the item
        response = api_client.delete(f"/vocabulary/{vocab_id}")
        assert response.status_code in [200, 204]
        
        # Verify deletion
        response = api_client.get("/vocabulary")
        assert response.status_code == 200
        
        vocabulary_list = response.json()
        deleted_vocab = next((v for v in vocabulary_list if v["id"] == vocab_id), None)
        assert deleted_vocab is None

    def test_delete_nonexistent_vocabulary(self, api_client):
        """Test deleting a vocabulary item that doesn't exist"""
        nonexistent_id = 99999
        response = api_client.delete(f"/vocabulary/{nonexistent_id}")
        assert response.status_code == 404

    @pytest.mark.slow
    def test_bulk_vocabulary_operations(self, api_client, clean_vocabulary_data, large_vocabulary_dataset, performance_monitor):
        """Test bulk operations with large dataset"""
        performance_monitor.start()
        
        # Bulk create
        created_ids = []
        for vocab_data in large_vocabulary_dataset:
            response = api_client.post("/vocabulary", json=vocab_data)
            if response.status_code in [200, 201]:
                created_vocab = response.json()
                created_ids.append(created_vocab["id"])
        
        performance_monitor.add_metric("bulk_create_count", len(created_ids))
        
        # Bulk read
        response = api_client.get("/vocabulary")
        assert response.status_code == 200
        vocabulary_list = response.json()
        performance_monitor.add_metric("bulk_read_count", len(vocabulary_list))
        
        # Bulk delete
        deleted_count = 0
        for vocab_id in created_ids[:10]:  # Delete first 10 items
            response = api_client.delete(f"/vocabulary/{vocab_id}")
            if response.status_code in [200, 204]:
                deleted_count += 1
        
        performance_monitor.add_metric("bulk_delete_count", deleted_count)
        performance_monitor.stop()
        
        assert len(created_ids) > 0, "Should create at least some vocabulary items"
        assert deleted_count > 0, "Should delete at least some vocabulary items"

    def test_vocabulary_data_validation(self, api_client, clean_vocabulary_data):
        """Test vocabulary data validation rules"""
        test_cases = [
            # Test word length limits
            {"word": "a" * 100, "meaning": "test", "should_pass": False},
            {"word": "test", "meaning": "a" * 500, "should_pass": False},
            
            # Test special characters
            {"word": "test-word", "meaning": "từ thử nghiệm", "should_pass": True},
            {"word": "test_word", "meaning": "từ thử nghiệm", "should_pass": True},
            {"word": "test123", "meaning": "từ thử nghiệm", "should_pass": True},
            
            # Test unicode characters
            {"word": "café", "meaning": "quán cà phê", "should_pass": True},
            {"word": "naïve", "meaning": "ngây thơ", "should_pass": True},
            
            # Test empty strings after trim
            {"word": "   ", "meaning": "test", "should_pass": False},
            {"word": "test", "meaning": "   ", "should_pass": False},
        ]
        
        for test_case in test_cases:
            vocab_data = {"word": test_case["word"], "meaning": test_case["meaning"]}
            response = api_client.post("/vocabulary", json=vocab_data)
            
            if test_case["should_pass"]:
                assert response.status_code in [200, 201], f"Should accept valid data: {vocab_data}"
            else:
                assert response.status_code in [400, 422], f"Should reject invalid data: {vocab_data}"

    def test_api_response_format(self, api_client, clean_vocabulary_data, vocabulary_factory):
        """Test API response format consistency"""
        # Test POST response format
        vocab_data = vocabulary_factory.create()
        response = api_client.post("/vocabulary", json=vocab_data)
        assert response.status_code in [200, 201]
        
        created_vocab = response.json()
        required_fields = ["id", "word", "meaning"]
        for field in required_fields:
            assert field in created_vocab, f"Missing field '{field}' in POST response"
        
        # Test GET response format
        response = api_client.get("/vocabulary")
        assert response.status_code == 200
        
        vocabulary_list = response.json()
        assert isinstance(vocabulary_list, list), "GET /vocabulary should return a list"
        
        if vocabulary_list:  # If list is not empty
            for vocab in vocabulary_list:
                for field in required_fields:
                    assert field in vocab, f"Missing field '{field}' in GET response item"

    def test_concurrent_vocabulary_operations(self, api_client, clean_vocabulary_data, vocabulary_factory):
        """Test concurrent operations on vocabulary"""
        import threading
        import queue
        
        results = queue.Queue()
        vocab_data = vocabulary_factory.create()
        
        def create_vocabulary():
            try:
                response = api_client.post("/vocabulary", json=vocab_data)
                results.put(("create", response.status_code, response.json() if response.status_code in [200, 201] else None))
            except Exception as e:
                results.put(("create", None, str(e)))
        
        def read_vocabulary():
            try:
                response = api_client.get("/vocabulary")
                results.put(("read", response.status_code, len(response.json()) if response.status_code == 200 else 0))
            except Exception as e:
                results.put(("read", None, str(e)))
        
        # Start concurrent operations
        threads = []
        for _ in range(3):
            threads.append(threading.Thread(target=create_vocabulary))
            threads.append(threading.Thread(target=read_vocabulary))
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Collect results
        create_results = []
        read_results = []
        
        while not results.empty():
            operation, status_code, data = results.get()
            if operation == "create":
                create_results.append((status_code, data))
            elif operation == "read":
                read_results.append((status_code, data))
        
        # Verify results
        assert len(create_results) == 3, "Should have 3 create operation results"
        assert len(read_results) == 3, "Should have 3 read operation results"
        
        # At least some operations should succeed
        successful_creates = sum(1 for status, _ in create_results if status in [200, 201])
        successful_reads = sum(1 for status, _ in read_results if status == 200)
        
        assert successful_creates > 0, "At least one create operation should succeed"
        assert successful_reads > 0, "At least one read operation should succeed"
