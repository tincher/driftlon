# syntax=docker/dockerfile:1
FROM python:3.7-alpine
WORKDIR /code
RUN apk add --update --no-cache g++ gcc libxslt-dev
COPY fetch_requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["sh", "fetch_batch.sh", "10"]
