"""
Benchmark module for comparing ScyllaDB and DuckDB performance.
"""

import os
import time
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Local imports
from db_connectors import get_connector, load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Benchmark:
    """Base class for database benchmarks."""
    
    def __init__(self, config_path: str = "config/benchmark_config.yaml"):
        """Initialize benchmark with configuration."""
        self.config = load_config(config_path)
        self.results = {}
        
        # Create results directory if it doesn't exist
        os.makedirs(self.config["output"]["results_dir"], exist_ok=True)
    
    def _time_operation(self, operation: Callable, *args, **kwargs) -> float:
        """Time an operation and return the elapsed time in seconds."""
        start_time = time.time()
        result = operation(*args, **kwargs)
        end_time = time.time()
        return end_time - start_time, result
    
    def run_benchmark(self, name: str, db_type: str, operation: Callable, 
                     iterations: int = None, warmup: int = None, 
                     *args, **kwargs) -> Dict[str, Any]:
        """Run a benchmark and record results."""
        if iterations is None:
            iterations = self.config["benchmarks"]["iterations"]
        
        if warmup is None:
            warmup = self.config["benchmarks"]["warmup_iterations"]
        
        logger.info(f"Running benchmark: {name} on {db_type}")
        
        # Perform warmup iterations
        for i in range(warmup):
            logger.info(f"Warmup iteration {i+1}/{warmup}")
            operation(*args, **kwargs)
        
        # Run actual benchmark iterations
        times = []
        for i in range(iterations):
            logger.info(f"Benchmark iteration {i+1}/{iterations}")
            elapsed_time, _ = self._time_operation(operation, *args, **kwargs)
            times.append(elapsed_time)
            logger.info(f"Iteration {i+1} completed in {elapsed_time:.4f} seconds")
        
        # Calculate statistics
        result = {
            "name": name,
            "database": db_type,
            "iterations": iterations,
            "times": times,
            "min": min(times),
            "max": max(times),
            "mean": np.mean(times),
            "median": np.median(times),
            "std_dev": np.std(times),
            "total": sum(times)
        }
        
        # Store result
        if name not in self.results:
            self.results[name] = []
        
        self.results[name].append(result)
        return result
    
    def save_results(self, format_type: str = "all") -> None:
        """Save benchmark results to files."""
        output_dir = self.config["output"]["results_dir"]
        
        if format_type == "all" or format_type == "csv":
            # Save as CSV
            for name, results in self.results.items():
                df = pd.DataFrame(results)
                csv_path = os.path.join(output_dir, f"{name}_results.csv")
                df.to_csv(csv_path, index=False)
                logger.info(f"Saved CSV results to {csv_path}")
        
        if format_type == "all" or format_type == "json":
            # Save as JSON
            json_path = os.path.join(output_dir, "benchmark_results.json")
            with open(json_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Saved JSON results to {json_path}")
        
        if format_type == "all" or format_type == "markdown":
            # Save as Markdown
            md_path = os.path.join(output_dir, "benchmark_results.md")
            with open(md_path, 'w') as f:
                f.write("# Database Benchmark Results\n\n")
                
                for name, results in self.results.items():
                    f.write(f"## {name}\n\n")
                    f.write("| Database | Min (s) | Max (s) | Mean (s) | Median (s) | Std Dev |\n")
                    f.write("|----------|---------|---------|----------|------------|--------|\n")
                    
                    for result in results:
                        f.write(f"| {result['database']} | {result['min']:.4f} | {result['max']:.4f} | ")
                        f.write(f"{result['mean']:.4f} | {result['median']:.4f} | {result['std_dev']:.4f} |\n")
                    
                    f.write("\n")
            
            logger.info(f"Saved Markdown results to {md_path}")


class DataLoadingBenchmark(Benchmark):
    """Benchmark for data loading performance."""
    
    def __init__(self, config_path: str = "config/benchmark_config.yaml"):
        """Initialize data loading benchmark."""
        super().__init__(config_path)
    
    def setup_scylla(self, data_path: str) -> None:
        """Set up ScyllaDB for data loading benchmark."""
        connector = get_connector("scylla")
        session = connector.connect()
        
        # Create table for benchmark
        session.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_data (
                id UUID PRIMARY KEY,
                timestamp TIMESTAMP,
                user_id INT,
                value FLOAT,
                category TEXT,
                tags LIST<TEXT>,
                metadata TEXT
            )
        """)
        
        connector.close()
    
    def setup_duckdb(self, data_path: str) -> None:
        """Set up DuckDB for data loading benchmark."""
        connector = get_connector("duckdb")
        conn = connector.connect()
        
        # Create table for benchmark
        conn.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_data (
                id VARCHAR,
                timestamp TIMESTAMP,
                user_id INTEGER,
                value FLOAT,
                category VARCHAR,
                tags VARCHAR[],
                metadata VARCHAR
            )
        """)
        
        connector.close()
    
    def load_data_scylla(self, data_path: str) -> None:
        """Load data into ScyllaDB."""
        connector = get_connector("scylla")
        session = connector.connect()
        
        # Load data from parquet
        df = pd.read_parquet(data_path)
        
        # Convert JSON columns to strings for ScyllaDB
        if 'metadata' in df.columns:
            df['metadata'] = df['metadata'].apply(json.dumps)
        
        # Prepare and execute batch insert
        prepared = session.prepare("""
            INSERT INTO benchmark_data (id, timestamp, user_id, value, category, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """)
        
        batch_size = 1000
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            
            for _, row in batch_df.iterrows():
                session.execute(prepared, (
                    uuid.UUID(row['id']),
                    row['timestamp'],
                    row['user_id'],
                    row['value'],
                    row['category'],
                    row['tags'],
                    row['metadata']
                ))
        
        connector.close()
    
    def load_data_duckdb(self, data_path: str) -> None:
        """Load data into DuckDB."""
        connector = get_connector("duckdb")
        conn = connector.connect()
        
        # Load data directly from parquet
        conn.execute(f"""
            INSERT INTO benchmark_data
            SELECT * FROM read_parquet('{data_path}')
        """)
        
        connector.close()
    
    def run(self, data_size: str = "small") -> Dict[str, Any]:
        """Run data loading benchmark for both databases."""
        data_path = self.config["data"][data_size]["file_path"]
        
        # Set up databases
        self.setup_scylla(data_path)
        self.setup_duckdb(data_path)
        
        # Run benchmarks
        scylla_result = self.run_benchmark(
            name=f"data_loading_{data_size}",
            db_type="scylla",
            operation=self.load_data_scylla,
            data_path=data_path
        )
        
        duckdb_result = self.run_benchmark(
            name=f"data_loading_{data_size}",
            db_type="duckdb",
            operation=self.load_data_duckdb,
            data_path=data_path
        )
        
        return {
            "scylla": scylla_result,
            "duckdb": duckdb_result
        }


