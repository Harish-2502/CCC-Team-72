FROM ubuntu:20.10

ARG SPARK_VERSION
ARG HADOOP_VERSION

ENV SPARK_ARCHIVE http://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz
ENV SPARK_HOME /usr/local/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}
ENV PATH $PATH:$SPARK_HOME/bin

EXPOSE 4040 6066 7077 8080

RUN apt-get update; \
    apt-get install -y apt-utils \
                       curl \
                       openjdk-8-jdk \
                       python3 \
                       python3-pip \
                       software-properties-common \
                       wget
RUN update-alternatives --install /usr/bin/python python $(which python3) 1
RUN wget -qO- ${SPARK_ARCHIVE} | tar -xz -C /usr/local/

# WordCount script and data
COPY ["wc.py", "wc.txt", "/tmp/"]

WORKDIR $SPARK_HOME
