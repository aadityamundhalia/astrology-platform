"""
Test script for Standalone MCP Server
Demonstrates all available endpoints and tools
"""

import requests
import json
from datetime import datetime

# Configuration
MCP_SERVER_URL = "http://localhost:8585"

# Test birth data
TEST_DATA = {
    "date_of_birth": "1990-05-15",
    "time_of_birth": "10:30",
    "place_of_birth": "Mumbai, India"
}


def print_separator(title):
    """Print a nice separator"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_health_check():
    """Test health check endpoint"""
    print_separator("Testing Health Check")
    
    response = requests.get(f"{MCP_SERVER_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_list_tools():
    """Test listing available tools"""
    print_separator("Listing Available Tools")
    
    response = requests.get(f"{MCP_SERVER_URL}/tools")
    print(f"Status Code: {response.status_code}")
    
    tools = response.json()["tools"]
    print(f"Found {len(tools)} tools:\n")
    
    for tool in tools:
        print(f"  • {tool['name']}")
        print(f"    Category: {tool['category']}")
        print(f"    Description: {tool['description']}")
        print()


def test_execute_tool():
    """Test executing a tool via /execute endpoint"""
    print_separator("Testing Tool Execution (via /execute)")
    
    payload = {
        "tool_name": "get_today_prediction",
        "arguments": TEST_DATA
    }
    
    response = requests.post(f"{MCP_SERVER_URL}/execute", json=payload)
    print(f"Status Code: {response.status_code}")
    
    result = response.json()
    if result["success"]:
        print("✅ Tool executed successfully!")
        print(f"\nToday's Rating: {result['data']['prediction']['overall_rating']}/10")
        print(f"Date: {result['data']['date']}")
    else:
        print(f"❌ Error: {result['error']}")


def test_direct_endpoints():
    """Test direct convenience endpoints"""
    print_separator("Testing Direct Endpoints")
    
    # Test today's prediction
    print("1. Today's Prediction:")
    response = requests.post(f"{MCP_SERVER_URL}/today", json=TEST_DATA)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Rating: {data['prediction']['overall_rating']}/10")
        print(f"   Summary: {data['prediction']['summary'][:100]}...")
    
    print()
    
    # Test birth chart
    print("2. Birth Chart:")
    response = requests.post(f"{MCP_SERVER_URL}/birth-chart", json=TEST_DATA)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Ascendant: {data['ascendant']['sign']}")
        print(f"   Moon Sign: {data['planets']['Moon']['sign']}")
        print(f"   Sun Sign: {data['planets']['Sun']['sign']}")


def test_wildcard_query():
    """Test wildcard prediction"""
    print_separator("Testing Wildcard Prediction")
    
    wildcard_data = {
        **TEST_DATA,
        "query": "I have a job interview on December 15th, 2024. How will it go?"
    }
    
    response = requests.post(f"{MCP_SERVER_URL}/wildcard", json=wildcard_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Query: {wildcard_data['query']}")
        print(f"\nSuccess Probability: {data.get('success_probability', {}).get('percentage', 'N/A')}%")
        print(f"Rating: {data.get('success_probability', {}).get('rating', 'N/A')}")


def test_love_prediction():
    """Test love prediction with date range"""
    print_separator("Testing Love Prediction (6 months)")
    
    love_data = {
        **TEST_DATA,
        "start_date": "2024-11-01",
        "end_date": "2025-04-30"
    }
    
    response = requests.post(f"{MCP_SERVER_URL}/love", json=love_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Love prediction generated!")
        print(f"\nPeriod: {data.get('period', 'N/A')}")
        
        if 'monthly_predictions' in data:
            print(f"\nMonthly breakdown:")
            for month in data['monthly_predictions'][:3]:  # Show first 3 months
                print(f"  • {month['month']}: Rating {month['overall_rating']}/10")


def run_all_tests():
    """Run all tests"""
    print("\n" + "🌟"*40)
    print("  Vedic Astrology MCP Server - Test Suite")
    print("🌟"*40)
    
    try:
        # Check if server is running
        response = requests.get(MCP_SERVER_URL, timeout=2)
        if response.status_code != 200:
            print(f"\n❌ MCP Server not responding at {MCP_SERVER_URL}")
            print("   Make sure the server is running: docker compose up -d")
            return
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to MCP Server at {MCP_SERVER_URL}")
        print("   Make sure the server is running: docker compose up -d")
        return
    
    # Run tests
    test_health_check()
    test_list_tools()
    test_execute_tool()
    test_direct_endpoints()
    test_wildcard_query()
    test_love_prediction()
    
    print_separator("All Tests Completed! ✅")
    print(f"\nAccess interactive docs at: {MCP_SERVER_URL}/docs")


if __name__ == "__main__":
    run_all_tests()