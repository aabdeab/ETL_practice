from flask import Flask, render_template, jsonify
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host="postgres",
        database="airflow",
        user="airflow",
        password="airflow"
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather/current')
def current_weather():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get the latest weather data for each city
    cur.execute("""
        WITH latest_records AS (
            SELECT city, MAX(timestamp) as max_time
            FROM weather_data
            GROUP BY city
        )
        SELECT w.* 
        FROM weather_data w
        JOIN latest_records l ON w.city = l.city AND w.timestamp = l.max_time
    """)
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    weather_data = []
    for row in results:
        weather_data.append({
            'city': row['city'],
            'temperature': row['temperature'],
            'humidity': row['humidity'],
            'description': row['description'],
            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(weather_data)

@app.route('/api/weather/history/<city>')
def weather_history(city):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get the weather data for the past 7 days for the specified city
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    cur.execute("""
        SELECT city, temperature, humidity, timestamp 
        FROM weather_data
        WHERE city = %s AND timestamp > %s
        ORDER BY timestamp ASC
    """, (city, seven_days_ago))
    
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    history_data = []
    for row in results:
        history_data.append({
            'temperature': row['temperature'],
            'humidity': row['humidity'],
            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(history_data)

@app.route('/weather/<city>')
def city_weather(city):
    return render_template('weather_data.html', city=city)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
