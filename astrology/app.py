# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import requests
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, Any
from local_calculate import LocalCalculate, calculate_chart
from predictions import generate_yearly_predictions
import logging
import logging.handlers
from pathlib import Path
import traceback
import json
from lottery_predictions import (
    generate_lottery_predictions,
    generate_all_lottery_predictions,
    LOTTERY_CONFIGS
)

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.handlers.RotatingFileHandler(
            logs_dir / 'app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
    ]
)

# Add error handler separately
error_handler = logging.handlers.RotatingFileHandler(
    logs_dir / 'errors.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(error_handler)

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()

app = FastAPI(title="Vedic Astrology API - Local", debug=True)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Vedic Astrology API",
        "version": "2.2.0",
        "status": "running",
        "documentation": "/docs",
        "endpoints": {
            "charts": ["/chart/complete", "/chart/quick"],
            "predictions": [
                "/predictions/today",
                "/predictions/week", 
                "/predictions/month",
                "/predictions/quarter",
                "/predictions/yearly"
            ],
            "area_specific": [
                "/predictions/love",
                "/predictions/career",
                "/predictions/wealth",
                "/predictions/health"
            ],
            "wildcard": "/predictions/wildcard",
            "lottery": ["/lottery/types", "/lottery/predict", "/lottery/predict-all"]
        }
    }

# Exception handler middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    try:
        response = await call_next(request)
        
        # Log successful requests
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Request: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s - Client: {request.client.host if request.client else 'unknown'}")
        
        return response
    except Exception as e:
        # Log the full error details
        process_time = (datetime.now() - start_time).total_seconds()
        error_details = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": request.client.host if request.client else None,
            "process_time": f"{process_time:.3f}s",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }
        
        root_logger.error(f"Unhandled exception: {json.dumps(error_details, indent=2)}")
        
        # Re-raise the exception to let FastAPI handle it
        raise

# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full error details
    error_details = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client": request.client.host if request.client else None,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "traceback": traceback.format_exc()
    }
    
    root_logger.error(f"Unhandled exception in route handler: {json.dumps(error_details, indent=2)}")
    
    # Return a 500 error response
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

class BirthData(BaseModel):
    date_of_birth: str  # YYYY-MM-DD
    time_of_birth: str  # HH:MM
    place_of_birth: str

class PredictionRequest(BaseModel):
    date_of_birth: str  # YYYY-MM-DD
    time_of_birth: str  # HH:MM
    place_of_birth: str
    start_date: str = None  # Optional: YYYY-MM-DD (default: today)
    end_date: str = None  # Optional: YYYY-MM-DD (default: 6 months from start_date)


