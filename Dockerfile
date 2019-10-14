FROM python:3

LABEL Name=url_shorter Version=1.1.3
EXPOSE 5000

WORKDIR /app
ADD ./static /app/static
ADD ./templates /app/templates
COPY import.py /app/import.py
COPY export.py /app/export.py
COPY main.py /app/main.py

#Make a complete system update
RUN apt update
RUN apt upgrade -y

#Install pipreqs. this tool is used to make the requirements.txt file automatic
RUN pip install pipreqs
RUN pipreqs . --force
#Install all required python libs
RUN python3 -m pip install -r requirements.txt

#Make a builddate file, used if you want to see the builddate in the webui
RUN date > builddate.txt

#everytime the container starts run main.py
ENTRYPOINT python3 main.py
