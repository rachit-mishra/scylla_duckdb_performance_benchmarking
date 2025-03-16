# Database Performance Benchmark: ScyllaDB vs DuckDB

This project provides a framework for benchmarking the performance of ScyllaDB and DuckDB across various operations including data loading, point queries, range queries, aggregation queries, and concurrent operations.

## Overview

The benchmark suite generates synthetic data and runs a series of tests to compare the performance characteristics of ScyllaDB (a distributed NoSQL database) and DuckDB (an embedded analytical database). Results are saved in multiple formats (CSV, JSON, Markdown) and visualized through charts.

## Key Features

- Configurable data sizes (small, medium, large)
- Multiple benchmark types (data loading, queries, concurrency)
- Automated Docker setup for reproducible environments
- Comprehensive result reporting and visualization
- Modular architecture for easy extension

## Project Structure

```
.
├── config/                 # Configuration files
│   └── benchmark_config.yaml  # Main configuration
├── data/                   # Generated and stored data
│   ├── duckdb/             # DuckDB database files
│   └── scylla/             # ScyllaDB data (when using volumes)
├── docker/                 # Docker configuration
│   ├── docker-compose.yml  # Services definition
│   └── scylla.yaml         # ScyllaDB configuration
├── results/                # Benchmark results and visualizations
├── scripts/                # Utility scripts
│   ├── init_git.sh         # Git initialization
│   └── run_docker_benchmark.sh  # Run benchmarks in Docker
├── src/                    # Source code
│   ├── benchmark.py        # Benchmark implementation
│   ├── data_generator.py   # Synthetic data generation
│   ├── db_connectors.py    # Database connection handling
│   ├── run_benchmarks.py   # Main entry point
│   └── visualize.py        # Results visualization
├── Dockerfile              # Docker image for benchmarks
├── BENCHMARK_SUMMARY.md    # Summary of benchmark results
└── requirements.txt        # Python dependencies
```

## Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Git

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/db-performance-benchmark.git
   cd db-performance-benchmark
   ```

2. Run the benchmark using Docker (recommended):
   ```bash
   ./scripts/run_docker_benchmark.sh --data-sizes small
   ```

   Available options:
   - `--data-sizes`: Comma-separated list of data sizes to benchmark (small, medium, large)
   - `--benchmark-types`: Comma-separated list of benchmark types (data_loading, point_reads, range_scans, aggregations, all)

3. View the results:
   - Text summaries in `results/benchmark_results.md`
   - CSV files in `results/` directory
   - Visualizations in `results/*.png`
   - Interactive dashboard in `results/benchmark_dashboard.html`

## Running Without Docker

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start ScyllaDB separately (using Docker or a local installation)

3. Update the configuration in `config/benchmark_config.yaml` to point to your ScyllaDB instance

4. Run the benchmark:
   ```bash
   python src/run_benchmarks.py --config config/benchmark_config.yaml --data-sizes small
   ```

## Configuration

The main configuration file `config/benchmark_config.yaml` allows you to customize:

- Database connection parameters
- Data generation settings
- Benchmark parameters (iterations, warmup)
- Output paths and formats

## Benchmark Types

1. **Data Loading**: Measures the time to load data from Parquet files into each database
2. **Point Queries**: Measures performance of lookups by primary key
3. **Range Queries**: Measures performance of range scans with filtering
4. **Aggregation Queries**: Measures performance of grouping and aggregation operations
5. **Concurrent Operations**: Measures performance under concurrent workloads with varying thread counts

## Results

See [BENCHMARK_SUMMARY.md](BENCHMARK_SUMMARY.md) for a detailed analysis of the benchmark results.

## Extending the Benchmarks

The modular architecture makes it easy to extend the benchmarks:

1. Add new benchmark types by extending the base `Benchmark` class in `src/benchmark.py`
2. Add new data generation patterns in `src/data_generator.py`
3. Add new database connectors in `src/db_connectors.py`
4. Add new visualization types in `src/visualize.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- ScyllaDB and DuckDB development teams
- Contributors to the Python data science ecosystem (pandas, numpy, matplotlib)
