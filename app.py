import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime

API_KEY = '9ff5f9b0ae9024afbb61a6b66afa360b'

def fetch_weather(city, units='imperial'):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={units}'
    response = requests.get(url)
    return response

def fetch_forecast(city, units='imperial'):
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={units}'
    response = requests.get(url)
    return response

st.title("Weather Dashboard")

st.sidebar.header("User Input")
city = st.sidebar.text_input("Enter city name", "Orlando")
units = 'imperial' if st.sidebar.checkbox("Use Imperial Units", True) else 'metric'
show_raw_data = st.sidebar.checkbox("Show Raw Data")

# New widgets
city_selectbox = st.sidebar.selectbox("Most viewed cities:", ["London", "New York", "Tokyo", "Sydney"])
date_input = st.sidebar.date_input("Select a date", datetime.now())
time_input = st.sidebar.time_input("Select a time", datetime.now().time())
forecast_days = st.sidebar.number_input("Enter number of days for forecast", min_value=1, max_value=7, value=3)
forecast_slider = st.sidebar.slider("Select forecast range (hours)", min_value=0, max_value=48, value=(0, 24))

if st.sidebar.button("Refresh Data"):
    response = fetch_weather(city, units)
    forecast_response = fetch_forecast(city, units)
else:
    response = fetch_weather(city, units)
    forecast_response = fetch_forecast(city, units)

if city:
    data = response.json()
    forecast_data = forecast_response.json()

    if response.status_code != 200:
        st.error(f"Error: {data.get('message', 'City not found.')}")
    else:
        st.success("City found. Weather data retrieved successfully.")
        st.header(f"Weather in {city}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Temperature:** {data['main']['temp']} °F" if units == 'imperial' else f"**Temperature:** {data['main']['temp']} °C")
        with col2:
            st.write(f"**Weather:** {data['weather'][0]['description'].title()}")
        with col3:
            st.write(f"**Humidity:** {data['main']['humidity']}%")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Wind Speed:** {data['wind']['speed']} mph" if units == 'imperial' else f"**Wind Speed:** {data['wind']['speed']} m/s")
        with col2:
            st.write(f"**Pressure:** {data['main']['pressure']} hPa")
        with col3:
            st.write(f"**Visibility:** {data.get('visibility', 'N/A')} meters")

        # Map
        st.map(pd.DataFrame([[data['coord']['lat'], data['coord']['lon']]], columns=['lat', 'lon']))

        # Extract and prepare forecast data for visualization
        forecast_list = forecast_data['list']
        forecast_df = pd.json_normalize(forecast_list)
        forecast_df['dt'] = pd.to_datetime(forecast_df['dt_txt'])
        
        # Extract weather descriptions
        forecast_df['weather_description'] = forecast_df['weather'].apply(lambda x: x[0]['description'])
        
        if show_raw_data:
            # Display interactive table
            st.dataframe(forecast_df[['dt_txt', 'main.temp', 'weather_description', 'main.humidity', 'main.pressure']], use_container_width=True)

        # Prepare data for charts
        chart_data = forecast_df[['dt', 'main.temp', 'main.humidity', 'main.pressure']]
        chart_data.columns = ['Date', 'Temperature', 'Humidity', 'Pressure']
        chart_data.set_index('Date', inplace=True)

        # Charts
        st.subheader("Temperature over Time")
        st.line_chart(chart_data[['Temperature']])

        st.subheader("Temperature Distribution")
        st.bar_chart(chart_data[['Temperature']])

        st.subheader("Humidity over Time")
        st.line_chart(chart_data[['Humidity']])

        st.subheader("Pressure over Time")
        st.line_chart(chart_data[['Pressure']])

        # Information box
        st.info("Tip: You can switch between imperial and metric units using the checkbox in the sidebar.")

        # Success box
        st.success("Weather data and forecast retrieved successfully. Use the charts to visualize the data over time.")
