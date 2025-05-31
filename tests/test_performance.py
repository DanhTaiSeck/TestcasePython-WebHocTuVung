"""
Performance tests for vocabulary learning app
"""

import pytest
import time
import statistics
import threading
import concurrent.futures
from typing import List, Dict, Any


@pytest.mark.performance
@pytest.mark.slow
class TestPerformance:
    """Performance testing for vocabulary app"""

    def test_api_response_time(self, api_client, performance_monitor, console_output):
        """Test API response times under normal load"""
        endpoints = [
            ("/vocabulary", "GET"),
        ]
        
        response_times = {}
        
        for endpoint, method in endpoints:
            times = []
            
            for _ in range(10):  # 10 requests per endpoint
                performance_monitor.start()
                
                if method == "GET":
                    response = api_client.get(endpoint)
                
                performance_monitor.stop()
                
                if response.status_code == 200:
                    times.append(performance_monitor.get_duration())
            
            if times:
                response_times[f"{method} {endpoint}"] = {
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "max": max(times),
                    "min": min(times)
                }
        
        # Display results
        console_output.print("\n[bold]API Response Time Results:[/bold]")
        for endpoint, stats in response_times.items():
            console_output.print(f"[blue]{endpoint}:[/blue]")
            console_output.print(f"  Mean: {stats['mean']:.3f}s")
            console_output.print(f"  Median: {stats['median']:.3f}s")
            console_output.print(f"  Max: {stats['max']:.3f}s")
            console_output.print(f"  Min: {stats['min']:.3f}s")
        
        # Performance assertions
        for endpoint, stats in response_times.items():
            assert stats["mean"] < 2.0, f"{endpoint} average response time too slow: {stats['mean']:.3f}s"
            assert stats["max"] < 5.0, f"{endpoint} max response time too slow: {stats['max']:.3f}s"

    def test_concurrent_api_requests(self, api_client, performance_monitor, console_output):
        """Test API performance under concurrent load"""
        num_concurrent_requests = 20
        
        def make_request():
            try:
                start_time = time.time()
                response = api_client.get("/vocabulary")
                end_time = time.time()
                
                return {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "status_code": None,
                    "response_time": None,
                    "success": False,
                    "error": str(e)
                }
        
        # Execute concurrent requests
        performance_monitor.start()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_request = {executor.submit(make_request): i for i in range(num_concurrent_requests)}
            results = []
            
            for future in concurrent.futures.as_completed(future_to_request):
                result = future.result()
                results.append(result)
        
        performance_monitor.stop()
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        success_rate = (len(successful_requests) / len(results)) * 100
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = float('inf')
            max_response_time = float('inf')
        
        # Display results
        console_output.print(f"\n[bold]Concurrent Load Test Results:[/bold]")
        console_output.print(f"Total requests: {len(results)}")
        console_output.print(f"Successful requests: {len(successful_requests)}")
        console_output.print(f"Failed requests: {len(failed_requests)}")
        console_output.print(f"Success rate: {success_rate:.1f}%")
        console_output.print(f"Average response time: {avg_response_time:.3f}s")
        console_output.print(f"Max response time: {max_response_time:.3f}s")
        console_output.print(f"Total test duration: {performance_monitor.get_duration():.3f}s")
        
        # Performance assertions
        assert success_rate >= 90.0, f"Success rate too low: {success_rate:.1f}%"
        assert avg_response_time < 3.0, f"Average response time too slow: {avg_response_time:.3f}s"

    def test_large_vocabulary_list_performance(self, api_client, clean_vocabulary_data, large_vocabulary_dataset, performance_monitor, console_output):
        """Test performance with large vocabulary datasets"""
        # Create large dataset
        console_output.print(f"[blue]Creating {len(large_vocabulary_dataset)} vocabulary items...[/blue]")
        
        creation_times = []
        created_count = 0
        
        for vocab_data in large_vocabulary_dataset[:50]:  # Limit to 50 for performance
            start_time = time.time()
            response = api_client.post("/vocabulary", json=vocab_data)
            end_time = time.time()
            
            creation_times.append(end_time - start_time)
            
            if response.status_code in [200, 201]:
                created_count += 1
        
        # Test retrieval performance
        performance_monitor.start()
        response = api_client.get("/vocabulary")
        performance_monitor.stop()
        
        retrieval_time = performance_monitor.get_duration()
        
        if response.status_code == 200:
            vocabulary_list = response.json()
            retrieved_count = len(vocabulary_list)
        else:
            retrieved_count = 0
        
        # Calculate statistics
        if creation_times:
            avg_creation_time = statistics.mean(creation_times)
            max_creation_time = max(creation_times)
        else:
            avg_creation_time = 0
            max_creation_time = 0
        
        # Display results
        console_output.print(f"\n[bold]Large Dataset Performance Results:[/bold]")
        console_output.print(f"Items created: {created_count}")
        console_output.print(f"Items retrieved: {retrieved_count}")
        console_output.print(f"Average creation time: {avg_creation_time:.3f}s")
        console_output.print(f"Max creation time: {max_creation_time:.3f}s")
        console_output.print(f"Retrieval time: {retrieval_time:.3f}s")
        
        # Performance assertions
        assert avg_creation_time < 1.0, f"Average creation time too slow: {avg_creation_time:.3f}s"
        assert retrieval_time < 2.0, f"Retrieval time too slow for {retrieved_count} items: {retrieval_time:.3f}s"

    def test_memory_usage_monitoring(self, api_client, console_output):
        """Test memory usage during operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform operations that might consume memory
        for i in range(10):
            response = api_client.get("/vocabulary")
            if response.status_code == 200:
                data = response.json()  # Keep reference to data
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        console_output.print(f"\n[bold]Memory Usage Results:[/bold]")
        console_output.print(f"Initial memory: {initial_memory:.2f} MB")
        console_output.print(f"Final memory: {final_memory:.2f} MB")
        console_output.print(f"Memory increase: {memory_increase:.2f} MB")
        
        # Memory assertions (these might be environment-dependent)
        assert memory_increase < 50, f"Memory increase too high: {memory_increase:.2f} MB"

    def test_quiz_performance(self, quiz_data, performance_monitor, console_output):
        """Test quiz processing performance"""
        from tests.test_quiz_logic import Quiz
        
        # Test quiz creation performance
        performance_monitor.start()
        quiz = Quiz(quiz_data)
        performance_monitor.stop()
        
        creation_time = performance_monitor.get_duration()
        
        # Test quiz answer processing performance
        answer_times = []
        
        for vocab in quiz_data:
            start_time = time.time()
            quiz.check_answer(vocab["meaning"])
            end_time = time.time()
            answer_times.append(end_time - start_time)
        
        avg_answer_time = statistics.mean(answer_times) if answer_times else 0
        max_answer_time = max(answer_times) if answer_times else 0
        
        console_output.print(f"\n[bold]Quiz Performance Results:[/bold]")
        console_output.print(f"Quiz creation time: {creation_time:.6f}s")
        console_output.print(f"Average answer processing time: {avg_answer_time:.6f}s")
        console_output.print(f"Max answer processing time: {max_answer_time:.6f}s")
        
        # Performance assertions
        assert creation_time < 0.1, f"Quiz creation too slow: {creation_time:.6f}s"
        assert avg_answer_time < 0.001, f"Answer processing too slow: {avg_answer_time:.6f}s"

    def test_stress_test_vocabulary_operations(self, api_client, clean_vocabulary_data, vocabulary_factory, performance_monitor, console_output):
        """Stress test with rapid operations"""
        operations_count = 100
        successful_operations = 0
        failed_operations = 0
        operation_times = []
        
        console_output.print(f"[blue]Running stress test with {operations_count} operations...[/blue]")
        
        performance_monitor.start()
        
        for i in range(operations_count):
            try:
                # Mix of operations
                if i % 3 == 0:
                    # CREATE
                    vocab_data = vocabulary_factory.create()
                    start_time = time.time()
                    response = api_client.post("/vocabulary", json=vocab_data)
                    end_time = time.time()
                    
                    if response.status_code in [200, 201]:
                        successful_operations += 1
                    else:
                        failed_operations += 1
                        
                elif i % 3 == 1:
                    # READ
                    start_time = time.time()
                    response = api_client.get("/vocabulary")
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        successful_operations += 1
                    else:
                        failed_operations += 1
                        
                else:
                    # READ (more reads than writes)
                    start_time = time.time()
                    response = api_client.get("/vocabulary")
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        successful_operations += 1
                    else:
                        failed_operations += 1
                
                operation_times.append(end_time - start_time)
                
            except Exception as e:
                failed_operations += 1
                console_output.print(f"[red]Operation {i} failed: {e}[/red]")
        
        performance_monitor.stop()
        
        # Calculate statistics
        total_time = performance_monitor.get_duration()
        operations_per_second = operations_count / total_time if total_time > 0 else 0
        success_rate = (successful_operations / operations_count) * 100
        
        if operation_times:
            avg_operation_time = statistics.mean(operation_times)
            max_operation_time = max(operation_times)
        else:
            avg_operation_time = 0
            max_operation_time = 0
        
        console_output.print(f"\n[bold]Stress Test Results:[/bold]")
        console_output.print(f"Total operations: {operations_count}")
        console_output.print(f"Successful operations: {successful_operations}")
        console_output.print(f"Failed operations: {failed_operations}")
        console_output.print(f"Success rate: {success_rate:.1f}%")
        console_output.print(f"Total time: {total_time:.3f}s")
        console_output.print(f"Operations per second: {operations_per_second:.2f}")
        console_output.print(f"Average operation time: {avg_operation_time:.3f}s")
        console_output.print(f"Max operation time: {max_operation_time:.3f}s")
        
        # Stress test assertions
        assert success_rate >= 80.0, f"Stress test success rate too low: {success_rate:.1f}%"
        assert operations_per_second > 5.0, f"Operations per second too low: {operations_per_second:.2f}"

    def test_database_performance_simulation(self, api_client, clean_vocabulary_data, vocabulary_factory, console_output):
        """Simulate database performance under load"""
        # This test simulates what might happen with database operations
        batch_sizes = [1, 5, 10, 20]
        results = {}
        
        for batch_size in batch_sizes:
            console_output.print(f"[blue]Testing batch size: {batch_size}[/blue]")
            
            # Generate batch data
            batch_data = vocabulary_factory.create_batch(batch_size)
            
            # Time batch creation
            start_time = time.time()
            created_count = 0
            
            for vocab_data in batch_data:
                response = api_client.post("/vocabulary", json=vocab_data)
                if response.status_code in [200, 201]:
                    created_count += 1
            
            end_time = time.time()
            batch_time = end_time - start_time
            
            # Time batch retrieval
            start_time = time.time()
            response = api_client.get("/vocabulary")
            end_time = time.time()
            retrieval_time = end_time - start_time
            
            items_per_second = created_count / batch_time if batch_time > 0 else 0
            
            results[batch_size] = {
                "created_count": created_count,
                "batch_time": batch_time,
                "retrieval_time": retrieval_time,
                "items_per_second": items_per_second
            }
        
        # Display results
        console_output.print(f"\n[bold]Database Performance Simulation Results:[/bold]")
        for batch_size, stats in results.items():
            console_output.print(f"Batch size {batch_size}:")
            console_output.print(f"  Created: {stats['created_count']} items")
            console_output.print(f"  Creation time: {stats['batch_time']:.3f}s")
            console_output.print(f"  Retrieval time: {stats['retrieval_time']:.3f}s")
            console_output.print(f"  Items per second: {stats['items_per_second']:.2f}")
        
        # Performance should not degrade significantly with batch size
        batch_times = [results[size]["batch_time"] for size in batch_sizes]
        # Ensure no batch takes unreasonably long
        assert all(time < 10.0 for time in batch_times), "Batch operations taking too long"
