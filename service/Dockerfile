FROM python:3.7-slim-buster

WORKDIR /app/

COPY dependencies ./dependencies
COPY client ./client
COPY server ./server
COPY requirements.txt ./requirements.txt
COPY setup_service_dependencies.sh ./setup_service_dependencies.sh

RUN apt-get update && apt-get install -y python3-opencv
RUN ls -aslrth
RUN ./setup_service_dependencies.sh

ENV PYTHONPATH=/usr/local/lib/python3.7/site-packages:/app/dependencies/ImageServiceGRPCModules/src
