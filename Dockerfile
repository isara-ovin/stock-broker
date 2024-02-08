
FROM python:3.9-buster

WORKDIR /usr/src/api

RUN  apt-get update && apt-get install -y\
    python3 python3-dev gcc \
    gfortran musl-dev g++ \
    libffi-dev\
    libxml2 libxml2-dev \
    libxslt-dev

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install --upgrade cython

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "StockBroker.wsgi", "--bind=0.0.0.0:8000"]