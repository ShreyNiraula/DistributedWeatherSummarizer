import os
import requests
from flask import Flask, jsonify, request
from datetime import datetime, timedelta

# VM2: weather_data_service.py
app = Flask(__name__)
app.config.from_object('config.Config')


# Function to limit the forcast datapoints to next hourly_limit
def limit_weather_data(json_data, hourly_limit=24):
    # Get the current time from the JSON data in UTC
    current_time = datetime.fromisoformat(json_data['current']['time'])

    # Calculate the cutoff time for the next 24 hours
    cutoff_time = current_time + timedelta(hours=hourly_limit)

    # Filter hourly data for the next 24 hours
    filtered_hourly_data = {
        key: [
            value for idx, value in enumerate(json_data['hourly'][key])
            if current_time <= datetime.fromisoformat(json_data['hourly']['time'][idx]) <= cutoff_time
        ]
        for key in json_data['hourly']
    }

    # Filter daily data for today and future days
    filtered_daily_data = {
        key: [
            value for idx, value in enumerate(json_data['daily'][key])
            if datetime.fromisoformat(json_data['daily']['time'][idx]).date() >= current_time.date()
        ]
        for key in json_data['daily']
    }

    # Add filtered data back to the JSON structure
    filtered_json_data = {
        **json_data,
        'hourly': filtered_hourly_data,
        'daily': filtered_daily_data
    }
    return filtered_json_data


@app.route('/fetch', methods=['POST'])
def fetch_weather_data():
    # get post data
    payload = request.get_json()

    # Open-Meteo API endpoint and parameters
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": float(payload['lat']),
        "longitude": float(payload['lon']),
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "wind_speed_10m"],
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "rain", "wind_speed_10m"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
        "timezone": "America/Chicago",
        "forecast_days": 3
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    filtered_response = limit_weather_data(response.json(), 24)
    return filtered_response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("VM2").split(":")[-1])
    # app.run(host='0.0.0.0', port=6002)
