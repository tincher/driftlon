# syntax=docker/dockerfile:1
FROM python:3.7-alpine
RUN apk add --update --no-cache g++ gcc libxslt-dev
COPY fetch_requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./data_fetcher/ /data_fetcher
COPY ./fetch_batch.sh /
COPY ./config.yml /
COPY ./driftlon_utils.py /
ENV PYTHONPATH "${PYTHONPATH}:/"
CMD ["sh", "fetch_batch.sh", "10"]
