# ScyllaDB vs DuckDB Performance Benchmark Summary

This document summarizes the results of performance benchmarks comparing ScyllaDB and DuckDB across various operations.

## Benchmark Environment

- **Hardware**: Docker containers on local machine
- **Dataset Size**: Small (10,000 rows)
- **Benchmark Types**: Data loading, point queries, range queries, aggregation queries, and concurrent operations
- **Iterations**: 3 iterations per benchmark (after warmup)

## Key Findings

### 1. Data Loading Performance

| Database | Mean Time (s) | Min Time (s) | Max Time (s) |
|----------|---------------|--------------|--------------|
| ScyllaDB | 6.49          | 6.43         | 6.60         |
| DuckDB   | 1.94          | 1.33         | 2.66         |

**Analysis**: DuckDB significantly outperforms ScyllaDB in data loading operations, being approximately 3.3x faster on average. This is expected as DuckDB is optimized for analytical workloads and can directly load data from Parquet files, while ScyllaDB requires row-by-row insertion.

### 2. Point Query Performance

| Database | Mean Time (s) | Min Time (s) | Max Time (s) |
|----------|---------------|--------------|--------------|
| ScyllaDB | 0.119         | 0.113        | 0.129        |
| DuckDB   | 0.057         | 0.046        | 0.063        |

**Analysis**: DuckDB is approximately 2.1x faster than ScyllaDB for point queries in this benchmark. This is somewhat surprising as ScyllaDB is designed for high-performance point lookups. The small dataset size may be a factor here, as DuckDB can keep the entire dataset in memory.

### 3. Range Query Performance

| Database | Mean Time (s) | Min Time (s) | Max Time (s) |
|----------|---------------|--------------|--------------|
| ScyllaDB | 2.64          | 2.60         | 2.67         |
| DuckDB   | 0.034         | 0.029        | 0.036        |

**Analysis**: DuckDB dramatically outperforms ScyllaDB in range queries, being approximately 77.6x faster. This highlights DuckDB's strength in analytical workloads that involve scanning ranges of data. ScyllaDB's performance is affected by the need to use the `ALLOW FILTERING` clause, which is not recommended for production use.

### 4. Aggregation Query Performance

| Database | Mean Time (s) | Min Time (s) | Max Time (s) |
|----------|---------------|--------------|--------------|
| ScyllaDB | 0.071         | 0.069        | 0.076        |
| DuckDB   | 0.048         | 0.047        | 0.051        |

**Analysis**: DuckDB is approximately 1.5x faster than ScyllaDB for aggregation queries. Note that the ScyllaDB implementation had to be simplified to use COUNT(*) instead of more complex aggregations due to ScyllaDB's limitations with non-primary key columns.

### 5. Concurrency Performance

#### 1 Thread

| Database | Mean Time (s) | Min Time (s) | Max Time (s) |
|----------|---------------|--------------|--------------|
| ScyllaDB | 0.063         | 0.060        | 0.064        |
| DuckDB   | 0.728         | 0.704        | 0.752        |

#### 4 Threads

| Database | Mean Time (s) | Min Time (s) | Max Time (s) |
|----------|---------------|--------------|--------------|
| ScyllaDB | 0.137         | 0.081        | 0.183        |
| DuckDB   | 0.917         | 0.880        | 0.968        |

#### 16 Threads

| Database | Mean Time (s) | Min Time (s) | Max Time (s) |
|----------|---------------|--------------|--------------|
| ScyllaDB | 0.142         | 0.120        | 0.169        |
| DuckDB   | 1.773         | 1.671        | 1.829        |

**Analysis**: ScyllaDB significantly outperforms DuckDB in concurrent operations, being approximately 11.6x faster with 1 thread, 6.7x faster with 4 threads, and 12.5x faster with 16 threads. This demonstrates ScyllaDB's strength in handling concurrent workloads, which is a key feature of its architecture. DuckDB's performance degrades as concurrency increases, which is expected for an embedded database not primarily designed for high concurrency.

## Overall Conclusions

1. **DuckDB excels at analytical workloads**: DuckDB significantly outperforms ScyllaDB in data loading, range queries, and shows better performance in point queries and aggregations with small datasets.

2. **ScyllaDB excels at concurrent operations**: ScyllaDB dramatically outperforms DuckDB when handling concurrent operations, showing its strength as a distributed database designed for high throughput.

3. **Use case recommendations**:
   - Choose **DuckDB** for analytical workloads, data exploration, and scenarios where you need fast range scans and aggregations on moderate-sized datasets.
   - Choose **ScyllaDB** for high-concurrency workloads, real-time applications, and scenarios where you need consistent performance with many simultaneous operations.

4. **Scaling considerations**: These benchmarks were performed with a small dataset (10,000 rows). As data size increases:
   - ScyllaDB's distributed architecture should scale well horizontally
   - DuckDB may face limitations as an embedded database when data exceeds memory

## Future Work

1. Run benchmarks with medium and large datasets to observe scaling behavior
2. Test more complex query patterns
3. Benchmark write-heavy workloads
4. Test performance under sustained load over longer periods
5. Measure resource utilization (CPU, memory, disk I/O)

---

*Note: These benchmarks represent a specific workload and environment. Your results may vary based on hardware, configuration, data characteristics, and query patterns.*