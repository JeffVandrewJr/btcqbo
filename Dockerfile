FROM python:3.7.1-alpine3.8

WORKDIR /btcqbo

COPY . /btcqbo

RUN apk add --no-cache tzdata
RUN ln -sf /usr/share/zoneinfo/Universal /etc/localtime
RUN pip install -r requirements.txt

ENV FLASK_APP=btcqbo.py
ENV TZ=Universal
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8001 --workers=2 --access-logfile=- --error-logfile=-"

EXPOSE 8001

CMD ["gunicorn", "btcqbo:app"]