class QueryBenchmark(Benchmark):
    """Benchmark for query performance."""
    
    def __init__(self, config_path: str = "config/benchmark_config.yaml"):
        """Initialize query benchmark."""
        super().__init__(config_path)
    
    def run_point_query_scylla(self, data_size: str) -> None:
        """Run point query benchmark on ScyllaDB."""
        connector = get_connector("scylla")
        session = connector.connect()
        
        # Get a random ID from the table
        rows = session.execute("SELECT id FROM benchmark_data LIMIT 1000")
        ids = [row.id for row in rows]
        
        if not ids:
            logger.error("No data found in ScyllaDB table")
            connector.close()
            return
        
        # Run point queries
        for _ in range(100):
            random_id = random.choice(ids)
            result = session.execute(
                "SELECT * FROM benchmark_data WHERE id = %s", 
                (random_id,)
            )
            # Consume the result
            list(result)
        
        connector.close()
    
    def run_point_query_duckdb(self, data_size: str) -> None:
        """Run point query benchmark on DuckDB."""
        connector = get_connector("duckdb")
        conn = connector.connect()
        
        # Get random IDs from the table
        result = conn.execute("SELECT id FROM benchmark_data LIMIT 1000").fetchall()
        ids = [row[0] for row in result]
        
        if not ids:
            logger.error("No data found in DuckDB table")
            connector.close()
            return
        
        # Run point queries
        for _ in range(100):
            random_id = random.choice(ids)
            conn.execute(f"SELECT * FROM benchmark_data WHERE id = '{random_id}'")
        
        connector.close()
    
    def run_range_query_scylla(self, data_size: str) -> None:
        """Run range query benchmark on ScyllaDB."""
        connector = get_connector("scylla")
        session = connector.connect()
        
        # Create secondary index if it doesn't exist
        session.execute("CREATE INDEX IF NOT EXISTS ON benchmark_data (user_id)")
        
        # Run range queries
        for _ in range(10):
            min_id = random.randint(1, 900000)
            max_id = min_id + 100000
            
            result = session.execute(
                "SELECT * FROM benchmark_data WHERE user_id >= %s AND user_id <= %s ALLOW FILTERING", 
                (min_id, max_id)
            )
            # Consume the result
            list(result)
        
        connector.close()
    
    def run_range_query_duckdb(self, data_size: str) -> None:
        """Run range query benchmark on DuckDB."""
        connector = get_connector("duckdb")
        conn = connector.connect()
        
        # Run range queries
        for _ in range(10):
            min_id = random.randint(1, 900000)
            max_id = min_id + 100000
            
            conn.execute(f"""
                SELECT * FROM benchmark_data 
                WHERE user_id >= {min_id} AND user_id <= {max_id}
            """)
        
        connector.close()
    
    def run_aggregation_query_scylla(self, data_size: str) -> None:
        """Run aggregation query benchmark on ScyllaDB."""
        connector = get_connector("scylla")
        session = connector.connect()
        
        # Create secondary index if it doesn't exist
        session.execute("CREATE INDEX IF NOT EXISTS ON benchmark_data (category)")
        
        # Get some categories from the table
        # Note: ScyllaDB doesn't support DISTINCT on non-partition key columns
        # So we'll use a different approach
        rows = session.execute("SELECT id, category FROM benchmark_data LIMIT 100")
        categories = list(set([row.category for row in rows]))
        
        if not categories:
            logger.error("No categories found in ScyllaDB table")
            connector.close()
            return
        
        # Run aggregation queries
        for _ in range(10):
            random_category = random.choice(categories)
            
            # ScyllaDB has limited aggregation support, so we'll just count rows
            result = session.execute(
                "SELECT COUNT(*) FROM benchmark_data WHERE category = %s ALLOW FILTERING", 
                (random_category,)
            )
            # Consume the result
            list(result)
        
        connector.close()
    
    def run_aggregation_query_duckdb(self, data_size: str) -> None:
        """Run aggregation query benchmark on DuckDB."""
        connector = get_connector("duckdb")
        conn = connector.connect()
        
        # Get distinct categories
        result = conn.execute("SELECT DISTINCT category FROM benchmark_data LIMIT 100").fetchall()
        categories = [row[0] for row in result]
        
        if not categories:
            logger.error("No categories found in DuckDB table")
            connector.close()
            return
        
        # Run aggregation queries
        for _ in range(10):
            random_category = random.choice(categories)
            
            conn.execute(f"""
                SELECT 
                    category,
                    COUNT(*) as count,
                    AVG(value) as avg_value,
                    MIN(value) as min_value,
                    MAX(value) as max_value
                FROM benchmark_data 
                WHERE category = '{random_category}'
                GROUP BY category
            """)
        
        connector.close()
    
    def run(self, data_size: str = "small", query_type: str = "all") -> Dict[str, Any]:
        """Run query benchmarks for both databases."""
        results = {}
        
        if query_type == "all" or query_type == "point_reads":
            # Run point query benchmarks
            scylla_result = self.run_benchmark(
                name=f"point_query_{data_size}",
                db_type="scylla",
                operation=self.run_point_query_scylla,
                data_size=data_size
            )
            
            duckdb_result = self.run_benchmark(
                name=f"point_query_{data_size}",
                db_type="duckdb",
                operation=self.run_point_query_duckdb,
                data_size=data_size
            )
            
            results["point_query"] = {
                "scylla": scylla_result,
                "duckdb": duckdb_result
            }
        
        if query_type == "all" or query_type == "range_scans":
            # Run range query benchmarks
            scylla_result = self.run_benchmark(
                name=f"range_query_{data_size}",
                db_type="scylla",
                operation=self.run_range_query_scylla,
                data_size=data_size
            )
            
            duckdb_result = self.run_benchmark(
                name=f"range_query_{data_size}",
                db_type="duckdb",
                operation=self.run_range_query_duckdb,
                data_size=data_size
            )
            
            results["range_query"] = {
                "scylla": scylla_result,
                "duckdb": duckdb_result
            }
        
        if query_type == "all" or query_type == "aggregations":
            # Run aggregation query benchmarks
            scylla_result = self.run_benchmark(
                name=f"aggregation_query_{data_size}",
                db_type="scylla",
                operation=self.run_aggregation_query_scylla,
                data_size=data_size
            )
            
            duckdb_result = self.run_benchmark(
                name=f"aggregation_query_{data_size}",
                db_type="duckdb",
                operation=self.run_aggregation_query_duckdb,
                data_size=data_size
            )
            
            results["aggregation_query"] = {
                "scylla": scylla_result,
                "duckdb": duckdb_result
            }
        
        return results


