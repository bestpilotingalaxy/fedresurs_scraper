FROM python:latest

WORKDIR /service

COPY . /service

RUN pip install -r requirements.txt

ENV FLASK_APP api.py


CMD ["flask", "run", "--host=0.0.0.0"]
