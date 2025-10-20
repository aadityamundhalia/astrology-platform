#!/usr/bin/env python3
"""Test script to verify lottery name mapping in Rudie agent"""

import asyncio
import sys
import os

# Set working directory to project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)
sys.path.insert(0, project_root)

from app.agents.rudie_agent import RudieAgent
from app.services.astrology_service import AstrologyService

async def test_lottery_mapping():
    """Test that Rudie agent correctly maps lottery names"""

    # Initialize services
    astrology_service = AstrologyService()
    rudie_agent = RudieAgent(astrology_service)

    # Test cases
    test_cases = [
        "Give me 3 sets for oz lotto",
        "Predict 5 sets for oz-lotto",
        "Can you predict powerball numbers for next week?",
        "Give me saturday lotto predictions"
    ]

    print("Testing lottery name mapping in Rudie agent...")
    print("=" * 50)

    for i, test_query in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_query}'")
        print("-" * 30)

        try:
            # Get response from agent
            user_context = {
                'name': 'TestUser',
                'date_of_birth': '1990-01-01',
                'time_of_birth': '12:00',
                'place_of_birth': 'Sydney, Australia',
                'memories': []
            }

            response = await rudie_agent.generate_response(
                user_message=test_query,
                user_context=user_context,
                astrology_service=astrology_service
            )

            print(f"Response: {response[:200]}...")

            # Check if tool was called (this would be in the internal processing)
            # For now, just check the response doesn't contain errors

        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 50)
    print("Test completed. Check the logs above for lottery type mappings.")

if __name__ == "__main__":
    asyncio.run(test_lottery_mapping())