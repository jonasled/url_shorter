# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:3

# If you prefer miniconda:
#FROM continuumio/miniconda3

LABEL Name=url_shorter Version=1.1.3
EXPOSE 5000

WORKDIR /app
ADD ./static /app/static
ADD ./templates /app/templates
COPY import.py /app/import.py
COPY export.py /app/export.py
COPY main.py /app/main.py

RUN apt update
RUN apt upgrade -y
RUN pip install pipreqs
RUN pipreqs . --force
RUN python3 -m pip install -r requirements.txt
RUN date > builddate.txt

ENTRYPOINT python3 main.py
