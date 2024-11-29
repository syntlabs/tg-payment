FROM python:3.12

RUN mkdir /usr/src/api
WORKDIR /usr/src/api

ADD requirements.txt requirements.txt

RUN mkdir /var/log/api

RUN apt update -y
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install fastapi[standard]