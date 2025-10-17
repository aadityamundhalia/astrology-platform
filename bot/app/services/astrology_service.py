"""Service for making astrology predictions using MCP HTTP server"""
import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class AstrologyService:
    def __init__(self):
        # Use MCP server URL instead of raw API
        self.base_url = settings.astrology_api_url.replace(':8087', ':8585')  # Switch to MCP port
        # Different timeouts for different prediction types
        self.quick_timeout = 30.0  # For today, weekly
        self.medium_timeout = 60.0  # For monthly, quarterly
        self.long_timeout = 120.0  # For yearly, love, career, wealth, health
        
    def _normalize_area_prediction(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize area-specific predictions (love, career, wealth, health)
        to a consistent format
        """
        if 'error' in response:
            return response
        
        # If already normalized, return as-is
        if 'period' in response:
            return response
        
        # Normalize MCP server response format
        normalized = {
            'area': response.get('area', 'unknown'),
            'period': response.get('prediction_period', 'Unknown period'),
            'generated_at': response.get('generated_at'),
            'monthly_predictions': response.get('monthly_predictions', []),
            'birth_chart_summary': response.get('birth_chart_summary', {})
        }
        
        # Extract overview data
        overview = response.get('overview', {})
        if overview:
            normalized['average_rating'] = overview.get('average_rating')
            normalized['trend'] = overview.get('trend')
            normalized['best_months'] = overview.get('best_months', [])
            normalized['challenging_months'] = overview.get('challenging_months', [])
        
        return normalized
        
    async def _make_request(self, endpoint: str, birth_data: Dict[str, Any], 
                           timeout: float = None) -> Dict[str, Any]:
        """Make HTTP request to MCP server"""
        if timeout is None:
            timeout = self.medium_timeout
            
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                logger.info(f"Making MCP request to {endpoint} (timeout: {timeout}s)")
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=birth_data
                )
                
                if response.status_code == 200:
                    logger.info(f"MCP request successful for {endpoint}")
                    return response.json()
                else:
                    logger.error(f"MCP request failed: {response.status_code} - {response.text}")
                    return {"error": f"HTTP {response.status_code}", "details": response.text[:200]}
                    
        except httpx.TimeoutException:
            logger.error(f"MCP request timed out for {endpoint} after {timeout}s")
            return {"error": "Request timed out", "timeout": timeout}
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to MCP server: {e}")
            return {"error": "Cannot connect to MCP server", "details": str(e)}
        except Exception as e:
            logger.error(f"MCP request error: {e}")
            return {"error": str(e)}
    
    async def get_birth_chart(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete birth chart"""
        return await self._make_request("/birth-chart", birth_data, self.quick_timeout)
    
    async def get_today_prediction(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get today's prediction"""
        return await self._make_request("/today", birth_data, self.quick_timeout)
    
    async def get_weekly_prediction(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get weekly forecast"""
        return await self._make_request("/weekly", birth_data, self.quick_timeout)
    
    async def get_current_month_prediction(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current month prediction"""
        return await self._make_request("/monthly", birth_data, self.medium_timeout)
    
    async def get_quarterly_prediction(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get 3-month forecast"""
        today = datetime.now()
        three_months = today + timedelta(days=90)
        
        birth_data_with_range = {
            **birth_data,
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": three_months.strftime("%Y-%m-%d")
        }
        return await self._make_request("/yearly", birth_data_with_range, self.long_timeout)
    
    async def get_yearly_prediction(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get yearly forecast"""
        return await self._make_request("/yearly", birth_data, self.long_timeout)
    
    async def get_love_prediction(self, birth_data: Dict[str, Any], months: int = 6) -> Dict[str, Any]:
        """
        Get love & relationship predictions
        
        Args:
            birth_data: User's birth information
            months: Number of months to predict (default 6, max 24)
        """
        today = datetime.now()
        end_date = today + timedelta(days=30 * months)
        
        birth_data_with_range = {
            **birth_data,
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        result = await self._make_request("/love", birth_data_with_range, self.long_timeout)
        return self._normalize_area_prediction(result)
    
    async def get_career_prediction(self, birth_data: Dict[str, Any], months: int = 6) -> Dict[str, Any]:
        """
        Get career predictions
        
        Args:
            birth_data: User's birth information
            months: Number of months to predict (default 6, max 24)
        """
        today = datetime.now()
        end_date = today + timedelta(days=30 * months)
        
        birth_data_with_range = {
            **birth_data,
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        result = await self._make_request("/career", birth_data_with_range, self.long_timeout)
        return self._normalize_area_prediction(result)
    
    async def get_wealth_prediction(self, birth_data: Dict[str, Any], months: int = 6) -> Dict[str, Any]:
        """
        Get wealth & financial predictions
        
        Args:
            birth_data: User's birth information
            months: Number of months to predict (default 6, max 24)
        """
        today = datetime.now()
        end_date = today + timedelta(days=30 * months)
        
        birth_data_with_range = {
            **birth_data,
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        result = await self._make_request("/wealth", birth_data_with_range, self.long_timeout)
        return self._normalize_area_prediction(result)
    
    async def get_health_prediction(self, birth_data: Dict[str, Any], months: int = 6) -> Dict[str, Any]:
        """
        Get health & wellness predictions
        
        Args:
            birth_data: User's birth information
            months: Number of months to predict (default 6, max 24)
        """
        today = datetime.now()
        end_date = today + timedelta(days=30 * months)
        
        birth_data_with_range = {
            **birth_data,
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        result = await self._make_request("/health", birth_data_with_range, self.long_timeout)
        return self._normalize_area_prediction(result)
    
    async def get_wildcard_prediction(self, birth_data: Dict[str, Any], query: str, 
                                     specific_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get specific event prediction based on natural language query
        
        Args:
            birth_data: User's birth information
            query: Natural language question (e.g., "Should I change jobs in December?")
            specific_date: Optional specific date for the event
        """
        wildcard_data = {**birth_data, "query": query}
        if specific_date:
            wildcard_data["specific_date"] = specific_date
            
        return await self._make_request("/wildcard", wildcard_data, self.medium_timeout)
    
    async def get_daily_horoscope(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get daily horoscope (alias for today's prediction)"""
        return await self.get_today_prediction(birth_data)
    
    async def get_weekly_horoscope(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get weekly horoscope"""
        return await self.get_weekly_prediction(birth_data)
    
    async def get_monthly_horoscope(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get monthly horoscope"""
        return await self.get_current_month_prediction(birth_data)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if MCP server is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    return response.json()
                return {"mcp_server": "unhealthy", "status_code": response.status_code}
        except Exception as e:
            return {"mcp_server": "unreachable", "error": str(e)}