from flask import request, jsonify, render_template, flash, redirect, url_for
from app.weather import fetch_weather_data
from app.prompt import analyze_weather
from app.database import save_user_to_db, get_all_subscribers
from app.alert import send_alert_to_users
from config import Config

# API endpoint to fetch weather data and analyze it
def get_weather():

    weather_data = fetch_weather_data()
    prompt, analysis = analyze_weather(weather_data)

    # Prepare data for the template
    hourly_data = zip(
        weather_data["hourly"]["time"],
        weather_data["hourly"]["temperature_2m"],
        weather_data["hourly"]["precipitation_probability"],
        weather_data["hourly"]["rain"],
        weather_data["hourly"]["wind_speed_10m"]
    )

    return render_template(
        'index.html',
        weather_data=hourly_data,
        analysis=analysis
    )
    # return jsonify({
    #     'weather_data': weather_data,
    #     'analysis': analysis,
    #     'prompt': prompt
    # })

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
    weather_data = fetch_weather_data()
    _, analysis = analyze_weather(weather_data)

    alert_msg = analysis['alert_msg']

    if "heavy rainfall" in alert_msg.lower() or "hurricane" in alert_msg.lower():
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

