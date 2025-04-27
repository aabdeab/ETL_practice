from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 4, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_data_etl',
    default_args=default_args,
    description='ETL pipeline for weather data',
    schedule_interval=timedelta(days=1),
)

def trigger_kafka_producer():
    import requests
    import json
    import os
    from kafka import KafkaProducer
    
    # Connect to Kafka
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    # Get data from Weather API (using OpenWeatherMap as an example)
    api_key = os.getenv('WEATHER_API_KEY', 'your_api_key')
    cities = ['London', 'New York', 'Tokyo', 'Sydney', 'Paris']
    
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
    
    producer.flush()
    producer.close()

trigger_producer = PythonOperator(
    task_id='trigger_kafka_producer',
    python_callable=trigger_kafka_producer,
    dag=dag,
)

process_data = SparkSubmitOperator(
    task_id='process_weather_data',
    application='/opt/spark-apps/weather_processing.py',
    conn_id='spark_default',
    verbose=True,
    dag=dag,
)

create_summary = PostgresOperator(
    task_id='create_daily_summary',
    postgres_conn_id='postgres_default',
    sql="""
    INSERT INTO weather_summary (date, avg_temp, min_temp, max_temp)
    SELECT 
        current_date as date,
        AVG(temperature) as avg_temp,
        MIN(temperature) as min_temp,
        MAX(temperature) as max_temp
    FROM weather_data
    WHERE DATE(timestamp) = current_date
    GROUP BY DATE(timestamp)
    """,
    dag=dag,
)

trigger_producer >> process_data >> create_summary