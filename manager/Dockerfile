FROM python:3

COPY src/ /app/src
COPY manager/run.py /app/run.py

WORKDIR /app

RUN pip install -e src

CMD [ "python", "run.py" ]
