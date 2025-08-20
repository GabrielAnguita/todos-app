#!/bin/bash

# Simple VM deployment script
set -e

echo "🚀 Deploying Todos App..."

# Stop any running containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Pull latest code (if using git)
if [ -d ".git" ]; then
    echo "📥 Pulling latest code..."
    git pull
fi

# Build and start containers
echo "🐳 Building and starting containers..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 10

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Run migrations
echo "🗃️  Running database migrations..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web python manage.py migrate

# Setup OAuth (if credentials are provided)
echo "🔐 Setting up OAuth..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T web python manage.py setup_oauth

# Show status
echo "📊 Container status:"
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

echo "✅ Deployment complete!"
echo "🌐 Your app should be running on http://$(curl -s ifconfig.me)"
echo "📋 Check logs with: docker-compose logs -f web"