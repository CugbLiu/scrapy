FROM python:2.7-slim
RUN mkdir /spider_master
ADD requirements.txt /spider_master/requirements.txt
WORKDIR /spider_master
RUN apt-get update
RUN pip install -r requirements.txt

