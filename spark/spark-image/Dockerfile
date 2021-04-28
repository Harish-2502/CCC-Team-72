FROM ubuntu:20.04

ARG SPARK_VERSION

ARG SPARK_ARCHIVE="http://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop2.7.tgz"
ENV SPARK_HOME /usr/local/spark-${SPARK_VERSION}-bin-hadoop2.7
ENV PATH $PATH:$SPARK_HOME/bin

EXPOSE 4040 6066 7077 8080

RUN apt-get update; \
    apt-get install -y apt-utils \
                       curl \
                       openjdk-8-jdk \
                       python \
                       software-properties-common \
                       wget;

RUN wget -qO- $SPARK_ARCHIVE | tar -xz -C /usr/local/

# WorcCount script and data
COPY ["wc.py", "wc.txt", "/root/"]

WORKDIR $SPARK_HOME
