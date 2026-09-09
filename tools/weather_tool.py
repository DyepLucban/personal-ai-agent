from langchain_core.tools import tool
import requests

@tool
def get_weather(city: str) -> dict:
    """Get the current weather for a given city."""
    geo_response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1}
    ).json()

    if not geo_response.get("results"):
        return {"status": "error", "message": f"Could not find location: {city}"}

    location = geo_response["results"][0]
    lat, lon = location["latitude"], location["longitude"]

    weather_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": lat, "longitude": lon, "current_weather": True}
    ).json()

    current = weather_response["current_weather"]

    return {
        "status": "success",
        "city": location["name"],
        "temperature_celsius": current["temperature"],
        "windspeed": current["windspeed"]
    }