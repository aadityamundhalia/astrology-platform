#!/usr/bin/env python3
"""Test script to demonstrate enhanced lottery response with timing and confidence"""

import asyncio
import sys
import os

# Set working directory to project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)
sys.path.insert(0, project_root)

from app.agents.rudie_agent import RudieAgent
from app.services.astrology_service import AstrologyService

async def test_enhanced_lottery_response():
    """Test the enhanced lottery response with timing and confidence info"""

    # Initialize services
    astrology_service = AstrologyService()
    rudie_agent = RudieAgent(astrology_service)

    # Test query
    test_query = "Give me oz lotto predictions"

    print("Testing enhanced lottery response with timing and confidence...")
    print("=" * 60)

    try:
        # Get response from agent
        user_context = {
            'name': 'Aditya',
            'date_of_birth': '1987-04-25',
            'time_of_birth': '00:25',
            'place_of_birth': 'Hisar, Haryana',
            'memories': []
        }

        response = await rudie_agent.generate_response(
            user_message=test_query,
            user_context=user_context,
            astrology_service=astrology_service
        )

        print(f"Enhanced Response:\n{response}")
        print("\n" + "=" * 60)
        print("✅ Response includes:")
        print("  • Clear number formatting")
        print("  • Best time to buy advice")
        print("  • Confidence level explanation")
        print("  • Lucky rituals for maximum chances")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_lottery_response())