from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType, ArrayType

def process_weather_data():
    # Create Spark session
    spark = SparkSession.builder \
        .appName("WeatherDataProcessing") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
        .getOrCreate()
    
    # Define schema for the weather data
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("main", StructType([
            StructField("temp", FloatType(), True),
            StructField("feels_like", FloatType(), True),
            StructField("temp_min", FloatType(), True),
            StructField("temp_max", FloatType(), True),
            StructField("pressure", IntegerType(), True),
            StructField("humidity", IntegerType(), True)
        ]), True),
        StructField("weather", ArrayType(StructType([
            StructField("id", IntegerType(), True),
            StructField("main", StringType(), True),
            StructField("description", StringType(), True),
            StructField("icon", StringType(), True)
        ])), True),
        StructField("wind", StructType([
            StructField("speed", FloatType(), True),
            StructField("deg", IntegerType(), True)
        ]), True),
        StructField("dt", IntegerType(), True)
    ])
    
    # Read from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "weather_data") \
        .load()
    
    # Parse JSON data
    parsed_df = df \
        .selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select(
            col("data.name").alias("city"),
            col("data.main.temp").alias("temperature"),
            col("data.main.humidity").alias("humidity"),
            col("data.main.pressure").alias("pressure"),
            col("data.wind.speed").alias("wind_speed"),
            explode(col("data.weather")).alias("weather"),
            to_timestamp(col("data.dt")).alias("timestamp")
        ) \
        .select(
            "city", 
            "temperature", 
            "humidity", 
            "pressure", 
            "wind_speed", 
            "weather.description", 
            "timestamp"
        )
    
    # Process and write to PostgreSQL
    query = parsed_df \
        .writeStream \
        .foreachBatch(lambda batch_df, batch_id: write_to_postgres(batch_df)) \
        .outputMode("append") \
        .start()
    
    query.awaitTermination()

def write_to_postgres(batch_df):
    # Write data to PostgreSQL
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/airflow") \
        .option("dbtable", "weather_data") \
        .option("user", "airflow") \
        .option("password", "airflow") \
        .mode("append") \
        .save()

if __name__ == "__main__":
    process_weather_data()