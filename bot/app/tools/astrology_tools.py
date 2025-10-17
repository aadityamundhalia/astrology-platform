"""Astrology tools for Semantic Kernel with MCP HTTP server"""
from semantic_kernel.functions import kernel_function
from typing import Annotated
import json

class AstrologyTools:
    """Tools for accessing MCP-based astrology predictions"""
    
    def __init__(self, astrology_service):
        self.astrology_service = astrology_service
    
    @kernel_function(
        name="get_today_prediction",
        description="Get today's astrological prediction and overall rating"
    )
    async def get_today_prediction(
        self,
        birth_data: Annotated[str, "JSON string with date_of_birth, time_of_birth, place_of_birth"]
    ) -> Annotated[str, "Today's prediction with rating"]:
        """Get today's prediction"""
        data = json.loads(birth_data)
        result = await self.astrology_service.get_today_prediction(data)
        return json.dumps(result, indent=2)
    
    @kernel_function(
        name="get_weekly_prediction",
        description="Get 7-day weekly forecast"
    )
    async def get_weekly_prediction(
        self,
        birth_data: Annotated[str, "JSON string with birth details"]
    ) -> Annotated[str, "Weekly forecast"]:
        """Get weekly prediction"""
        data = json.loads(birth_data)
        result = await self.astrology_service.get_weekly_prediction(data)
        return json.dumps(result, indent=2)
    
    @kernel_function(
        name="get_love_prediction",
        description="Get love and relationship predictions for the next period"
    )
    async def get_love_prediction(
        self,
        birth_data: Annotated[str, "JSON string with birth details"]
    ) -> Annotated[str, "Love predictions with best months"]:
        """Get love predictions"""
        data = json.loads(birth_data)
        result = await self.astrology_service.get_love_prediction(data)
        return json.dumps(result, indent=2)
    
    @kernel_function(
        name="get_career_prediction",
        description="Get career and professional predictions"
    )
    async def get_career_prediction(
        self,
        birth_data: Annotated[str, "JSON string with birth details"]
    ) -> Annotated[str, "Career predictions"]:
        """Get career predictions"""
        data = json.loads(birth_data)
        result = await self.astrology_service.get_career_prediction(data)
        return json.dumps(result, indent=2)
    
    @kernel_function(
        name="get_wealth_prediction",
        description="Get financial and wealth predictions"
    )
    async def get_wealth_prediction(
        self,
        birth_data: Annotated[str, "JSON string with birth details"]
    ) -> Annotated[str, "Wealth predictions"]:
        """Get wealth predictions"""
        data = json.loads(birth_data)
        result = await self.astrology_service.get_wealth_prediction(data)
        return json.dumps(result, indent=2)
    
    @kernel_function(
        name="ask_specific_question",
        description="Ask a specific question about an event, decision, or timing. Use this for YES/NO/WAIT answers about specific situations like job offers, relationships, purchases, etc."
    )
    async def ask_specific_question(
        self,
        birth_data: Annotated[str, "JSON string with birth details"],
        question: Annotated[str, "The specific question to ask (e.g., 'Should I take this job offer on Dec 15?')"],
        specific_date: Annotated[str, "Optional specific date in YYYY-MM-DD format"] = None
    ) -> Annotated[str, "Answer with success probability and recommendation"]:
        """Ask a specific question using wildcard endpoint"""
        data = json.loads(birth_data)
        result = await self.astrology_service.get_wildcard_prediction(
            data, 
            question, 
            specific_date
        )
        return json.dumps(result, indent=2)