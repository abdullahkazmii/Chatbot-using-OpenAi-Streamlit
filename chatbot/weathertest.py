import requests
import streamlit as st

# Your OpenWeather API key
OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]

# OpenWeather API URL
API_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(lat: float, lon: float, location: str, format: str = "celsius"):
    """Fetch weather data for a given location."""
    units = 'metric' if format == 'celsius' else 'imperial'  # Use 'metric' for °C and 'imperial' for °F
    
    # Parameters for the API request
    params = {
        'lat': lat,
        'lon': lon,
        'appid': OPENWEATHER_API_KEY,
        'units': units  # Use 'imperial' for Fahrenheit, 'metric' for Celsius
    }

    try:
        # Making the API call
        response = requests.get(API_URL, params=params)
        
        # Checking if the response is successful
        if response.status_code == 200:
            data = response.json()  # Parsing the response as JSON
            temperature_unit = "°C" if format == "celsius" else "°F"
            
            # Structuring the weather data
            weather = {
                "location": data.get('name', 'Unknown location'),
                "temperature": f"{data['main']['temp']}{temperature_unit}",
                "description": data['weather'][0]['description'],
            }
            return weather
        else:
            return {"error": f"Error: {response.status_code}, {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}

# Example: Testing weather in Lahore
latitude = 33.6995  # Latitude for Lahore
longitude = 73.0363  # Longitude for Lahore
location = "Islamabad"
format = "celsius"  # Change to 'fahrenheit' for Fahrenheit

# Fetching the weather data
weather_data = get_weather(latitude, longitude, location, format)

# Displaying the result
if "error" in weather_data:
    print(f"Error fetching weather: {weather_data['error']}")
else:
    print(f"Weather in {weather_data['location']}:")
    print(f"Temperature: {weather_data['temperature']}")
    print(f"Description: {weather_data['description']}")
