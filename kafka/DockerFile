FROM python:3.9-slim

WORKDIR /app

COPY weather_producer.py /app/

RUN pip install requests kafka-python

CMD ["python", "weather_producer.py"]