# predictions.py
"""
Generate monthly predictions for next 12 months
Based on transits, dashas, and natal chart positions
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from local_calculate import LocalCalculate, PlanetName, ZODIAC_SIGNS, calculate_chart
import calendar
import re


def extract_date_from_query(query: str) -> str:
    """Extract date from natural language query"""
    # Common date patterns
    patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',      # Month DD, YYYY
        r'(\d{1,2})\s+(\w+)\s+(\d{4})',        # DD Month YYYY
        r'(\d{1,2})(?:st|nd|rd|th)?\s+of\s+(\w+)\s+(\d{4})',  # DDth of Month YYYY
    ]
    
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    query_lower = query.lower()
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            groups = match.groups()
            try:
                # Pattern 1 & 2: numeric dates
                if groups[0].isdigit() and groups[1].isdigit() and groups[2].isdigit():
                    if len(groups[0]) == 4:  # YYYY-MM-DD
                        return f"{groups[0]}-{int(groups[1]):02d}-{int(groups[2]):02d}"
                    else:  # DD-MM-YYYY
                        return f"{groups[2]}-{int(groups[1]):02d}-{int(groups[0]):02d}"
                
                # Pattern 3 & 4: text months
                month_str = groups[0] if not groups[0].isdigit() else groups[1]
                day = groups[1] if groups[0].isdigit() else groups[0]
                year = groups[2]
                
                month = month_names.get(month_str.lower())
                if month:
                    return f"{year}-{month:02d}-{int(day):02d}"
            except (ValueError, IndexError):
                continue
    
    return None

class PredictionEngine:
    """Generate astrological predictions"""
    
    # House significations
    HOUSE_MEANINGS = {
        1: {"area": "Self, Health, Personality", "keywords": ["identity", "vitality", "appearance", "new beginnings"]},
        2: {"area": "Wealth, Family, Speech", "keywords": ["money", "savings", "family", "values", "food"]},
        3: {"area": "Courage, Siblings, Communication", "keywords": ["efforts", "short travels", "skills", "siblings"]},
        4: {"area": "Home, Mother, Property", "keywords": ["home", "comfort", "emotions", "real estate", "mother"]},
        5: {"area": "Children, Romance, Creativity", "keywords": ["love", "children", "speculation", "education", "creativity"]},
        6: {"area": "Health Issues, Enemies, Service", "keywords": ["obstacles", "competition", "health problems", "debts"]},
        7: {"area": "Marriage, Partnerships, Business", "keywords": ["spouse", "partnerships", "contracts", "business"]},
        8: {"area": "Longevity, Transformation, Hidden", "keywords": ["transformation", "inheritance", "mysteries", "research"]},
        9: {"area": "Fortune, Father, Spirituality", "keywords": ["luck", "higher learning", "travel", "dharma", "father"]},
        10: {"area": "Career, Status, Authority", "keywords": ["profession", "reputation", "authority", "achievements"]},
        11: {"area": "Gains, Friends, Aspirations", "keywords": ["income", "gains", "friends", "ambitions", "network"]},
        12: {"area": "Expenses, Foreign, Spirituality", "keywords": ["losses", "foreign lands", "spirituality", "isolation"]}
    }
    
    # Planet effects
    PLANET_EFFECTS = {
        PlanetName.SUN: {
            "positive": ["confidence", "authority", "recognition", "vitality", "leadership"],
            "negative": ["ego conflicts", "authority issues", "health concerns", "father issues"],
            "areas": ["career", "father", "health", "government", "authority"]
        },
        PlanetName.MOON: {
            "positive": ["emotional stability", "mental peace", "intuition", "popularity", "comfort"],
            "negative": ["mood swings", "anxiety", "emotional instability", "mother issues"],
            "areas": ["emotions", "mind", "mother", "home", "public"]
        },
        PlanetName.MARS: {
            "positive": ["energy", "courage", "success in competition", "property gains", "siblings support"],
            "negative": ["conflicts", "accidents", "aggression", "impulsiveness", "legal issues"],
            "areas": ["energy", "property", "siblings", "courage", "competition"]
        },
        PlanetName.MERCURY: {
            "positive": ["intelligence", "communication skills", "business success", "learning", "writing"],
            "negative": ["confusion", "communication problems", "indecision", "nervous tension"],
            "areas": ["communication", "business", "intellect", "trade", "education"]
        },
        PlanetName.JUPITER: {
            "positive": ["wisdom", "growth", "fortune", "spiritual progress", "wealth", "children"],
            "negative": ["overconfidence", "excess", "legal issues", "weight gain"],
            "areas": ["wisdom", "wealth", "children", "education", "spirituality"]
        },
        PlanetName.VENUS: {
            "positive": ["love", "luxury", "artistic success", "relationships", "comforts", "marriage"],
            "negative": ["relationship issues", "overindulgence", "financial extravagance"],
            "areas": ["love", "marriage", "luxury", "arts", "beauty", "vehicles"]
        },
        PlanetName.SATURN: {
            "positive": ["discipline", "hard work rewards", "stability", "longevity", "career growth"],
            "negative": ["delays", "restrictions", "hard work", "obstacles", "depression", "losses"],
            "areas": ["career", "discipline", "delays", "longevity", "servants"]
        },
        PlanetName.RAHU: {
            "positive": ["sudden gains", "foreign opportunities", "innovation", "unconventional success"],
            "negative": ["confusion", "deception", "obsession", "scandals", "addictions"],
            "areas": ["foreign", "technology", "sudden events", "materialism"]
        },
        PlanetName.KETU: {
            "positive": ["spirituality", "liberation", "past karma resolution", "occult knowledge"],
            "negative": ["losses", "detachment", "confusion", "accidents", "mysterious problems"],
            "areas": ["spirituality", "detachment", "past life", "occult", "moksha"]
        }
    }
    
    @staticmethod
    def get_transit_predictions(natal_chart: Dict, start_date: datetime, 
                                end_date: datetime, lat: float, lon: float) -> List[Dict]:
        """Generate predictions based on planetary transits"""
        
        predictions = []
        current_date = start_date
        
        while current_date <= end_date:
            # Calculate transit positions for this date
            jd = LocalCalculate.get_julian_day(current_date)
            ayanamsa = LocalCalculate.get_ayanamsa(jd)
            house_cusps = LocalCalculate.get_house_cusps(jd, lat, lon, ayanamsa)
            
            month_predictions = {
                "month": current_date.strftime("%B %Y"),
                "date_range": {
                    "start": current_date.strftime("%Y-%m-%d"),
                    "end": (current_date + timedelta(days=30)).strftime("%Y-%m-%d")
                },
                "transits": [],
                "key_areas": {
                    "love": {"score": 0, "events": []},
                    "career": {"score": 0, "events": []},
                    "wealth": {"score": 0, "events": []},
                    "health": {"score": 0, "events": []},
                },
                "overall_rating": 0,
                "summary": ""
            }
            
            # Analyze each planet's transit
            for planet_name in [PlanetName.JUPITER, PlanetName.SATURN, PlanetName.MARS,
                              PlanetName.VENUS, PlanetName.MERCURY, PlanetName.SUN, PlanetName.MOON]:
                
                transit_long = LocalCalculate.get_planet_longitude(planet_name, jd, ayanamsa)
                transit_house = LocalCalculate.get_planet_house(transit_long, house_cusps)
                transit_sign, _ = LocalCalculate.longitude_to_sign(transit_long)
                
                # Get natal position
                natal_planet = natal_chart["planets"][planet_name]
                natal_house = natal_planet["house"]
                
                # Analyze transit effects
                transit_effect = PredictionEngine._analyze_transit_effect(
                    planet_name, transit_house, natal_house, natal_chart
                )
                
                month_predictions["transits"].append({
                    "planet": planet_name,
                    "transit_house": transit_house,
                    "transit_sign": transit_sign,
                    "effect": transit_effect["effect"],
                    "description": transit_effect["description"],
                    "areas_affected": transit_effect["areas"]
                })
                
                # Update key areas scores
                PredictionEngine._update_area_scores(
                    month_predictions["key_areas"], 
                    transit_effect, 
                    planet_name,
                    transit_house
                )
            
            # Calculate overall rating
            month_predictions["overall_rating"] = PredictionEngine._calculate_overall_rating(
                month_predictions["key_areas"]
            )
            
            # Generate summary
            month_predictions["summary"] = PredictionEngine._generate_monthly_summary(
                month_predictions
            )
            
            predictions.append(month_predictions)
            
            # Move to next month
            next_month = current_date.month % 12 + 1
            next_year = current_date.year + (1 if next_month == 1 else 0)
            current_date = datetime(next_year, next_month, 1)
        
        return predictions
    
    @staticmethod
    def _analyze_transit_effect(planet: str, transit_house: int, 
                                natal_house: int, natal_chart: Dict) -> Dict:
        """Analyze the effect of a planet's transit"""
        
        planet_effects = PredictionEngine.PLANET_EFFECTS.get(planet, {})
        house_info = PredictionEngine.HOUSE_MEANINGS.get(transit_house, {})
        
        # Determine if transit is beneficial
        beneficial_houses = [1, 2, 4, 5, 7, 9, 10, 11]  # Natural benefic houses
        challenging_houses = [6, 8, 12]  # Dusthana houses
        
        effect = "neutral"
        description = ""
        
        # Check if planet is benefic or malefic in natal chart
        is_benefic = planet in [PlanetName.JUPITER, PlanetName.VENUS, PlanetName.MERCURY]
        is_malefic = planet in [PlanetName.SATURN, PlanetName.MARS, PlanetName.RAHU, PlanetName.KETU]
        
        if transit_house in beneficial_houses:
            if is_benefic:
                effect = "positive"
                description = f"{planet} transiting {transit_house}th house brings {', '.join(planet_effects.get('positive', [])[:2])} related to {house_info.get('area', '')}."
            else:
                effect = "mixed"
                description = f"{planet} in {transit_house}th house requires careful handling of {house_info.get('area', '')}."
        elif transit_house in challenging_houses:
            if is_malefic:
                effect = "challenging"
                description = f"{planet} in {transit_house}th house may bring {', '.join(planet_effects.get('negative', [])[:2])} affecting {house_info.get('area', '')}."
            else:
                effect = "mixed"
                description = f"{planet} transiting {transit_house}th house provides support despite challenges in {house_info.get('area', '')}."
        
        return {
            "effect": effect,
            "description": description,
            "areas": planet_effects.get("areas", [])
        }
    
    @staticmethod
    def _update_area_scores(key_areas: Dict, transit_effect: Dict, 
                           planet: str, transit_house: int):
        """Update scores for key life areas"""
        
        effect_scores = {
            "positive": 2,
            "mixed": 0,
            "neutral": 0,
            "challenging": -2
        }
        
        score = effect_scores.get(transit_effect["effect"], 0)
        
        # Map houses to life areas
        house_to_area = {
            5: "love", 7: "love", 11: "love",  # Love related
            2: "wealth", 11: "wealth",  # Wealth related
            1: "health", 6: "health",  # Health related
            10: "career", 6: "career",  # Career related
        }
        
        if transit_house in house_to_area:
            area = house_to_area[transit_house]
            key_areas[area]["score"] += score
            key_areas[area]["events"].append({
                "planet": planet,
                "effect": transit_effect["effect"],
                "description": transit_effect["description"]
            })
    
    @staticmethod
    def _calculate_overall_rating(key_areas: Dict) -> int:
        """Calculate overall rating 1-10"""
        total_score = sum(area["score"] for area in key_areas.values())
        # Normalize to 1-10 scale
        rating = max(1, min(10, 5 + (total_score // 2)))
        return rating
    
    @staticmethod
    def _generate_monthly_summary(month_data: Dict) -> str:
        """Generate AI-friendly summary of the month"""
        
        rating = month_data["overall_rating"]
        
        if rating >= 8:
            tone = "Excellent month ahead!"
        elif rating >= 6:
            tone = "Positive month with good opportunities."
        elif rating >= 4:
            tone = "Mixed month requiring balance and patience."
        else:
            tone = "Challenging month requiring caution and planning."
        
        # Identify strongest and weakest areas
        areas = month_data["key_areas"]
        sorted_areas = sorted(areas.items(), key=lambda x: x[1]["score"], reverse=True)
        
        strongest = sorted_areas[0][0] if sorted_areas else "general"
        weakest = sorted_areas[-1][0] if sorted_areas else "none"
        
        summary = f"{tone} Focus on {strongest}. Be cautious with {weakest}. "
        summary += f"Overall rating: {rating}/10."
        
        return summary


def generate_yearly_predictions(natal_chart: Dict, lat: float, lon: float) -> Dict[str, Any]:
    """
    Generate predictions for next 12 months
    
    Args:
        natal_chart: Birth chart data
        lat: Latitude for transit calculations
        lon: Longitude for transit calculations
    
    Returns:
        Comprehensive predictions for 12 months
    """
    
    today = datetime.now()
    end_date = today + timedelta(days=365)
    
    predictions = PredictionEngine.get_transit_predictions(
        natal_chart, today, end_date, lat, lon
    )
    
    # Add yearly overview
    yearly_overview = {
        "period": f"{today.strftime('%B %Y')} to {end_date.strftime('%B %Y')}",
        "best_months": [],
        "challenging_months": [],
        "key_themes": {
            "love": {"trend": "", "advice": ""},
            "career": {"trend": "", "advice": ""},
            "wealth": {"trend": "", "advice": ""},
            "health": {"trend": "", "advice": ""}
        }
    }
    
    # Analyze best and worst months
    sorted_predictions = sorted(predictions, key=lambda x: x["overall_rating"], reverse=True)
    yearly_overview["best_months"] = [
        {"month": p["month"], "rating": p["overall_rating"]} 
        for p in sorted_predictions[:3]
    ]
    yearly_overview["challenging_months"] = [
        {"month": p["month"], "rating": p["overall_rating"]} 
        for p in sorted_predictions[-3:]
    ]
    
    # Calculate trends for each area
    for area in ["love", "career", "wealth", "health"]:
        scores = [p["key_areas"][area]["score"] for p in predictions]
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 3:
            trend = "Very positive year ahead"
            advice = f"Excellent time to focus on {area}. Take initiative and make important decisions."
        elif avg_score > 0:
            trend = "Generally favorable year"
            advice = f"Good opportunities in {area}. Stay consistent and work steadily."
        elif avg_score > -3:
            trend = "Mixed results expected"
            advice = f"Balance and patience needed in {area}. Focus on long-term planning."
        else:
            trend = "Challenging year ahead"
            advice = f"Be cautious with {area}. Focus on damage control and building foundation."
        
        yearly_overview["key_themes"][area] = {
            "trend": trend,
            "advice": advice,
            "average_score": round(avg_score, 1)
        }
    
    return {
        "generated_at": today.strftime("%Y-%m-%d %H:%M:%S"),
        "yearly_overview": yearly_overview,
        "monthly_predictions": predictions,
        "llm_guidance": {
            "usage": "Use monthly_predictions for specific time-based queries. Use yearly_overview for general guidance.",
            "interpretation": "Higher scores (positive) indicate favorable periods. Lower scores (negative) indicate challenges.",
            "areas": "love=relationships/marriage, career=profession/business, wealth=money/finances, health=wellbeing"
        }
    }


def generate_area_specific_predictions(natal_chart: Dict, lat: float, lon: float, 
                                       area: str, months: int = 6, start_date: datetime = None) -> Dict[str, Any]:
    """
    Generate predictions for a specific life area (love, career, wealth, health) for custom period
    
    Args:
        natal_chart: Birth chart data
        lat: Latitude for transit calculations
        lon: Longitude for transit calculations
        area: "love", "career", "wealth", or "health"
        months: Number of months to predict (default 6)
        start_date: Start date for predictions (default today)
    
    Returns:
        Detailed area-specific predictions with precise dates, ratings, and advice
    """
    
    if start_date is None:
        start_date = datetime.now()
    
    end_date = start_date + timedelta(days=30 * months)
    
    # Get general predictions
    monthly_predictions = PredictionEngine.get_transit_predictions(
        natal_chart, start_date, end_date, lat, lon
    )
    
    # Focus on specific area
    area_predictions = []
    
    for month_data in monthly_predictions:
        if area not in month_data["key_areas"]:
            continue
            
        area_data = month_data["key_areas"][area]
        
        # Calculate precise date ranges
        start_date = datetime.strptime(month_data["date_range"]["start"], "%Y-%m-%d")
        end_date_month = datetime.strptime(month_data["date_range"]["end"], "%Y-%m-%d")
        
        # Rating from 1-10
        score = area_data["score"]
        rating = max(1, min(10, 5 + score))
        
        # Determine quality
        if rating >= 8:
            quality = "Excellent"
            advice = f"This is a highly favorable month for {area}. Take initiative and make important decisions."
        elif rating >= 6:
            quality = "Good"
            advice = f"Positive month for {area}. Good time for moderate actions and planning."
        elif rating >= 4:
            quality = "Average"
            advice = f"Mixed results in {area}. Focus on stability and avoid major risks."
        else:
            quality = "Challenging"
            advice = f"Difficult period for {area}. Exercise caution and focus on damage control."
        
        # Get specific transits affecting this area
        relevant_transits = _get_area_relevant_transits(month_data["transits"], area)
        
        # Remedies for challenging times
        remedies = _get_remedies_for_area(area, rating, relevant_transits)
        
        # Best dates in the month
        best_dates = _calculate_best_dates_in_month(start_date, end_date_month, 
                                                    natal_chart, lat, lon, area)
        
        area_predictions.append({
            "month": month_data["month"],
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date_month.strftime("%Y-%m-%d"),
                "start_day": start_date.strftime("%A, %B %d, %Y"),
                "end_day": end_date_month.strftime("%A, %B %d, %Y")
            },
            "rating": rating,
            "quality": quality,
            "score": score,
            "advice": advice,
            "key_transits": relevant_transits,
            "best_dates": best_dates,
            "remedies": remedies,
            "what_to_do": _get_action_items(area, rating),
            "what_to_avoid": _get_avoid_items(area, rating)
        })
    
    # Create overview
    overview = _create_area_overview(area_predictions, area)
    
    # Calculate prediction period from actual predictions
    if area_predictions:
        first_month = area_predictions[0]["month"]
        last_month = area_predictions[-1]["month"]
        prediction_period = f"{first_month} to {last_month}"
    else:
        prediction_period = f"{start_date.strftime('%B %Y')} to {(start_date + timedelta(days=30*months)).strftime('%B %Y')}"
    
    return {
        "area": area,
        "prediction_period": prediction_period,
        "generated_at": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "overview": overview,
        "monthly_predictions": area_predictions,
        "birth_chart_summary": {
            "ascendant": natal_chart["ascendant"]["sign"],
            "moon_sign": natal_chart["planets"]["Moon"]["sign"],
            "sun_sign": natal_chart["planets"]["Sun"]["sign"]
        }
    }


def _get_area_relevant_transits(transits: List[Dict], area: str) -> List[Dict]:
    """Get transits relevant to specific area"""
    
    # Map areas to relevant planets
    area_planets = {
        "love": ["Venus", "Moon", "Jupiter", "Mars"],
        "career": ["Sun", "Saturn", "Jupiter", "Mercury"],
        "wealth": ["Jupiter", "Venus", "Mercury", "Moon"],
        "health": ["Sun", "Moon", "Mars", "Saturn"]
    }
    
    relevant = []
    for transit in transits:
        if transit["planet"] in area_planets.get(area, []):
            relevant.append({
                "planet": transit["planet"],
                "sign": transit["transit_sign"],
                "house": transit["transit_house"],
                "effect": transit["effect"],
                "description": transit["description"]
            })
    
    return relevant[:5]  # Top 5 most relevant


def _get_remedies_for_area(area: str, rating: int, transits: List[Dict]) -> List[str]:
    """Get remedies for challenging periods"""
    
    if rating >= 7:
        return ["Continue with positive momentum", "Express gratitude for favorable period"]
    
    remedies = []
    
    # Area-specific remedies
    area_remedies = {
        "love": [
            "Wear white or pastel colors on Fridays",
            "Donate to women's charities",
            "Chant Venus mantra on Fridays",
            "Strengthen communication with partner",
            "Practice patience and understanding"
        ],
        "career": [
            "Wear copper or ruby on Sundays",
            "Offer water to Sun at sunrise",
            "Focus on discipline and hard work",
            "Network with seniors and mentors",
            "Avoid conflicts with authority"
        ],
        "wealth": [
            "Donate yellow items on Thursdays",
            "Keep a clean and organized wallet",
            "Chant Lakshmi mantra on Fridays",
            "Avoid unnecessary expenses",
            "Focus on savings rather than spending"
        ],
        "health": [
            "Practice yoga and meditation daily",
            "Maintain regular sleep schedule",
            "Eat sattvic (pure) foods",
            "Offer water to plants daily",
            "Avoid stress and negative thoughts"
        ]
    }
    
    # Add challenging planet remedies
    for transit in transits:
        if transit["effect"] == "challenging":
            planet = transit["planet"]
            if planet == "Saturn":
                remedies.append("Donate to elderly or disabled on Saturdays")
            elif planet == "Mars":
                remedies.append("Donate red items on Tuesdays")
            elif planet == "Rahu":
                remedies.append("Donate to charitable causes on Saturdays")
    
    base_remedies = area_remedies.get(area, [])
    remedies.extend(base_remedies[:3])
    
    return remedies[:5]


def _calculate_best_dates_in_month(start_date: datetime, end_date: datetime,
                                   natal_chart: Dict, lat: float, lon: float,
                                   area: str) -> List[Dict]:
    """Calculate best dates in a month for specific area"""
    
    best_dates = []
    current = start_date
    
    # Sample 5 dates throughout the month
    date_interval = (end_date - start_date).days // 5
    
    for i in range(5):
        check_date = current + timedelta(days=i * date_interval)
        if check_date > end_date:
            break
            
        jd = LocalCalculate.get_julian_day(check_date)
        ayanamsa = LocalCalculate.get_ayanamsa(jd)
        
        # Get Moon position (important for daily muhurta)
        moon_long = LocalCalculate.get_planet_longitude("Moon", jd, ayanamsa)
        moon_sign, _ = LocalCalculate.longitude_to_sign(moon_long)
        moon_nakshatra, _ = LocalCalculate.get_nakshatra(moon_long)
        
        # Calculate quality score
        quality_score = _calculate_date_quality(check_date, natal_chart, lat, lon, area)
        
        if quality_score >= 6:
            best_dates.append({
                "date": check_date.strftime("%Y-%m-%d"),
                "day": check_date.strftime("%A"),
                "full_date": check_date.strftime("%A, %B %d, %Y"),
                "quality_score": quality_score,
                "moon_sign": moon_sign,
                "moon_nakshatra": moon_nakshatra,
                "recommendation": "Favorable day for important activities" if quality_score >= 8 else "Good day for moderate activities"
            })
    
    return sorted(best_dates, key=lambda x: x["quality_score"], reverse=True)[:3]


def _calculate_date_quality(date: datetime, natal_chart: Dict, lat: float, 
                            lon: float, area: str) -> int:
    """Calculate quality score for a specific date (1-10)"""
    
    jd = LocalCalculate.get_julian_day(date)
    ayanamsa = LocalCalculate.get_ayanamsa(jd)
    house_cusps = LocalCalculate.get_house_cusps(jd, lat, lon, ayanamsa)
    
    score = 5  # Base score
    
    # Check relevant planets for the area
    area_planets = {
        "love": ["Venus", "Moon"],
        "career": ["Sun", "Saturn"],
        "wealth": ["Jupiter", "Mercury"],
        "health": ["Sun", "Moon"]
    }
    
    for planet in area_planets.get(area, []):
        planet_long = LocalCalculate.get_planet_longitude(planet, jd, ayanamsa)
        planet_house = LocalCalculate.get_planet_house(planet_long, house_cusps)
        
        # Benefic houses increase score
        if planet_house in [1, 2, 4, 5, 7, 9, 10, 11]:
            score += 1
        # Malefic houses decrease score
        elif planet_house in [6, 8, 12]:
            score -= 1
    
    return max(1, min(10, score))


def _get_action_items(area: str, rating: int) -> List[str]:
    """Get recommended actions based on area and rating"""
    
    actions = {
        "love": {
            "high": [
                "Express your feelings openly",
                "Plan romantic dates or getaways",
                "Propose or take relationship to next level",
                "Meet potential partners through social events",
                "Strengthen existing relationships"
            ],
            "medium": [
                "Focus on communication with partner",
                "Spend quality time together",
                "Work on resolving minor issues",
                "Be patient and understanding"
            ],
            "low": [
                "Focus on self-love and self-care",
                "Avoid major relationship decisions",
                "Work on personal development",
                "Give space in relationships"
            ]
        },
        "career": {
            "high": [
                "Ask for promotion or raise",
                "Start new projects or ventures",
                "Network actively with industry leaders",
                "Apply for dream jobs",
                "Launch new business initiatives"
            ],
            "medium": [
                "Focus on current responsibilities",
                "Build professional relationships",
                "Upgrade skills through training",
                "Maintain steady work pace"
            ],
            "low": [
                "Avoid confrontations with bosses",
                "Focus on completing existing tasks",
                "Don't make major career changes",
                "Build skills for future opportunities"
            ]
        },
        "wealth": {
            "high": [
                "Make calculated investments",
                "Start new income streams",
                "Negotiate better deals",
                "Purchase assets or property",
                "Expand business operations"
            ],
            "medium": [
                "Focus on savings and budgeting",
                "Pay off existing debts",
                "Research investment opportunities",
                "Maintain financial discipline"
            ],
            "low": [
                "Avoid major financial commitments",
                "Focus on expense reduction",
                "Don't take unnecessary loans",
                "Postpone big purchases",
                "Build emergency fund"
            ]
        },
        "health": {
            "high": [
                "Start new fitness regime",
                "Schedule elective medical procedures",
                "Begin new health practices",
                "Join gym or sports activities",
                "Focus on preventive health"
            ],
            "medium": [
                "Maintain current health routines",
                "Get regular health checkups",
                "Practice stress management",
                "Focus on balanced diet"
            ],
            "low": [
                "Avoid strenuous physical activities",
                "Postpone elective surgeries",
                "Rest and recover properly",
                "Consult doctors for any concerns",
                "Focus on gentle exercises only"
            ]
        }
    }
    
    level = "high" if rating >= 7 else "medium" if rating >= 4 else "low"
    return actions.get(area, {}).get(level, [])[:3]


def _get_avoid_items(area: str, rating: int) -> List[str]:
    """Get things to avoid based on area and rating"""
    
    if rating >= 7:
        return ["Overconfidence", "Complacency"]
    
    avoid = {
        "love": [
            "Arguments and confrontations",
            "Making hasty relationship decisions",
            "Neglecting partner's feelings",
            "Being overly critical or demanding"
        ],
        "career": [
            "Conflicts with superiors",
            "Taking unnecessary risks",
            "Changing jobs impulsively",
            "Overcommitting to projects"
        ],
        "wealth": [
            "Speculative investments",
            "Lending money to others",
            "Unnecessary luxury spending",
            "Starting new financial ventures"
        ],
        "health": [
            "Ignoring health symptoms",
            "Excessive stress or overwork",
            "Unhealthy food and habits",
            "Skipping medications or checkups"
        ]
    }
    
    return avoid.get(area, [])[:3]


def _create_area_overview(predictions: List[Dict], area: str) -> Dict:
    """Create overview of area predictions"""
    
    if not predictions:
        return {}
    
    # Find best and worst months
    sorted_preds = sorted(predictions, key=lambda x: x["rating"], reverse=True)
    best_months = sorted_preds[:3]
    worst_months = sorted_preds[-3:]
    
    # Calculate average rating
    avg_rating = sum(p["rating"] for p in predictions) / len(predictions)
    
    # Determine trend
    first_half = predictions[:len(predictions)//2]
    second_half = predictions[len(predictions)//2:]
    
    # Handle edge cases where halves might be empty
    if not first_half:
        first_avg = avg_rating  # Use overall average if no first half
    else:
        first_avg = sum(p["rating"] for p in first_half) / len(first_half)
    
    if not second_half:
        second_avg = avg_rating  # Use overall average if no second half
    else:
        second_avg = sum(p["rating"] for p in second_half) / len(second_half)
    
    if second_avg > first_avg + 1:
        trend = "Improving - Things get better as time progresses"
    elif second_avg < first_avg - 1:
        trend = "Declining - Early months are better than later ones"
    else:
        trend = "Stable - Consistent throughout the period"
    
    return {
        "average_rating": round(avg_rating, 1),
        "trend": trend,
        "best_months": [
            {
                "month": m["month"],
                "rating": m["rating"],
                "dates": f"{m['date_range']['start']} to {m['date_range']['end']}"
            }
            for m in best_months
        ],
        "challenging_months": [
            {
                "month": m["month"],
                "rating": m["rating"],
                "dates": f"{m['date_range']['start']} to {m['date_range']['end']}"
            }
            for m in worst_months
        ],
        "overall_guidance": _get_overall_guidance(area, avg_rating, trend)
    }


def _get_overall_guidance(area: str, avg_rating: float, trend: str) -> str:
    """Get overall guidance for the period"""
    
    if avg_rating >= 7:
        quality = "excellent"
        action = "take full advantage of this favorable period"
    elif avg_rating >= 5:
        quality = "good"
        action = "make steady progress with balanced approach"
    else:
        quality = "challenging"
        action = "focus on building foundation and exercising patience"
    
    return f"This is a {quality} period for {area}. {action.capitalize()}. {trend}"


def _fix_date_format(date_str: str) -> str:
    """Try to fix common date format issues"""
    import re
    
    # Handle cases like "2025-11-2025" -> assume it's "2025-11-25" (day repeated)
    if re.match(r'^\d{4}-\d{2}-\d{4}$', date_str):
        parts = date_str.split('-')
        if len(parts) == 3:
            year1, month, year2 = parts
            if year1 == year2[:4]:  # Year repeated
                # Extract the day from the repeated year part
                if len(year2) > 4:
                    day_str = year2[4:]
                else:
                    # If year is exactly repeated, assume the day is the last two digits
                    day_str = year2[-2:]
                
                if day_str and day_str.isdigit():
                    day = int(day_str)
                    if 1 <= day <= 31:
                        return f"{year1}-{month}-{day:02d}"
    
    # Handle other common formats
    # MM/DD/YYYY -> YYYY-MM-DD
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', date_str)
    if match:
        month, day, year = match.groups()
        try:
            return f"{year}-{int(month):02d}-{int(day):02d}"
        except ValueError:
            pass
    
    # DD/MM/YYYY -> YYYY-MM-DD  
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', date_str)
    if match:
        day, month, year = match.groups()
        try:
            return f"{year}-{int(month):02d}-{int(day):02d}"
        except ValueError:
            pass
    
    return None


def generate_wildcard_prediction(natal_chart: Dict, lat: float, lon: float,
                                 query: str, specific_date: str = None) -> Dict[str, Any]:
    """
    Generate ultra-precise prediction for specific query and date
    
    Args:
        natal_chart: Birth chart data
        lat: Latitude for transit calculations
        lon: Longitude for transit calculations
        query: Natural language query
        specific_date: Specific date in YYYY-MM-DD format (optional)
    
    Returns:
        Detailed prediction with success probability, timing, and advice
    """
    
    # Extract date from query if not provided or invalid
    if not specific_date:
        specific_date = extract_date_from_query(query)
    
    if not specific_date:
        # If no specific date, analyze near future (next 30 days)
        target_date = datetime.now() + timedelta(days=15)
        specific_date = target_date.strftime("%Y-%m-%d")
        date_extracted = False
    else:
        # Validate and fix the provided specific_date
        try:
            # Try to parse the date to validate format
            datetime.strptime(specific_date, "%Y-%m-%d")
            date_extracted = True
        except ValueError:
            # Try to fix common date format issues
            fixed_date = _fix_date_format(specific_date)
            if fixed_date:
                specific_date = fixed_date
                date_extracted = True
            else:
                # If specific_date is invalid and can't be fixed, try to extract from query
                extracted_date = extract_date_from_query(query)
                if extracted_date:
                    specific_date = extracted_date
                    date_extracted = True
                else:
                    # If no valid date found anywhere, use fallback
                    target_date = datetime.now() + timedelta(days=15)
                    specific_date = target_date.strftime("%Y-%m-%d")
                    date_extracted = False
    
    try:
        event_date = datetime.strptime(specific_date, "%Y-%m-%d")
    except ValueError:
        # Final fallback if all else fails
        event_date = datetime.now() + timedelta(days=15)
        date_extracted = False
    
    # Analyze query to determine area of concern
    query_lower = query.lower()
    
    area = "general"
    concern_type = "event"
    
    if any(word in query_lower for word in ["date", "love", "romance", "relationship", "marry", "propose", "lucky"]):
        area = "love"
        concern_type = "romance"
    elif any(word in query_lower for word in ["job", "interview", "promotion", "career", "work", "redundancy", "fired"]):
        area = "career"
        concern_type = "professional"
    elif any(word in query_lower for word in ["money", "investment", "business", "financial", "buy", "purchase", "contract"]):
        area = "wealth"
        concern_type = "financial"
    elif any(word in query_lower for word in ["health", "safe", "safety", "accident", "motorcycle", "surgery", "medical"]):
        area = "health"
        concern_type = "safety"
    
    # Calculate transit positions for the event date
    jd = LocalCalculate.get_julian_day(event_date)
    ayanamsa = LocalCalculate.get_ayanamsa(jd)
    house_cusps = LocalCalculate.get_house_cusps(jd, lat, lon, ayanamsa)
    
    # Get all planetary positions on event date
    event_planets = {}
    for planet_name in [PlanetName.SUN, PlanetName.MOON, PlanetName.MARS, 
                       PlanetName.MERCURY, PlanetName.JUPITER, PlanetName.VENUS,
                       PlanetName.SATURN, PlanetName.RAHU, PlanetName.KETU]:
        planet_long = LocalCalculate.get_planet_longitude(planet_name, jd, ayanamsa)
        planet_house = LocalCalculate.get_planet_house(planet_long, house_cusps)
        planet_sign, _ = LocalCalculate.longitude_to_sign(planet_long)
        planet_nakshatra, _ = LocalCalculate.get_nakshatra(planet_long)
        
        event_planets[planet_name] = {
            "longitude": round(planet_long, 2),
            "sign": planet_sign,
            "house": planet_house,
            "nakshatra": planet_nakshatra
        }
    
    # Calculate success probability
    success_probability = _calculate_success_probability(
        natal_chart, event_planets, area, concern_type, query_lower
    )
    
    # Get best time of day
    best_hours = _calculate_best_hours(event_date, natal_chart, area)
    
    # Get specific advice
    specific_advice = _generate_specific_advice(
        success_probability, area, concern_type, query, event_planets
    )
    
    # Get remedies
    remedies = _get_event_specific_remedies(success_probability, area, event_planets)
    
    # Get lucky factors
    lucky_factors = _get_lucky_factors(event_date, event_planets, natal_chart)
    
    # Risk assessment
    risks = _assess_risks(success_probability, area, concern_type, event_planets, query_lower)
    
    return {
        "query": query,
        "event_date": {
            "date": event_date.strftime("%Y-%m-%d"),
            "day": event_date.strftime("%A"),
            "full_date": event_date.strftime("%A, %B %d, %Y"),
            "extracted_from_query": date_extracted
        },
        "area_of_concern": area,
        "concern_type": concern_type,
        "success_probability": {
            "percentage": success_probability,
            "rating": "Very High" if success_probability >= 80 else
                     "High" if success_probability >= 65 else
                     "Moderate" if success_probability >= 50 else
                     "Low" if success_probability >= 35 else "Very Low",
            "interpretation": _interpret_probability(success_probability, concern_type)
        },
        "planetary_positions_on_date": event_planets,
        "best_time_of_day": best_hours,
        "specific_advice": specific_advice,
        "risks_and_challenges": risks,
        "mitigation_strategies": _get_mitigation_strategies(risks, area),
        "remedies": remedies,
        "lucky_factors": lucky_factors,
        "overall_recommendation": _get_overall_recommendation(success_probability, area, concern_type),
        "birth_chart_context": {
            "ascendant": natal_chart["ascendant"]["sign"],
            "moon_sign": natal_chart["planets"]["Moon"]["sign"],
            "key_strengths": _identify_key_strengths(natal_chart, area)
        }
    }


def _calculate_success_probability(natal_chart: Dict, event_planets: Dict,
                                   area: str, concern_type: str, query: str) -> int:
    """Calculate success probability percentage (0-100)"""
    
    base_score = 50  # Start at 50%
    
    # Check key planets for the area
    area_key_planets = {
        "love": [("Venus", 20), ("Moon", 15), ("Jupiter", 10)],
        "career": [("Sun", 20), ("Saturn", 15), ("Mercury", 10)],
        "wealth": [("Jupiter", 20), ("Mercury", 15), ("Venus", 10)],
        "health": [("Sun", 20), ("Moon", 15), ("Mars", 10)],
        "general": [("Jupiter", 15), ("Venus", 10), ("Sun", 10)]
    }
    
    key_planets = area_key_planets.get(area, area_key_planets["general"])
    
    for planet, weight in key_planets:
        planet_data = event_planets.get(planet, {})
        house = planet_data.get("house", 6)
        
        # Benefic houses increase probability
        if house in [1, 2, 4, 5, 7, 9, 10, 11]:
            base_score += weight * 0.3
        # Neutral houses
        elif house in [3]:
            base_score += weight * 0.1
        # Malefic houses decrease probability
        else:
            base_score -= weight * 0.3
    
    # Moon's influence (emotional/mental state)
    moon_data = event_planets.get("Moon", {})
    moon_nakshatra = moon_data.get("nakshatra", "")
    
    # Favorable nakshatras
    if moon_nakshatra in ["Rohini", "Pushya", "Hasta", "Shravana", "Revati"]:
        base_score += 10
    # Challenging nakshatras
    elif moon_nakshatra in ["Ashlesha", "Jyeshtha", "Moola", "Ardra"]:
        base_score -= 10
    
    # Check for negative keywords in query
    if any(word in query for word in ["redundancy", "fired", "accident", "problem", "fail"]):
        # These are risk-averse queries, adjust score accordingly
        if "safe" in query or "avoid" in query:
            pass  # User asking about safety, don't penalize
        else:
            base_score -= 5
    
    # Normalize to 0-100
    return max(0, min(100, int(base_score)))


def _calculate_best_hours(event_date: datetime, natal_chart: Dict, area: str) -> List[Dict]:
    """Calculate best hours of the day for the event"""
    
    # Planetary hours (simplified)
    planet_order = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
    day_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    day_name = event_date.strftime("%A")
    day_index = day_order.index(day_name) if day_name in day_order else 0
    
    # Get ruling planets for the area
    area_planets = {
        "love": ["Venus", "Moon"],
        "career": ["Sun", "Jupiter"],
        "wealth": ["Jupiter", "Mercury"],
        "health": ["Sun", "Moon"],
        "general": ["Jupiter", "Venus"]
    }
    
    favorable_planets = area_planets.get(area, area_planets["general"])
    
    best_hours = []
    
    # Calculate planetary hours (simplified version)
    hour_blocks = [
        {"start": "06:00", "end": "09:00", "period": "Early Morning"},
        {"start": "09:00", "end": "12:00", "period": "Late Morning"},
        {"start": "12:00", "end": "15:00", "period": "Afternoon"},
        {"start": "15:00", "end": "18:00", "period": "Evening"},
        {"start": "18:00", "end": "21:00", "period": "Night"}
    ]
    
    for i, block in enumerate(hour_blocks):
        # Simple planetary hour calculation
        planet_index = (day_index + i) % 7
        ruling_planet = planet_order[planet_index]
        
        if ruling_planet in favorable_planets:
            best_hours.append({
                "time_range": f"{block['start']} - {block['end']}",
                "period": block['period'],
                "ruling_planet": ruling_planet,
                "quality": "Highly Favorable",
                "recommendation": f"Best time for {area}-related activities"
            })
    
    if not best_hours:
        # If no specific favorable hours, suggest general good times
        best_hours = [
            {
                "time_range": "09:00 - 12:00",
                "period": "Late Morning",
                "quality": "Favorable",
                "recommendation": "Generally auspicious time for most activities"
            }
        ]
    
    return best_hours[:3]


def _generate_specific_advice(probability: int, area: str, concern_type: str,
                              query: str, event_planets: Dict) -> List[str]:
    """Generate specific advice based on the situation"""
    
    advice = []
    
    if probability >= 70:
        advice.append(f"High probability of success - proceed with confidence")
        advice.append(f"This is a favorable time for {concern_type} matters")
        advice.append("Trust your instincts and take decisive action")
    elif probability >= 50:
        advice.append(f"Moderate probability - prepare thoroughly before proceeding")
        advice.append(f"Success possible with proper planning and effort")
        advice.append("Stay positive but remain realistic about expectations")
    else:
        advice.append(f"Lower probability - consider postponing if possible")
        advice.append(f"If must proceed, take extra precautions")
        advice.append("Focus on damage control and risk mitigation")
    
    # Area-specific advice
    if area == "love":
        if probability >= 60:
            advice.append("Express yourself authentically and openly")
            advice.append("Choose romantic settings and timing")
        else:
            advice.append("Be patient and don't force outcomes")
            advice.append("Focus on building emotional connection")
    
    elif area == "career":
        if "interview" in query.lower():
            advice.append("Prepare thoroughly and arrive early")
            advice.append("Dress professionally and confidently")
        elif "redundancy" in query.lower() or "fired" in query.lower():
            if probability >= 60:
                advice.append("Your position appears relatively secure")
                advice.append("Continue performing well and stay visible")
            else:
                advice.append("Update your resume and start networking")
                advice.append("Build relationships with decision-makers")
    
    elif area == "health":
        if "safe" in query.lower():
            if probability >= 60:
                advice.append("Generally favorable for the activity")
                advice.append("Still maintain normal safety precautions")
            else:
                advice.append("Exercise extra caution and vigilance")
                advice.append("Consider additional safety measures")
    
    elif area == "wealth":
        if probability >= 60:
            advice.append("Favorable time for financial decisions")
            advice.append("Still do proper due diligence")
        else:
            advice.append("Be conservative with financial commitments")
            advice.append("Seek professional advice before proceeding")
    
    return advice


def _assess_risks(probability: int, area: str, concern_type: str,
                 event_planets: Dict, query: str) -> List[Dict]:
    """Assess risks and challenges"""
    
    risks = []
    
    # Check malefic planets in challenging houses
    mars_house = event_planets.get("Mars", {}).get("house", 0)
    saturn_house = event_planets.get("Saturn", {}).get("house", 0)
    rahu_house = event_planets.get("Rahu", {}).get("house", 0)
    
    if mars_house in [6, 8, 12]:
        risks.append({
            "factor": "Mars in challenging position",
            "risk_level": "Moderate",
            "description": "Potential for conflicts, accidents, or aggressive situations",
            "impact_areas": ["conflicts", "accidents", "impulsiveness"]
        })
    
    if saturn_house in [6, 8, 12]:
        risks.append({
            "factor": "Saturn creating obstacles",
            "risk_level": "Moderate",
            "description": "Possible delays, restrictions, or additional responsibilities",
            "impact_areas": ["delays", "obstacles", "pessimism"]
        })
    
    if rahu_house in [6, 8, 12]:
        risks.append({
            "factor": "Rahu causing confusion",
            "risk_level": "Low to Moderate",
            "description": "Potential for unexpected situations or deception",
            "impact_areas": ["confusion", "deception", "unexpected events"]
        })
    
    # Query-specific risks
    if "motorcycle" in query or "bike" in query:
        risks.append({
            "factor": "Vehicle safety concern",
            "risk_level": "High" if probability < 50 else "Moderate",
            "description": "Need for extra caution while riding",
            "impact_areas": ["accidents", "health", "safety"]
        })
    
    if "redundancy" in query or "layoff" in query:
        risks.append({
            "factor": "Job security concern",
            "risk_level": "High" if probability < 50 else "Low",
            "description": "Organizational changes affecting employment",
            "impact_areas": ["career", "income", "stress"]
        })
    
    if not risks:
        risks.append({
            "factor": "General life challenges",
            "risk_level": "Low",
            "description": "Normal life uncertainties apply",
            "impact_areas": ["general"]
        })
    
    return risks


def _get_mitigation_strategies(risks: List[Dict], area: str) -> List[str]:
    """Get strategies to mitigate identified risks"""
    
    strategies = []
    
    for risk in risks:
        risk_level = risk["risk_level"]
        factor = risk["factor"]
        
        if "Mars" in factor:
            strategies.append("Practice patience and avoid conflicts")
            strategies.append("Channel energy into productive activities")
        
        if "Saturn" in factor:
            strategies.append("Be prepared for delays and have backup plans")
            strategies.append("Focus on long-term thinking and discipline")
        
        if "Rahu" in factor:
            strategies.append("Verify information carefully before acting")
            strategies.append("Avoid get-rich-quick schemes or shortcuts")
        
        if "vehicle" in factor.lower() or "motorcycle" in factor.lower():
            strategies.append("Wear proper safety gear at all times")
            strategies.append("Avoid riding in bad weather or at night")
            strategies.append("Take a defensive driving course")
            strategies.append("Regular vehicle maintenance is crucial")
        
        if "job security" in factor.lower() or "redundancy" in factor.lower():
            strategies.append("Document your achievements and contributions")
            strategies.append("Build relationships across the organization")
            strategies.append("Develop new skills to increase value")
            strategies.append("Maintain a financial safety net")
    
    if not strategies:
        strategies = [
            "Stay positive and focused on your goals",
            "Prepare thoroughly for important events",
            "Maintain good physical and mental health"
        ]
    
    return strategies[:6]


def _get_event_specific_remedies(probability: int, area: str, event_planets: Dict) -> List[str]:
    """Get remedies specific to the event"""
    
    remedies = []
    
    if probability < 60:
        # Need more remedies for lower probability
        remedies.append("Chant your personal mantra 108 times before the event")
        remedies.append("Donate to charity one day before the event")
        remedies.append("Fast or eat sattvic food on the event day")
    
    # Area-specific remedies
    if area == "love":
        remedies.append("Wear white or pink colors on the day")
        remedies.append("Carry rose quartz crystal")
        remedies.append("Offer flowers at a temple")
    
    elif area == "career":
        remedies.append("Wear yellow or orange colors on the day")
        remedies.append("Touch feet of elders for blessings")
        remedies.append("Offer water to Sun at sunrise")
    
    elif area == "wealth":
        remedies.append("Keep a clean wallet with organized bills")
        remedies.append("Donate yellow items before the event")
        remedies.append("Keep a silver coin in pocket")
    
    elif area == "health":
        remedies.append("Practice pranayama (breathing exercises)")
        remedies.append("Wear an energized rudraksha")
        remedies.append("Avoid negative thoughts and people")
    
    # Check for weak planets
    for planet, data in event_planets.items():
        if data.get("house") in [6, 8, 12]:
            if planet == "Sun":
                remedies.append("Offer water to Sun at sunrise on event day")
            elif planet == "Moon":
                remedies.append("Drink water from silver vessel")
            elif planet == "Mars":
                remedies.append("Donate red items on Tuesday before event")
            elif planet == "Jupiter":
                remedies.append("Wear yellow on the day")
    
    return remedies[:6]


def _get_lucky_factors(event_date: datetime, event_planets: Dict, natal_chart: Dict) -> Dict:
    """Get lucky factors for the day"""
    
    # Lucky colors based on day of week
    day_colors = {
        "Sunday": ["Red", "Orange", "Gold"],
        "Monday": ["White", "Silver", "Light Blue"],
        "Tuesday": ["Red", "Maroon", "Scarlet"],
        "Wednesday": ["Green", "Light Green", "Emerald"],
        "Thursday": ["Yellow", "Gold", "Cream"],
        "Friday": ["White", "Pink", "Light Blue"],
        "Saturday": ["Black", "Dark Blue", "Navy"]
    }
    
    day_name = event_date.strftime("%A")
    
    # Lucky numbers based on planets
    moon_nak = event_planets.get("Moon", {}).get("nakshatra", "")
    lucky_numbers = [1, 3, 5, 7, 9]  # Default
    
    # Lucky directions
    ascendant = natal_chart["ascendant"]["sign"]
    directions = {
        "Aries": "East", "Taurus": "South-East", "Gemini": "North",
        "Cancer": "North-West", "Leo": "East", "Virgo": "South",
        "Libra": "West", "Scorpio": "South", "Sagittarius": "North-East",
        "Capricorn": "South", "Aquarius": "West", "Pisces": "North"
    }
    
    return {
        "colors": day_colors.get(day_name, ["White", "Gold"]),
        "numbers": lucky_numbers[:5],
        "direction": directions.get(ascendant, "East"),
        "gemstone": _get_lucky_gemstone(event_planets, natal_chart),
        "deity_to_worship": _get_deity_for_area(event_planets)
    }


def _get_lucky_gemstone(event_planets: Dict, natal_chart: Dict) -> str:
    """Get lucky gemstone for the event"""
    
    # Based on ascendant
    ascendant = natal_chart["ascendant"]["sign"]
    
    gemstones = {
        "Aries": "Red Coral",
        "Taurus": "Diamond",
        "Gemini": "Emerald",
        "Cancer": "Pearl",
        "Leo": "Ruby",
        "Virgo": "Emerald",
        "Libra": "Diamond",
        "Scorpio": "Red Coral",
        "Sagittarius": "Yellow Sapphire",
        "Capricorn": "Blue Sapphire",
        "Aquarius": "Blue Sapphire",
        "Pisces": "Yellow Sapphire"
    }
    
    return gemstones.get(ascendant, "Clear Quartz")


def _get_deity_for_area(event_planets: Dict) -> str:
    """Get deity to worship based on planetary positions"""
    
    # Check which planet needs strengthening
    jupiter_house = event_planets.get("Jupiter", {}).get("house", 1)
    venus_house = event_planets.get("Venus", {}).get("house", 1)
    
    if jupiter_house in [6, 8, 12]:
        return "Lord Vishnu or Guru (Jupiter deity)"
    elif venus_house in [6, 8, 12]:
        return "Goddess Lakshmi (Venus deity)"
    else:
        return "Lord Ganesha (remover of obstacles)"


def _interpret_probability(probability: int, concern_type: str) -> str:
    """Interpret probability percentage"""
    
    if probability >= 80:
        return f"Excellent prospects for {concern_type} success. Highly favorable planetary alignment."
    elif probability >= 65:
        return f"Good chances for positive outcome in {concern_type} matters. Supportive planetary influences."
    elif probability >= 50:
        return f"Moderate probability of success. Mixed planetary influences requiring effort and preparation."
    elif probability >= 35:
        return f"Lower probability but not impossible. Challenging planetary positions requiring extra caution."
    else:
        return f"Difficult planetary configuration. Consider postponing or taking extensive precautions."


def _get_overall_recommendation(probability: int, area: str, concern_type: str) -> str:
    """Get overall recommendation"""
    
    if probability >= 75:
        return f"Proceed with confidence. This is a favorable time for {concern_type} activities. Trust your preparation and stay positive."
    elif probability >= 60:
        return f"Good time to proceed with {concern_type} plans. Prepare well and maintain realistic expectations."
    elif probability >= 45:
        return f"Proceed with caution in {concern_type} matters. Thorough preparation and backup plans recommended."
    elif probability >= 30:
        return f"Consider postponing {concern_type} activities if possible. If you must proceed, take all precautions and lower expectations."
    else:
        return f"Not favorable time for {concern_type} matters. Strong recommendation to postpone. If unavoidable, extreme caution required."


def _identify_key_strengths(natal_chart: Dict, area: str) -> List[str]:
    """Identify key strengths from natal chart relevant to area"""
    
    strengths = []
    
    planets = natal_chart.get("planets", {})
    
    # Check exalted planets
    for planet_name, planet_data in planets.items():
        if planet_data.get("is_exalted"):
            strengths.append(f"Exalted {planet_name} gives natural advantage")
    
    # Check planets in own sign
    for planet_name, planet_data in planets.items():
        if planet_data.get("dignity") == "own_sign":
            strengths.append(f"{planet_name} in own sign provides stability")
    
    # Area-specific strengths
    if area == "love":
        venus = planets.get("Venus", {})
        if venus.get("house") in [1, 5, 7, 11]:
            strengths.append("Venus well-placed for relationships")
    
    elif area == "career":
        sun = planets.get("Sun", {})
        if sun.get("house") in [1, 10, 11]:
            strengths.append("Sun favorable for career growth")
    
    elif area == "wealth":
        jupiter = planets.get("Jupiter", {})
        if jupiter.get("house") in [1, 2, 5, 9, 11]:
            strengths.append("Jupiter supports financial prosperity")
    
    if not strengths:
        strengths = ["Natural resilience and adaptability"]
    
    return strengths[:3]


def generate_daily_horoscope(birth_date: str, birth_time: str, lat: float, lon: float) -> Dict[str, Any]:
    """
    Generate daily horoscope based on Moon sign (Rashi)
    Uses current day's transits to provide personalized predictions
    """
    
    # Calculate birth chart to get Moon sign
    natal_chart = calculate_chart(birth_date, birth_time, lat, lon)
    moon_sign = natal_chart["planets"]["Moon"]["sign"]
    ascendant_sign = natal_chart["ascendant"]["sign"]
    
    # Get today's date
    today = datetime.now()
    jd = LocalCalculate.get_julian_day(today)
    ayanamsa = LocalCalculate.get_ayanamsa(jd)
    house_cusps = LocalCalculate.get_house_cusps(jd, lat, lon, ayanamsa)
    
    # Calculate today's planetary positions
    transits = {}
    for planet_name in [PlanetName.SUN, PlanetName.MOON, PlanetName.MARS,
                       PlanetName.MERCURY, PlanetName.JUPITER, PlanetName.VENUS,
                       PlanetName.SATURN]:
        planet_long = LocalCalculate.get_planet_longitude(planet_name, jd, ayanamsa)
        planet_house = LocalCalculate.get_planet_house(planet_long, house_cusps)
        planet_sign, degrees = LocalCalculate.longitude_to_sign(planet_long)
        nakshatra, pada = LocalCalculate.get_nakshatra(planet_long)
        
        transits[planet_name] = {
            "longitude": round(planet_long, 2),
            "sign": planet_sign,
            "house": planet_house,
            "degrees": round(degrees, 2),
            "nakshatra": nakshatra,
            "pada": pada
        }
    
    # Calculate Moon's current position relative to birth Moon
    moon_transit = transits["Moon"]
    moon_sign_index = ZODIAC_SIGNS.index(moon_sign)
    current_moon_index = ZODIAC_SIGNS.index(moon_transit["sign"])
    
    # Calculate which house Moon is transiting from natal Moon (Chandra Lagna)
    moon_house_from_moon = ((current_moon_index - moon_sign_index) % 12) + 1
    
    # Interpret based on Moon's transit house from natal Moon
    moon_transit_effects = {
        1: {"mood": "Confident", "energy": 8, "advice": "Good day for personal initiatives and self-expression"},
        2: {"mood": "Stable", "energy": 7, "advice": "Focus on finances and family matters"},
        3: {"mood": "Active", "energy": 8, "advice": "Communication and short travels favored"},
        4: {"mood": "Comfortable", "energy": 6, "advice": "Spend time at home, nurture emotional wellbeing"},
        5: {"mood": "Creative", "energy": 9, "advice": "Excellent for romance, creativity, and speculation"},
        6: {"mood": "Challenging", "energy": 5, "advice": "Be cautious with health and conflicts"},
        7: {"mood": "Social", "energy": 8, "advice": "Good for partnerships and collaborations"},
        8: {"mood": "Introspective", "energy": 4, "advice": "Avoid major decisions, focus on research and introspection"},
        9: {"mood": "Optimistic", "energy": 9, "advice": "Luck and fortune favor you, pursue higher goals"},
        10: {"mood": "Ambitious", "energy": 8, "advice": "Career matters highlighted, seek recognition"},
        11: {"mood": "Rewarding", "energy": 9, "advice": "Gains and fulfillment of desires indicated"},
        12: {"mood": "Reflective", "energy": 5, "advice": "Time for spirituality and letting go, avoid expenses"}
    }
    
    moon_effect = moon_transit_effects.get(moon_house_from_moon, moon_transit_effects[1])
    
    # Analyze key transits
    key_influences = []
    
    # Jupiter's influence
    jupiter_house = transits["Jupiter"]["house"]
    if jupiter_house in [1, 2, 5, 7, 9, 11]:
        key_influences.append(f"Jupiter in {jupiter_house}th house brings expansion and growth")
    
    # Saturn's influence
    saturn_house = transits["Saturn"]["house"]
    if saturn_house in [3, 6, 11]:
        key_influences.append(f"Saturn in {saturn_house}th house brings discipline and rewards for hard work")
    elif saturn_house in [1, 4, 7, 8, 10, 12]:
        key_influences.append(f"Saturn in {saturn_house}th house requires patience and perseverance")
    
    # Mars energy
    mars_house = transits["Mars"]["house"]
    if mars_house in [1, 3, 6, 10, 11]:
        key_influences.append(f"Mars in {mars_house}th house provides energy and courage")
    
    # Venus for relationships and pleasures
    venus_house = transits["Venus"]["house"]
    if venus_house in [1, 2, 5, 7, 11]:
        key_influences.append(f"Venus in {venus_house}th house enhances harmony and pleasures")
    
    # Lucky number based on day and Moon nakshatra
    day_num = today.day
    lucky_numbers = [(day_num % 9) + 1, (day_num % 9) + 2]
    
    # Lucky color based on current weekday
    weekday_colors = {
        0: "White",      # Monday - Moon
        1: "Red",        # Tuesday - Mars
        2: "Green",      # Wednesday - Mercury
        3: "Yellow",     # Thursday - Jupiter
        4: "White",      # Friday - Venus
        5: "Blue",       # Saturday - Saturn
        6: "Orange"      # Sunday - Sun
    }
    lucky_color = weekday_colors[today.weekday()]
    
    return {
        "date": today.strftime("%Y-%m-%d"),
        "day": today.strftime("%A"),
        "moon_sign": moon_sign,
        "ascendant": ascendant_sign,
        "overall_rating": moon_effect["energy"],
        "mood": moon_effect["mood"],
        "energy_level": f"{moon_effect['energy']}/10",
        "daily_advice": moon_effect["advice"],
        "key_influences": key_influences[:3],
        "current_transits": {
            "moon": f"{moon_transit['sign']} - {moon_transit['nakshatra']}",
            "sun": f"{transits['Sun']['sign']}",
            "jupiter": f"{transits['Jupiter']['sign']} (House {jupiter_house})",
            "saturn": f"{transits['Saturn']['sign']} (House {saturn_house})"
        },
        "lucky_elements": {
            "color": lucky_color,
            "numbers": lucky_numbers,
            "time": "Early morning (6-8 AM) and Evening (6-8 PM)"
        },
        "areas_of_focus": {
            "favorable": _get_favorable_areas(moon_house_from_moon, transits),
            "caution": _get_caution_areas(moon_house_from_moon, transits)
        }
    }


def generate_weekly_horoscope(birth_date: str, birth_time: str, lat: float, lon: float) -> Dict[str, Any]:
    """
    Generate weekly horoscope based on Moon sign
    Analyzes the week ahead using planetary transits
    """
    
    # Calculate birth chart
    natal_chart = calculate_chart(birth_date, birth_time, lat, lon)
    moon_sign = natal_chart["planets"]["Moon"]["sign"]
    ascendant_sign = natal_chart["ascendant"]["sign"]
    
    # Get current week dates
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    
    # Analyze mid-week (Wednesday) transits for overall week
    mid_week = week_start + timedelta(days=2)
    jd = LocalCalculate.get_julian_day(mid_week)
    ayanamsa = LocalCalculate.get_ayanamsa(jd)
    house_cusps = LocalCalculate.get_house_cusps(jd, lat, lon, ayanamsa)
    
    # Calculate planetary positions for the week
    week_transits = {}
    for planet_name in [PlanetName.SUN, PlanetName.MOON, PlanetName.MARS,
                       PlanetName.MERCURY, PlanetName.JUPITER, PlanetName.VENUS,
                       PlanetName.SATURN]:
        planet_long = LocalCalculate.get_planet_longitude(planet_name, jd, ayanamsa)
        planet_house = LocalCalculate.get_planet_house(planet_long, house_cusps)
        planet_sign, degrees = LocalCalculate.longitude_to_sign(planet_long)
        
        week_transits[planet_name] = {
            "sign": planet_sign,
            "house": planet_house,
            "degrees": round(degrees, 2)
        }
    
    # Calculate week rating based on major planet positions
    week_score = 5  # Base score
    
    # Jupiter influence
    if week_transits["Jupiter"]["house"] in [1, 2, 5, 7, 9, 11]:
        week_score += 2
    
    # Saturn influence
    if week_transits["Saturn"]["house"] in [3, 6, 11]:
        week_score += 1
    elif week_transits["Saturn"]["house"] in [8, 12]:
        week_score -= 1
    
    # Mars influence
    if week_transits["Mars"]["house"] in [3, 6, 10, 11]:
        week_score += 1
    elif week_transits["Mars"]["house"] in [8, 12]:
        week_score -= 1
    
    week_score = max(1, min(10, week_score))
    
    # Day-by-day brief predictions
    daily_highlights = []
    current_day = week_start
    
    for i in range(7):
        day_jd = LocalCalculate.get_julian_day(current_day)
        day_ayanamsa = LocalCalculate.get_ayanamsa(day_jd)
        
        # Get Moon's position for each day
        moon_long = LocalCalculate.get_planet_longitude(PlanetName.MOON, day_jd, day_ayanamsa)
        moon_sign_day, _ = LocalCalculate.longitude_to_sign(moon_long)
        nakshatra, _ = LocalCalculate.get_nakshatra(moon_long)
        
        # Simple day rating based on Moon nakshatra
        favorable_nakshatras = ["Rohini", "Pushya", "Hasta", "Shravana", "Revati", "Ashwini", "Uttara Phalguni"]
        day_quality = "Good" if nakshatra in favorable_nakshatras else "Moderate"
        
        daily_highlights.append({
            "date": current_day.strftime("%Y-%m-%d"),
            "day": current_day.strftime("%A"),
            "moon_transit": moon_sign_day,
            "nakshatra": nakshatra,
            "quality": day_quality
        })
        
        current_day += timedelta(days=1)
    
    # Weekly themes based on transit patterns
    weekly_themes = []
    
    # Check for significant aspects or patterns
    sun_house = week_transits["Sun"]["house"]
    if sun_house in [1, 5, 9, 10]:
        weekly_themes.append("Career and personal recognition highlighted")
    
    venus_house = week_transits["Venus"]["house"]
    if venus_house in [1, 5, 7]:
        weekly_themes.append("Relationships and social connections flourish")
    
    mercury_house = week_transits["Mercury"]["house"]
    if mercury_house in [1, 2, 3, 10]:
        weekly_themes.append("Communication and business matters favored")
    
    return {
        "week_period": f"{week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}",
        "moon_sign": moon_sign,
        "ascendant": ascendant_sign,
        "overall_rating": week_score,
        "week_summary": _generate_week_summary(week_score, weekly_themes),
        "weekly_themes": weekly_themes,
        "key_transits": {
            "jupiter": f"{week_transits['Jupiter']['sign']} (House {week_transits['Jupiter']['house']})",
            "saturn": f"{week_transits['Saturn']['sign']} (House {week_transits['Saturn']['house']})",
            "mars": f"{week_transits['Mars']['sign']} (House {week_transits['Mars']['house']})",
            "venus": f"{week_transits['Venus']['sign']} (House {week_transits['Venus']['house']})"
        },
        "daily_highlights": daily_highlights,
        "best_days": [d["day"] for d in daily_highlights if d["quality"] == "Good"][:3],
        "areas_to_focus": {
            "career": _rate_area_for_period("career", week_transits),
            "relationships": _rate_area_for_period("relationships", week_transits),
            "finance": _rate_area_for_period("finance", week_transits),
            "health": _rate_area_for_period("health", week_transits)
        }
    }


def generate_monthly_horoscope(birth_date: str, birth_time: str, lat: float, lon: float) -> Dict[str, Any]:
    """
    Generate monthly horoscope based on Moon sign
    Provides comprehensive monthly outlook using major transits
    """
    
    # Calculate birth chart
    natal_chart = calculate_chart(birth_date, birth_time, lat, lon)
    moon_sign = natal_chart["planets"]["Moon"]["sign"]
    ascendant_sign = natal_chart["ascendant"]["sign"]
    
    # Get current month dates
    today = datetime.now()
    month_start = datetime(today.year, today.month, 1)
    
    # Calculate last day of month
    if today.month == 12:
        month_end = datetime(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
    
    # Analyze mid-month transits
    mid_month = month_start + timedelta(days=15)
    jd = LocalCalculate.get_julian_day(mid_month)
    ayanamsa = LocalCalculate.get_ayanamsa(jd)
    house_cusps = LocalCalculate.get_house_cusps(jd, lat, lon, ayanamsa)
    
    # Calculate major planetary positions for the month
    month_transits = {}
    for planet_name in [PlanetName.SUN, PlanetName.MARS, PlanetName.MERCURY,
                       PlanetName.JUPITER, PlanetName.VENUS, PlanetName.SATURN]:
        planet_long = LocalCalculate.get_planet_longitude(planet_name, jd, ayanamsa)
        planet_house = LocalCalculate.get_planet_house(planet_long, house_cusps)
        planet_sign, degrees = LocalCalculate.longitude_to_sign(planet_long)
        is_retro = LocalCalculate.is_planet_retrograde(planet_name, jd)
        
        month_transits[planet_name] = {
            "sign": planet_sign,
            "house": planet_house,
            "degrees": round(degrees, 2),
            "retrograde": is_retro
        }
    
    # Calculate overall month rating
    month_score = 5
    
    # Jupiter's monthly influence
    jupiter_house = month_transits["Jupiter"]["house"]
    if jupiter_house in [1, 2, 5, 7, 9, 11]:
        month_score += 2
        jupiter_effect = "highly favorable"
    elif jupiter_house in [6, 8, 12]:
        jupiter_effect = "requires patience"
    else:
        jupiter_effect = "neutral"
    
    # Saturn's monthly influence
    saturn_house = month_transits["Saturn"]["house"]
    if saturn_house in [3, 6, 11]:
        month_score += 1
        saturn_effect = "rewards hard work"
    elif saturn_house in [1, 4, 7, 8, 10, 12]:
        month_score -= 1
        saturn_effect = "brings challenges requiring persistence"
    else:
        saturn_effect = "neutral"
    
    # Mars energy for the month
    mars_house = month_transits["Mars"]["house"]
    if mars_house in [3, 6, 10, 11]:
        month_score += 1
        mars_effect = "energizes"
    elif mars_house in [8, 12]:
        mars_effect = "requires caution"
    else:
        mars_effect = "moderate"
    
    month_score = max(1, min(10, month_score))
    
    # Identify key dates (New Moon and Full Moon approximations)
    key_dates = []
    
    # Find days when Moon is in same sign as natal Moon (emotional high points)
    current_check = month_start
    while current_check <= month_end:
        check_jd = LocalCalculate.get_julian_day(current_check)
        check_ayanamsa = LocalCalculate.get_ayanamsa(check_jd)
        moon_long = LocalCalculate.get_planet_longitude(PlanetName.MOON, check_jd, check_ayanamsa)
        moon_sign_check, _ = LocalCalculate.longitude_to_sign(moon_long)
        
        if moon_sign_check == moon_sign:
            key_dates.append({
                "date": current_check.strftime("%Y-%m-%d"),
                "significance": "Moon returns to your sign - good for personal matters"
            })
        
        current_check += timedelta(days=1)
    
    # Monthly themes
    monthly_themes = []
    
    sun_house = month_transits["Sun"]["house"]
    if sun_house in [1, 5, 9, 10]:
        monthly_themes.append("Personal growth and recognition")
    elif sun_house in [2, 11]:
        monthly_themes.append("Financial gains and stability")
    
    if month_transits["Venus"]["house"] in [1, 5, 7, 11]:
        monthly_themes.append("Harmonious relationships and social pleasures")
    
    if month_transits["Mercury"]["house"] in [1, 3, 6, 10]:
        monthly_themes.append("Enhanced communication and intellectual pursuits")
    
    # Check for retrograde impacts
    retrograde_planets = [p for p, data in month_transits.items() if data.get("retrograde")]
    if retrograde_planets:
        monthly_themes.append(f"{', '.join(retrograde_planets)} retrograde - review and revise")
    
    return {
        "month": month_start.strftime("%B %Y"),
        "period": f"{month_start.strftime('%B %d')} - {month_end.strftime('%B %d, %Y')}",
        "moon_sign": moon_sign,
        "ascendant": ascendant_sign,
        "overall_rating": month_score,
        "month_summary": _generate_month_summary(month_score, monthly_themes),
        "key_themes": monthly_themes[:4],
        "major_transits": {
            "jupiter": {
                "position": f"{month_transits['Jupiter']['sign']} (House {jupiter_house})",
                "effect": jupiter_effect
            },
            "saturn": {
                "position": f"{month_transits['Saturn']['sign']} (House {saturn_house})",
                "effect": saturn_effect
            },
            "mars": {
                "position": f"{month_transits['Mars']['sign']} (House {mars_house})",
                "effect": mars_effect
            }
        },
        "retrograde_planets": retrograde_planets,
        "key_dates": key_dates[:3],  # Top 3 significant dates
        "areas_forecast": {
            "career": {
                "rating": _rate_area_for_period("career", month_transits),
                "advice": _get_area_advice("career", month_transits)
            },
            "relationships": {
                "rating": _rate_area_for_period("relationships", month_transits),
                "advice": _get_area_advice("relationships", month_transits)
            },
            "finance": {
                "rating": _rate_area_for_period("finance", month_transits),
                "advice": _get_area_advice("finance", month_transits)
            },
            "health": {
                "rating": _rate_area_for_period("health", month_transits),
                "advice": _get_area_advice("health", month_transits)
            }
        },
        "lucky_days": [d["date"] for d in key_dates]
    }


# Helper functions for horoscope generation

def _get_favorable_areas(moon_house: int, transits: Dict) -> List[str]:
    """Get favorable areas based on Moon position and transits"""
    favorable = []
    
    house_areas = {
        1: ["Personal growth", "New initiatives"],
        2: ["Financial planning", "Family time"],
        3: ["Communication", "Learning"],
        4: ["Home improvement", "Emotional bonding"],
        5: ["Creative projects", "Romance"],
        6: ["Health routines", "Service"],
        7: ["Partnerships", "Negotiations"],
        8: ["Research", "Transformation"],
        9: ["Higher learning", "Travel"],
        10: ["Career advancement", "Public recognition"],
        11: ["Networking", "Achieving goals"],
        12: ["Spirituality", "Letting go"]
    }
    
    favorable = house_areas.get(moon_house, ["General wellbeing"])
    
    # Add transit-based favorable areas
    if transits["Jupiter"]["house"] in [1, 5, 9]:
        favorable.append("Learning and wisdom")
    
    return favorable[:3]


def _get_caution_areas(moon_house: int, transits: Dict) -> List[str]:
    """Get areas requiring caution"""
    caution = []
    
    if moon_house in [6, 8, 12]:
        caution.append("Avoid major commitments")
    
    if transits["Saturn"]["house"] in [8, 12]:
        caution.append("Financial caution advised")
    
    if transits["Mars"]["house"] in [6, 8, 12]:
        caution.append("Manage anger and impulsiveness")
    
    if not caution:
        caution = ["None significant"]
    
    return caution[:2]


def _generate_week_summary(rating: int, themes: List[str]) -> str:
    """Generate weekly summary text"""
    if rating >= 8:
        tone = "Excellent week ahead!"
    elif rating >= 6:
        tone = "Positive week with good opportunities."
    elif rating >= 4:
        tone = "Mixed week requiring balance."
    else:
        tone = "Challenging week - stay focused."
    
    theme_text = " ".join(themes[:2]) if themes else "General stability indicated."
    return f"{tone} {theme_text}"


def _generate_month_summary(rating: int, themes: List[str]) -> str:
    """Generate monthly summary text"""
    if rating >= 8:
        tone = "Highly favorable month!"
    elif rating >= 6:
        tone = "Promising month with growth opportunities."
    elif rating >= 4:
        tone = "Balanced month requiring mindful action."
    else:
        tone = "Challenging month - patience and perseverance needed."
    
    theme_text = " ".join(themes[:2]) if themes else "Steady progress indicated."
    return f"{tone} {theme_text}"


def _rate_area_for_period(area: str, transits: Dict) -> int:
    """Rate a life area (1-10) based on transits"""
    score = 5
    
    area_planets = {
        "career": ["Sun", "Saturn", "Jupiter"],
        "relationships": ["Venus", "Jupiter"],
        "finance": ["Jupiter", "Venus"],
        "health": ["Sun", "Mars"]
    }
    
    key_planets = area_planets.get(area, ["Jupiter"])
    
    for planet in key_planets:
        if planet in transits:
            house = transits[planet]["house"]
            if house in [1, 2, 5, 7, 9, 10, 11]:
                score += 1
            elif house in [6, 8, 12]:
                score -= 1
    
    return max(1, min(10, score))


def _get_area_advice(area: str, transits: Dict) -> str:
    """Get specific advice for a life area"""
    rating = _rate_area_for_period(area, transits)
    
    advice_map = {
        "career": {
            "high": "Excellent time for career advancement. Take initiative on important projects.",
            "medium": "Steady progress in career. Focus on building skills and relationships.",
            "low": "Career challenges require patience. Avoid major changes, focus on stability."
        },
        "relationships": {
            "high": "Harmonious period for relationships. Good time for commitments.",
            "medium": "Relationships stable. Communication is key to growth.",
            "low": "Relationships need attention. Practice patience and understanding."
        },
        "finance": {
            "high": "Financial gains indicated. Good time for investments.",
            "medium": "Financial stability maintained. Plan for future growth.",
            "low": "Financial caution advised. Avoid risks and focus on saving."
        },
        "health": {
            "high": "Good vitality and energy. Maintain healthy routines.",
            "medium": "Health stable. Regular exercise and diet important.",
            "low": "Health needs attention. Avoid stress and maintain regular checkups."
        }
    }
    
    level = "high" if rating >= 7 else "medium" if rating >= 5 else "low"
    return advice_map.get(area, {}).get(level, "Stay balanced and mindful.")