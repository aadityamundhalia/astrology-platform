"""
Local Vedic Astrology Calculator
Performs essential calculations without API calls
"""

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import math
import pytz

# Set ephemeris path (download from https://www.astro.com/ftp/swisseph/ephe/)
swe.set_ephe_path('./ephe')

class PlanetName:
    SUN = "Sun"
    MOON = "Moon"
    MARS = "Mars"
    MERCURY = "Mercury"
    JUPITER = "Jupiter"
    VENUS = "Venus"
    SATURN = "Saturn"
    RAHU = "Rahu"
    KETU = "Ketu"

class ZodiacSign:
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Swiss Ephemeris planet IDs
PLANET_IDS = {
    PlanetName.SUN: swe.SUN,
    PlanetName.MOON: swe.MOON,
    PlanetName.MARS: swe.MARS,
    PlanetName.MERCURY: swe.MERCURY,
    PlanetName.JUPITER: swe.JUPITER,
    PlanetName.VENUS: swe.VENUS,
    PlanetName.SATURN: swe.SATURN,
    PlanetName.RAHU: swe.MEAN_NODE,  # Rahu (North Node)
    PlanetName.KETU: swe.MEAN_NODE,  # Ketu (South Node - opposite of Rahu)
}

# Ayanamsa (precession correction) - Lahiri
AYANAMSA = swe.SIDM_LAHIRI


