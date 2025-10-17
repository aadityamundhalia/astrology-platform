#!/usr/bin/env python3
"""
Test script for new enhanced prediction endpoints
Tests 24-month predictions and wildcard endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80 + "\n")

def test_love_predictions():
    """Test 24-month love predictions"""
    print_section("TEST 1: Love Predictions (24 Months)")
    
    data = {
        "date_of_birth": "1990-05-15",
        "time_of_birth": "10:30",
        "place_of_birth": "Mumbai, India"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predictions/love", json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Area: {result['area']}")
            print(f"📅 Period: {result['prediction_period']}")
            print(f"⭐ Average Rating: {result['overview']['average_rating']}/10")
            print(f"📈 Trend: {result['overview']['trend']}")
            print(f"\n🌟 Best Months:")
            for month in result['overview']['best_months'][:3]:
                print(f"   - {month['month']}: {month['rating']}/10")
            print(f"\n⚠️  Challenging Months:")
            for month in result['overview']['challenging_months'][:3]:
                print(f"   - {month['month']}: {month['rating']}/10")
            print(f"\n📊 Total months predicted: {len(result['monthly_predictions'])}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_career_predictions():
    """Test 24-month career predictions"""
    print_section("TEST 2: Career Predictions (24 Months)")
    
    data = {
        "date_of_birth": "1985-08-22",
        "time_of_birth": "14:45",
        "place_of_birth": "New York, USA"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predictions/career", json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Area: {result['area']}")
            print(f"📅 Period: {result['prediction_period']}")
            print(f"⭐ Average Rating: {result['overview']['average_rating']}/10")
            
            # Show sample month
            if result['monthly_predictions']:
                sample = result['monthly_predictions'][0]
                print(f"\n📆 Sample Month: {sample['month']}")
                print(f"   Rating: {sample['rating']}/10 ({sample['quality']})")
                print(f"   Advice: {sample['advice']}")
                print(f"   What to do:")
                for action in sample['what_to_do'][:2]:
                    print(f"      • {action}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_wildcard_date_query():
    """Test wildcard endpoint with date query"""
    print_section("TEST 3: Wildcard - Date Query")
    
    data = {
        "date_of_birth": "1990-05-15",
        "time_of_birth": "10:30",
        "place_of_birth": "London, UK",
        "query": "I'm going on a date on December 20th 2024, what are my chances to get lucky?"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predictions/wildcard", json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"🔍 Query: {result['query']}")
            print(f"📅 Event Date: {result['event_date']['full_date']}")
            print(f"🎯 Area: {result['area_of_concern']}")
            print(f"🎲 Success Probability: {result['success_probability']['percentage']}%")
            print(f"📊 Rating: {result['success_probability']['rating']}")
            print(f"💡 Interpretation: {result['success_probability']['interpretation'][:100]}...")
            
            print(f"\n⏰ Best Time of Day:")
            for time_slot in result['best_time_of_day'][:2]:
                print(f"   {time_slot['time_range']} - {time_slot['period']}")
            
            print(f"\n💬 Specific Advice:")
            for advice in result['specific_advice'][:3]:
                print(f"   • {advice}")
            
            print(f"\n🔮 Remedies:")
            for remedy in result['remedies'][:3]:
                print(f"   • {remedy}")
            
            print(f"\n🍀 Lucky Factors:")
            print(f"   Colors: {', '.join(result['lucky_factors']['colors'][:3])}")
            print(f"   Direction: {result['lucky_factors']['direction']}")
            print(f"   Gemstone: {result['lucky_factors']['gemstone']}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_wildcard_job_query():
    """Test wildcard endpoint with job query"""
    print_section("TEST 4: Wildcard - Job Security Query")
    
    data = {
        "date_of_birth": "1988-03-10",
        "time_of_birth": "09:15",
        "place_of_birth": "San Francisco, USA",
        "query": "My company is going through redundancy in December 2025, what are my chances to be safe?",
        "specific_date": "2025-12-15"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predictions/wildcard", json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"🔍 Query: {result['query']}")
            print(f"📅 Event Date: {result['event_date']['full_date']}")
            print(f"🎯 Concern: {result['concern_type']}")
            print(f"🎲 Safety Probability: {result['success_probability']['percentage']}%")
            print(f"📊 Rating: {result['success_probability']['rating']}")
            
            print(f"\n⚠️  Risks & Challenges:")
            for risk in result['risks_and_challenges'][:2]:
                print(f"   • {risk['factor']} (Risk Level: {risk['risk_level']})")
                print(f"     {risk['description']}")
            
            print(f"\n🛡️  Mitigation Strategies:")
            for strategy in result['mitigation_strategies'][:3]:
                print(f"   • {strategy}")
            
            print(f"\n✅ Overall Recommendation:")
            print(f"   {result['overall_recommendation']}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_wildcard_safety_query():
    """Test wildcard endpoint with safety query"""
    print_section("TEST 5: Wildcard - Motorcycle Safety Query")
    
    data = {
        "date_of_birth": "1992-11-08",
        "time_of_birth": "18:20",
        "place_of_birth": "Sydney, Australia",
        "query": "I'm buying a motorcycle on November 5th 2024, will I be safe riding it?"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predictions/wildcard", json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"🔍 Query: {result['query']}")
            print(f"📅 Purchase Date: {result['event_date']['full_date']}")
            print(f"🛡️  Safety Rating: {result['success_probability']['rating']}")
            print(f"🎲 Safety Probability: {result['success_probability']['percentage']}%")
            
            print(f"\n⚠️  Safety Risks:")
            for risk in result['risks_and_challenges']:
                print(f"   • {risk['factor']} (Risk Level: {risk['risk_level']})")
            
            print(f"\n🛡️  Safety Strategies:")
            for strategy in result['mitigation_strategies'][:4]:
                print(f"   • {strategy}")
            
            print(f"\n📋 Planetary Positions on Purchase Date:")
            for planet in ['Mars', 'Saturn', 'Sun']:
                if planet in result['planetary_positions_on_date']:
                    pos = result['planetary_positions_on_date'][planet]
                    print(f"   {planet}: {pos['sign']} in House {pos['house']}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_health_predictions():
    """Test 24-month health predictions"""
    print_section("TEST 6: Health Predictions (24 Months)")
    
    data = {
        "date_of_birth": "1995-02-14",
        "time_of_birth": "06:00",
        "place_of_birth": "Tokyo, Japan"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predictions/health", json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Area: {result['area']}")
            print(f"📅 Period: {result['prediction_period']}")
            print(f"⭐ Average Rating: {result['overview']['average_rating']}/10")
            print(f"📈 Trend: {result['overview']['trend']}")
            
            # Show month with best dates
            if result['monthly_predictions']:
                sample = result['monthly_predictions'][0]
                if sample.get('best_dates'):
                    print(f"\n🌟 Best Dates in {sample['month']}:")
                    for date in sample['best_dates'][:2]:
                        print(f"   • {date['full_date']} (Score: {date['quality_score']}/10)")
                        print(f"     Moon: {date['moon_sign']} - {date['moon_nakshatra']}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("\n" + "🌟"*40)
    print("  VEDIC ASTROLOGY API - NEW ENDPOINTS TEST")
    print("🌟"*40)
    print(f"\nStarting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target API: {BASE_URL}")
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API is running!")
        else:
            print("⚠️  API responded but docs not accessible")
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        print("   Please start the API first: python app.py")
        return
    
    # Run tests
    tests = [
        test_love_predictions,
        test_career_predictions,
        test_wildcard_date_query,
        test_wildcard_job_query,
        test_wildcard_safety_query,
        test_health_predictions
    ]
    
    for test_func in tests:
        try:
            test_func()
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
    
    print_section("TEST SUMMARY")
    print("✅ All tests completed!")
    print("\n📚 For detailed documentation, see: API_DOCUMENTATION.md")
    print("🔗 Interactive API docs: http://localhost:8000/docs")
    print("\n" + "🌟"*40 + "\n")

if __name__ == "__main__":
    main()
