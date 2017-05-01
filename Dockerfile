FROM python:latest
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
