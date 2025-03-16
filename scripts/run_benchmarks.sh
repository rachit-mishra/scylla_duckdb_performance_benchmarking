#!/bin/bash
# Script to run the benchmarks

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
DATA_SIZES="small,medium"
BENCHMARK_TYPES="all"
SKIP_DATA_GENERATION=false
SKIP_VISUALIZATION=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --data-sizes)
            DATA_SIZES="$2"
            shift
            shift
            ;;
        --benchmark-types)
            BENCHMARK_TYPES="$2"
            shift
            shift
            ;;
        --skip-data-generation)
            SKIP_DATA_GENERATION=true
            shift
            ;;
        --skip-visualization)
            SKIP_VISUALIZATION=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --data-sizes <sizes>         Comma-separated list of data sizes (small,medium,large)"
            echo "  --benchmark-types <types>    Comma-separated list of benchmark types (data_loading,queries,concurrent,all)"
            echo "  --skip-data-generation       Skip data generation step"
            echo "  --skip-visualization         Skip visualization generation step"
            echo "  --help                       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $key"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not available. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Start Docker containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
docker-compose up -d

# Wait for ScyllaDB to be ready
echo -e "${YELLOW}Waiting for ScyllaDB to be ready...${NC}"

# Get the ScyllaDB container name
SCYLLA_CONTAINER=$(docker ps --filter "name=scylla" --format "{{.Names}}" | head -n 1)

if [ -z "$SCYLLA_CONTAINER" ]; then
    echo -e "${RED}ScyllaDB container not found. Check if it's running.${NC}"
    exit 1
fi

echo -e "${YELLOW}Found ScyllaDB container: $SCYLLA_CONTAINER${NC}"

for i in {1..30}; do
    if docker exec $SCYLLA_CONTAINER cqlsh -e "SHOW VERSION" > /dev/null 2>&1; then
        echo -e "${GREEN}ScyllaDB is ready!${NC}"
        break
    fi
    echo -e "${YELLOW}Waiting for ScyllaDB to start (attempt $i/30)...${NC}"
    sleep 5
    
    if [ $i -eq 30 ]; then
        echo -e "${RED}Timed out waiting for ScyllaDB to start.${NC}"
        exit 1
    fi
done

# Create data directories if they don't exist
echo -e "${GREEN}Creating data directories...${NC}"
mkdir -p data/duckdb
mkdir -p results

# Build command arguments
CMD_ARGS=""

if [ "$SKIP_DATA_GENERATION" = true ]; then
    CMD_ARGS="$CMD_ARGS --skip-data-generation"
fi

if [ "$SKIP_VISUALIZATION" = true ]; then
    CMD_ARGS="$CMD_ARGS --skip-visualization"
fi

# Run benchmarks
echo -e "${GREEN}Running benchmarks with data sizes: $DATA_SIZES and benchmark types: $BENCHMARK_TYPES${NC}"
cd "$(dirname "$0")/.." || exit 1
python3 src/run_benchmarks.py --data-sizes "$DATA_SIZES" --benchmark-types "$BENCHMARK_TYPES" $CMD_ARGS

echo -e "${GREEN}Benchmarks completed successfully!${NC}"
echo -e "${YELLOW}Results are available in the results/ directory.${NC}"

# Ask if user wants to stop Docker containers
echo -e "${YELLOW}Do you want to stop the Docker containers? (y/n)${NC}"
read -r stop_containers

if [ "$stop_containers" = "y" ] || [ "$stop_containers" = "Y" ]; then
    echo -e "${GREEN}Stopping Docker containers...${NC}"
    docker-compose down
    echo -e "${GREEN}Docker containers stopped.${NC}"
else
    echo -e "${YELLOW}Docker containers are still running. You can stop them later with 'docker-compose down'.${NC}"
fi 