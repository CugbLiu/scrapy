FROM python:2.7-slim
RUN mkdir /iaga_slave
ADD requirements.txt /iaga_slave/requirements.txt
WORKDIR /iaga_slave
RUN apt-get update
RUN apt-get install -y gcc
RUN pip install -r requirements.txt

