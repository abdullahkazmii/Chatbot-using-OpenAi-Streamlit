from openai import OpenAI
import streamlit as st
import requests
import json

# Initialize OpenAI client with API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("ChatGPT Clone with OpenWeather API")

OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
API_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(location: str, format: str = 'celsius'):
    """Fetch weather data using city name from the OpenWeather API."""
    units = 'metric' if format == 'celsius' else 'imperial'

    params = {
        'q': location,
        'appid': OPENWEATHER_API_KEY,
        'units': units
    }

    try:
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            weather = {
                "location": data['name'],
                "temperature": f"{data['main']['temp']}°{'C' if format == 'celsius' else 'F'}",
                "description": data['weather'][0]['description'],
            }
            return weather
        else:
            return {"error": f"Location not found! Status code: {response.status_code}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}

# Set default model if not in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

# Display assistant's welcome message
if "messages" not in st.session_state:
    st.session_state.messages = []
    with st.chat_message("assistant"):
        st.write("Hey there! I'm a chatbot. How can I help you today?")

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("What's up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Create a placeholder for the assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get the current weather for a given location based on city name",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "Name of the city, e.g., San Francisco, CA"
                                },
                                "format": {
                                    "type": "string",
                                    "enum": ["celsius", "fahrenheit"],
                                    "description": "Temperature format"
                                }
                            },
                            "required": ["location", "format"],
                        }
                    }
                }
            ]

            # Call the OpenAI API with the function tools
            response = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                tools=tools,
            )

            # Check if the response is valid and has the expected attributes
            if response.choices and response.choices[0].message:
                message_content = response.choices[0].message.content
                tool_calls = getattr(response.choices[0].message, "tool_calls", [])

                # If there are function calls, process each one
                if tool_calls:
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)

                        if function_name == "get_weather":
                            # Extract parameters and call the get_weather function
                            location = arguments.get("location")
                            format_ = arguments.get("format")
                            weather_data = get_weather(location=location, format=format_)

                            # Formulate the function response
                            function_response = weather_data.get(
                                "error",
                                f"The weather in {weather_data['location']} is {weather_data['temperature']} with {weather_data['description']}."
                            )

                            st.session_state.messages.append({'role': 'assistant', 'content': function_response})
                            message_placeholder.markdown(function_response)
                        else:
                            st.error("Unexpected function call name.")
                else:
                    # Handle as a regular AI assistant response
                    if message_content:  # Check if the message content is not None
                        full_response = message_content
                        st.session_state.messages.append({'role': 'assistant', 'content': full_response})
                        message_placeholder.markdown(full_response)
                    else:
                        # Fallback response if no valid response content
                        full_response = "I'm here to help!"
                        st.session_state.messages.append({'role': 'assistant', 'content': full_response})
                        message_placeholder.markdown(full_response)
            else:
                # Fallback response if no valid response from the API
                full_response = "I'm here to help!"
                st.session_state.messages.append({'role': 'assistant', 'content': full_response})
                message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.write("Debugging Error:", str(e))
