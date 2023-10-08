FROM python:3.10.12

WORKDIR /flask-python-app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY . /flask-python-app

CMD flask --app main run -h 0.0.0.0 -p $PORT