import json
import google.generativeai as genai


# Function to analyze weather data using ChatGPT
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
        # "response_mime_type": "text/plain",
        "response_mime_type": "application/json",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    chat_session = model.start_chat(
        history=[]
    )
    response = chat_session.send_message(prompt)

    # Try to parse the response as JSON
    try:
        parsed_response = json.loads(response.text)
        # If parsing is successful, you can use the parsed JSON here
        print(parsed_response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        parsed_response = {
            "text": "Unable to parse the response from genai",
            "alert": False,
            "alert_msg": "",
        }

    return prompt, parsed_response