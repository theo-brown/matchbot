FROM python:3

COPY src/ /app/src

COPY matchstarter/run.py /app/run.py

WORKDIR /app

RUN pip install -e src

CMD [ "python", "run.py" ]
