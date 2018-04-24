FROM ubuntu:17.10

RUN apt-get update
RUN apt-get install -y curl software-properties-common apt-utils
#RUN add-apt-repository ppa:openjdk-r/ppa
#RUN apt-get update
RUN apt-get install -y openjdk-8-jdk
#RUN add-apt-repository ppa:webupd8team/java
#RUN apt-get install -y oracle-java9-installer

#ARG JAVA_ARCHIVE=http://download.oracle.com/otn-pub/java/jdk/10.0.1+10/fb4372174a714e6b8c52526dc134031e/jdk-10.0.1_linux-x64_bin.tar.gz
RUN java -version
#ENV JAVA_HOME /usr/local/jdk-8.0.4
#ENV PATH $PATH:$JAVA_HOME/bin
#RUN curl -sL --retry 3 --insecure \
#  --header "Cookie: oraclelicense=accept-securebackup-cookie;" $JAVA_ARCHIVE \
#  | tar -xz -C /usr/local/ && ln -s $JAVA_HOME /usr/local/java

ARG SPARK_ARCHIVE=http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-hadoop2.7.tgz
RUN curl -s $SPARK_ARCHIVE | tar -xz -C /usr/local/
RUN apt-get install -y python 

ENV SPARK_HOME /usr/local/spark-2.1.0-bin-hadoop2.7
ENV PATH $PATH:$SPARK_HOME/bin

# WorcCount script and data
COPY wc.py /root/
COPY wc.txt /root/

EXPOSE 4040 6066 7077 8080

WORKDIR $SPARK_HOME