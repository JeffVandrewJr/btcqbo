FROM python:3.7.1

WORKDIR /btcqbo

COPY . /btcqbo

RUN pip install -r requirements.txt

EXPOSE 8001

CMD ["gunicorn", "-b 0.0.0.0:8001", "-w 2", "btcqbo:app"]
