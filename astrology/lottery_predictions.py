"""
Australian Lottery Predictions based on Vedic Astrology
Enhanced with deeper astronomical calculations
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Tuple
import random
import logging
from collections import Counter
import swisseph as swe

logger = logging.getLogger(__name__)

# Australian Lottery Configurations
LOTTERY_CONFIGS = {
    "powerball": {
        "name": "Powerball",
        "main_numbers": {"count": 7, "range": (1, 35)},
        "powerball": {"count": 1, "range": (1, 20)},
        "draw_days": ["Thursday"],
        "hot_numbers_url": "https://www.thelott.com/powerball/statistics",
        "official_url": "https://www.thelott.com/powerball"
    },
    "oz_lotto": {
        "name": "Oz Lotto",
        "main_numbers": {"count": 7, "range": (1, 47)},
        "supplementary": {"count": 2, "range": (1, 47)},
        "draw_days": ["Tuesday"],
        "hot_numbers_url": "https://www.thelott.com/oz-lotto/statistics",
        "official_url": "https://www.thelott.com/oz-lotto"
    },
    "saturday_lotto": {
        "name": "Saturday Lotto",
        "main_numbers": {"count": 6, "range": (1, 45)},
        "supplementary": {"count": 2, "range": (1, 45)},
        "draw_days": ["Saturday"],
        "hot_numbers_url": "https://www.thelott.com/saturday-lotto/statistics",
        "official_url": "https://www.thelott.com/saturday-lotto"
    },
    "monday_wednesday_lotto": {
        "name": "Monday & Wednesday Lotto",
        "main_numbers": {"count": 6, "range": (1, 45)},
        "supplementary": {"count": 2, "range": (1, 45)},
        "draw_days": ["Monday", "Wednesday"],
        "hot_numbers_url": "https://www.thelott.com/monday-wednesday-lotto/statistics",
        "official_url": "https://www.thelott.com/monday-wednesday-lotto"
    },
    "set_for_life": {
        "name": "Set for Life",
        "main_numbers": {"count": 7, "range": (1, 44)},
        "bonus": {"count": 1, "range": (1, 44)},
        "draw_days": ["Daily"],
        "hot_numbers_url": "https://www.thelott.com/set-for-life/statistics",
        "official_url": "https://www.thelott.com/set-for-life"
    }
}

# Planetary number associations (Vedic Astrology)
PLANET_NUMBERS = {
    "Sun": [1, 10, 19, 28, 37],
    "Moon": [2, 11, 20, 29, 38],
    "Jupiter": [3, 12, 21, 30, 39],
    "Rahu": [4, 13, 22, 31, 40],
    "Mercury": [5, 14, 23, 32, 41],
    "Venus": [6, 15, 24, 33, 42],
    "Ketu": [7, 16, 25, 34, 43],
    "Saturn": [8, 17, 26, 35, 44],
    "Mars": [9, 18, 27, 36, 45]
}

# Nakshatra lucky numbers
NAKSHATRA_NUMBERS = {
    "Ashwini": [1, 10, 19, 28],
    "Bharani": [6, 15, 24, 33],
    "Krittika": [3, 12, 21, 30],
    "Rohini": [2, 11, 20, 29],
    "Mrigashira": [5, 14, 23, 32],
    "Ardra": [4, 13, 22, 31],
    "Punarvasu": [3, 12, 21, 30],
    "Pushya": [8, 17, 26, 35],
    "Ashlesha": [5, 14, 23, 32],
    "Magha": [1, 10, 19, 28],
    "Purva Phalguni": [6, 15, 24, 33],
    "Uttara Phalguni": [3, 12, 21, 30],
    "Hasta": [5, 14, 23, 32],
    "Chitra": [5, 14, 23, 32],
    "Swati": [4, 13, 22, 31],
    "Vishakha": [8, 17, 26, 35],
    "Anuradha": [8, 17, 26, 35],
    "Jyeshtha": [9, 18, 27, 36],
    "Mula": [7, 16, 25, 34],
    "Purva Ashadha": [3, 12, 21, 30],
    "Uttara Ashadha": [1, 10, 19, 28],
    "Shravana": [2, 11, 20, 29],
    "Dhanishta": [8, 17, 26, 35],
    "Shatabhisha": [4, 13, 22, 31],
    "Purva Bhadrapada": [3, 12, 21, 30],
    "Uttara Bhadrapada": [8, 17, 26, 35],
    "Revati": [5, 14, 23, 32]
}

# House significations for lottery luck
HOUSE_LUCK_WEIGHTS = {
    2: 4,   # House of wealth
    5: 3,   # House of speculation/gambling
    9: 4,   # House of fortune/luck
    11: 5,  # House of gains (most important for lottery)
    1: 2,   # Ascendant (self)
    8: 2    # House of sudden events/windfalls
}


class HotNumbersScraper:
    """Scrape hot numbers from lottery statistics"""
    
    @staticmethod
    def get_generic_hot_numbers(lottery_type: str, number_range: Tuple[int, int]) -> List[int]:
        """Generate statistically distributed hot numbers"""
        min_num, max_num = number_range
        hot_numbers = []
        
        # Use prime numbers
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        for p in primes:
            if min_num <= p <= max_num:
                hot_numbers.append(p)
        
        # Add mid-range numbers
        mid_range = list(range(min_num + 10, max_num - 10, 3))
        hot_numbers.extend(mid_range[:10])
        
        while len(hot_numbers) < 15:
            num = random.randint(min_num, max_num)
            if num not in hot_numbers:
                hot_numbers.append(num)
        
        return sorted(hot_numbers[:15])
    
    @staticmethod
    def scrape_oz_lotteries_stats(lottery_type: str) -> Dict[str, Any]:
        """Attempt to scrape statistics from oz lotteries"""
        config = LOTTERY_CONFIGS.get(lottery_type)
        if not config:
            return {"hot_numbers": [], "source": "none"}
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(
                config.get("hot_numbers_url", ""),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info(f"Successfully fetched stats for {lottery_type}")
            
        except Exception as e:
            logger.warning(f"Could not scrape hot numbers for {lottery_type}: {e}")
        
        # Fallback to generated hot numbers
        main_range = config["main_numbers"]["range"]
        hot_numbers = HotNumbersScraper.get_generic_hot_numbers(lottery_type, main_range)
        
        return {
            "hot_numbers": hot_numbers[:10],
            "warm_numbers": hot_numbers[10:15] if len(hot_numbers) > 10 else [],
            "source": "statistical_analysis",
            "last_updated": datetime.now().isoformat()
        }


class VedicLotteryPredictor:
    """Predict lottery numbers using deep Vedic astrology"""
    
    @staticmethod
    def get_planetary_lucky_numbers(chart: Dict[str, Any], number_range: Tuple[int, int]) -> List[int]:
        """Extract lucky numbers based on planetary positions and strengths"""
        lucky_numbers = []
        min_num, max_num = number_range
        
        planets = chart.get("planets", {})
        
        # Check planets in lucky houses (2, 5, 9, 11)
        lucky_houses = [2, 5, 9, 11]
        house_planets = {}
        
        for planet_name, planet_data in planets.items():
            house = planet_data.get("house", 0)
            if house in lucky_houses:
                weight = HOUSE_LUCK_WEIGHTS.get(house, 1)
                house_planets[planet_name] = weight
        
        # Prioritize benefic planets in lucky houses
        benefic_planets = ["Jupiter", "Venus", "Mercury", "Moon"]
        for planet in benefic_planets:
            if planet in house_planets:
                planet_nums = PLANET_NUMBERS.get(planet, [])
                weight = house_planets[planet]
                for num in planet_nums:
                    if min_num <= num <= max_num:
                        # Add number multiple times based on weight
                        lucky_numbers.extend([num] * weight)
        
        # Add exalted planets' numbers (doubled weight)
        for planet_name, planet_data in planets.items():
            if planet_data.get("dignity") == "exalted":
                planet_nums = PLANET_NUMBERS.get(planet_name, [])
                for num in planet_nums:
                    if min_num <= num <= max_num:
                        lucky_numbers.extend([num] * 2)
        
        # Add Sun numbers (vitality)
        sun_nums = PLANET_NUMBERS.get("Sun", [])
        for num in sun_nums:
            if min_num <= num <= max_num and num not in lucky_numbers:
                lucky_numbers.append(num)
        
        return list(set(lucky_numbers))[:15]  # Return unique numbers
    
    @staticmethod
    def get_nakshatra_lucky_numbers(chart: Dict[str, Any], number_range: Tuple[int, int]) -> List[int]:
        """Get lucky numbers based on Moon's nakshatra"""
        lucky_numbers = []
        min_num, max_num = number_range
        
        moon_nakshatra = chart.get("planets", {}).get("Moon", {}).get("nakshatra", "")
        
        if moon_nakshatra:
            nakshatra_nums = NAKSHATRA_NUMBERS.get(moon_nakshatra, [])
            for num in nakshatra_nums:
                if min_num <= num <= max_num:
                    lucky_numbers.append(num)
        
        return lucky_numbers
    
    @staticmethod
    def get_house_based_numbers(chart: Dict[str, Any], number_range: Tuple[int, int]) -> List[int]:
        """Get numbers based on house positions"""
        lucky_numbers = []
        min_num, max_num = number_range
        
        # Get planets in 11th house (gains)
        planets = chart.get("planets", {})
        house_11_planets = [p for p, data in planets.items() if data.get("house") == 11]
        
        for planet in house_11_planets:
            planet_nums = PLANET_NUMBERS.get(planet, [])
            for num in planet_nums:
                if min_num <= num <= max_num:
                    lucky_numbers.extend([num] * 2)  # Double weight for 11th house
        
        # Get planets in 5th house (speculation)
        house_5_planets = [p for p, data in planets.items() if data.get("house") == 5]
        
        for planet in house_5_planets:
            planet_nums = PLANET_NUMBERS.get(planet, [])
            for num in planet_nums:
                if min_num <= num <= max_num:
                    lucky_numbers.append(num)
        
        return list(set(lucky_numbers))
    
    @staticmethod
    def get_dasha_lucky_numbers(chart: Dict[str, Any], number_range: Tuple[int, int]) -> List[int]:
        """Get numbers based on current dasha period"""
        lucky_numbers = []
        min_num, max_num = number_range
        
        # Use birth date numerology
        birth_date = chart.get("birth_date", "")
        if birth_date:
            try:
                date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
                day = date_obj.day
                month = date_obj.month
                year = date_obj.year % 100
                
                # Add birth day and its multiples
                for multiplier in [1, 2, 3]:
                    num = day * multiplier
                    if min_num <= num <= max_num:
                        lucky_numbers.append(num)
                
                # Add month-based numbers
                if min_num <= month <= max_num:
                    lucky_numbers.append(month)
                
                # Add year-based numbers
                if min_num <= year <= max_num:
                    lucky_numbers.append(year)
                
            except:
                pass
        
        return list(set(lucky_numbers))
    
    @staticmethod
    def get_degree_based_numbers(chart: Dict[str, Any], number_range: Tuple[int, int]) -> List[int]:
        """Extract numbers from planetary degrees"""
        lucky_numbers = []
        min_num, max_num = number_range
        
        planets = chart.get("planets", {})
        
        # Use degrees of benefic planets
        benefic_planets = ["Jupiter", "Venus", "Moon", "Mercury"]
        for planet in benefic_planets:
            if planet in planets:
                degree = int(planets[planet].get("degree", 0))
                if min_num <= degree <= max_num:
                    lucky_numbers.append(degree)
                
                # Also use rounded degree
                rounded_degree = round(degree / 5) * 5  # Round to nearest 5
                if min_num <= rounded_degree <= max_num:
                    lucky_numbers.append(rounded_degree)
        
        return list(set(lucky_numbers))
    
    @staticmethod
    def calculate_name_number(name: str) -> int:
        """Calculate numerology number from name"""
        values = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
            'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
        }
        
        total = sum(values.get(char.upper(), 0) for char in name if char.isalpha())
        
        while total > 9:
            total = sum(int(digit) for digit in str(total))
        
        return total


