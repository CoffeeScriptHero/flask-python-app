FROM python:3.10.12

WORKDIR /flask-python-app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY . /flask-python-app

ENV FLASK_APP=webapp

CMD flask --app webapp run -h 0.0.0.0 -p $PORT