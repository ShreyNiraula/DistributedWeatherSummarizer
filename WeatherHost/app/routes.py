import json
import os
from unittest.mock import patch

from flask import request, jsonify, render_template, flash, redirect, url_for, session
from app.weather import fetch_weather_data
from app.prompt import analyze_weather
from app.database import save_user_to_db, get_all_subscribers
from app.alert import send_alert_to_users
import requests

def fetch_weather_from_vm2(long_lat):
    # fetch weather from WeatherFetch VM
    # url_vm2 = "http://<VM2-IP>:6001/"

    url_vm2 = f"http://{os.getenv('VM2')}/fetch"
    try:
        response = requests.post(url_vm2, json=long_lat)
        response.raise_for_status()  # Check if the request was successful
        weather_data = response.json()
        return weather_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def fetch_analysis_from_vm3(weather_data):
    # url_vm3 = "http://<VM3-IP>:6002/"
    url_vm3 = f"http://{os.getenv('VM3')}/analyze"
    try:
        response = requests.post(url_vm3, json=weather_data)
        response.raise_for_status()  # Check if the request was successful
        analysis = response.json()
        return analysis
    except requests.exceptions.RequestException as e:
        print(f"Error fetching analysis data: {e}")
        return None

# APT endpoint to render home
def home():
    return render_template(
        'weather.html'
    )

# Index route (home page)
def index():
    return render_template('index.html')

# API endpoint to fetch weather data and analyze it
def get_weather():
    # latitude and longitude data from search bar
    data = request.get_json()

    # for fetch result vm2
    weather_data = fetch_weather_from_vm2(long_lat=data)

    # for analysis result vm3
    analysis = fetch_analysis_from_vm3(weather_data=weather_data)



    # Redirect to display page
    # return render_template('index.html', weather_data=hourly_data, analysis=analysis)
    return redirect(url_for('index'))

# API endpoint to handle user subscription
def subscribe():
    email = request.form['email']
    username = request.form['username']
    already_exists, is_success = save_user_to_db(email, username)

    # Flash appropriate messages
    if not is_success:
        flash('There was an error in registering the user. Please try again.', 'error')
    else:
        if already_exists:
            flash('This email has already been registered.', 'warning')
        else:
            flash(
                'You\'re all set! 🎉 Thanks for subscribing. You will receive timely alerts in case of severe weather like hurricanes. Stay safe and informed!',
                'success')

    # Redirect back to the main page
    return redirect(url_for('get_weather'))

# Endpoint to trigger alert (can be scheduled or triggered manually)
def trigger_alert():
    weather_data = fetch_weather_from_vm2()
    analysis = fetch_analysis_from_vm3(weather_data)

    alert_msg = analysis['alert_msg']

    # if "heavy rainfall" in alert_msg.lower() or "hurricane" in alert_msg.lower():
    if not analysis.get("alert"):
        try:
            send_alert_to_users(alert_msg)
        except Exception as e:
            # flash('Error Triggering email', 'danger')
            return redirect(url_for('get_weather'))

        finally:
            return redirect(url_for('get_weather'))
    else:
        print("Safe weather, no alert!!")
        return redirect(url_for('get_weather'))