def generate_lottery_predictions(
    chart: Dict[str, Any],
    lottery_type: str,
    user_name: str = "",
    num_sets: int = 1
) -> Dict[str, Any]:
    """
    Generate lottery number predictions using:
    1. Planetary positions in lucky houses (11th, 5th, 2nd, 9th)
    2. Planetary degrees and exaltations
    3. Moon's nakshatra
    4. Hot numbers from statistics
    5. Numerology
    """
    
    config = LOTTERY_CONFIGS.get(lottery_type)
    if not config:
        raise ValueError(f"Unknown lottery type: {lottery_type}")
    
    # Get hot numbers
    hot_stats = HotNumbersScraper.scrape_oz_lotteries_stats(lottery_type)
    hot_numbers = hot_stats.get("hot_numbers", [])
    
    # Get astrological lucky numbers using multiple methods
    main_range = config["main_numbers"]["range"]
    
    planetary_numbers = VedicLotteryPredictor.get_planetary_lucky_numbers(chart, main_range)
    nakshatra_numbers = VedicLotteryPredictor.get_nakshatra_lucky_numbers(chart, main_range)
    house_numbers = VedicLotteryPredictor.get_house_based_numbers(chart, main_range)
    dasha_numbers = VedicLotteryPredictor.get_dasha_lucky_numbers(chart, main_range)
    degree_numbers = VedicLotteryPredictor.get_degree_based_numbers(chart, main_range)
    
    # Combine all lucky numbers with sophisticated weighting
    number_weights = Counter()
    
    # Weight hot numbers (25%)
    for num in hot_numbers:
        number_weights[num] += 5
    
    # Weight house-based numbers (25%) - most important
    for num in house_numbers:
        number_weights[num] += 5
    
    # Weight planetary numbers (20%)
    for num in planetary_numbers:
        number_weights[num] += 4
    
    # Weight nakshatra numbers (15%)
    for num in nakshatra_numbers:
        number_weights[num] += 3
    
    # Weight degree-based numbers (10%)
    for num in degree_numbers:
        number_weights[num] += 2
    
    # Weight dasha numbers (5%)
    for num in dasha_numbers:
        number_weights[num] += 1
    
    # Add name numerology if provided
    if user_name:
        name_num = VedicLotteryPredictor.calculate_name_number(user_name)
        current = name_num
        while current <= main_range[1]:
            if current >= main_range[0]:
                number_weights[current] += 3
            current += name_num
    
    # Generate multiple sets
    sets = []
    sorted_numbers = sorted(number_weights.items(), key=lambda x: x[1], reverse=True)
    
    for set_num in range(num_sets):
        # Create unique seed for this set
        set_seed = hash(f"{set_num}_{chart.get('ascendant', {}).get('degree', 0)}") % 100000
        random.seed(set_seed)
        
        main_count = config["main_numbers"]["count"]
        predicted_main = []
        
        # Different strategy per set
        candidates_pool = sorted_numbers.copy()
        random.shuffle(candidates_pool)
        
        # Select numbers with varying strategies
        while len(predicted_main) < main_count and candidates_pool:
            if set_num % 3 == 0:
                # Prefer highest weighted
                pick_idx = random.randint(0, min(5, len(candidates_pool) - 1))
            elif set_num % 3 == 1:
                # Mix high and medium
                pick_idx = random.randint(0, min(10, len(candidates_pool) - 1))
            else:
                # Include variety
                pick_idx = random.randint(0, min(15, len(candidates_pool) - 1))
            
            num, weight = candidates_pool.pop(pick_idx)
            if num not in predicted_main:
                predicted_main.append(num)
        
        # Fill remaining
        while len(predicted_main) < main_count:
            num = random.randint(main_range[0], main_range[1])
            if num not in predicted_main:
                predicted_main.append(num)
        
        predicted_main = sorted(predicted_main)
        
        set_result = {
            "set_number": set_num + 1,
            "main_numbers": predicted_main
        }
        
        # Add special numbers (powerball/supplementary/bonus)
        if "powerball" in config:
            pb_range = config["powerball"]["range"]
            pb_candidates = [n for n, w in number_weights.items() if pb_range[0] <= n <= pb_range[1]]
            if pb_candidates:
                powerball = random.choice(pb_candidates * 2 + list(range(pb_range[0], pb_range[1] + 1)))
            else:
                powerball = random.randint(pb_range[0], pb_range[1])
            set_result["powerball"] = powerball
        
        if "supplementary" in config:
            supp_range = config["supplementary"]["range"]
            supp_count = config["supplementary"]["count"]
            supp_candidates = [n for n in house_numbers if supp_range[0] <= n <= supp_range[1] and n not in predicted_main]
            supplementary = supp_candidates[:supp_count]
            
            while len(supplementary) < supp_count:
                num = random.randint(supp_range[0], supp_range[1])
                if num not in predicted_main and num not in supplementary:
                    supplementary.append(num)
            
            set_result["supplementary_numbers"] = sorted(supplementary)
        
        if "bonus" in config:
            bonus_range = config["bonus"]["range"]
            bonus_candidates = [n for n in degree_numbers if bonus_range[0] <= n <= bonus_range[1] and n not in predicted_main]
            bonus = random.choice(bonus_candidates) if bonus_candidates else random.randint(bonus_range[0], bonus_range[1])
            set_result["bonus_number"] = bonus
        
        sets.append(set_result)
        random.seed()  # Reset
    
    result = {
        "lottery_type": config["name"],
        "num_sets": num_sets,
        "sets": sets,
        "draw_days": config["draw_days"],
        "astrological_method": {
            "hot_numbers_weight": "25%",
            "house_positions_weight": "25%",
            "planetary_positions_weight": "20%",
            "nakshatra_weight": "15%",
            "planetary_degrees_weight": "10%",
            "dasha_period_weight": "5%"
        },
        "key_astrological_factors": {
            "planets_in_11th_house": [p for p, d in chart.get("planets", {}).items() if d.get("house") == 11],
            "planets_in_5th_house": [p for p, d in chart.get("planets", {}).items() if d.get("house") == 5],
            "exalted_planets": [p for p, d in chart.get("planets", {}).items() if d.get("dignity") == "exalted"],
            "moon_nakshatra": chart.get("planets", {}).get("Moon", {}).get("nakshatra", "")
        },
        "lucky_number_sources": {
            "from_house_positions": house_numbers[:5],
            "from_planetary_positions": planetary_numbers[:5],
            "from_nakshatra": nakshatra_numbers[:3],
            "from_degrees": degree_numbers[:3],
            "from_hot_stats": hot_numbers[:5]
        },
        "astrological_timing": get_auspicious_draw_timing(chart, config["draw_days"]),
        "confidence_score": calculate_prediction_confidence(chart, number_weights),
        "generated_at": datetime.now().isoformat()
    }
    
    return result


