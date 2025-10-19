#!/bin/bash

# Script to run tests for all Docker Compose services
# Services: astrology, bot, memory

set -e  # Exit on any error

echo "🚀 Starting test execution for all services..."
echo "=============================================="

# Function to run command in container and check result
run_test() {
    local service=$1
    local command=$2
    local description=$3
    local test_files=$4  # Optional: files to copy into container

    echo ""
    echo "🧪 Testing $description ($service)..."

    # Copy test files if specified
    if [ -n "$test_files" ]; then
        echo "📋 Copying test files to container..."
        for file in $test_files; do
            if [ -f "$file" ]; then
                sudo docker cp "$file" "$service:/app/$(basename "$file")"
                echo "  Copied $file"
            fi
        done
    fi

    # Install additional dependencies if needed
    if [ "$service" = "astrology-mcp" ]; then
        echo "📦 Installing test dependencies..."
        sudo docker compose exec $service pip install requests
    fi

    echo "Command: sudo docker compose exec $service $command"

    if sudo docker compose exec $service $command; then
        echo "✅ $description tests passed!"
    else
        echo "❌ $description tests failed!"
        return 1
    fi
}

# Check if services are running
echo "📋 Checking service status..."
if ! sudo docker compose ps | grep -q "Up"; then
    echo "❌ No services are running. Please start services with 'sudo docker compose up -d' first."
    exit 1
fi

# Run astrology tests (MCP server tests cover both API and MCP)
run_test "astrology-mcp" "python test_mcp_server.py" "Astrology MCP Server" "astrology/test_mcp_server.py astrology/test_horoscope_endpoints.py astrology/test_new_endpoints.py"

# Run bot tests
run_test "bot" "python run_tests.py" "Bot Service"

# Run memory tests
run_test "memory-service" "pytest tests/ -v" "Memory Service"

echo ""
echo "=============================================="
echo "🎉 All tests completed successfully!"
echo "=============================================="