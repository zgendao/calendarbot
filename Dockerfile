FROM python:3.8.9.4-slim-buster

WORKDIR /usr/src/calendarbot

COPY requirements.txt .
RUN pip3 install requirements.txt

COPY . .
CMD [ "python", "main.py" ]