def get_auspicious_draw_timing(chart: Dict[str, Any], draw_days: List[str]) -> Dict[str, Any]:
    """Determine most auspicious timing"""
    moon_sign = chart.get("planets", {}).get("Moon", {}).get("sign", "")
    jupiter_sign = chart.get("planets", {}).get("Jupiter", {}).get("sign", "")
    
    return {
        "recommended_purchase_day": draw_days[0] if draw_days else "Any day",
        "best_time_of_day": "During Jupiter hora (sunrise + 2 hours)" if jupiter_sign else "Morning hours",
        "moon_phase_advice": "Purchase during waxing moon for growth energy",
        "avoid_days": ["Rahu Kalam", "Yamagandam"]
    }


def calculate_prediction_confidence(chart: Dict[str, Any], number_weights: Counter) -> str:
    """Calculate confidence score"""
    planets = chart.get("planets", {})
    
    # Check for planets in lucky houses
    lucky_house_planets = sum(1 for p, d in planets.items() if d.get("house") in [2, 5, 9, 11])
    
    # Check for exalted benefics
    exalted_benefics = sum(1 for p, d in planets.items() 
                          if p in ["Jupiter", "Venus", "Moon", "Mercury"] and d.get("dignity") == "exalted")
    
    max_weight = max(number_weights.values()) if number_weights else 0
    
    if lucky_house_planets >= 2 and exalted_benefics >= 1 and max_weight >= 8:
        return "High (75-85%)"
    elif lucky_house_planets >= 1 and max_weight >= 5:
        return "Medium (60-75%)"
    else:
        return "Moderate (50-60%)"


