#!/usr/bin/env python3
"""
Main script to run all benchmarks for ScyllaDB and DuckDB.
"""

import os
import sys
import logging
import argparse
from typing import Dict, List, Any

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Local imports
from data_generator import DataGenerator
from benchmark import DataLoadingBenchmark, QueryBenchmark, ConcurrentBenchmark
from visualize import BenchmarkVisualizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run database benchmarks")
    
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/benchmark_config.yaml",
        help="Path to benchmark configuration file"
    )
    
    parser.add_argument(
        "--data-sizes",
        type=str,
        default="small,medium,large",
        help="Comma-separated list of data sizes to benchmark (small, medium, large)"
    )
    
    parser.add_argument(
        "--benchmark-types",
        type=str,
        default="all",
        help="Comma-separated list of benchmark types to run (data_loading, queries, concurrent, all)"
    )
    
    parser.add_argument(
        "--skip-data-generation",
        action="store_true",
        help="Skip data generation step"
    )
    
    parser.add_argument(
        "--skip-visualization",
        action="store_true",
        help="Skip visualization generation step"
    )
    
    return parser.parse_args()


def generate_data(config_path: str, data_sizes: List[str]) -> Dict[str, str]:
    """Generate data for benchmarks."""
    logger.info("Generating benchmark data")
    
    generator = DataGenerator(config_path)
    dataset_paths = {}
    
    for size in data_sizes:
        if size in ["small", "medium", "large"]:
            logger.info(f"Generating {size} dataset")
            df = generator.generate_dataset(size)
            path = generator.save_dataset(df, size)
            dataset_paths[size] = path
    
    return dataset_paths


def run_benchmarks(config_path: str, data_sizes: List[str], benchmark_types: List[str]) -> None:
    """Run all specified benchmarks."""
    results = {}
    
    for data_size in data_sizes:
        logger.info(f"Running benchmarks for {data_size} data size")
        
        if "all" in benchmark_types or "data_loading" in benchmark_types:
            logger.info("Running data loading benchmarks")
            benchmark = DataLoadingBenchmark(config_path)
            results.update(benchmark.run(data_size))
            benchmark.save_results()
        
        if "all" in benchmark_types or "queries" in benchmark_types:
            logger.info("Running query benchmarks")
            benchmark = QueryBenchmark(config_path)
            results.update(benchmark.run(data_size))
            benchmark.save_results()
        
        if "all" in benchmark_types or "concurrent" in benchmark_types:
            logger.info("Running concurrency benchmarks")
            benchmark = ConcurrentBenchmark(config_path)
            results.update(benchmark.run(data_size))
            benchmark.save_results()
    
    return results


def generate_visualizations(config_path: str) -> None:
    """Generate visualizations from benchmark results."""
    logger.info("Generating visualizations")
    
    visualizer = BenchmarkVisualizer()
    visualizer.generate_all_visualizations()


def main():
    """Main function to run benchmarks."""
    args = parse_args()
    
    # Parse data sizes
    data_sizes = [size.strip() for size in args.data_sizes.split(",")]
    
    # Parse benchmark types
    benchmark_types = [btype.strip() for btype in args.benchmark_types.split(",")]
    
    # Generate data if needed
    if not args.skip_data_generation:
        generate_data(args.config, data_sizes)
    
    # Run benchmarks
    run_benchmarks(args.config, data_sizes, benchmark_types)
    
    # Generate visualizations if needed
    if not args.skip_visualization:
        generate_visualizations(args.config)
    
    logger.info("Benchmarks completed successfully")


if __name__ == "__main__":
    main() 