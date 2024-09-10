FROM python:3.12

RUN mkdir /usr/src/api
WORKDIR /usr/src/api

ADD requirements.txt requirements.txt

RUN mkdir /var/log/api

RUN apt update -y
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install fastapi[standard]
ARG API_SERVICE_PORT
ENV API_SERVICE_PORT $API_SERVICE_PORT
CMD ["fastapi", "run", "main.py", "--host", "127.0.0.1", "--port", $API_SERVICE_PORT, "--workers", "4", "--reload"]