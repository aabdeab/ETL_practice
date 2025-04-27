FROM apache/airflow:2.7.1

USER root
RUN apt-get update && apt-get install -y openjdk-11-jdk
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

USER airflow
RUN pip install apache-airflow-providers-apache-spark \
    apache-airflow-providers-postgres \
    kafka-python \
    requests