def geocode_location(place: str) -> tuple[float, float]:
    """Geocode place name to lat/lon coordinates"""
    place = place.title()
    
    geocode_url = (
        f"https://nominatim.openstreetmap.org/search?q={place}"
        "&format=json&limit=1"
    )
    
    try:
        response = requests.get(
            geocode_url,
            headers={'User-Agent': 'astro-app'},
            timeout=10
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Geocode failed: {str(e)}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Geocode error: {response.status_code}")
    
    try:
        data = response.json()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid geocode response")
    
    if not data:
        raise HTTPException(status_code=400, detail=f"Place not found: {place}")
    
    location = data[0]
    lat = float(location['lat'])
    lon = float(location['lon'])
    
    return lat, lon

@app.post("/chart/complete")
def get_complete_chart(data: BirthData) -> Dict[str, Any]:
    """
    Get Complete Birth Chart - Comprehensive Astrological Analysis
    
    USE THIS WHEN: User asks for complete birth chart, full horoscope, or detailed planetary positions.
    
    RETURNS: Complete natal chart including:
    - All 9 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
    - Planetary positions in signs, houses, and nakshatras
    - Ascendant (Lagna) details
    - All 12 houses with their lords and occupants
    - Pre-analyzed interpretations for love, wealth, career, and health
    
    EXAMPLE QUERIES:
    - "Show me my complete birth chart"
    - "What does my horoscope say?"
    - "Give me full astrological analysis"
    - "Tell me about all my planetary positions"
    
    INPUT FORMAT:
    {
        "date_of_birth": "YYYY-MM-DD",
        "time_of_birth": "HH:MM",
        "place_of_birth": "City, State/Country"
    }
    """
    try:
        # Geocode location
        lat, lon = geocode_location(data.place_of_birth)
        
        # Calculate chart
        chart = calculate_chart(
            data.date_of_birth,
            data.time_of_birth,
            lat,
            lon
        )
        
        # Add location info
        chart["location"] = {
            "place": data.place_of_birth,
            "latitude": lat,
            "longitude": lon
        }
        
        return chart
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.post("/chart/quick")
def get_quick_chart(data: BirthData) -> Dict[str, Any]:
    """
    Get essential chart data - faster response.
    Returns: Ascendant, Moon sign, Sun sign, and basic planetary positions.
    """
    try:
        lat, lon = geocode_location(data.place_of_birth)
        
        # Parse datetime
        dt_str = f"{data.date_of_birth} {data.time_of_birth}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        
        # Calculate essentials
        jd = LocalCalculate.get_julian_day(dt)
        ayanamsa = LocalCalculate.get_ayanamsa(jd)
        
        # Get ascendant
        asc_long = LocalCalculate.get_ascendant(jd, lat, lon, ayanamsa)
        asc_sign, _ = LocalCalculate.longitude_to_sign(asc_long)
        
        # Get Moon sign
        moon_long = LocalCalculate.get_planet_longitude("Moon", jd, ayanamsa)
        moon_sign, _ = LocalCalculate.longitude_to_sign(moon_long)
        
        # Get Sun sign
        sun_long = LocalCalculate.get_planet_longitude("Sun", jd, ayanamsa)
        sun_sign, _ = LocalCalculate.longitude_to_sign(sun_long)
        
        return {
            "ascendant_sign": asc_sign,
            "moon_sign": moon_sign,
            "sun_sign": sun_sign,
            "location": data.place_of_birth
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/today")
def today_prediction(data: BirthData) -> Dict[str, Any]:
    """
    Today's Prediction - Daily Forecast (Ultra Fast)
    
    USE THIS WHEN: User asks about "today", "right now", or needs immediate daily guidance.
    
    RETURNS: Detailed today's analysis including:
    - Overall rating for today (1-10)
    - Current planetary transits affecting user today
    - Scores for love, career, wealth, health today
    - Moon phase and its effects
    - Auspicious and inauspicious times today
    - Best activities for today
    - Things to avoid today
    - Quick actionable advice
    
    EXAMPLE QUERIES:
    - "How is today for me?"
    - "What should I do today?"
    - "Is today auspicious?"
    - "Should I start something today?"
    - "How's my day looking?"
    - "Give me today's horoscope"
    - "What's the best time today?"
    
    WHAT YOU GET:
    - Fastest response (only today's calculations)
    - Hour-by-hour guidance if needed
    - Immediate actionable insights
    - Perfect for daily decision-making
    
    NOTE: Most focused and fastest endpoint. Use for immediate daily guidance.
    """
    try:
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        from predictions import PredictionEngine
        
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        # Get today's transit prediction
        predictions = PredictionEngine.get_transit_predictions(
            chart, today, tomorrow, lat, lon
        )
        
        today_data = predictions[0] if predictions else {}
        
        # Add enhanced daily info
        jd = LocalCalculate.get_julian_day(today)
        ayanamsa = LocalCalculate.get_ayanamsa(jd)
        
        # Get current Moon position for daily mood
        moon_long = LocalCalculate.get_planet_longitude("Moon", jd, ayanamsa)
        moon_sign, _ = LocalCalculate.longitude_to_sign(moon_long)
        moon_nakshatra, _ = LocalCalculate.get_nakshatra(moon_long)
        
        return {
            "date": today.strftime("%Y-%m-%d"),
            "day_of_week": today.strftime("%A"),
            "prediction": today_data,
            "moon_transit": {
                "sign": moon_sign,
                "nakshatra": moon_nakshatra,
                "influence": "Emotional and mental state influenced by Moon in " + moon_sign
            },
            "birth_details": {
                "ascendant": chart["ascendant"]["sign"],
                "moon_sign": chart["planets"]["Moon"]["sign"]
            },
            "quick_advice": today_data.get("summary", "Focus on the present moment.")
        }
        
    except Exception as e:
        # Log the error before raising HTTPException
        root_logger.error(f"Error in today_prediction: {str(e)} - Birth data: {data.dict()}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/week")
def week_prediction(data: BirthData) -> Dict[str, Any]:
    """
    This Week's Prediction - 7-Day Forecast
    
    USE THIS WHEN: User asks about "this week", "next 7 days", or short-term weekly planning.
    
    RETURNS: Detailed weekly forecast including:
    - Overall rating for the week (1-10)
    - Day-by-day breakdown with ratings
    - Best days and challenging days this week
    - Weekly planetary movements
    - Scores for love, career, wealth, health for the week
    - Important transits affecting this week
    - Day-wise recommendations
    - Best day for important activities
    
    EXAMPLE QUERIES:
    - "How is this week for me?"
    - "What does this week look like?"
    - "When should I do [activity] this week?"
    - "Which day is best this week?"
    - "Give me weekly predictions"
    - "How will next 7 days be?"
    - "What to expect this week?"
    
    PERFECT FOR:
    - Weekly planning and scheduling
    - Identifying best days for activities
    - Short-term decision making
    - Meeting and event planning
    - Daily task prioritization
    
    NOTE: Balanced between detail and speed. Great for weekly guidance.
    """
    try:
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        from predictions import PredictionEngine
        
        today = datetime.now()
        week_end = today + timedelta(days=7)
        
        # Get predictions for each day of the week
        daily_predictions = []
        current = today
        
        while current < week_end:
            next_day = current + timedelta(days=1)
            day_pred = PredictionEngine.get_transit_predictions(
                chart, current, next_day, lat, lon
            )
            
            if day_pred:
                daily_predictions.append({
                    "date": current.strftime("%Y-%m-%d"),
                    "day": current.strftime("%A"),
                    "rating": day_pred[0]["overall_rating"],
                    "key_areas": day_pred[0]["key_areas"],
                    "summary": day_pred[0]["summary"]
                })
            
            current = next_day
        
        # Calculate weekly overview
        if daily_predictions:
            avg_rating = sum(d["rating"] for d in daily_predictions) / len(daily_predictions)
            best_day = max(daily_predictions, key=lambda x: x["rating"])
            worst_day = min(daily_predictions, key=lambda x: x["rating"])
        else:
            avg_rating = 5
            best_day = worst_day = None
        
        return {
            "week_period": f"{today.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
            "weekly_rating": round(avg_rating, 1),
            "best_day": best_day,
            "challenging_day": worst_day,
            "daily_breakdown": daily_predictions,
            "birth_details": {
                "ascendant": chart["ascendant"]["sign"],
                "moon_sign": chart["planets"]["Moon"]["sign"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/quarter")
def quarter_prediction(data: BirthData) -> Dict[str, Any]:
    """
    This Quarter's Prediction - 3-Month Forecast
    
    USE THIS WHEN: User asks about "this quarter", "next 3 months", or medium-term planning.
    
    RETURNS: Comprehensive quarterly forecast including:
    - Overall rating for the quarter (1-10)
    - Month-by-month breakdown for 3 months
    - Best month and challenging month
    - Major planetary transits this quarter
    - Scores for love, career, wealth, health per month
    - Important events and timing
    - Business quarter planning insights
    - Key opportunities and challenges
    
    EXAMPLE QUERIES:
    - "How is this quarter looking?"
    - "Next 3 months predictions"
    - "What's coming in Q1/Q2/Q3/Q4?"
    - "Business forecast for this quarter"
    - "When should I launch my project?"
    - "Best time in next 3 months for [activity]"
    - "Quarterly outlook please"
    
    PERFECT FOR:
    - Business planning and strategy
    - Quarterly goal setting
    - Project timing and launches
    - Medium-term investments
    - Career moves and transitions
    - Major life decisions
    
    NOTE: Ideal for business professionals and strategic planning.
    """
    try:
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        from predictions import PredictionEngine
        
        today = datetime.now()
        quarter_end = today + timedelta(days=90)  # Approximately 3 months
        
        # Get monthly predictions for the quarter
        predictions = PredictionEngine.get_transit_predictions(
            chart, today, quarter_end, lat, lon
        )
        
        # Take first 3 months
        quarterly_predictions = predictions[:3] if len(predictions) >= 3 else predictions
        
        # Calculate quarter overview
        if quarterly_predictions:
            avg_rating = sum(p["overall_rating"] for p in quarterly_predictions) / len(quarterly_predictions)
            best_month = max(quarterly_predictions, key=lambda x: x["overall_rating"])
            worst_month = min(quarterly_predictions, key=lambda x: x["overall_rating"])
            
            # Aggregate scores by area
            area_trends = {}
            for area in ["love", "career", "wealth", "health"]:
                scores = [p["key_areas"][area]["score"] for p in quarterly_predictions]
                area_trends[area] = {
                    "average_score": round(sum(scores) / len(scores), 1),
                    "trend": "improving" if scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable"
                }
        else:
            avg_rating = 5
            best_month = worst_month = None
            area_trends = {}
        
        # Determine current quarter
        current_quarter = (today.month - 1) // 3 + 1
        
        return {
            "quarter": f"Q{current_quarter} {today.year}",
            "period": f"{today.strftime('%B %Y')} - {quarter_end.strftime('%B %Y')}",
            "quarterly_rating": round(avg_rating, 1),
            "best_month": {
                "month": best_month["month"],
                "rating": best_month["overall_rating"]
            } if best_month else None,
            "challenging_month": {
                "month": worst_month["month"],
                "rating": worst_month["overall_rating"]
            } if worst_month else None,
            "area_trends": area_trends,
            "monthly_breakdown": quarterly_predictions,
            "birth_details": {
                "ascendant": chart["ascendant"]["sign"],
                "moon_sign": chart["planets"]["Moon"]["sign"]
            },
            "strategic_advice": f"Quarter rating: {round(avg_rating, 1)}/10. Focus on planning during best month and caution during challenging periods."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/yearly")
def yearly_predictions(data: BirthData) -> Dict[str, Any]:
    """
    12-Month Predictions - Complete Yearly Forecast
    
    USE THIS WHEN: User asks about future, upcoming year, monthly predictions, or "what's coming".
    
    RETURNS: Comprehensive 12-month forecast including:
    - Monthly predictions for next 12 months with ratings (1-10)
    - Transit effects for all major planets
    - Best months for love, career, wealth, and health
    - Challenging months to be cautious
    - Specific events and their timing
    - Area-wise scores (love/career/wealth/health) for each month
    - Actionable advice for each life area
    - Yearly overview with trends and guidance
    
    EXAMPLE QUERIES:
    - "What does this year look like for me?"
    - "When should I get married this year?"
    - "Which months are good for business?"
    - "Tell me my predictions for next year"
    - "When will I make money?"
    - "What's coming in my future?"
    - "How will next 12 months be?"
    
    HOW TO USE THE DATA:
    - overall_rating 8-10 = Excellent month
    - overall_rating 6-7 = Good month
    - overall_rating 4-5 = Average/mixed month
    - overall_rating 1-3 = Challenging month
    - Check key_areas scores for specific life aspects
    - Use best_months for important decisions/events
    - Avoid challenging_months for major initiatives
    """
    try:
        lat, lon = geocode_location(data.place_of_birth)
        
        # Get natal chart
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        # Generate predictions
        predictions = generate_yearly_predictions(chart, lat, lon)
        
        # Add birth details for context
        predictions["birth_details"] = {
            "date": data.date_of_birth,
            "time": data.time_of_birth,
            "place": data.place_of_birth,
            "ascendant": chart["ascendant"]["sign"],
            "moon_sign": chart["planets"]["Moon"]["sign"],
            "sun_sign": chart["planets"]["Sun"]["sign"]
        }
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/current-month")
def current_month_prediction(data: BirthData) -> Dict[str, Any]:
    """
    Current Month Prediction - Immediate Forecast (Fast Response)
    
    USE THIS WHEN: User asks about "this month", "now", "currently", or needs quick immediate guidance.
    
    RETURNS: Detailed current month analysis including:
    - Overall rating for this month (1-10)
    - All planetary transits affecting user now
    - Scores for love, career, wealth, health this month
    - Specific events and their effects this month
    - Transit descriptions for each planet
    - AI-friendly summary for quick interpretation
    - Best areas to focus on right now
    - Areas requiring caution this month
    
    EXAMPLE QUERIES:
    - "How is this month for me?"
    - "What should I focus on right now?"
    - "Is this a good time to start something?"
    - "How is my career this month?"
    - "Should I make a decision now?"
    - "What's happening currently in my life?"
    - "Give me quick guidance for now"
    
    ADVANTAGES OVER YEARLY:
    - Much faster response (only calculates 1 month)
    - More detailed transit analysis for current period
    - Perfect for immediate decision-making
    - Less data = easier for LLM to process quickly
    
    NOTE: This is optimized for speed. Use yearly_predictions for long-term planning.
    """
    try:
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        # Generate just current month
        from predictions import PredictionEngine
        
        today = datetime.now()
        end_of_month = today + timedelta(days=30)
        
        predictions = PredictionEngine.get_transit_predictions(
            chart, today, end_of_month, lat, lon
        )
        
        return {
            "current_month": predictions[0] if predictions else {},
            "birth_details": {
                "ascendant": chart["ascendant"]["sign"],
                "moon_sign": chart["planets"]["Moon"]["sign"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/yearly")
def get_yearly_predictions(data: BirthData) -> Dict[str, Any]:
    """
    Get predictions for next 12 months.
    Optimized for LLM to guide users on their life path.
    Includes: monthly forecasts, best/worst months, trends for love/career/wealth/health.
    """
    try:
        lat, lon = geocode_location(data.place_of_birth)
        
        # Get natal chart
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        # Generate predictions
        predictions = generate_yearly_predictions(chart, lat, lon)
        
        # Add birth details for context
        predictions["birth_details"] = {
            "date": data.date_of_birth,
            "time": data.time_of_birth,
            "place": data.place_of_birth,
            "ascendant": chart["ascendant"]["sign"],
            "moon_sign": chart["planets"]["Moon"]["sign"],
            "sun_sign": chart["planets"]["Sun"]["sign"]
        }
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/current-month")
def get_current_month_prediction(data: BirthData) -> Dict[str, Any]:
    """
    Get detailed prediction for current month only.
    Faster response for immediate guidance.
    """
    try:
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        # Generate just current month
        from datetime import datetime, timedelta
        from predictions import PredictionEngine
        
        today = datetime.now()
        end_of_month = today + timedelta(days=30)
        
        predictions = PredictionEngine.get_transit_predictions(
            chart, today, end_of_month, lat, lon
        )
        
        return {
            "current_month": predictions[0] if predictions else {},
            "birth_details": {
                "ascendant": chart["ascendant"]["sign"],
                "moon_sign": chart["planets"]["Moon"]["sign"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/love")
def predict_love_24months(data: PredictionRequest) -> Dict[str, Any]:
    """
    Love & Relationship Predictions with Custom Date Range
    
    USE THIS WHEN: User asks about future love life, relationships, marriage timing, or romance prospects.
    
    RETURNS: Comprehensive love forecast including:
    - Month-by-month love ratings (1-10) with precise date ranges
    - Best months for marriage, proposals, or starting relationships
    - Challenging periods in relationships and how to overcome them
    - Venus transits through all 12 houses with exact dates
    - Jupiter aspects affecting 7th house (marriage house)
    - Specific dates for important relationship events
    - Remedies and advice for difficult periods
    - Lucky dates for love-related activities
    
    INPUT:
    - date_of_birth, time_of_birth, place_of_birth (required)
    - start_date (optional, defaults to today)
    - end_date (optional, defaults to 6 months from start_date)
    
    EXAMPLE QUERIES:
    - "When should I get married in the next 6 months?"
    - "What are my relationship prospects from January to December 2026?"
    - "How is my love life looking in the coming months?"
    """
    try:
        from predictions import generate_area_specific_predictions
        
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        # Parse dates or use defaults
        start_date = datetime.strptime(data.start_date, "%Y-%m-%d") if data.start_date else datetime.now()
        
        if data.end_date:
            end_date = datetime.strptime(data.end_date, "%Y-%m-%d")
        else:
            end_date = start_date + timedelta(days=180)  # 6 months default
        
        # Calculate number of months
        months = ((end_date.year - start_date.year) * 12 + end_date.month - start_date.month)
        months = max(1, months)  # At least 1 month
        
        if months > 12:
            raise HTTPException(status_code=400, detail="Max 12 months")
        
        predictions = generate_area_specific_predictions(
            chart, lat, lon, "love", months=months, start_date=start_date
        )
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error in predict_love_24months: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/health")
def predict_health_24months(data: PredictionRequest) -> Dict[str, Any]:
    """
    Health & Wellness Predictions with Custom Date Range
    
    USE THIS WHEN: User asks about future health, wellness timing, medical procedures, or health precautions.
    
    RETURNS: Comprehensive health forecast including:
    - Month-by-month health ratings (1-10) with precise date ranges
    - Vulnerable periods requiring health precautions
    - Best months for medical procedures or surgeries
    - Sun and Moon transits affecting vitality
    - 6th house (disease) and 8th house (chronic) transit effects
    - Specific dates to be cautious about health
    - Remedies and preventive measures for challenging times
    - Best periods for starting fitness regimes
    
    INPUT:
    - date_of_birth, time_of_birth, place_of_birth (required)
    - start_date (optional, defaults to today)
    - end_date (optional, defaults to 6 months from start_date)
    
    EXAMPLE QUERIES:
    - "When should I schedule my surgery?"
    - "What months should I be careful about my health?"
    - "When is the best time to start exercising?"
    """
    try:
        from predictions import generate_area_specific_predictions
        
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        # Parse dates or use defaults
        start_date = datetime.strptime(data.start_date, "%Y-%m-%d") if data.start_date else datetime.now()
        
        if data.end_date:
            end_date = datetime.strptime(data.end_date, "%Y-%m-%d")
        else:
            end_date = start_date + timedelta(days=180)  # 6 months default
        
        # Calculate number of months
        months = ((end_date.year - start_date.year) * 12 + end_date.month - start_date.month)
        months = max(1, months)  # At least 1 month
        
        if months > 12:
            raise HTTPException(status_code=400, detail="Max 12 months")
        
        predictions = generate_area_specific_predictions(
            chart, lat, lon, "health", months=months, start_date=start_date
        )
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error in predict_health_24months: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/career")
def predict_career_24months(data: PredictionRequest) -> Dict[str, Any]:
    """
    Career & Professional Predictions with Custom Date Range
    
    USE THIS WHEN: User asks about career prospects, job changes, promotions, or business timing.
    
    RETURNS: Comprehensive career forecast including:
    - Month-by-month career ratings (1-10) with precise date ranges
    - Best months for job changes, promotions, or starting business
    - Challenging periods at work and how to navigate them
    - Saturn and Jupiter transits affecting 10th house (career)
    - Sun transits for authority and recognition
    - Specific dates for important career decisions
    - Strategies for overcoming professional obstacles
    - Best timing for negotiations and interviews
    
    INPUT:
    - date_of_birth, time_of_birth, place_of_birth (required)
    - start_date (optional, defaults to today)
    - end_date (optional, defaults to 6 months from start_date)
    
    EXAMPLE QUERIES:
    - "When should I ask for a promotion?"
    - "Is it a good time to change jobs?"
    - "When should I start my business?"
    """
    try:
        from predictions import generate_area_specific_predictions
        
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        # Parse dates or use defaults
        start_date = datetime.strptime(data.start_date, "%Y-%m-%d") if data.start_date else datetime.now()
        
        if data.end_date:
            end_date = datetime.strptime(data.end_date, "%Y-%m-%d")
        else:
            end_date = start_date + timedelta(days=180)  # 6 months default
        
        # Calculate number of months
        months = ((end_date.year - start_date.year) * 12 + end_date.month - start_date.month)
        months = max(1, months)  # At least 1 month
        
        if months > 12:
            raise HTTPException(status_code=400, detail="Max 12 months")
        
        predictions = generate_area_specific_predictions(
            chart, lat, lon, "career", months=months, start_date=start_date
        )
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error in predict_career_24months: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/predictions/wealth")
def predict_wealth_24months(data: PredictionRequest) -> Dict[str, Any]:
    """
    Wealth & Financial Predictions with Custom Date Range
    
    USE THIS WHEN: User asks about financial prospects, investment timing, income growth, or money matters.
    
    RETURNS: Comprehensive financial forecast including:
    - Month-by-month wealth ratings (1-10) with precise date ranges
    - Best months for investments, business deals, or financial gains
    - Periods of financial challenges and mitigation strategies
    - Jupiter and Venus transits affecting 2nd house (wealth) and 11th house (gains)
    - Specific dates for important financial decisions
    - Risk periods for investments and expenses
    - Remedies for financial difficulties
    - Lucky periods for monetary growth
    
    INPUT:
    - date_of_birth, time_of_birth, place_of_birth (required)
    - start_date (optional, defaults to today)
    - end_date (optional, defaults to 6 months from start_date)
    
    EXAMPLE QUERIES:
    - "When should I invest in property?"
    - "What months are good for business deals?"
    - "When will I make money?"
    """
    try:
        from predictions import generate_area_specific_predictions
        
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        # Parse dates or use defaults
        start_date = datetime.strptime(data.start_date, "%Y-%m-%d") if data.start_date else datetime.now()
        
        if data.end_date:
            end_date = datetime.strptime(data.end_date, "%Y-%m-%d")
        else:
            end_date = start_date + timedelta(days=180)  # 6 months default
        
        # Calculate number of months
        months = ((end_date.year - start_date.year) * 12 + end_date.month - start_date.month)
        months = max(1, months)  # At least 1 month
        
        if months > 12:
            raise HTTPException(status_code=400, detail="Max 12 months")
        
        predictions = generate_area_specific_predictions(
            chart, lat, lon, "wealth", months=months, start_date=start_date
        )
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error in predict_wealth_24months: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


class SpecificQueryData(BaseModel):
    date_of_birth: str  # YYYY-MM-DD
    time_of_birth: str  # HH:MM
    place_of_birth: str
    query: str  # Natural language query
    specific_date: str = None  # Optional: YYYY-MM-DD for date-specific queries


@app.post("/predictions/wildcard")
def wildcard_prediction(data: SpecificQueryData) -> Dict[str, Any]:
    """
    Wildcard Prediction - Extreme Precision for Specific Queries & Events
    
    USE THIS WHEN: User asks very specific questions about particular dates, events, or situations.
    
    THIS IS THE MOST POWERFUL ENDPOINT - Performs detailed calculations for:
    - Specific date queries (e.g., "I'm going on a date on Oct 20th")
    - Event-based predictions (e.g., "job interview on Dec 15th")
    - Activity timing (e.g., "buying a motorcycle", "starting a business")
    - Situation analysis (e.g., "company redundancy in December")
    - Risk assessment (e.g., "chances of safety", "probability of success")
    
    RETURNS: Ultra-precise analysis including:
    - Success probability rating (0-100%)
    - Day-specific planetary positions and their effects
    - Muhurta (auspicious timing) analysis for the event
    - Beneficial and malefic influences on that specific day
    - Risk factors and mitigation strategies
    - Best time of day for the activity (hour-level precision)
    - Remedies to enhance positive outcomes
    - Detailed advice on how to proceed
    - Lucky colors, numbers, directions for that day
    
    EXAMPLE QUERIES:
    - "I'm going on a date on October 20th, what are my chances to get lucky?"
    - "My company is going through redundancy in December 2025, will I be safe?"
    - "I'm buying a motorcycle on November 5th, will I be safe riding it?"
    - "Should I sign a contract on January 15th, 2026?"
    - "I have a job interview on March 3rd, 2025, how will it go?"
    - "Planning to propose on Valentine's Day 2025, good idea?"
    - "Starting a new business on April 1st, 2025, will it succeed?"
    
    INPUT FORMAT:
    {
        "date_of_birth": "YYYY-MM-DD",
        "time_of_birth": "HH:MM",
        "place_of_birth": "City, Country",
        "query": "Your specific question in natural language",
        "specific_date": "YYYY-MM-DD" (optional, extracted from query if not provided)
    }
    
    CALCULATION DEPTH:
    - Transit positions for all 9 planets on the specific date
    - Dasha periods active on that date
    - Aspects and yogas forming on that date
    - Ashtakavarga scores for that date
    - Panchanga (5 limbs) analysis
    - Tarabala and Chandrabala calculations
    - House activation and timing
    - Specific event muhurta quality
    """
    try:
        from predictions import generate_wildcard_prediction
        
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        
        prediction = generate_wildcard_prediction(
            natal_chart=chart,
            lat=lat,
            lon=lon,
            query=data.query,
            specific_date=data.specific_date
        )
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/horoscope/daily")
def daily_horoscope(data: BirthData) -> Dict[str, Any]:
    """
    Daily Horoscope - Personalized Daily Predictions
    
    Based on:
    - Moon sign (Rashi) transits
    - Current planetary positions
    - Daily nakshatra effects
    - Chandra Lagna (Moon-based house system)
    
    Provides:
    - Overall daily rating (1-10)
    - Mood and energy level forecast
    - Lucky elements (colors, numbers, times)
    - Favorable and cautionary areas
    - Key planetary influences for the day
    - Practical daily advice
    
    Example:
    {
        "date_of_birth": "1990-05-15",
        "time_of_birth": "14:30",
        "place_of_birth": "New Delhi, India"
    }
    """
    try:
        from predictions import generate_daily_horoscope
        
        lat, lon = geocode_location(data.place_of_birth)
        
        horoscope = generate_daily_horoscope(
            birth_date=data.date_of_birth,
            birth_time=data.time_of_birth,
            lat=lat,
            lon=lon
        )
        
        return horoscope
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/horoscope/weekly")
def weekly_horoscope(data: BirthData) -> Dict[str, Any]:
    """
    Weekly Horoscope - Week Ahead Predictions
    
    Based on:
    - Major planetary transits for the week
    - Moon's weekly journey through signs
    - Daily nakshatra quality ratings
    - Weekly thematic patterns
    
    Provides:
    - Overall weekly rating (1-10)
    - Weekly summary and key themes
    - Day-by-day highlights with Moon positions
    - Best days of the week
    - Area-wise focus (career, relationships, finance, health)
    - Major transit influences
    
    Example:
    {
        "date_of_birth": "1990-05-15",
        "time_of_birth": "14:30",
        "place_of_birth": "New Delhi, India"
    }
    """
    try:
        from predictions import generate_weekly_horoscope
        
        lat, lon = geocode_location(data.place_of_birth)
        
        horoscope = generate_weekly_horoscope(
            birth_date=data.date_of_birth,
            birth_time=data.time_of_birth,
            lat=lat,
            lon=lon
        )
        
        return horoscope
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/horoscope/monthly")
def monthly_horoscope(data: BirthData) -> Dict[str, Any]:
    """
    Monthly Horoscope - Comprehensive Month Ahead Outlook
    
    Based on:
    - Jupiter, Saturn, and Mars major transits
    - Sun's monthly progression
    - Retrograde planet impacts
    - Moon return dates (emotionally significant)
    - Monthly thematic analysis
    
    Provides:
    - Overall monthly rating (1-10)
    - Monthly summary and key themes
    - Major transit positions and effects
    - Key dates (Moon returns, significant transits)
    - Detailed area forecasts with advice:
        * Career outlook and guidance
        * Relationship dynamics
        * Financial prospects
        * Health focus areas
    - Retrograde planet notifications
    - Lucky days for important activities
    
    Example:
    {
        "date_of_birth": "1990-05-15",
        "time_of_birth": "14:30",
        "place_of_birth": "New Delhi, India"
    }
    """
    try:
        from predictions import generate_monthly_horoscope
        
        lat, lon = geocode_location(data.place_of_birth)
        
        horoscope = generate_monthly_horoscope(
            birth_date=data.date_of_birth,
            birth_time=data.time_of_birth,
            lat=lat,
            lon=lon
        )
        
        return horoscope
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
class LotteryRequest(BaseModel):
    date_of_birth: str
    time_of_birth: str
    place_of_birth: str
    lottery_type: str
    user_name: str = ""

class AllLotteryRequest(BaseModel):
    date_of_birth: str
    time_of_birth: str
    place_of_birth: str
    user_name: str = ""

@app.get("/lottery/types")
def get_lottery_types():
    """Get all available Australian lottery types"""
    return {
        "available_lotteries": {
            lottery_id: {
                "name": config["name"],
                "draw_days": config["draw_days"],
                "main_numbers": config["main_numbers"],
                "special_numbers": {
                    k: v for k, v in config.items() 
                    if k in ["powerball", "supplementary", "bonus"]
                },
                "official_url": config.get("official_url", "")
            }
            for lottery_id, config in LOTTERY_CONFIGS.items()
        }
    }


@app.post("/lottery/predict")
def predict_lottery_numbers(data: LotteryRequest) -> Dict[str, Any]:
    """Predict lottery numbers for a specific game"""
    try:
        if data.lottery_type not in LOTTERY_CONFIGS:
            available = ", ".join(LOTTERY_CONFIGS.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Invalid lottery type. Available: {available}"
            )
        
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        chart["birth_date"] = data.date_of_birth
        
        prediction = generate_lottery_predictions(
            chart, data.lottery_type, data.user_name
        )
        
        prediction["birth_details"] = {
            "date": data.date_of_birth,
            "time": data.time_of_birth,
            "place": data.place_of_birth,
            "ascendant": chart["ascendant"]["sign"],
            "moon_sign": chart["planets"]["Moon"]["sign"]
        }
        
        return prediction
        
    except Exception as e:
        logger.error(f"Error in lottery prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/lottery/predict-all")
def predict_all_lotteries(data: AllLotteryRequest) -> Dict[str, Any]:
    """Predict numbers for all Australian lotteries"""
    try:
        lat, lon = geocode_location(data.place_of_birth)
        chart = calculate_chart(data.date_of_birth, data.time_of_birth, lat, lon)
        chart["birth_date"] = data.date_of_birth
        
        all_predictions = generate_all_lottery_predictions(chart, data.user_name)
        
        all_predictions["birth_details"] = {
            "date": data.date_of_birth,
            "time": data.time_of_birth,
            "place": data.place_of_birth
        }
        
        return all_predictions
        
    except Exception as e:
        logger.error(f"Error in all lottery predictions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")