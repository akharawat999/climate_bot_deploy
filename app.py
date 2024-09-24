import streamlit as st
import openai
import requests

# Retrieve API keys from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
weather_api_key = st.secrets["WEATHER_API_KEY"]
air_quality_api_key = st.secrets["AIR_QUALITY_API_KEY"]

# Check for missing API keys
if not openai.api_key or not weather_api_key or not air_quality_api_key:
    st.error("Missing API keys. Please set them in Streamlit secrets.")

# Streamlit page configuration
st.set_page_config(page_title="Weather and PM2.5 Chatbot", layout="centered", initial_sidebar_state="collapsed")

# UI Styling
st.markdown(
    """
    <style>
        .reportview-container {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
        }
    </style>
    """, unsafe_allow_html=True
)

st.title("🌦️ Weather and PM2.5 Chatbot")


# Function to fetch weather data from OpenWeatherMap API
def get_weather(city):
    """Fetch the current weather data for a given city using OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        return f"The current weather in {city} is {weather} with a temperature of {temp}°C, feeling like {feels_like}°C."
    else:
        return "Sorry, I couldn't fetch the weather data. Please check the city name."


# Function to fetch PM2.5 data from IQAir or OpenWeatherMap API
def get_pm25(city):
    """Fetch PM2.5 data for a given city using IQAir API."""
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?q={city}&appid={air_quality_api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        pm25_value = data['list'][0]['components']['pm2_5']
        return f"The current PM2.5 level in {city} is {pm25_value} µg/m³."
    else:
        return "Sorry, I couldn't fetch the PM2.5 data. Please check the city name."


# Function to generate a response from OpenAI
def get_response(prompt):
    """Generate a response using OpenAI's GPT model."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# User input
st.subheader("Ask me about the weather, PM2.5, or anything else!")
user_input = st.text_input("You: ", "")

# Process user input and generate response
if user_input:
    # Check if the input asks about weather
    if "weather in" in user_input.lower():
        # Extract the city name
        city = user_input.lower().split("weather in")[-1].strip()
        weather_info = get_weather(city)
        st.write(f"**Bot's Response:** {weather_info}")

    # Check if the input asks about PM2.5
    elif "pm2.5 in" in user_input.lower() or "air quality in" in user_input.lower():
        # Extract the city name
        city = user_input.lower().split("in")[-1].strip()
        pm25_info = get_pm25(city)
        st.write(f"**Bot's Response:** {pm25_info}")

    else:
        # Generate a general response from OpenAI
        response = get_response(user_input)
        # Display the bot's response with adjustable height
        st.text_area("Bot:", value=response, height=300)
