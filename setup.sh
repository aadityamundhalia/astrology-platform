#!/bin/bash

# Astrology Platform Setup Script
# This script helps set up the environment for the first time

set -e

echo "=================================="
echo "Astrology Platform Setup"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists."
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping .env creation"
    else
        cp .env.example .env
        echo "✅ Created .env from .env.example"
    fi
else
    cp .env.example .env
    echo "✅ Created .env from .env.example"
fi

echo ""
echo "=================================="
echo "Configuration Required"
echo "=================================="
echo ""
echo "You need to configure the following in .env:"
echo ""
echo "1. TELEGRAM_BOT_TOKEN - Get from @BotFather on Telegram"
echo "2. CHAT_ENCRYPTION_KEY - Generate with:"
echo "   python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
echo ""
echo "3. (Optional) Update passwords:"
echo "   - POSTGRES_PASSWORD"
echo "   - REDIS_PASSWORD"
echo ""
echo "4. (Optional) Update Ollama host if different:"
echo "   - OLLAMA_HOST"
echo "   - OLLAMA_EMBEDDING_BASE_URL"
echo ""

read -p "Press Enter to open .env file for editing..."

# Try to open with common editors
if command -v nano &> /dev/null; then
    nano .env
elif command -v vim &> /dev/null; then
    vim .env
elif command -v vi &> /dev/null; then
    vi .env
else
    echo "Please edit .env manually with your preferred editor"
fi

echo ""
echo "=================================="
echo "Ready to Start"
echo "=================================="
echo ""
echo "To start all services, run:"
echo "  docker-compose up -d"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To check service health:"
echo "  docker-compose ps"
echo ""
echo "For more commands, see README.md"
echo ""