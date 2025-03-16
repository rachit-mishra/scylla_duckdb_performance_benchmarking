"""
Visualization module for benchmark results.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional

# Set up plotting style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")


class BenchmarkVisualizer:
    """Visualize benchmark results."""
    
    def __init__(self, results_dir: str = "results"):
        """Initialize visualizer with results directory."""
        self.results_dir = results_dir
        self.results = self._load_results()
    
    def _load_results(self) -> Dict[str, Any]:
        """Load benchmark results from JSON file."""
        json_path = os.path.join(self.results_dir, "benchmark_results.json")
        
        if not os.path.exists(json_path):
            return {}
        
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def _prepare_comparison_data(self, benchmark_name: str) -> pd.DataFrame:
        """Prepare data for comparison visualization."""
        if benchmark_name not in self.results:
            raise ValueError(f"Benchmark '{benchmark_name}' not found in results")
        
        data = []
        for result in self.results[benchmark_name]:
            row = {
                "Database": result["database"],
                "Min (s)": result["min"],
                "Max (s)": result["max"],
                "Mean (s)": result["mean"],
                "Median (s)": result["median"],
                "Std Dev": result["std_dev"]
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def create_bar_chart(self, benchmark_name: str, metric: str = "Mean (s)") -> None:
        """Create a bar chart comparing databases for a specific benchmark."""
        df = self._prepare_comparison_data(benchmark_name)
        
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x="Database", y=metric, data=df)
        
        plt.title(f"{benchmark_name} - {metric} Comparison")
        plt.ylabel(metric)
        plt.tight_layout()
        
        # Add values on top of bars
        for i, v in enumerate(df[metric]):
            ax.text(i, v + 0.01, f"{v:.4f}", ha='center')
        
        # Save figure
        output_path = os.path.join(self.results_dir, f"{benchmark_name}_{metric.replace(' ', '_')}_bar.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        
        print(f"Bar chart saved to {output_path}")
    
    def create_comparison_chart(self, benchmark_names: List[str], metric: str = "Mean (s)") -> None:
        """Create a chart comparing multiple benchmarks."""
        data = []
        
        for benchmark_name in benchmark_names:
            if benchmark_name not in self.results:
                continue
            
            for result in self.results[benchmark_name]:
                row = {
                    "Benchmark": benchmark_name,
                    "Database": result["database"],
                    metric: result[metric.split(" ")[0].lower()]
                }
                data.append(row)
        
        if not data:
            print("No data available for comparison chart")
            return
        
        df = pd.DataFrame(data)
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(x="Benchmark", y=metric, hue="Database", data=df)
        
        plt.title(f"Benchmark Comparison - {metric}")
        plt.ylabel(metric)
        plt.xticks(rotation=45)
        plt.legend(title="Database")
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.results_dir, f"benchmark_comparison_{metric.replace(' ', '_')}.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        
        print(f"Comparison chart saved to {output_path}")
    
    def create_scaling_chart(self, benchmark_prefix: str, metric: str = "Mean (s)") -> None:
        """Create a chart showing how performance scales with data size."""
        data = []
        
        # Find all benchmarks with the given prefix
        for benchmark_name in self.results.keys():
            if benchmark_name.startswith(benchmark_prefix):
                # Extract data size from benchmark name
                if "small" in benchmark_name:
                    size = "Small"
                elif "medium" in benchmark_name:
                    size = "Medium"
                elif "large" in benchmark_name:
                    size = "Large"
                else:
                    continue
                
                for result in self.results[benchmark_name]:
                    row = {
                        "Data Size": size,
                        "Database": result["database"],
                        metric: result[metric.split(" ")[0].lower()]
                    }
                    data.append(row)
        
        if not data:
            print(f"No scaling data available for benchmark prefix '{benchmark_prefix}'")
            return
        
        df = pd.DataFrame(data)
        
        # Order data sizes correctly
        size_order = ["Small", "Medium", "Large"]
        df["Data Size"] = pd.Categorical(df["Data Size"], categories=size_order, ordered=True)
        df = df.sort_values("Data Size")
        
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x="Data Size", y=metric, hue="Database", marker="o", data=df)
        
        plt.title(f"{benchmark_prefix} Scaling Performance - {metric}")
        plt.ylabel(metric)
        plt.grid(True)
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.results_dir, f"{benchmark_prefix}_scaling_{metric.replace(' ', '_')}.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        
        print(f"Scaling chart saved to {output_path}")
    
    def create_concurrency_chart(self, metric: str = "Mean (s)") -> None:
        """Create a chart showing how performance scales with concurrency."""
        data = []
        
        # Find all concurrent benchmarks
        for benchmark_name in self.results.keys():
            if benchmark_name.startswith("concurrent_"):
                # Extract concurrency level from benchmark name
                parts = benchmark_name.split("_")
                if len(parts) >= 2 and parts[1].isdigit():
                    concurrency = int(parts[1])
                    
                    for result in self.results[benchmark_name]:
                        row = {
                            "Concurrency": concurrency,
                            "Database": result["database"],
                            metric: result[metric.split(" ")[0].lower()]
                        }
                        data.append(row)
        
        if not data:
            print("No concurrency data available")
            return
        
        df = pd.DataFrame(data)
        df = df.sort_values("Concurrency")
        
        plt.figure(figsize=(10, 6))
        ax = sns.lineplot(x="Concurrency", y=metric, hue="Database", marker="o", data=df)
        
        plt.title(f"Concurrency Scaling - {metric}")
        plt.xlabel("Concurrency Level")
        plt.ylabel(metric)
        plt.grid(True)
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.results_dir, f"concurrency_scaling_{metric.replace(' ', '_')}.png")
        plt.savefig(output_path, dpi=300)
        plt.close()
        
        print(f"Concurrency chart saved to {output_path}")
    
    def create_interactive_dashboard(self) -> None:
        """Create an interactive HTML dashboard with Plotly."""
        all_data = []
        
        for benchmark_name, results in self.results.items():
            for result in results:
                # Parse benchmark name to extract type and size
                parts = benchmark_name.split("_")
                benchmark_type = parts[0]
                
                # Determine data size if present
                data_size = "N/A"
                for part in parts:
                    if part in ["small", "medium", "large"]:
                        data_size = part.capitalize()
                
                # Determine concurrency if present
                concurrency = "N/A"
                if benchmark_type == "concurrent" and len(parts) >= 2 and parts[1].isdigit():
                    concurrency = int(parts[1])
                
                row = {
                    "Benchmark": benchmark_name,
                    "Type": benchmark_type,
                    "Data Size": data_size,
                    "Concurrency": concurrency,
                    "Database": result["database"],
                    "Min (s)": result["min"],
                    "Max (s)": result["max"],
                    "Mean (s)": result["mean"],
                    "Median (s)": result["median"],
                    "Std Dev": result["std_dev"]
                }
                all_data.append(row)
        
        if not all_data:
            print("No data available for interactive dashboard")
            return
        
        df = pd.DataFrame(all_data)
        
        # Create interactive bar chart
        fig1 = px.bar(
            df, 
            x="Benchmark", 
            y="Mean (s)", 
            color="Database",
            barmode="group",
            title="Mean Execution Time by Benchmark",
            hover_data=["Min (s)", "Max (s)", "Median (s)", "Std Dev"]
        )
        
        # Create interactive line chart for concurrency
        concurrency_df = df[df["Concurrency"] != "N/A"].sort_values("Concurrency")
        if not concurrency_df.empty:
            fig2 = px.line(
                concurrency_df,
                x="Concurrency",
                y="Mean (s)",
                color="Database",
                markers=True,
                title="Performance Scaling with Concurrency"
            )
        else:
            fig2 = go.Figure()
            fig2.update_layout(title="No concurrency data available")
        
        # Create interactive line chart for data size scaling
        size_order = {"Small": 1, "Medium": 2, "Large": 3, "N/A": 0}
        scaling_df = df[df["Data Size"] != "N/A"].copy()
        if not scaling_df.empty:
            scaling_df["Size Order"] = scaling_df["Data Size"].map(size_order)
            scaling_df = scaling_df.sort_values("Size Order")
            
            fig3 = px.line(
                scaling_df,
                x="Data Size",
                y="Mean (s)",
                color="Database",
                facet_col="Type",
                markers=True,
                title="Performance Scaling with Data Size"
            )
        else:
            fig3 = go.Figure()
            fig3.update_layout(title="No data size scaling data available")
        
        # Create HTML file with all figures
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Database Benchmark Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .chart {{ margin-bottom: 30px; }}
                h1 {{ color: #333; }}
            </style>
        </head>
        <body>
            <h1>ScyllaDB vs DuckDB Performance Benchmark</h1>
            
            <div class="chart" id="chart1"></div>
            <div class="chart" id="chart2"></div>
            <div class="chart" id="chart3"></div>
            
            <script>
                var fig1 = {fig1.to_json()};
                var fig2 = {fig2.to_json()};
                var fig3 = {fig3.to_json()};
                
                Plotly.newPlot('chart1', fig1.data, fig1.layout);
                Plotly.newPlot('chart2', fig2.data, fig2.layout);
                Plotly.newPlot('chart3', fig3.data, fig3.layout);
            </script>
        </body>
        </html>
        """
        
        # Save dashboard
        output_path = os.path.join(self.results_dir, "benchmark_dashboard.html")
        with open(output_path, 'w') as f:
            f.write(dashboard_html)
        
        print(f"Interactive dashboard saved to {output_path}")
    
    def generate_all_visualizations(self) -> None:
        """Generate all visualizations for the benchmark results."""
        # Create bar charts for each benchmark
        for benchmark_name in self.results.keys():
            self.create_bar_chart(benchmark_name)
        
        # Create comparison charts for similar benchmarks
        benchmark_types = {
            "data_loading": [],
            "point_query": [],
            "range_query": [],
            "aggregation_query": [],
            "concurrent": []
        }
        
        for benchmark_name in self.results.keys():
            for benchmark_type in benchmark_types.keys():
                if benchmark_name.startswith(benchmark_type):
                    benchmark_types[benchmark_type].append(benchmark_name)
        
        for benchmark_type, benchmarks in benchmark_types.items():
            if benchmarks:
                self.create_comparison_chart(benchmarks)
        
        # Create scaling charts
        for benchmark_type in ["data_loading", "point_query", "range_query", "aggregation_query"]:
            self.create_scaling_chart(benchmark_type)
        
        # Create concurrency chart
        self.create_concurrency_chart()
        
        # Create interactive dashboard
        self.create_interactive_dashboard()


if __name__ == "__main__":
    visualizer = BenchmarkVisualizer()
    visualizer.generate_all_visualizations() 