FROM python:3.9.6

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN apt update && apt -qy install gcc redis poppler-utils

WORKDIR /app

#RUN mkdir /app/static && mkdir /app/media
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . /app

