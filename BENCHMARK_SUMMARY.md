# ScyllaDB vs DuckDB Performance Benchmark Summary

This document summarizes the results of performance benchmarks comparing ScyllaDB and DuckDB across various operations.

## Benchmark Environment

- **Hardware**: Docker containers on local machine
- **Dataset Sizes**: 
  - Small: 10,000 rows
  - Medium: 100,000 rows
- **Benchmark Types**: Data loading, point queries, range queries, aggregation queries, and concurrent operations
- **Iterations**: 3 iterations per benchmark (after warmup)

## Key Findings

### 1. Data Loading Performance

| Database | Dataset | Mean Time (s) | Min Time (s) | Max Time (s) | Ratio |
|----------|---------|---------------|--------------|--------------|-------|
| ScyllaDB | Small   | 6.49          | 6.43         | 6.60         | 1.0   |
| DuckDB   | Small   | 1.94          | 1.33         | 2.66         | 3.3x  |
| ScyllaDB | Medium  | 63.25         | 63.19        | 63.30        | 1.0   |
| DuckDB   | Medium  | 5.59          | 4.96         | 6.54         | 11.3x |

**Analysis**: DuckDB significantly outperforms ScyllaDB in data loading operations, being approximately 3.3x faster for small datasets and 11.3x faster for medium datasets. The performance gap widens as the dataset size increases, highlighting DuckDB's efficiency in bulk data loading from Parquet files. ScyllaDB's row-by-row insertion approach shows linear scaling with dataset size.

### 2. Point Query Performance

| Database | Dataset | Mean Time (s) | Min Time (s) | Max Time (s) | Ratio |
|----------|---------|---------------|--------------|--------------|-------|
| ScyllaDB | Small   | 0.119         | 0.113        | 0.129        | 1.0   |
| DuckDB   | Small   | 0.057         | 0.046        | 0.063        | 2.1x  |
| ScyllaDB | Medium  | 0.079         | 0.072        | 0.086        | 1.0   |
| DuckDB   | Medium  | 0.040         | 0.037        | 0.041        | 2.0x  |

**Analysis**: DuckDB maintains approximately a 2x performance advantage over ScyllaDB for point queries across both dataset sizes. Interestingly, ScyllaDB's point query performance slightly improved with the medium dataset, possibly due to caching effects or more efficient index usage with larger datasets.

### 3. Range Query Performance

| Database | Dataset | Mean Time (s) | Min Time (s) | Max Time (s) | Ratio |
|----------|---------|---------------|--------------|--------------|-------|
| ScyllaDB | Small   | 2.64          | 2.60         | 2.67         | 1.0   |
| DuckDB   | Small   | 0.034         | 0.029        | 0.036        | 77.6x |
| ScyllaDB | Medium  | 31.18         | 30.76        | 31.57        | 1.0   |
| DuckDB   | Medium  | 0.026         | 0.026        | 0.026        | 1199x |

**Analysis**: DuckDB's advantage in range queries becomes even more pronounced with larger datasets. While DuckDB was 77.6x faster for small datasets, it's approximately 1199x faster for medium datasets. ScyllaDB's performance degrades significantly with larger datasets when using `ALLOW FILTERING`, which is not recommended for production use. This highlights the fundamental architectural differences between the two databases for analytical workloads.

### 4. Aggregation Query Performance

| Database | Dataset | Mean Time (s) | Min Time (s) | Max Time (s) | Ratio |
|----------|---------|---------------|--------------|--------------|-------|
| ScyllaDB | Small   | 0.071         | 0.069        | 0.076        | 1.0   |
| DuckDB   | Small   | 0.048         | 0.047        | 0.051        | 1.5x  |
| ScyllaDB | Medium  | 0.208         | 0.205        | 0.211        | 1.0   |
| DuckDB   | Medium  | 0.054         | 0.050        | 0.056        | 3.9x  |

**Analysis**: DuckDB's advantage in aggregation queries increases with dataset size, from 1.5x faster for small datasets to 3.9x faster for medium datasets. Note that the ScyllaDB implementation had to be simplified to use COUNT(*) instead of more complex aggregations due to ScyllaDB's limitations with non-primary key columns.

### 5. Concurrency Performance

#### 1 Thread

| Database | Dataset | Mean Time (s) | Min Time (s) | Max Time (s) | Ratio |
|----------|---------|---------------|--------------|--------------|-------|
| ScyllaDB | Small   | 0.063         | 0.060        | 0.064        | 1.0   |
| DuckDB   | Small   | 0.728         | 0.704        | 0.752        | 0.09x |
| ScyllaDB | Medium  | 0.074         | 0.041        | 0.136        | 1.0   |
| DuckDB   | Medium  | 0.882         | 0.827        | 0.955        | 0.08x |

#### 4 Threads

