FROM python:3.10.7-slim-bullseye

EXPOSE 8000
ARG token
ARG host
ARG database
ARG user
ARG password

ENV PYTHONPATH /app
ENV DEBIAN_FRONTEND=noninteractive

# install jdk 8, for jdbc driver
# this is required for remote connection
# gcc and g++ are rquired to compile the api for jdbc library
RUN mkdir -p /usr/share/man/man1 /usr/share/man/man2

RUN apt-get update && \
apt-get install -y --no-install-recommends \
        openjdk-11-jre gcc g++

# Prints installed java version, just for checking
RUN java --version

WORKDIR /app/
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./src/ ./src/
COPY ./entrypoint.sh .
COPY ./postgresql-42.4.0.jar .
COPY ./preset.json .

COPY Config.py .
COPY main.py .
COPY server_setting.json .

# generate the secret config
RUN echo "[server]\n token= ${token}\n[database]\n host = ${host}\n database = ${database}\n user = ${user}\n password = ${password}">secret.cfg

ENTRYPOINT ./entrypoint.sh

