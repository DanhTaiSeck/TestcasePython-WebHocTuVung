#!/usr/bin/env python3
"""
Comprehensive test runner for Vocabulary Learning App
Provides test execution, reporting, and monitoring capabilities
"""

import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text
import requests

console = Console()

class VocabularyTestRunner:
    """Main test runner for vocabulary app testing"""
    
    def __init__(self, config_file: str = "test_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[red]Config file {self.config_file} not found. Using defaults.[/red]")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON in config file: {e}[/red]")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "api_base_url": "http://localhost:3000/api",
            "frontend_url": "http://localhost:5000",
            "test_timeout": 30,
            "max_retries": 3,
            "environments": {
                "local": {
                    "api_url": "http://localhost:3000/api",
                    "database_url": "local"
                }
            },
            "test_categories": {
                "unit": True,
                "integration": True,
                "api": True,
                "performance": False,
                "security": True
            },
            "reporting": {
                "html_report": True,
                "json_report": True,
                "console_output": True
            },
            "performance_thresholds": {
                "api_response_time": 2.0,
                "concurrent_success_rate": 90.0,
                "memory_limit_mb": 100
            }
        }
    
    def check_environment(self) -> bool:
        """Check if test environment is ready"""
        console.print("\n[bold blue]🔍 Checking Test Environment[/bold blue]")
        
        checks = {
            "API Server": self.check_api_server(),
            "Dependencies": self.check_dependencies(),
            "Test Data": self.check_test_data_structure(),
            "Reports Directory": self.check_reports_directory()
        }
        
        table = Table(title="Environment Check Results")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        
        all_passed = True
        for component, status in checks.items():
            status_text = "[green]✓ PASS[/green]" if status else "[red]✗ FAIL[/red]"
            table.add_row(component, status_text)
            if not status:
                all_passed = False
        
        console.print(table)
        
        if not all_passed:
            console.print("\n[red]❌ Environment check failed. Please fix the issues above before running tests.[/red]")
        
        return all_passed
    
    def check_api_server(self) -> bool:
        """Check if API server is running"""
        try:
            api_url = self.config.get("api_base_url", "http://localhost:3000/api")
            base_url = api_url.replace("/api", "")
            response = requests.get(base_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        required_modules = ["pytest", "requests", "rich", "faker"]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                return False
        return True
    
    def check_test_data_structure(self) -> bool:
        """Check if test directory structure exists"""
        required_dirs = ["tests", "tests/factories", "tests/utils", "tests/reports"]
        return all(os.path.exists(directory) for directory in required_dirs)
    
    def check_reports_directory(self) -> bool:
        """Check and create reports directory if needed"""
        reports_dir = Path("tests/reports")
        if not reports_dir.exists():
            try:
                reports_dir.mkdir(parents=True, exist_ok=True)
                return True
            except OSError:
                return False
        return True
    
    def run_tests(self, test_categories: List[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """Run specified test categories"""
        self.start_time = time.time()
        
        if test_categories is None:
            test_categories = [cat for cat, enabled in self.config["test_categories"].items() if enabled]
        
        console.print(f"\n[bold green]🚀 Starting Test Execution[/bold green]")
        console.print(f"Test Categories: {', '.join(test_categories)}")
        
        results = {}
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            main_task = progress.add_task("Running Tests", total=len(test_categories))
            
            for category in test_categories:
                category_task = progress.add_task(f"Running {category} tests", total=1)
                
                console.print(f"\n[blue]📝 Running {category.upper()} tests[/blue]")
                result = self.run_test_category(category, verbose)
                results[category] = result
                
                progress.update(category_task, completed=1)
                progress.update(main_task, advance=1)
        
        self.end_time = time.time()
        self.test_results = results
        
        return results
    
    def run_test_category(self, category: str, verbose: bool = False) -> Dict[str, Any]:
        """Run tests for a specific category"""
        pytest_args = [
            "python", "-m", "pytest",
            f"-m", category,
            "--tb=short" if not verbose else "--tb=long",
            "-v" if verbose else "-q",
            "tests/"
        ]
        
        # Add HTML report generation
        if self.config["reporting"]["html_report"]:
            report_file = f"tests/reports/{category}_report.html"
            pytest_args.extend(["--html", report_file, "--self-contained-html"])
        
        # Add JSON report generation
        if self.config["reporting"]["json_report"]:
            json_file = f"tests/reports/{category}_results.json"
            pytest_args.extend(["--json-report", f"--json-report-file={json_file}"])
        
        try:
            start_time = time.time()
            result = subprocess.run(
                pytest_args,
                capture_output=True,
                text=True,
                timeout=self.config.get("test_timeout", 300)
            )
            end_time = time.time()
            
            return {
                "category": category,
                "exit_code": result.returncode,
                "duration": end_time - start_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                "category": category,
                "exit_code": -1,
                "duration": self.config.get("test_timeout", 300),
                "stdout": "",
                "stderr": "Test execution timed out",
                "success": False
            }
        except Exception as e:
            return {
                "category": category,
                "exit_code": -1,
                "duration": 0,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    def generate_summary_report(self) -> None:
        """Generate comprehensive test summary report"""
        if not self.test_results:
            console.print("[yellow]No test results to report[/yellow]")
            return
        
        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        # Summary statistics
        total_categories = len(self.test_results)
        successful_categories = sum(1 for result in self.test_results.values() if result["success"])
        failed_categories = total_categories - successful_categories
        
        # Create summary table
        table = Table(title="Test Execution Summary")
        table.add_column("Category", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Duration", style="magenta")
        table.add_column("Exit Code", style="yellow")
        
        for category, result in self.test_results.items():
            status = "[green]✓ PASS[/green]" if result["success"] else "[red]✗ FAIL[/red]"
            duration = f"{result['duration']:.2f}s"
            exit_code = str(result["exit_code"])
            
            table.add_row(category, status, duration, exit_code)
        
        console.print("\n")
        console.print(table)
        
        # Overall summary panel
        summary_text = f"""
[bold]Overall Results:[/bold]
• Total Categories: {total_categories}
• Successful: [green]{successful_categories}[/green]
• Failed: [red]{failed_categories}[/red]
• Total Duration: {total_duration:.2f}s
• Success Rate: {(successful_categories/total_categories*100):.1f}%
        """
        
        panel_style = "green" if failed_categories == 0 else "red"
        console.print(Panel(summary_text.strip(), title="Test Summary", style=panel_style))
        
        # Show failed test details
        if failed_categories > 0:
            console.print("\n[bold red]Failed Test Details:[/bold red]")
            for category, result in self.test_results.items():
                if not result["success"]:
                    console.print(f"\n[red]❌ {category.upper()} Tests Failed[/red]")
                    if result["stderr"]:
                        console.print(f"[dim]Error: {result['stderr'][:200]}...[/dim]")
    
    def run_performance_benchmark(self) -> Dict[str, Any]:
        """Run performance benchmark tests"""
        console.print("\n[bold yellow]⚡ Running Performance Benchmarks[/bold yellow]")
        
        benchmark_results = {}
        
        # API Response Time Benchmark
        try:
            api_url = self.config["api_base_url"] + "/vocabulary"
            response_times = []
            
            console.print("Testing API response times...")
            for i in range(10):
                start_time = time.time()
                response = requests.get(api_url, timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            
            if response_times:
                benchmark_results["api_response_time"] = {
                    "avg": sum(response_times) / len(response_times),
                    "max": max(response_times),
                    "min": min(response_times),
                    "samples": len(response_times)
                }
        except Exception as e:
            benchmark_results["api_response_time"] = {"error": str(e)}
        
        # Memory Usage Benchmark
        try:
            import psutil
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Simulate some operations
            for _ in range(100):
                requests.get(self.config["api_base_url"] + "/vocabulary", timeout=5)
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before
            
            benchmark_results["memory_usage"] = {
                "initial_mb": memory_before,
                "final_mb": memory_after,
                "increase_mb": memory_increase
            }
        except Exception as e:
            benchmark_results["memory_usage"] = {"error": str(e)}
        
        # Display benchmark results
        if benchmark_results:
            console.print("\n[bold]Benchmark Results:[/bold]")
            for benchmark, results in benchmark_results.items():
                if "error" not in results:
                    console.print(f"[green]✓ {benchmark}[/green]: {results}")
                else:
                    console.print(f"[red]✗ {benchmark}[/red]: {results['error']}")
        
        return benchmark_results
    
    def cleanup_test_environment(self) -> None:
        """Clean up test environment after execution"""
        console.print("\n[blue]🧹 Cleaning up test environment[/blue]")
        
        try:
            # Clean up any test data that might have been created
            api_url = self.config["api_base_url"] + "/vocabulary"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                vocabularies = response.json()
                test_items = [v for v in vocabularies if "test" in v.get("word", "").lower()]
                
                for item in test_items:
                    if "id" in item:
                        delete_url = f"{api_url}/{item['id']}"
                        requests.delete(delete_url, timeout=10)
                
                if test_items:
                    console.print(f"[green]✓ Cleaned up {len(test_items)} test vocabulary items[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ Warning: Could not clean up test data: {e}[/yellow]")
    
    def save_test_report(self) -> None:
        """Save comprehensive test report to file"""
        if not self.test_results:
            return
        
        report_data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total_duration": self.end_time - self.start_time if self.start_time and self.end_time else 0,
            "config": self.config,
            "results": self.test_results,
            "summary": {
                "total_categories": len(self.test_results),
                "successful_categories": sum(1 for r in self.test_results.values() if r["success"]),
                "failed_categories": sum(1 for r in self.test_results.values() if not r["success"])
            }
        }
        
        # Save JSON report
        json_file = f"tests/reports/test_summary_{int(time.time())}.json"
        try:
            with open(json_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            console.print(f"[green]✓ Test report saved to {json_file}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to save test report: {e}[/red]")


def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(description="Vocabulary Learning App Test Runner")
    parser.add_argument("--config", default="test_config.json", help="Test configuration file")
    parser.add_argument("--categories", nargs="+", help="Test categories to run (unit, integration, api, performance, security)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--benchmark", "-b", action="store_true", help="Run performance benchmarks")
    parser.add_argument("--check-env", action="store_true", help="Only check environment and exit")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test environment")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = VocabularyTestRunner(args.config)
    
    # Display banner
    console.print(Panel.fit(
        "[bold blue]Vocabulary Learning App Test Suite[/bold blue]\n"
        "[dim]Comprehensive testing framework with API, performance, and security testing[/dim]",
        style="blue"
    ))
    
    try:
        # Check environment if requested
        if args.check_env:
            success = runner.check_environment()
            sys.exit(0 if success else 1)
        
        # Check environment before running tests
        if not runner.check_environment():
            console.print("[red]Environment check failed. Aborting test execution.[/red]")
            sys.exit(1)
        
        # Run performance benchmarks if requested
        if args.benchmark:
            benchmark_results = runner.run_performance_benchmark()
        
        # Run tests
        if not args.benchmark or args.categories:
            test_results = runner.run_tests(args.categories, args.verbose)
            runner.generate_summary_report()
            runner.save_test_report()
        
        # Cleanup if requested
        if args.cleanup:
            runner.cleanup_test_environment()
        
        # Exit with appropriate code
        if runner.test_results:
            failed_tests = sum(1 for result in runner.test_results.values() if not result["success"])
            sys.exit(1 if failed_tests > 0 else 0)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Test execution interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