class ConcurrentBenchmark(Benchmark):
    """Benchmark for concurrent operations."""
    
    def __init__(self, config_path: str = "config/benchmark_config.yaml"):
        """Initialize concurrent operations benchmark."""
        super().__init__(config_path)
    
    def run_concurrent_scylla(self, data_size: str, num_threads: int) -> None:
        """Run concurrent operations on ScyllaDB."""
        connector = get_connector("scylla")
        session = connector.connect()
        
        # Get random IDs from the table
        rows = session.execute("SELECT id FROM benchmark_data LIMIT 1000")
        ids = [row.id for row in rows]
        
        if not ids:
            logger.error("No data found in ScyllaDB table")
            connector.close()
            return
        
        def worker(worker_id):
            # Each worker does a mix of operations
            for i in range(10):
                op_type = i % 3
                
                if op_type == 0:  # Point read
                    random_id = random.choice(ids)
                    result = session.execute(
                        "SELECT * FROM benchmark_data WHERE id = %s", 
                        (random_id,)
                    )
                    list(result)
                
                elif op_type == 1:  # Write
                    # Insert a new row
                    new_id = uuid.uuid4()
                    session.execute("""
                        INSERT INTO benchmark_data (id, timestamp, user_id, value, category, tags, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        new_id,
                        datetime.now(),
                        random.randint(1, 1000000),
                        random.uniform(0, 1000.0),
                        f"category_{random.randint(1, 100)}",
                        [f"tag_{random.randint(1, 100)}" for _ in range(3)],
                        json.dumps({"key": f"value_{random.randint(1, 100)}"})
                    ))
                
                else:  # Update
                    if ids:
                        random_id = random.choice(ids)
                        session.execute("""
                            UPDATE benchmark_data 
                            SET value = %s, timestamp = %s
                            WHERE id = %s
                        """, (
                            random.uniform(0, 1000.0),
                            datetime.now(),
                            random_id
                        ))
        
        # Run workers concurrently
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            for future in futures:
                future.result()  # Wait for completion
        
        connector.close()
    
    def run_concurrent_duckdb(self, data_size: str, num_threads: int) -> None:
        """Run concurrent operations on DuckDB."""
        # Note: DuckDB has limited concurrency support
        # We'll create separate connections for each thread
        
        # Get random IDs from the table
        connector = get_connector("duckdb")
        conn = connector.connect()
        try:
            result = conn.execute("SELECT id FROM benchmark_data LIMIT 1000").fetchall()
            ids = [row[0] for row in result]
            connector.close()
            
            if not ids:
                logger.error("No data found in DuckDB table")
                return
            
            def worker(worker_id):
                try:
                    # Create a new connection for each worker
                    connector = get_connector("duckdb")
                    conn = connector.connect()
                    
                    # Each worker does a mix of operations
                    for i in range(10):
                        op_type = i % 3
                        
                        if op_type == 0:  # Point read
                            random_id = random.choice(ids)
                            conn.execute(f"SELECT * FROM benchmark_data WHERE id = '{random_id}'")
                        
                        elif op_type == 1:  # Write
                            # Insert a new row
                            new_id = str(uuid.uuid4())
                            conn.execute(f"""
                                INSERT INTO benchmark_data 
                                VALUES (
                                    '{new_id}',
                                    TIMESTAMP '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}',
                                    {random.randint(1, 1000000)},
                                    {random.uniform(0, 1000.0)},
                                    'category_{random.randint(1, 100)}',
                                    ['tag_{random.randint(1, 100)}', 'tag_{random.randint(1, 100)}'],
                                    '{{"key": "value_{random.randint(1, 100)}"}}'
                                )
                            """)
                        
                        else:  # Update
                            if ids:
                                try:
                                    random_id = random.choice(ids)
                                    conn.execute(f"""
                                        UPDATE benchmark_data 
                                        SET value = {random.uniform(0, 1000.0)},
                                            timestamp = TIMESTAMP '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'
                                        WHERE id = '{random_id}'
                                    """)
                                except Exception as e:
                                    logger.warning(f"DuckDB update failed: {e}")
                    
                    connector.close()
                except Exception as e:
                    logger.warning(f"DuckDB worker error: {e}")
            
            # Run workers concurrently
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(worker, i) for i in range(num_threads)]
                for future in futures:
                    try:
                        future.result()  # Wait for completion
                    except Exception as e:
                        logger.warning(f"DuckDB concurrent operation failed: {e}")
        except Exception as e:
            logger.warning(f"DuckDB concurrent benchmark error: {e}")
            # If we can't run the concurrent benchmark, we'll just log the error
            logger.warning("DuckDB concurrent benchmark skipped due to transaction conflicts")
    
    def run(self, data_size: str = "small") -> Dict[str, Any]:
        """Run concurrent operation benchmarks for both databases."""
        results = {}
        
        for concurrency in self.config["benchmarks"]["concurrency"]:
            # Run ScyllaDB concurrent benchmark
            scylla_result = self.run_benchmark(
                name=f"concurrent_{concurrency}_{data_size}",
                db_type="scylla",
                operation=self.run_concurrent_scylla,
                data_size=data_size,
                num_threads=concurrency
            )
            
            # Run DuckDB concurrent benchmark
            duckdb_result = self.run_benchmark(
                name=f"concurrent_{concurrency}_{data_size}",
                db_type="duckdb",
                operation=self.run_concurrent_duckdb,
                data_size=data_size,
                num_threads=concurrency
            )
            
            results[f"concurrent_{concurrency}"] = {
                "scylla": scylla_result,
                "duckdb": duckdb_result
            }
        
        return results


# Import missing modules
import uuid
import random
from datetime import datetime