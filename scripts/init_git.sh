#!/bin/bash
# Script to initialize Git repository and push to GitHub

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Initializing Git repository for ScyllaDB vs DuckDB Performance Benchmark${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed. Please install Git and try again.${NC}"
    exit 1
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo -e "${GREEN}Initializing Git repository...${NC}"
    git init
else
    echo -e "${YELLOW}Git repository already initialized.${NC}"
fi

# Create .gitignore file
echo -e "${GREEN}Creating .gitignore file...${NC}"
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# Data files
data/*.parquet
data/duckdb/*.db

# Results
results/*.csv
results/*.json
results/*.png
results/*.html

# Jupyter Notebook
.ipynb_checkpoints

# IDE files
.idea/
.vscode/
*.swp
*.swo

# OS specific files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOL

# Add all files to git
echo -e "${GREEN}Adding files to Git...${NC}"
git add .

# Commit changes
echo -e "${GREEN}Committing initial project structure...${NC}"
git commit -m "Initial commit: ScyllaDB vs DuckDB Performance Benchmark"

# Ask for GitHub repository details
echo -e "${YELLOW}Do you want to push to GitHub? (y/n)${NC}"
read -r push_to_github

if [ "$push_to_github" = "y" ] || [ "$push_to_github" = "Y" ]; then
    echo -e "${YELLOW}Enter your GitHub username:${NC}"
    read -r github_username
    
    echo -e "${YELLOW}Enter the name for your GitHub repository:${NC}"
    read -r repo_name
    
    # Create GitHub repository
    echo -e "${GREEN}Creating GitHub repository ${github_username}/${repo_name}...${NC}"
    echo -e "${YELLOW}Please create a new repository on GitHub named '${repo_name}' and press Enter when done.${NC}"
    read -r
    
    # Add GitHub remote
    echo -e "${GREEN}Adding GitHub remote...${NC}"
    git remote add origin "https://github.com/${github_username}/${repo_name}.git"
    
    # Push to GitHub
    echo -e "${GREEN}Pushing to GitHub...${NC}"
    git push -u origin master || git push -u origin main
    
    echo -e "${GREEN}Successfully pushed to GitHub repository: https://github.com/${github_username}/${repo_name}${NC}"
else
    echo -e "${YELLOW}Skipping GitHub push. You can push to GitHub later using:${NC}"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "  git push -u origin master"
fi

echo -e "${GREEN}Git initialization completed successfully!${NC}" 