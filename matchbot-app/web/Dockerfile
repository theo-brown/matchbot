FROM python:3

WORKDIR /app

RUN pip install aioredis aiopg

COPY run.py /app

CMD [ "python", "run.py" ]
