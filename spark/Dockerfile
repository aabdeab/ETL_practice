FROM bitnami/spark:3.1.2

USER root

# Install dependencies including wget
RUN apt-get update && apt-get install -y python3-pip wget

# Install Python packages
RUN pip3 install pyspark==3.1.2 psycopg2-binary kafka-python

# Add the PostgreSQL JDBC driver
RUN wget https://jdbc.postgresql.org/download/postgresql-42.3.1.jar -O /opt/bitnami/spark/jars/postgresql-42.3.1.jar