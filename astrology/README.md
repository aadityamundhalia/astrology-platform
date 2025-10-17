# 🌟 Vedic Astrology API with Standalone MCP Server

> **Ultra-precise astrological predictions with 24-month forecasts, event-specific analysis, and standalone HTTP-based MCP server**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Swiss Ephemeris](https://img.shields.io/badge/Swiss_Ephemeris-Latest-orange.svg)](https://www.astro.com/swisseph/)
[![MCP](https://img.shields.io/badge/MCP-Standalone-purple.svg)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 📋 Table of Contents

- [What's New](#-whats-new-in-v22)
- [Quick Start](#-quick-start)
- [MCP Server - Standalone HTTP API](#-mcp-server---standalone-http-api)
- [Usage Examples](#-usage-examples)
- [Available Endpoints](#-all-available-endpoints)
- [Architecture](#-architecture)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 What's New in v2.2?

### 🤖 **NEW: Standalone HTTP-Based MCP Server**
- **No Claude Desktop dependency** - Works independently
- Full HTTP/REST API on port 8585
- Can be used by any HTTP client (curl, Postman, Python, etc.)
- Interactive Swagger documentation at `/docs`
- Generic `/execute` endpoint for flexible tool calling
- Direct convenience endpoints for each prediction type
- Health checks and service monitoring

### ✨ Core Prediction Features

1. **`/predictions/love`** - 24-month love & relationship forecast
2. **`/predictions/health`** - 24-month health & wellness forecast  
3. **`/predictions/career`** - 24-month career & professional forecast
4. **`/predictions/wealth`** - 24-month financial & wealth forecast
5. **`/predictions/wildcard`** 🎯 - Specific event predictions with success probability

### 🎯 Key Features

- ✅ **Standalone MCP Server** - HTTP-based, works with any client
- ✅ **Dual API System** - Main API (8087) + MCP Server (8585)
- ✅ **24-Month Forecasts** with precise date ranges
- ✅ **Success Probability** ratings (0-100%)
- ✅ **Hour-Level Timing** precision
- ✅ **Natural Language Queries** via wildcard endpoint
- ✅ **Risk Assessment** with mitigation strategies
- ✅ **Actionable Remedies** for challenging times
- ✅ **Docker Deployment** - Easy containerized setup
- ✅ **Interactive API Docs** - Swagger UI for both services

---

## 🏃 Quick Start

### Docker Deployment (Recommended)

```bash
# 1. Navigate to project directory
cd vedastro

# 2. Build and start all services
sudo docker compose up -d --build

# 3. Verify services are running
sudo docker compose ps

# Expected output:
# NAME                      STATUS    PORTS
# vedastro-vedastro-api-1   Up        0.0.0.0:8087->8087/tcp
# vedastro-vedastro-mcp-1   Up        0.0.0.0:8585->8585/tcp

# 4. Check logs
sudo docker compose logs -f
```

**Services Running:**
- **Vedastro API**: `http://localhost:8087` - Main astrological calculations
- **MCP Server**: `http://localhost:8585` - Standalone tool execution server

### Verify Installation

```bash
# Test Main API
curl http://localhost:8087/

# Test MCP Server
curl http://localhost:8585/

# Check MCP Server health
curl http://localhost:8585/health
```

---

## 🤖 MCP Server - Standalone HTTP API

### Overview

The MCP Server is a **standalone FastAPI service** that provides tool-based access to the Vedic Astrology API. Unlike traditional MCP servers that require Claude Desktop, this runs as an independent HTTP service.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Any HTTP Client (curl, Python, etc.)           │
│              Browser, Mobile App, Scripts                │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP/REST API
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│              MCP Server (Port 8585)                      │
│                  FastAPI Service                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │  • /tools       - List available tools             │ │
│  │  • /execute     - Execute any tool by name         │ │
│  │  • /birth-chart - Direct birth chart access        │ │
│  │  • /today       - Today's prediction               │ │
│  │  • /weekly      - Weekly forecast                  │ │
│  │  • /yearly      - Yearly forecast                  │ │
│  │  • /love        - Love predictions                 │ │
│  │  • /career      - Career predictions               │ │
│  │  • /wealth      - Wealth predictions               │ │
│  │  • /health      - Health predictions               │ │
│  │  • /wildcard    - Specific event queries           │ │
│  │  • /docs        - Interactive documentation        │ │
│  └────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP/JSON
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Vedastro API (Port 8087)                    │
│          Swiss Ephemeris + Vedic Calculations            │
└─────────────────────────────────────────────────────────┘
```

### MCP Server Endpoints

#### 1. Server Information
```bash
# Get server info
curl http://localhost:8585/

# Response:
{
  "service": "Vedic Astrology MCP Server",
  "version": "1.0.0",
  "status": "running",
  "api_url": "http://vedastro-api:8087",
  "endpoints": {
    "tools": "/tools",
    "execute": "/execute",
    "health": "/health",
    "docs": "/docs"
  }
}
```

#### 2. Health Check
```bash
# Check service health
curl http://localhost:8585/health

# Response:
{
  "mcp_server": "healthy",
  "vedastro_api": "healthy",
  "timestamp": "2024-10-17T10:30:00"
}
```

#### 3. List Available Tools
```bash
# Get all available tools
curl http://localhost:8585/tools

# Response shows 10 tools with descriptions:
{
  "tools": [
    {
      "name": "get_birth_chart",
      "description": "Get complete birth chart...",
      "category": "chart",
      "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
      "optional_fields": []
    },
    ...
  ]
}
```

### Using the MCP Server

#### Method 1: Generic Execute Endpoint

Execute any tool by name using the `/execute` endpoint:

```bash
curl -X POST http://localhost:8585/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_birth_chart",
    "arguments": {
      "date_of_birth": "1990-05-15",
      "time_of_birth": "10:30",
      "place_of_birth": "Mumbai, India"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ascendant": {"sign": "Cancer", "degree": 15.23},
    "planets": {...},
    "houses": {...}
  }
}
```

#### Method 2: Direct Convenience Endpoints

Use direct endpoints for simpler access:

```bash
# Birth Chart
curl -X POST http://localhost:8585/birth-chart \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India"
  }'

# Today's Prediction
curl -X POST http://localhost:8585/today \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India"
  }'

# Wildcard Query
curl -X POST http://localhost:8585/wildcard \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "London, UK",
    "query": "I have a job interview on December 15th, 2024. How will it go?"
  }'
```

#### Method 3: Interactive Documentation

Open in your browser:
```
http://localhost:8585/docs
```

You'll see Swagger UI where you can:
- Browse all endpoints
- Test requests interactively
- See request/response schemas
- Download API specifications

---

## 💡 Usage Examples

### Example 1: Using Python Requests

```python
import requests

# MCP Server URL
MCP_URL = "http://localhost:8585"

# Birth data
birth_data = {
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India"
}

# Method 1: Using execute endpoint
response = requests.post(
    f"{MCP_URL}/execute",
    json={
        "tool_name": "get_today_prediction",
        "arguments": birth_data
    }
)

result = response.json()
if result["success"]:
    print(f"Today's Rating: {result['data']['prediction']['overall_rating']}/10")
else:
    print(f"Error: {result['error']}")

# Method 2: Using direct endpoint
response = requests.post(f"{MCP_URL}/today", json=birth_data)
data = response.json()
print(f"Rating: {data['prediction']['overall_rating']}/10")
```

### Example 2: Birth Chart Analysis

```python
import requests
import json

MCP_URL = "http://localhost:8585"

# Get complete birth chart
response = requests.post(
    f"{MCP_URL}/birth-chart",
    json={
        "date_of_birth": "1990-05-15",
        "time_of_birth": "10:30",
        "place_of_birth": "Mumbai, India"
    }
)

chart = response.json()

# Display key information
print(f"Ascendant: {chart['ascendant']['sign']}")
print(f"Moon Sign: {chart['planets']['Moon']['sign']}")
print(f"Sun Sign: {chart['planets']['Sun']['sign']}")

# Display all planets
print("\nPlanetary Positions:")
for planet, data in chart['planets'].items():
    print(f"  {planet}: {data['sign']} ({data['degree']:.2f}°)")
```

### Example 3: Wildcard Queries

```python
import requests

MCP_URL = "http://localhost:8585"

# Ask specific questions
queries = [
    "I have a job interview on December 15th, 2024. How will it go?",
    "Should I buy a motorcycle? Will I be safe?",
    "When should I get married in 2025?",
    "Is starting a business on January 1st, 2025 a good idea?"
]

birth_data = {
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India"
}

for query in queries:
    print(f"\nQuery: {query}")
    
    response = requests.post(
        f"{MCP_URL}/wildcard",
        json={**birth_data, "query": query}
    )
    
    result = response.json()
    if 'success_probability' in result:
        prob = result['success_probability']
        print(f"  Success: {prob['percentage']}%")
        print(f"  Rating: {prob['rating']}")
```

### Example 4: Love Predictions with Date Range

```python
import requests
from datetime import datetime, timedelta

MCP_URL = "http://localhost:8585"

# Get love predictions for next 6 months
today = datetime.now()
six_months = today + timedelta(days=180)

response = requests.post(
    f"{MCP_URL}/love",
    json={
        "date_of_birth": "1990-05-15",
        "time_of_birth": "10:30",
        "place_of_birth": "Mumbai, India",
        "start_date": today.strftime("%Y-%m-%d"),
        "end_date": six_months.strftime("%Y-%m-%d")
    }
)

predictions = response.json()

print(f"Love Forecast: {predictions['period']}")
print(f"\nBest Months:")
for month in predictions.get('best_months', [])[:3]:
    print(f"  • {month['month']}: {month['rating']}/10")
```

### Example 5: Complete Client Class

```python
import requests
from typing import Dict, Any, Optional

class VedastroMCPClient:
    """Client for Vedastro MCP Server"""
    
    def __init__(self, base_url: str = "http://localhost:8585"):
        self.base_url = base_url
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute any tool by name"""
        response = requests.post(
            f"{self.base_url}/execute",
            json={"tool_name": tool_name, "arguments": arguments}
        )
        return response.json()
    
    def get_birth_chart(self, dob: str, time: str, place: str) -> Dict[str, Any]:
        """Get complete birth chart"""
        response = requests.post(
            f"{self.base_url}/birth-chart",
            json={
                "date_of_birth": dob,
                "time_of_birth": time,
                "place_of_birth": place
            }
        )
        return response.json()
    
    def get_today_prediction(self, dob: str, time: str, place: str) -> Dict[str, Any]:
        """Get today's prediction"""
        response = requests.post(
            f"{self.base_url}/today",
            json={
                "date_of_birth": dob,
                "time_of_birth": time,
                "place_of_birth": place
            }
        )
        return response.json()
    
    def wildcard_query(self, dob: str, time: str, place: str, 
                      query: str, specific_date: Optional[str] = None) -> Dict[str, Any]:
        """Ask specific questions"""
        data = {
            "date_of_birth": dob,
            "time_of_birth": time,
            "place_of_birth": place,
            "query": query
        }
        if specific_date:
            data["specific_date"] = specific_date
        
        response = requests.post(f"{self.base_url}/wildcard", json=data)
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def list_tools(self) -> Dict[str, Any]:
        """List all available tools"""
        response = requests.get(f"{self.base_url}/tools")
        return response.json()

# Usage
client = VedastroMCPClient()

# Check if server is healthy
health = client.health_check()
print(f"MCP Server: {health['mcp_server']}")
print(f"API Server: {health['vedastro_api']}")

# Get birth chart
chart = client.get_birth_chart("1990-05-15", "10:30", "Mumbai, India")
print(f"\nAscendant: {chart['ascendant']['sign']}")

# Ask a question
result = client.wildcard_query(
    "1990-05-15", "10:30", "Mumbai, India",
    "Should I change jobs in December?"
)
print(f"\nSuccess Probability: {result.get('success_probability', {}).get('percentage')}%")
```

### Example 6: Using curl Commands

```bash
# List all tools
curl http://localhost:8585/tools | jq

# Get today's prediction
curl -X POST http://localhost:8585/today \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India"
  }' | jq

# Weekly forecast
curl -X POST http://localhost:8585/weekly \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India"
  }' | jq '.weekly_rating'

# Career predictions for 6 months
curl -X POST http://localhost:8585/career \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India",
    "start_date": "2024-11-01",
    "end_date": "2025-04-30"
  }' | jq '.monthly_predictions[] | {month, rating: .overall_rating}'
```

---

## 📊 All Available Endpoints

### Main Vedastro API (Port 8087)

#### Chart Endpoints
- `POST /chart/complete` - Complete birth chart
- `POST /chart/quick` - Quick essentials

#### Time-Based Predictions
- `POST /predictions/today` - Today's forecast
- `POST /predictions/week` - 7-day forecast
- `POST /predictions/month` - Current month
- `POST /predictions/quarter` - 3-month forecast
- `POST /predictions/yearly` - 12-month forecast

#### Area-Specific Predictions
- `POST /predictions/love` - Love & relationships (up to 12 months)
- `POST /predictions/health` - Health & wellness (up to 12 months)
- `POST /predictions/career` - Career & professional (up to 12 months)
- `POST /predictions/wealth` - Financial & wealth (up to 12 months)

#### Wildcard
- `POST /predictions/wildcard` - Specific event analysis

### MCP Server (Port 8585)

#### Server Management
- `GET /` - Server information
- `GET /health` - Health check (both services)
- `GET /tools` - List all available tools
- `GET /docs` - Interactive Swagger documentation

#### Tool Execution
- `POST /execute` - Execute any tool by name

#### Direct Tool Access
- `POST /birth-chart` - Get birth chart
- `POST /today` - Today's prediction
- `POST /weekly` - Weekly forecast
- `POST /monthly` - Monthly forecast
- `POST /yearly` - Yearly forecast
- `POST /love` - Love predictions
- `POST /career` - Career predictions
- `POST /wealth` - Wealth predictions
- `POST /health` - Health predictions
- `POST /wildcard` - Wildcard queries

---

## 🏗️ Architecture

### Two-Tier System

```
┌──────────────────────────────────────────────────────────┐
│                    External Clients                       │
│  • Python Scripts    • curl Commands    • Web Apps       │
│  • Mobile Apps       • Other Services   • Automation     │
└────────────────┬─────────────────────────┬───────────────┘
                 │                         │
                 │ Port 8585               │ Port 8087
                 │ (MCP Tools)             │ (Direct API)
                 ↓                         ↓
┌─────────────────────────────┐  ┌──────────────────────────┐
│      MCP Server             │  │    Vedastro API          │
│   (Tool Execution)          │→│  (Core Calculations)     │
│                             │  │                          │
│  • Tool management          │  │  • Swiss Ephemeris       │
│  • Request validation       │  │  • Birth charts          │
│  • Response formatting      │  │  • Predictions           │
│  • Health monitoring        │  │  • Transit analysis      │
└─────────────────────────────┘  └──────────────────────────┘
```

### Key Differences

| Feature | Main API (8087) | MCP Server (8585) |
|---------|----------------|-------------------|
| **Purpose** | Core calculations | Tool-based access |
| **Access Pattern** | Direct endpoints | Tool execution model |
| **Response Format** | Raw data | Tool execution wrapper |
| **Use Case** | Integration | Flexible tool calling |
| **Documentation** | `/docs` | `/docs` + `/tools` |

---

## 🧪 Testing

### Automated Test Script

Run the complete test suite:

```bash
# Test both API and MCP server
python test_mcp_server.py
```

The test script will:
1. Check MCP server health
2. List all available tools
3. Test tool execution
4. Test direct endpoints
5. Test wildcard queries
6. Test area-specific predictions

### Manual Testing

```bash
# 1. Check if services are running
sudo docker compose ps

# 2. Test main API
curl http://localhost:8087/

# 3. Test MCP server
curl http://localhost:8585/

# 4. Check MCP health
curl http://localhost:8585/health

# 5. List MCP tools
curl http://localhost:8585/tools | jq '.tools[].name'

# 6. Test a simple prediction
curl -X POST http://localhost:8585/today \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India"
  }' | jq '.prediction.overall_rating'
```

### Interactive Testing

Open in your browser:
- **Main API**: http://localhost:8087/docs
- **MCP Server**: http://localhost:8585/docs

Both provide interactive Swagger UI for testing all endpoints.

---

## 📦 Project Structure

```
vedastro/
├── app.py                      # Main FastAPI application (port 8087)
├── mcp_server.py              # Standalone MCP server (port 8585)
├── predictions.py              # Prediction engine & calculations
├── local_calculate.py          # Core astrology calculations
├── test_new_endpoints.py       # API tests
├── test_mcp_server.py         # MCP server tests
│
├── requirements.txt            # Main API dependencies
├── requirements.mcp.txt        # MCP server dependencies
│
├── docker-compose.yml          # Multi-container orchestration
├── Dockerfile                  # Main API container
├── Dockerfile.mcp             # MCP server container
│
├── README.md                  # This file
├── API_DOCUMENTATION.md        # Complete API reference
├── UPDATE_SUMMARY.md          # Version history
│
├── ephe/                      # Swiss Ephemeris data files
├── logs/                      # Application logs (auto-created)
└── __pycache__/              # Python cache
```

---

## 🔧 Technical Details

### Core Technologies

**Main API:**
- FastAPI (Python web framework)
- Swiss Ephemeris (astronomical calculations)
- Uvicorn (ASGI server)
- Pydantic (data validation)

**MCP Server:**
- FastAPI (HTTP server)
- httpx (async HTTP client)
- Pydantic (request/response models)

**Infrastructure:**
- Docker & Docker Compose
- Bridge networking (internal)
- Health checks on both services

### Performance

| Operation | Main API | MCP Server (Total) |
|-----------|----------|-------------------|
| Birth Chart | 1-2s | 1.5-2.5s |
| Today's Prediction | 1-3s | 1.5-3.5s |
| Weekly Forecast | 2-5s | 2.5-5.5s |
| Monthly Forecast | 3-8s | 3.5-8.5s |
| Yearly Forecast | 10-30s | 10.5-30.5s |
| Wildcard Query | 5-15s | 5.5-15.5s |

*MCP Server adds ~0.5-1 second overhead for request forwarding*

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Complete reset
sudo docker compose down -v
sudo docker compose up -d --build

# Check status
sudo docker compose ps

# View logs
sudo docker compose logs -f
```

### Port Already in Use

```bash
# Check what's using the ports
sudo lsof -i :8087  # Main API
sudo lsof -i :8585  # MCP Server

# Kill the process
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
```

### MCP Server Not Responding

```bash
# Check container status
sudo docker compose ps vedastro-mcp

# View logs
sudo docker compose logs vedastro-mcp

# Restart service
sudo docker compose restart vedastro-mcp

# Test connectivity
curl http://localhost:8585/health
```

### Connection Between Services Failed

```bash
# Test from MCP container to API
sudo docker exec vedastro-vedastro-mcp-1 curl http://vedastro-api:8087/

# Check network
sudo docker network inspect vedastro_vedastro-network

# Rebuild if needed
sudo docker compose down
sudo docker compose up -d --build
```

### Slow Predictions

This is normal behavior:
- 24-month predictions: 10-30 seconds
- Yearly predictions: 10-30 seconds
- Wildcard queries: 5-15 seconds
- First calculation is slower (ephemeris loading)

### API Returns Errors

```bash
# Check API logs
sudo docker compose logs vedastro-api

# Test API directly
curl http://localhost:8087/

# Verify data format
curl -X POST http://localhost:8087/chart/quick \
  -H "Content-Type: application/json" \
  -d '{
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India"
  }'
```

---

## 🌟 Key Features Summary

| Feature | Description |
|---------|-------------|
| **Standalone MCP Server** | HTTP-based, no Claude Desktop needed |
| **Dual Access** | Direct API + Tool execution layer |
| **10 Prediction Tools** | Birth chart to wildcard queries |
| **Interactive Docs** | Swagger UI on both services |
| **Health Monitoring** | `/health` endpoint for both services |
| **Docker Ready** | One command deployment |
| **Python Client** | Easy integration examples |
| **Flexible Querying** | Generic `/execute` or direct endpoints |

---

## 📜 License

This software uses Swiss Ephemeris which has specific licensing:
- **Free for personal and research use**
- **Commercial use requires license from Astrodienst**
- See: https://www.astro.com/swisseph/

---

## 🚀 Getting Started Checklist

- [ ] Clone/download the repository
- [ ] Run `sudo docker compose up -d --build`
- [ ] Verify services: `sudo docker compose ps`
- [ ] Test main API: `curl http://localhost:8087/`
- [ ] Test MCP server: `curl http://localhost:8585/health`
- [ ] Open docs: http://localhost:8585/docs
- [ ] Run test script: `python test_mcp_server.py`
- [ ] Try example queries from this README
- [ ] Build your integration using the Python examples

---

## 💡 Quick Examples

```bash
# Health check
curl http://localhost:8585/health

# List tools
curl http://localhost:8585/tools | jq '.tools[].name'

# Today's prediction
curl -X POST http://localhost:8585/today \
  -H "Content-Type: application/json" \
  -d '{"date_of_birth":"1990-05-15","time_of_birth":"10:30","place_of_birth":"Mumbai, India"}' \
  | jq '.prediction.overall_rating'

# Wildcard query
curl -X POST http://localhost:8585/wildcard \
  -H "Content-Type: application/json" \
  -d '{"date_of_birth":"1990-05-15","time_of_birth":"10:30","place_of_birth":"Mumbai, India","query":"Should I change jobs in December?"}' \
  | jq '.success_probability'
```

---

**Made with ❤️ using FastAPI, Swiss Ephemeris, and Vedic Astrology wisdom**

**🌟 Star this repo if you find it useful! 🌟**