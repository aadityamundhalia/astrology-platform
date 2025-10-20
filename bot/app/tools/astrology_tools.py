"""Astrology tools for Semantic Kernel with MCP HTTP server"""
from semantic_kernel.functions import kernel_function
from typing import Annotated, Optional
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
        specific_date: str | None = None
    ) -> Annotated[str, "Answer with success probability and recommendation"]:
        """Ask a specific question using wildcard endpoint"""
        data = json.loads(birth_data)
        result = await self.astrology_service.get_wildcard_prediction(
            data, 
            question, 
            specific_date
        )
        return json.dumps(result, indent=2)
    
    @kernel_function(
        name="get_lottery_types",
        description="Get all available Australian lottery types and their configurations"
    )
    async def get_lottery_types(self) -> Annotated[str, "List of available lottery types"]:
        """Get lottery types"""
        result = await self.astrology_service.get_lottery_types()
        return json.dumps(result, indent=2)
    
    @kernel_function(
        name="predict_lottery_numbers",
        description="Predict lucky lottery numbers for a specific Australian lottery type based on birth chart"
    )
    async def predict_lottery_numbers(
        self,
        birth_data: Annotated[str, "JSON string with birth details"],
        lottery_type: Annotated[str, "Lottery type (e.g., 'powerball', 'oz-lotto', 'tatts-lotto')"],
        user_name: str | None = None,
        num_sets: Annotated[int, "Number of sets of numbers to generate (default: 1)"] = 1
    ) -> Annotated[str, "Lottery prediction with lucky numbers"]:
        """Predict lottery numbers for specific type"""
        data = json.loads(birth_data)
        result = await self.astrology_service.predict_lottery_numbers(
            data, 
            lottery_type, 
            user_name,
            num_sets
        )
        return json.dumps(result, indent=2)
    
    @kernel_function(
        name="predict_all_lotteries",
        description="Predict lucky numbers for ALL available Australian lotteries based on birth chart"
    )
    async def predict_all_lotteries(
        self,
        birth_data: Annotated[str, "JSON string with birth details"],
        user_name: str | None = None,
        num_sets: Annotated[int, "Number of sets of numbers to generate for each lottery (default: 1)"] = 1
    ) -> Annotated[str, "Predictions for all lottery types"]:
        """Predict numbers for all lotteries"""
        data = json.loads(birth_data)
        result = await self.astrology_service.predict_all_lotteries(
            data, 
            user_name,
            num_sets
        )
        return json.dumps(result, indent=2)