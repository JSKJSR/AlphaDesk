#!/bin/bash

# TradingAgents Claude Setup Script
# This script creates a virtual environment and installs dependencies

echo "=========================================="
echo "  TradingAgents - Claude Edition Setup"
echo "=========================================="

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
fi

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p results
mkdir -p tradingagents/dataflows/data_cache

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the environment:  source venv/bin/activate"
echo "2. Edit .env with your API keys"
echo "3. Run the CLI:  python -m cli.main"
echo ""
