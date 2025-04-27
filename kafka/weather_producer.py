import requests
import json
import time
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_weather_data():
    # Initialize Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    # Get data from Weather API (using OpenWeatherMap as an example)
    api_key = os.getenv('WEATHER_API_KEY')
    cities = ['London', 'New York', 'Tokyo', 'Sydney', 'Paris']
    
    while True:
        for city in cities:
            try:
                response = requests.get(
                    f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
                )
                data = response.json()
                
                # Send the data to Kafka
                producer.send('weather_data', data)
                print(f"Sent data for {city} to Kafka")
            except Exception as e:
                print(f"Error getting data for {city}: {e}")
        
        # Wait for a while before the next batch
        time.sleep(3600)  # Fetch data every hour

if __name__ == "__main__":
    get_weather_data()
