FROM ubuntu:latest

ENV TZ=Europe/Moscow

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y && \
    apt-get install -y python3-dev && \
    apt-get install -y python3-pip && \
    apt-get install -y firefox

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /parser

ADD . /parser

RUN pip3 install -r requirements.txt

COPY . ./service

# # Права драйверу
RUN chmod 755 ./WebDriver/geckodriver

