import os

from flask import Flask, request, jsonify
import json
import google.generativeai as genai

app = Flask(__name__)
app.config.from_object('config.Config')

# Configure Google AI API key
genai.configure(api_key=app.config['GENAI_API_KEY'])


# Function to analyze weather data using the ChatGPT API
def analyze_weather(data):
    n_hourly_data = len(data.get("hourly", {}))

    prompt = f"""
    Input:
    This JSON contains current weather data under the 'current' key and an hourly forecast for the next {n_hourly_data} hours under the 'hourly' key. Aggregated daily forecasts for today and tomorrow are also included.
    {data}

    Output:
    Create a JSON response with three keys:

    1. **text**: A short summary (within 100 words) describing the current weather and upcoming forecast. Include mentions of high chances of severe weather, such as rainfall, hurricanes, or any significant warnings. If there are alert signals, specify and briefly explain them.

    2. **alert**: A boolean set to `true` if any conditions require user alert, such as heavy rainfall, strong winds, extreme heat, or other adverse weather. Set it to `false` otherwise.

    3. **alert_msg**: A brief message (within 50 words) advising on any severe weather and providing recommendations for user safety.

    Ensure that the response is valid JSON format only.
    """

    generation_config = {
        "temperature": 0.9,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    # Initialize the generative model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    chat_session = model.start_chat(history=[])

    # Send the prompt to the model
    response = chat_session.send_message(prompt)

    # Try to parse the response as JSON
    try:
        parsed_response = json.loads(response.text)
        # Successfully parsed JSON response
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        parsed_response = {
            "text": "Unable to parse the response from genai",
            "alert": False,
            "alert_msg": "",
        }

    return parsed_response

@app.route('/analyze', methods=['POST'])
# Function to analyze weather data using ChatGPT
def analyze_weather_route():
    # Get the JSON payload from the POST request
    data = request.get_json()

    # Call the analyze_weather function with the incoming data
    analysis_result = analyze_weather(data)

    # Return the analysis result as a JSON response
    return jsonify(analysis_result)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6002)  # Run on 0.0.0.0 to allow external access