| Database | Dataset | Mean Time (s) | Min Time (s) | Max Time (s) | Ratio |
|----------|---------|---------------|--------------|--------------|-------|
| ScyllaDB | Small   | 0.137         | 0.081        | 0.183        | 1.0   |
| DuckDB   | Small   | 0.917         | 0.880        | 0.968        | 0.15x |
| ScyllaDB | Medium  | 0.054         | 0.052        | 0.057        | 1.0   |
| DuckDB   | Medium  | 1.100         | 1.077        | 1.121        | 0.05x |

#### 16 Threads

| Database | Dataset | Mean Time (s) | Min Time (s) | Max Time (s) | Ratio |
|----------|---------|---------------|--------------|--------------|-------|
| ScyllaDB | Small   | 0.142         | 0.120        | 0.169        | 1.0   |
| DuckDB   | Small   | 1.773         | 1.671        | 1.829        | 0.08x |
| ScyllaDB | Medium  | 0.115         | 0.100        | 0.138        | 1.0   |
| DuckDB   | Medium  | 1.784         | 1.515        | 2.081        | 0.06x |

**Analysis**: ScyllaDB significantly outperforms DuckDB in concurrent operations across all thread counts and dataset sizes. With the medium dataset, ScyllaDB is approximately 12.5x faster with 1 thread, 20x faster with 4 threads, and 16.7x faster with 16 threads. DuckDB's performance degrades as concurrency increases, and it encountered transaction conflicts with larger datasets, requiring error handling. This demonstrates ScyllaDB's strength in handling concurrent workloads, which is a key feature of its distributed architecture.

## Scaling Behavior

### ScyllaDB Scaling

| Operation      | Small (s) | Medium (s) | Scaling Factor |
|----------------|-----------|------------|----------------|
| Data Loading   | 6.49      | 63.25      | 9.7x           |
| Point Queries  | 0.119     | 0.079      | 0.7x (better)  |
| Range Queries  | 2.64      | 31.18      | 11.8x          |
| Aggregations   | 0.071     | 0.208      | 2.9x           |
| Concurrent (1) | 0.063     | 0.074      | 1.2x           |
| Concurrent (4) | 0.137     | 0.054      | 0.4x (better)  |
| Concurrent (16)| 0.142     | 0.115      | 0.8x (better)  |

### DuckDB Scaling

| Operation      | Small (s) | Medium (s) | Scaling Factor |
|----------------|-----------|------------|----------------|
| Data Loading   | 1.94      | 5.59       | 2.9x           |
| Point Queries  | 0.057     | 0.040      | 0.7x (better)  |
| Range Queries  | 0.034     | 0.026      | 0.8x (better)  |
| Aggregations   | 0.048     | 0.054      | 1.1x           |
| Concurrent (1) | 0.728     | 0.882      | 1.2x           |
| Concurrent (4) | 0.917     | 1.100      | 1.2x           |
| Concurrent (16)| 1.773     | 1.784      | 1.0x           |

**Analysis**: 
- ScyllaDB shows near-linear scaling for data loading and range queries as dataset size increases 10x, but interestingly shows better performance for point queries and concurrent operations with larger datasets.
- DuckDB shows sub-linear scaling for data loading (2.9x slower for 10x more data) and even improves performance for point and range queries with larger datasets, likely due to optimization techniques like caching and vectorized execution.
- For concurrent operations, DuckDB's performance degrades consistently by about 20% with larger datasets, while ScyllaDB's concurrent performance actually improves in some cases with larger datasets.

## Overall Conclusions

1. **DuckDB excels at analytical workloads**: DuckDB significantly outperforms ScyllaDB in data loading, range queries, and shows better performance in point queries and aggregations. This advantage becomes even more pronounced with larger datasets.

2. **ScyllaDB excels at concurrent operations**: ScyllaDB dramatically outperforms DuckDB when handling concurrent operations, showing its strength as a distributed database designed for high throughput. This advantage is maintained or even improved with larger datasets.

3. **Scaling characteristics**:
   - ScyllaDB scales linearly for data loading and range queries but shows better-than-expected scaling for point queries and concurrent operations.
   - DuckDB shows excellent sub-linear scaling for most operations, demonstrating its efficiency with larger datasets.

4. **Use case recommendations**:
   - Choose **DuckDB** for analytical workloads, data exploration, and scenarios where you need fast range scans and aggregations on moderate-sized datasets.
   - Choose **ScyllaDB** for high-concurrency workloads, real-time applications, and scenarios where you need consistent performance with many simultaneous operations.

5. **Transaction handling**: DuckDB encountered transaction conflicts with concurrent operations on larger datasets, requiring error handling. ScyllaDB's architecture is better suited for concurrent write operations.

## Future Work

1. Run benchmarks with large datasets (1,000,000+ rows) to observe scaling behavior at even larger scales
2. Test more complex query patterns including joins and window functions
3. Benchmark write-heavy workloads with different consistency levels
4. Measure resource utilization (CPU, memory, disk I/O)
5. Test with distributed ScyllaDB cluster to evaluate horizontal scaling

---

*Note: These benchmarks represent a specific workload and environment. Your results may vary based on hardware, configuration, data characteristics, and query patterns.*