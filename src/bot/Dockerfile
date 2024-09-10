FROM python:3.12

RUN mkdir /usr/src/bot
WORKDIR /usr/src/bot

COPY requirements.txt requirements.txt

RUN mkdir /var/log/bot

RUN apt update -y
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
CMD ["python", "main.py"]