#!/usr/bin/env python3
"""
Test script for new horoscope endpoints
"""

import requests
import json

# API base URL
BASE_URL = "http://192.168.0.200:8087"

# Test birth data
test_data = {
    "date_of_birth": "1987-04-25",
    "time_of_birth": "00:25",
    "place_of_birth": "Hisar, Haryana"
}

def test_daily_horoscope():
    """Test daily horoscope endpoint"""
    print("\n" + "="*80)
    print("TESTING: Daily Horoscope Endpoint")
    print("="*80)
    
    url = f"{BASE_URL}/horoscope/daily"
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\n✅ Status: {response.status_code}")
        print(f"\n📅 Date: {result.get('date')} ({result.get('day')})")
        print(f"🌙 Moon Sign: {result.get('moon_sign')}")
        print(f"⭐ Ascendant: {result.get('ascendant')}")
        print(f"📊 Overall Rating: {result.get('overall_rating')}/10")
        print(f"😊 Mood: {result.get('mood')}")
        print(f"⚡ Energy Level: {result.get('energy_level')}")
        print(f"\n💡 Daily Advice: {result.get('daily_advice')}")
        
        print(f"\n🔮 Key Influences:")
        for influence in result.get('key_influences', []):
            print(f"   • {influence}")
        
        print(f"\n🎯 Areas of Focus:")
        print(f"   Favorable: {', '.join(result.get('areas_of_focus', {}).get('favorable', []))}")
        print(f"   Caution: {', '.join(result.get('areas_of_focus', {}).get('caution', []))}")
        
        lucky = result.get('lucky_elements', {})
        print(f"\n🍀 Lucky Elements:")
        print(f"   Color: {lucky.get('color')}")
        print(f"   Numbers: {lucky.get('numbers')}")
        print(f"   Time: {lucky.get('time')}")
        
        print("\n✅ Daily horoscope test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_weekly_horoscope():
    """Test weekly horoscope endpoint"""
    print("\n" + "="*80)
    print("TESTING: Weekly Horoscope Endpoint")
    print("="*80)
    
    url = f"{BASE_URL}/horoscope/weekly"
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\n✅ Status: {response.status_code}")
        print(f"\n📅 Week Period: {result.get('week_period')}")
        print(f"🌙 Moon Sign: {result.get('moon_sign')}")
        print(f"⭐ Ascendant: {result.get('ascendant')}")
        print(f"📊 Overall Rating: {result.get('overall_rating')}/10")
        print(f"\n📝 Week Summary: {result.get('week_summary')}")
        
        print(f"\n🎯 Weekly Themes:")
        for theme in result.get('weekly_themes', []):
            print(f"   • {theme}")
        
        print(f"\n🌟 Key Transits:")
        transits = result.get('key_transits', {})
        for planet, position in transits.items():
            print(f"   {planet.title()}: {position}")
        
        print(f"\n📆 Best Days: {', '.join(result.get('best_days', []))}")
        
        print(f"\n🎭 Areas to Focus:")
        areas = result.get('areas_to_focus', {})
        for area, rating in areas.items():
            print(f"   {area.title()}: {rating}/10")
        
        print(f"\n📅 Daily Highlights:")
        for day in result.get('daily_highlights', [])[:3]:
            print(f"   {day['day']}: {day['moon_transit']} - {day['nakshatra']} ({day['quality']})")
        
        print("\n✅ Weekly horoscope test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_monthly_horoscope():
    """Test monthly horoscope endpoint"""
    print("\n" + "="*80)
    print("TESTING: Monthly Horoscope Endpoint")
    print("="*80)
    
    url = f"{BASE_URL}/horoscope/monthly"
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\n✅ Status: {response.status_code}")
        print(f"\n📅 Month: {result.get('month')}")
        print(f"📆 Period: {result.get('period')}")
        print(f"🌙 Moon Sign: {result.get('moon_sign')}")
        print(f"⭐ Ascendant: {result.get('ascendant')}")
        print(f"📊 Overall Rating: {result.get('overall_rating')}/10")
        print(f"\n📝 Month Summary: {result.get('month_summary')}")
        
        print(f"\n🎯 Key Themes:")
        for theme in result.get('key_themes', []):
            print(f"   • {theme}")
        
        print(f"\n🌟 Major Transits:")
        transits = result.get('major_transits', {})
        for planet, data in transits.items():
            print(f"   {planet.title()}: {data.get('position')} - {data.get('effect')}")
        
        retrograde = result.get('retrograde_planets', [])
        if retrograde:
            print(f"\n⏮️  Retrograde Planets: {', '.join(retrograde)}")
        
        print(f"\n📅 Key Dates:")
        for date_info in result.get('key_dates', []):
            print(f"   {date_info['date']}: {date_info['significance']}")
        
        print(f"\n🎭 Areas Forecast:")
        areas = result.get('areas_forecast', {})
        for area, data in areas.items():
            print(f"\n   {area.title()}:")
            print(f"      Rating: {data.get('rating')}/10")
            print(f"      Advice: {data.get('advice')}")
        
        print("\n✅ Monthly horoscope test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("VEDIC ASTROLOGY API - HOROSCOPE ENDPOINTS TEST")
    print("="*80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test Data: {test_data}")
    
    results = {
        "Daily Horoscope": test_daily_horoscope(),
        "Weekly Horoscope": test_weekly_horoscope(),
        "Monthly Horoscope": test_monthly_horoscope()
    }
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests PASSED!")
    else:
        print("\n⚠️  Some tests FAILED")


if __name__ == "__main__":
    main()
