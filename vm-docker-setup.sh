#!/bin/bash

# Single VM + Docker Compose Setup
# This is the SIMPLEST possible deployment

set -e

echo "🚀 Setting up VM with Docker Compose..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose

# Install git for code deployment
sudo apt install -y git

# Create app directory
mkdir -p ~/todos-app

echo "✅ VM setup complete!"
echo "🐳 Docker and Docker Compose installed"
echo "📁 App directory: ~/todos-app"
echo ""
echo "Next steps:"
echo "1. Upload your code to ~/todos-app"
echo "2. Run: docker-compose up -d"
echo "3. That's it! 🎉"