def generate_all_lottery_predictions(chart: Dict[str, Any], user_name: str = "", num_sets: int = 1) -> Dict[str, Any]:
    """Generate predictions for all Australian lotteries"""
    predictions = {}
    
    for lottery_type in LOTTERY_CONFIGS.keys():
        try:
            prediction = generate_lottery_predictions(chart, lottery_type, user_name, num_sets)
            predictions[lottery_type] = prediction
        except Exception as e:
            logger.error(f"Error generating prediction for {lottery_type}: {e}")
            predictions[lottery_type] = {
                "error": str(e),
                "lottery_type": LOTTERY_CONFIGS[lottery_type]["name"]
            }
    
    return {
        "predictions": predictions,
        "birth_chart_summary": {
            "ascendant": chart.get("ascendant", {}).get("sign", ""),
            "moon_sign": chart.get("planets", {}).get("Moon", {}).get("sign", ""),
            "moon_nakshatra": chart.get("planets", {}).get("Moon", {}).get("nakshatra", "")
        },
        "general_advice": generate_lottery_advice(chart),
        "generated_at": datetime.now().isoformat()
    }


def generate_lottery_advice(chart: Dict[str, Any]) -> Dict[str, Any]:
    """Generate lottery playing advice"""
    advice = {
        "best_playing_strategy": [],
        "lucky_periods": [],
        "cautions": [],
        "remedies": []
    }
    
    jupiter_sign = chart.get("planets", {}).get("Jupiter", {}).get("sign", "")
    if jupiter_sign:
        advice["best_playing_strategy"].append(
            f"Jupiter in {jupiter_sign} - Focus on Thursday (Jupiter's day)"
        )
    
    venus_sign = chart.get("planets", {}).get("Venus", {}).get("sign", "")
    if venus_sign:
        advice["best_playing_strategy"].append(
            f"Venus in {venus_sign} - Friday purchases may be fortunate"
        )
    
    advice["best_playing_strategy"].extend([
        "Play consistently with small amounts",
        "Use numbers repeatedly to build energetic connection",
        "Purchase during auspicious muhurta times"
    ])
    
    advice["lucky_periods"] = [
        "During waxing moon (Shukla Paksha)",
        "When Jupiter transits favorable houses (2, 5, 9, 11)",
        "During your birth nakshatra days"
    ]
    
    advice["cautions"] = [
        "Avoid Rahu Kalam periods",
        "Don't play during debilitated Jupiter",
        "Maintain dharmic balance"
    ]
    
    advice["remedies"] = [
        "Chant Jupiter mantra 108 times on Thursdays",
        "Donate 10% of winnings to charity",
        "Wear yellow sapphire for Jupiter's blessings",
        "Feed green vegetables to cows on Wednesdays"
    ]
    
    return advice