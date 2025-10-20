"""
Standalone MCP Server for Vedic Astrology API
HTTP-based server that can work independently or with Claude Desktop
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vedastro-mcp")

# Configuration
VEDASTRO_API_URL = os.environ.get("VEDASTRO_API_URL", "http://vedastro-api:8087")
MCP_PORT = int(os.environ.get("MCP_PORT", "8585"))

# Initialize FastAPI app
app = FastAPI(
    title="Vedic Astrology MCP Server",
    description="Standalone MCP server for astrological calculations",
    version="1.0.0"
)


class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


class ToolResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Helper function to call the Vedic Astrology API
async def call_vedastro_api(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Call the Vedic Astrology API"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{VEDASTRO_API_URL}{endpoint}",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"API call failed: {e}")
            raise


@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "service": "Vedic Astrology MCP Server",
        "version": "1.0.0",
        "status": "running",
        "api_url": VEDASTRO_API_URL,
        "endpoints": {
            "tools": "/tools",
            "execute": "/execute",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if API is reachable
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{VEDASTRO_API_URL}/")
            api_status = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        api_status = f"unhealthy: {str(e)}"
    
    return {
        "mcp_server": "healthy",
        "vedastro_api": api_status,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    return {
        "tools": [
            {
                "name": "get_birth_chart",
                "description": "Get a complete birth chart with planetary positions, houses, and nakshatras",
                "category": "chart",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": []
            },
            {
                "name": "get_today_prediction",
                "description": "Get today's astrological prediction with ratings for love, career, wealth, and health",
                "category": "predictions",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": []
            },
            {
                "name": "get_weekly_prediction",
                "description": "Get 7-day forecast with day-by-day breakdown",
                "category": "predictions",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": []
            },
            {
                "name": "get_monthly_prediction",
                "description": "Get current month's detailed prediction with transit analysis",
                "category": "predictions",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": []
            },
            {
                "name": "get_yearly_prediction",
                "description": "Get 12-month comprehensive forecast",
                "category": "predictions",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": []
            },
            {
                "name": "get_love_prediction",
                "description": "Get love and relationship predictions (up to 12 months)",
                "category": "area_specific",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": ["start_date", "end_date"]
            },
            {
                "name": "get_career_prediction",
                "description": "Get career and professional predictions (up to 12 months)",
                "category": "area_specific",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": ["start_date", "end_date"]
            },
            {
                "name": "get_wealth_prediction",
                "description": "Get wealth and financial predictions (up to 12 months)",
                "category": "area_specific",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": ["start_date", "end_date"]
            },
            {
                "name": "get_health_prediction",
                "description": "Get health and wellness predictions (up to 12 months)",
                "category": "area_specific",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": ["start_date", "end_date"]
            },
            {
                "name": "get_wildcard_prediction",
                "description": "Get precise predictions for specific events with success probability",
                "category": "wildcard",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth", "query"],
                "optional_fields": ["specific_date"]
            },
            {
                "name": "get_lottery_types",
                "description": "Get all available Australian lottery types and configurations",
                "category": "lottery",
                "required_fields": [],
                "optional_fields": []
            },
            {
                "name": "predict_lottery_numbers",
                "description": "Predict lucky lottery numbers for specific Australian lottery",
                "category": "lottery",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth", "lottery_type"],
                "optional_fields": ["user_name", "num_sets"]
            },
            {
                "name": "predict_all_lotteries",
                "description": "Predict lucky numbers for ALL Australian lotteries",
                "category": "lottery",
                "required_fields": ["date_of_birth", "time_of_birth", "place_of_birth"],
                "optional_fields": ["user_name", "num_sets"]
            }
        ]
    }


@app.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute a specific MCP tool"""
    
    # Map tool names to API endpoints
    endpoint_map = {
        "get_birth_chart": "/chart/complete",
        "get_today_prediction": "/predictions/today",
        "get_weekly_prediction": "/predictions/week",
        "get_monthly_prediction": "/predictions/current-month",
        "get_yearly_prediction": "/predictions/yearly",
        "get_love_prediction": "/predictions/love",
        "get_career_prediction": "/predictions/career",
        "get_wealth_prediction": "/predictions/wealth",
        "get_health_prediction": "/predictions/health",
        "get_wildcard_prediction": "/predictions/wildcard",
        "get_lottery_types": "/lottery/types",
        "predict_lottery_numbers": "/lottery/predict",
        "predict_all_lotteries": "/lottery/predict-all",
    }
    
    tool_name = request.tool_name
    endpoint = endpoint_map.get(tool_name)
    
    if not endpoint:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tool: {tool_name}. Use /tools to see available tools."
        )
    
    try:
        logger.info(f"Executing tool: {tool_name} with endpoint: {endpoint}")
        result = await call_vedastro_api(endpoint, request.arguments)
        
        return ToolResponse(
            success=True,
            data=result
        )
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error executing tool {tool_name}: {e}")
        return ToolResponse(
            success=False,
            error=f"API call failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
        return ToolResponse(
            success=False,
            error=str(e)
        )


# Convenience endpoints for direct tool access
@app.post("/birth-chart")
async def get_birth_chart(data: Dict[str, Any]):
    """Direct endpoint for birth chart"""
    result = await execute_tool(ToolRequest(
        tool_name="get_birth_chart",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/today")
async def get_today(data: Dict[str, Any]):
    """Direct endpoint for today's prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="get_today_prediction",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/weekly")
async def get_weekly(data: Dict[str, Any]):
    """Direct endpoint for weekly prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="get_weekly_prediction",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/monthly")
async def get_monthly(data: Dict[str, Any]):
    """Direct endpoint for monthly prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="get_monthly_prediction",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/yearly")
async def get_yearly(data: Dict[str, Any]):
    """Direct endpoint for yearly prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="get_yearly_prediction",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/love")
async def get_love(data: Dict[str, Any]):
    """Direct endpoint for love prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="get_love_prediction",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/career")
async def get_career(data: Dict[str, Any]):
    """Direct endpoint for career prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="get_career_prediction",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/wealth")
async def get_wealth(data: Dict[str, Any]):
    """Direct endpoint for wealth prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="get_wealth_prediction",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/health")
async def get_health(data: Dict[str, Any]):
    """Direct endpoint for health prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="get_health_prediction",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/wildcard")
async def get_wildcard(data: Dict[str, Any]):
    """Direct endpoint for wildcard prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="get_wildcard_prediction",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data

@app.get("/lottery-types")
async def get_lottery_types_mcp():
    """Direct endpoint for lottery types"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{VEDASTRO_API_URL}/lottery/types")
        return response.json()


@app.post("/lottery")
async def predict_lottery_mcp(data: Dict[str, Any]):
    """Direct endpoint for lottery prediction"""
    result = await execute_tool(ToolRequest(
        tool_name="predict_lottery_numbers",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data


@app.post("/lottery-all")
async def predict_all_lotteries_mcp(data: Dict[str, Any]):
    """Direct endpoint for all lottery predictions"""
    result = await execute_tool(ToolRequest(
        tool_name="predict_all_lotteries",
        arguments=data
    ))
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result.data

if __name__ == "__main__":
    logger.info(f"Starting Vedic Astrology MCP Server on port {MCP_PORT}")
    logger.info(f"Connecting to Vedastro API at: {VEDASTRO_API_URL}")
    logger.info(f"Access documentation at: http://localhost:{MCP_PORT}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=MCP_PORT,
        log_level="info"
    )