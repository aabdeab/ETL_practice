FROM apache/airflow:2.7.1

USER root
RUN apt-get update && apt-get install -y openjdk-11-jdk
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

USER airflow
# Install specific compatible versions
RUN pip install \
    apache-airflow-providers-apache-spark==4.1.1 \
    apache-airflow-providers-postgres==5.5.1 \
    apache-airflow-providers-openlineage==1.8.0 \
    kafka-python \
    requests