FROM python:3.10.7-slim-bullseye

EXPOSE 8000
ARG token
ARG host
ARG database
ARG user
ARG password

ENV PYTHONPATH /app

WORKDIR /app/
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./src/ ./src/

COPY Config.py .
COPY main.py .
COPY server_setting.json .

ENTRYPOINT python main.py ${token} ${host} ${database} ${user} ${password}

