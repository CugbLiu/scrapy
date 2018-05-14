FROM python:2.7-slim
RUN mkdir /istp_slave
ADD requirements.txt /istp_slave/requirements.txt
WORKDIR /istp_slave
RUN apt-get update
RUN apt-get install -y gcc
RUN pip install -r requirements.txt