class LocalCalculate:
    """Local Vedic Astrology Calculator"""
    
    @staticmethod
    def get_julian_day(dt: datetime) -> float:
        """Convert datetime to Julian Day"""
        return swe.julday(dt.year, dt.month, dt.day, 
                         dt.hour + dt.minute/60.0 + dt.second/3600.0)
    
    @staticmethod
    def get_ayanamsa(jd: float) -> float:
        """Get Ayanamsa (precession correction) for given Julian Day"""
        swe.set_sid_mode(AYANAMSA)
        return swe.get_ayanamsa(jd)
    
    @staticmethod
    def get_planet_longitude(planet_name: str, jd: float, ayanamsa: float) -> float:
        """Get Nirayana (sidereal) longitude of planet"""
        if planet_name not in PLANET_IDS:
            raise ValueError(f"Unknown planet: {planet_name}")
        
        planet_id = PLANET_IDS[planet_name]
        result = swe.calc_ut(jd, planet_id)[0]
        
        # Get tropical longitude
        tropical_long = result[0]
        
        # Convert to sidereal (Nirayana)
        nirayana_long = tropical_long - ayanamsa
        
        # Handle Ketu (opposite of Rahu)
        if planet_name == PlanetName.KETU:
            nirayana_long = (nirayana_long + 180) % 360
        
        # Normalize to 0-360
        if nirayana_long < 0:
            nirayana_long += 360
            
        return nirayana_long
    
    @staticmethod
    def longitude_to_sign(longitude: float) -> Tuple[str, float]:
        """Convert longitude to zodiac sign and degrees in sign"""
        sign_index = int(longitude / 30)
        degrees_in_sign = longitude % 30
        return ZODIAC_SIGNS[sign_index], degrees_in_sign
    
    @staticmethod
    def get_ascendant(jd: float, lat: float, lon: float, ayanamsa: float) -> float:
        """Calculate Ascendant (Lagna)"""
        # Get houses using Placidus system
        houses = swe.houses(jd, lat, lon)[0]
        tropical_asc = houses[0]  # First house cusp is Ascendant
        
        # Convert to sidereal
        nirayana_asc = tropical_asc - ayanamsa
        if nirayana_asc < 0:
            nirayana_asc += 360
            
        return nirayana_asc
    
    @staticmethod
    def get_house_cusps(jd: float, lat: float, lon: float, ayanamsa: float) -> List[float]:
        """Get all 12 house cusps in Nirayana"""
        houses = swe.houses(jd, lat, lon)[0]
        nirayana_houses = []
        
        for house in houses:
            nirayana = house - ayanamsa
            if nirayana < 0:
                nirayana += 360
            nirayana_houses.append(nirayana)
            
        return nirayana_houses
    
    @staticmethod
    def get_planet_house(planet_long: float, house_cusps: List[float]) -> int:
        """Determine which house a planet is in"""
        for i in range(12):
            next_i = (i + 1) % 12
            start = house_cusps[i]
            end = house_cusps[next_i]
            
            # Handle wrap-around at 0/360
            if end < start:
                if planet_long >= start or planet_long < end:
                    return i + 1
            else:
                if start <= planet_long < end:
                    return i + 1
        
        return 1  # Default to 1st house
    
    @staticmethod
    def get_nakshatra(longitude: float) -> Tuple[str, int]:
        """Get Nakshatra (constellation) and pada"""
        NAKSHATRAS = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        nakshatra_index = int(longitude / 13.333333)
        pada = int((longitude % 13.333333) / 3.333333) + 1
        
        return NAKSHATRAS[nakshatra_index], pada
    
    @staticmethod
    def is_planet_retrograde(planet_name: str, jd: float) -> bool:
        """Check if planet is retrograde"""
        if planet_name in [PlanetName.SUN, PlanetName.MOON, PlanetName.RAHU, PlanetName.KETU]:
            return False  # These don't go retrograde
        
        planet_id = PLANET_IDS[planet_name]
        result = swe.calc_ut(jd, planet_id)[0]
        speed = result[3]  # Speed in longitude
        
        return speed < 0
    
    @staticmethod
    def get_lord_of_sign(sign: str) -> str:
        """Get ruling planet of a zodiac sign"""
        SIGN_LORDS = {
            "Aries": PlanetName.MARS,
            "Taurus": PlanetName.VENUS,
            "Gemini": PlanetName.MERCURY,
            "Cancer": PlanetName.MOON,
            "Leo": PlanetName.SUN,
            "Virgo": PlanetName.MERCURY,
            "Libra": PlanetName.VENUS,
            "Scorpio": PlanetName.MARS,
            "Sagittarius": PlanetName.JUPITER,
            "Capricorn": PlanetName.SATURN,
            "Aquarius": PlanetName.SATURN,
            "Pisces": PlanetName.JUPITER
        }
        return SIGN_LORDS.get(sign, "Unknown")
    
    @staticmethod
    def is_exalted(planet_name: str, longitude: float) -> bool:
        """Check if planet is exalted"""
        EXALTATION_POINTS = {
            PlanetName.SUN: (10, 10),      # 10° Aries
            PlanetName.MOON: (33, 3),       # 3° Taurus
            PlanetName.MARS: (280, 28),     # 28° Capricorn
            PlanetName.MERCURY: (165, 15),  # 15° Virgo
            PlanetName.JUPITER: (95, 5),    # 5° Cancer
            PlanetName.VENUS: (357, 27),    # 27° Pisces
            PlanetName.SATURN: (200, 20),   # 20° Libra
        }
        
        if planet_name not in EXALTATION_POINTS:
            return False
        
        exalt_long, _ = EXALTATION_POINTS[planet_name]
        sign_index = int(longitude / 30)
        exalt_sign_index = int(exalt_long / 30)
        
        return sign_index == exalt_sign_index
    
    @staticmethod
    def is_debilitated(planet_name: str, longitude: float) -> bool:
        """Check if planet is debilitated (opposite of exaltation)"""
        DEBILITATION_POINTS = {
            PlanetName.SUN: (190, 10),      # 10° Libra
            PlanetName.MOON: (213, 3),      # 3° Scorpio
            PlanetName.MARS: (100, 28),     # 28° Cancer
            PlanetName.MERCURY: (345, 15),  # 15° Pisces
            PlanetName.JUPITER: (275, 5),   # 5° Capricorn
            PlanetName.VENUS: (177, 27),    # 27° Virgo
            PlanetName.SATURN: (20, 20),    # 20° Aries
        }
        
        if planet_name not in DEBILITATION_POINTS:
            return False
        
        debil_long, _ = DEBILITATION_POINTS[planet_name]
        sign_index = int(longitude / 30)
        debil_sign_index = int(debil_long / 30)
        
        return sign_index == debil_sign_index
    
    @staticmethod
    def get_planet_relationships(planet_name: str, other_planet: str) -> str:
        """Get natural relationship between two planets"""
        RELATIONSHIPS = {
            PlanetName.SUN: {
                "friends": [PlanetName.MOON, PlanetName.MARS, PlanetName.JUPITER],
                "enemies": [PlanetName.VENUS, PlanetName.SATURN],
                "neutral": [PlanetName.MERCURY]
            },
            PlanetName.MOON: {
                "friends": [PlanetName.SUN, PlanetName.MERCURY],
                "enemies": [],
                "neutral": [PlanetName.MARS, PlanetName.JUPITER, PlanetName.VENUS, PlanetName.SATURN]
            },
            PlanetName.MARS: {
                "friends": [PlanetName.SUN, PlanetName.MOON, PlanetName.JUPITER],
                "enemies": [PlanetName.MERCURY],
                "neutral": [PlanetName.VENUS, PlanetName.SATURN]
            },
            PlanetName.MERCURY: {
                "friends": [PlanetName.SUN, PlanetName.VENUS],
                "enemies": [PlanetName.MOON],
                "neutral": [PlanetName.MARS, PlanetName.JUPITER, PlanetName.SATURN]
            },
            PlanetName.JUPITER: {
                "friends": [PlanetName.SUN, PlanetName.MOON, PlanetName.MARS],
                "enemies": [PlanetName.MERCURY, PlanetName.VENUS],
                "neutral": [PlanetName.SATURN]
            },
            PlanetName.VENUS: {
                "friends": [PlanetName.MERCURY, PlanetName.SATURN],
                "enemies": [PlanetName.SUN, PlanetName.MOON],
                "neutral": [PlanetName.MARS, PlanetName.JUPITER]
            },
            PlanetName.SATURN: {
                "friends": [PlanetName.MERCURY, PlanetName.VENUS],
                "enemies": [PlanetName.SUN, PlanetName.MOON, PlanetName.MARS],
                "neutral": [PlanetName.JUPITER]
            }
        }
        
        if planet_name not in RELATIONSHIPS:
            return "neutral"
        
        rel = RELATIONSHIPS[planet_name]
        if other_planet in rel["friends"]:
            return "friend"
        elif other_planet in rel["enemies"]:
            return "enemy"
        else:
            return "neutral"
    
    @staticmethod
    def get_complete_chart(dt: datetime, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get complete birth chart with all essential data
        Focus on: Love, Money, Health, Business, Career
        """
        
        jd = LocalCalculate.get_julian_day(dt)
        ayanamsa = LocalCalculate.get_ayanamsa(jd)
        
        # Calculate all planets
        planets = {}
        for planet_name in [PlanetName.SUN, PlanetName.MOON, PlanetName.MARS, 
                           PlanetName.MERCURY, PlanetName.JUPITER, PlanetName.VENUS, 
                           PlanetName.SATURN, PlanetName.RAHU, PlanetName.KETU]:
            
            planet_long = LocalCalculate.get_planet_longitude(planet_name, jd, ayanamsa)
            sign, degrees = LocalCalculate.longitude_to_sign(planet_long)
            nakshatra, pada = LocalCalculate.get_nakshatra(planet_long)
            
            planets[planet_name] = {
                "longitude": planet_long,
                "sign": sign,
                "degrees_in_sign": degrees,
                "nakshatra": nakshatra,
                "nakshatra_pada": pada,
                "lord_of_sign": LocalCalculate.get_lord_of_sign(sign),
                "is_retrograde": LocalCalculate.is_planet_retrograde(planet_name, jd),
                "is_exalted": LocalCalculate.is_exalted(planet_name, planet_long),
                "is_debilitated": LocalCalculate.is_debilitated(planet_name, planet_long),
            }
        
        # Calculate Ascendant and Houses
        asc_long = LocalCalculate.get_ascendant(jd, lat, lon, ayanamsa)
        asc_sign, asc_degrees = LocalCalculate.longitude_to_sign(asc_long)
        house_cusps = LocalCalculate.get_house_cusps(jd, lat, lon, ayanamsa)
        
        # Assign planets to houses
        for planet_name, planet_data in planets.items():
            planet_house = LocalCalculate.get_planet_house(planet_data["longitude"], house_cusps)
            planet_data["house"] = planet_house
        
        # Prepare houses data
        houses = {}
        for i in range(12):
            house_num = i + 1
            house_sign, _ = LocalCalculate.longitude_to_sign(house_cusps[i])
            
            # Find planets in this house
            planets_in_house = [p for p, data in planets.items() if data["house"] == house_num]
            
            houses[f"House_{house_num}"] = {
                "sign": house_sign,
                "cusp_longitude": house_cusps[i],
                "lord": LocalCalculate.get_lord_of_sign(house_sign),
                "planets": planets_in_house
            }
        
        # Key interpretations for queries
        interpretations = {
            "love_and_marriage": {
                "7th_house": houses["House_7"],
                "7th_lord": houses["House_7"]["lord"],
                "venus": planets[PlanetName.VENUS],
                "moon": planets[PlanetName.MOON],
            },
            "money_and_wealth": {
                "2nd_house": houses["House_2"],
                "11th_house": houses["House_11"],
                "2nd_lord": houses["House_2"]["lord"],
                "11th_lord": houses["House_11"]["lord"],
                "jupiter": planets[PlanetName.JUPITER],
                "venus": planets[PlanetName.VENUS],
            },
            "career_and_business": {
                "10th_house": houses["House_10"],
                "10th_lord": houses["House_10"]["lord"],
                "sun": planets[PlanetName.SUN],
                "saturn": planets[PlanetName.SATURN],
                "mercury": planets[PlanetName.MERCURY],
            },
            "health": {
                "1st_house": houses["House_1"],
                "6th_house": houses["House_6"],
                "8th_house": houses["House_8"],
                "sun": planets[PlanetName.SUN],
                "moon": planets[PlanetName.MOON],
            }
        }
        
        return {
            "birth_details": {
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M:%S"),
                "latitude": lat,
                "longitude": lon,
                "julian_day": jd,
                "ayanamsa": ayanamsa
            },
            "ascendant": {
                "longitude": asc_long,
                "sign": asc_sign,
                "degrees": asc_degrees
            },
            "planets": planets,
            "houses": houses,
            "interpretations": interpretations
        }


# Convenience function for API
def calculate_chart(date_of_birth: str, time_of_birth: str, 
                   latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Calculate complete birth chart
    
    Args:
        date_of_birth: Format "YYYY-MM-DD"
        time_of_birth: Format "HH:MM"
        latitude: Latitude of birth place
        longitude: Longitude of birth place
    
    Returns:
        Complete birth chart dictionary
    """
    # Parse datetime
    date_str = f"{date_of_birth} {time_of_birth}"
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    
    # Calculate chart
    chart = LocalCalculate.get_complete_chart(dt, latitude, longitude)
    
    return chart