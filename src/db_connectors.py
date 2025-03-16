"""
Database connector utilities for ScyllaDB and DuckDB.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

# For ScyllaDB
from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy

# For DuckDB
import duckdb

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/benchmark_config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise


class ScyllaConnector:
    """Connector for ScyllaDB."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ScyllaDB connector with configuration."""
        if config is None:
            config = load_config()["databases"]["scylla"]
        
        self.config = config
        self.cluster = None
        self.session = None
    
    def connect(self) -> Session:
        """Connect to ScyllaDB cluster."""
        try:
            auth_provider = None
            if self.config.get("username") and self.config.get("password"):
                auth_provider = PlainTextAuthProvider(
                    username=self.config["username"],
                    password=self.config["password"]
                )
            
            # Try to connect to the Docker container first, then fallback to localhost
            hosts = ["scylla", "scylla-node", self.config["host"]]
            connected = False
            
            for host in hosts:
                try:
                    logger.info(f"Attempting to connect to ScyllaDB at {host}:{self.config['port']}")
                    self.cluster = Cluster(
                        contact_points=[host],
                        port=self.config["port"],
                        auth_provider=auth_provider,
                        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='datacenter1'),
                        protocol_version=4
                    )
                    
                    self.session = self.cluster.connect(wait_for_all_pools=False)
                    connected = True
                    logger.info(f"Connected to ScyllaDB at {host}:{self.config['port']}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to connect to ScyllaDB at {host}: {e}")
                    continue
            
            if not connected:
                raise Exception("Failed to connect to any ScyllaDB host")
            
            # Create keyspace if it doesn't exist
            self.session.execute(
                f"""
                CREATE KEYSPACE IF NOT EXISTS {self.config["keyspace"]}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
                """
            )
            
            self.session.set_keyspace(self.config["keyspace"])
            return self.session
        
        except Exception as e:
            logger.error(f"Error connecting to ScyllaDB: {e}")
            raise
    
    def close(self) -> None:
        """Close the ScyllaDB connection."""
        if self.cluster:
            self.cluster.shutdown()
            logger.info("ScyllaDB connection closed")


class DuckDBConnector:
    """Connector for DuckDB."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize DuckDB connector with configuration."""
        if config is None:
            config = load_config()["databases"]["duckdb"]
        
        self.config = config
        self.connection = None
    
    def connect(self) -> duckdb.DuckDBPyConnection:
        """Connect to DuckDB database."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config["database_path"]), exist_ok=True)
            
            # Connect to DuckDB
            self.connection = duckdb.connect(self.config["database_path"])
            
            # Configure connection
            self.connection.execute(f"PRAGMA memory_limit='{self.config['memory_limit']}'")
            self.connection.execute(f"PRAGMA threads={self.config['threads']}")
            
            logger.info(f"Connected to DuckDB at {self.config['database_path']}")
            return self.connection
        
        except Exception as e:
            logger.error(f"Error connecting to DuckDB: {e}")
            raise
    
    def close(self) -> None:
        """Close the DuckDB connection."""
        if self.connection:
            self.connection.close()
            logger.info("DuckDB connection closed")


# Factory function to get the appropriate connector
def get_connector(db_type: str, config: Optional[Dict[str, Any]] = None):
    """Get a database connector based on the database type."""
    if db_type.lower() == "scylla":
        return ScyllaConnector(config)
    elif db_type.lower() == "duckdb":
        return DuckDBConnector(config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}") 