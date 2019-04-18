FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y curl software-properties-common apt-utils wget
RUN apt-get install -y openjdk-8-jdk
RUN java -version

ARG SPARK_ARCHIVE="http://mirror.intergrid.com.au/apache/spark/spark-2.4.1/spark-2.4.1-bin-hadoop2.7.tgz"
RUN wget -qO- $SPARK_ARCHIVE | tar -xz -C /usr/local/
RUN apt-get install -y python

ENV SPARK_HOME /usr/local/spark-2.4.1-bin-hadoop2.7
ENV PATH $PATH:$SPARK_HOME/bin

# WorcCount script and data
COPY wc.py /root/
COPY wc.txt /root/

EXPOSE 4040 6066 7077 8080

WORKDIR $SPARK_HOME
