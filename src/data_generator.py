"""
Data generator for creating synthetic datasets for benchmarking.
"""

import os
import uuid
import json
import random
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataGenerator:
    """Generate synthetic data for benchmarking."""
    
    def __init__(self, config_path: str = "config/benchmark_config.yaml"):
        """Initialize data generator with configuration."""
        import yaml
        
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)["data"]
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def _generate_column_value(self, column_def: Dict[str, Any]) -> Any:
        """Generate a value for a column based on its definition."""
        col_type = column_def["type"].lower()
        
        if col_type == "uuid":
            return str(uuid.uuid4())
        
        elif col_type == "timestamp":
            # Generate a timestamp within the last year
            days_ago = random.randint(0, 365)
            return datetime.now() - timedelta(days=days_ago)
        
        elif col_type == "int":
            return random.randint(1, 1000000)
        
        elif col_type == "float":
            return random.uniform(0, 1000.0)
        
        elif col_type == "string":
            cardinality = column_def.get("cardinality", 1000)
            return f"category_{random.randint(1, cardinality)}"
        
        elif col_type.startswith("list<"):
            max_length = column_def.get("max_length", 5)
            length = random.randint(0, max_length)
            
            if "string" in col_type:
                return [f"tag_{random.randint(1, 100)}" for _ in range(length)]
            else:
                return [random.randint(1, 100) for _ in range(length)]
        
        elif col_type == "json":
            max_keys = column_def.get("max_keys", 5)
            num_keys = random.randint(1, max_keys)
            
            # Create a JSON object with numeric values only to avoid serialization issues
            return {
                f"key_{i}": random.choice([
                    random.randint(1, 100),
                    round(random.uniform(0, 100.0), 2),
                    random.randint(0, 1)  # Use 0/1 instead of boolean
                ])
                for i in range(num_keys)
            }
        
        else:
            logger.warning(f"Unknown column type: {col_type}, using string")
            return f"unknown_{random.randint(1, 1000)}"
    
    def generate_dataset(self, size: str = "small") -> pd.DataFrame:
        """Generate a dataset of the specified size."""
        if size not in self.config:
            raise ValueError(f"Unknown dataset size: {size}")
        
        num_rows = self.config[size]["rows"]
        columns = self.config["columns"]
        
        logger.info(f"Generating {size} dataset with {num_rows} rows")
        
        # Initialize empty dataframe
        df = pd.DataFrame()
        
        # Generate data for each column
        for col_def in columns:
            col_name = col_def["name"]
            logger.info(f"Generating column: {col_name}")
            
            # Generate values for this column
            if col_def["type"].lower() == "json":
                # Handle JSON columns specially - convert to strings for storage
                values = [json.dumps(self._generate_column_value(col_def)) for _ in range(num_rows)]
                df[col_name] = values
            else:
                # Generate values for other column types
                values = [self._generate_column_value(col_def) for _ in range(num_rows)]
                df[col_name] = values
        
        return df
    
    def save_dataset(self, df: pd.DataFrame, size: str = "small") -> str:
        """Save the dataset to a file."""
        if size not in self.config:
            raise ValueError(f"Unknown dataset size: {size}")
        
        file_path = self.config[size]["file_path"]
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save as parquet
        df.to_parquet(file_path, index=False)
        logger.info(f"Saved {size} dataset to {file_path}")
        
        return file_path
    
    def generate_and_save_all_datasets(self) -> Dict[str, str]:
        """Generate and save all datasets defined in the configuration."""
        dataset_paths = {}
        
        for size in ["small", "medium", "large"]:
            if size in self.config:
                df = self.generate_dataset(size)
                path = self.save_dataset(df, size)
                dataset_paths[size] = path
        
        return dataset_paths


if __name__ == "__main__":
    # When run directly, generate all datasets
    generator = DataGenerator()
    paths = generator.generate_and_save_all_datasets()
    
    for size, path in paths.items():
        print(f"Generated {size} dataset: {path}") 