FROM python:3.9.4-slim-buster

WORKDIR /usr/src/calendarbot

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .
CMD [ "python3", "main.py" ]
