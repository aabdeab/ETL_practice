CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    temperature FLOAT,
    humidity INT,
    pressure INT,
    wind_speed FLOAT,
    description VARCHAR(200),
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weather_summary (
    id SERIAL PRIMARY KEY,
    date DATE,
    avg_temp FLOAT,
    min_temp FLOAT,
    max_temp FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
