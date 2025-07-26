#!/bin/bash

# Setup script for Humsafar Financial AI Assistant
# 
# To run this script:
# 1. Make it executable: chmod +x setup.sh
# 2. Run it: ./setup.sh
# 
# Or run directly with bash: bash setup.sh

echo "Setting up Humsafar Financial AI Assistant environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Copy .env.example to .env if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your actual Google API Key!"
    echo "   Replace 'YOUR_API_KEY_HERE' with your real API key."
else
    echo ".env file already exists, skipping creation."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the environment: source venv/bin/activate"
echo "2. Edit .env file and add your Google API Key"
echo "3. Run the application: python main.py"
