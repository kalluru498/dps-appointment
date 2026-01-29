#!/bin/bash

# Quick Start Script for DPS Monitor
# This script helps you set up and run the monitor locally

set -e

echo "================================================"
echo "Texas DPS Appointment Monitor - Quick Start"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11+ required (found $python_version)"
    exit 1
fi
echo "✅ Python $python_version found"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers (this may take a few minutes)..."
playwright install chromium
playwright install-deps chromium
echo "✅ Playwright browsers installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your actual information!"
    echo "   Run: nano .env"
    echo ""
    read -p "Press Enter to continue after editing .env..."
else
    echo "✅ .env file found"
fi
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p logs screenshots results
echo "✅ Directories created"
echo ""

# Ask if user wants to run tests
read -p "Do you want to run tests? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running tests..."
    pytest tests/ -v -m "not integration"
    echo ""
fi

# Ask if user wants to run the checker
read -p "Do you want to run the appointment checker now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "================================================"
    echo "Running Appointment Checker..."
    echo "================================================"
    echo ""
    cd src
    python appointment_checker.py
    cd ..
fi

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your actual information"
echo "2. Run the checker: cd src && python appointment_checker.py"
echo "3. Or set up GitHub Actions for automated monitoring"
echo ""
echo "For GitHub Actions setup, see README.md"
echo ""
