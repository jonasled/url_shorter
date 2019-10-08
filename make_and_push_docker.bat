echo off
title Building and Pushing docker image
cls


docker build --rm -f "Dockerfile" -t url_shorter:latest .
docker tag url_shorter docker.jonasled.de/url_shorter/url_shorter
docker push docker.jonasled.de/url_shorter/url_shorter