"""Test MCP HTTP server integration"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.astrology_service import AstrologyService

async def test_mcp_integration():
    """Test all MCP endpoints"""
    service = AstrologyService()
    
    print("Testing MCP HTTP Server Integration")
    print("="*60)
    
    # Test data
    birth_data = {
        "date_of_birth": "1990-01-15",
        "time_of_birth": "10:30",
        "place_of_birth": "New Delhi, India"
    }
    
    # Test 1: Health check
    print("\n1. Health Check")
    health = await service.health_check()
    print(f"   MCP Server: {health.get('mcp_server', 'unknown')}")
    print(f"   Vedastro API: {health.get('vedastro_api', 'unknown')}")
    
    # Test 2: Today's prediction
    print("\n2. Today's Prediction (Quick)")
    today = await service.get_today_prediction(birth_data)
    if 'prediction' in today:
        rating = today['prediction'].get('overall_rating', 'N/A')
        print(f"   ✅ Rating: {rating}/10")
    else:
        print(f"   ❌ Error: {today.get('error', 'Unknown')}")
    
    # Test 3: Weekly prediction
    print("\n3. Weekly Prediction (Quick)")
    weekly = await service.get_weekly_prediction(birth_data)
    if 'weekly_rating' in weekly:
        print(f"   ✅ Rating: {weekly['weekly_rating']}/10")
    else:
        print(f"   ❌ Error: {weekly.get('error', 'Unknown')}")
    
    # Test 4: Wildcard query
    print("\n4. Wildcard Query (Medium - ~30-60s)")
    wildcard = await service.get_wildcard_prediction(
        birth_data,
        "Should I change jobs in December 2024?"
    )
    if 'success_probability' in wildcard:
        prob = wildcard['success_probability']
        print(f"   ✅ Success: {prob.get('percentage', 'N/A')}%")
        print(f"   ✅ Rating: {prob.get('rating', 'N/A')}")
    else:
        print(f"   ❌ Error: {wildcard.get('error', 'Unknown')}")
    
    # Test 5: Love prediction (6 months) - WITH NORMALIZATION
    print("\n5. Love Prediction - 6 months (Long - ~60-120s)")
    print("   ⏳ This may take 1-2 minutes...")
    love = await service.get_love_prediction(birth_data, months=6)
    
    if 'error' in love:
        print(f"   ❌ Error: {love['error']}")
        if 'timeout' in love:
            print(f"   ⚠️ Timed out after {love['timeout']}s")
    elif 'period' in love:
        print(f"   ✅ Period: {love['period']}")
        print(f"   ✅ Average Rating: {love.get('average_rating', 'N/A')}/10")
        print(f"   ✅ Trend: {love.get('trend', 'N/A')}")
        if 'best_months' in love:
            best = love['best_months'][:3]  # Show top 3
            print(f"   ✅ Best Months ({len(love['best_months'])} total):")
            for month in best:
                print(f"      • {month['month']}: {month['rating']}/10")
    else:
        print(f"   ⚠️ Unexpected response format")
        print(f"   Keys: {list(love.keys())}")
    
    # Test 6: Career prediction (3 months) - WITH NORMALIZATION
    print("\n6. Career Prediction - 3 months (Medium - ~30-60s)")
    career = await service.get_career_prediction(birth_data, months=3)
    
    if 'error' in career:
        print(f"   ❌ Error: {career['error']}")
    elif 'period' in career:
        print(f"   ✅ Period: {career['period']}")
        print(f"   ✅ Average Rating: {career.get('average_rating', 'N/A')}/10")
        print(f"   ✅ Trend: {career.get('trend', 'N/A')}")
        if 'monthly_predictions' in career:
            print(f"   ✅ Got {len(career['monthly_predictions'])} months of detailed data")
    else:
        print(f"   ⚠️ Unexpected response format")
    
    # Test 7: Lottery Types
    print("\n7. Lottery Types (Quick)")
    lottery_types = await service.get_lottery_types()
    if 'error' in lottery_types:
        print(f"   ❌ Error: {lottery_types['error']}")
    elif isinstance(lottery_types, list):
        print(f"   ✅ Found {len(lottery_types)} lottery types")
        for lottery in lottery_types[:3]:  # Show first 3
            print(f"      • {lottery.get('name', 'Unknown')}")
    else:
        print(f"   ⚠️ Unexpected response format")
        print(f"   Type: {type(lottery_types)}")
    
    # Test 8: Lottery Prediction (Medium - ~30-60s)
    print("\n8. Lottery Prediction - Powerball (Medium - ~30-60s)")
    lottery_pred = await service.predict_lottery_numbers(
        birth_data, 
        "powerball",
        "Test User"
    )
    if 'error' in lottery_pred:
        print(f"   ❌ Error: {lottery_pred['error']}")
    elif 'lottery_type' in lottery_pred:
        print(f"   ✅ Lottery: {lottery_pred['lottery_type']}")
        if 'numbers' in lottery_pred:
            numbers = lottery_pred['numbers']
            print(f"   ✅ Numbers: {numbers.get('main_numbers', [])}")
            print(f"   ✅ Powerball: {numbers.get('powerball', 'N/A')}")
    else:
        print(f"   ⚠️ Unexpected response format")
    
    # Test 9: All Lotteries Prediction (Long - ~60-120s)
    print("\n9. All Lotteries Prediction (Long - ~60-120s)")
    print("   ⏳ This may take 1-2 minutes...")
    all_lotteries = await service.predict_all_lotteries(birth_data, "Test User")
    
    if 'error' in all_lotteries:
        print(f"   ❌ Error: {all_lotteries['error']}")
        if 'timeout' in all_lotteries:
            print(f"   ⚠️ Timed out after {all_lotteries['timeout']}s")
    elif isinstance(all_lotteries, list):
        print(f"   ✅ Got predictions for {len(all_lotteries)} lotteries")
        for lottery in all_lotteries[:2]:  # Show first 2
            lotto_type = lottery.get('lottery_type', 'Unknown')
            numbers = lottery.get('numbers', {})
            main_nums = numbers.get('main_numbers', [])
            print(f"      • {lotto_type}: {main_nums}")
    else:
        print(f"   ⚠️ Unexpected response format")
        print(f"   Keys: {list(all_lotteries.keys()) if isinstance(all_lotteries, dict) else 'Not dict'}")
    
    print("\n" + "="*60)
    print("\n✅ All Tests Complete!")
    print("\nTest Summary:")
    print("  ✅ Quick predictions: <30s (today, weekly, lottery types)")
    print("  ⏳ Medium predictions: 30-60s (wildcard, monthly, single lottery)")
    print("  ⏰ Long predictions: 60-120s (love, career, wealth, health, all lotteries)")
    print("\n💡 Tip: Limit months parameter to 3-6 for faster responses")
    print("💡 Normalized responses now have consistent structure!")

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())