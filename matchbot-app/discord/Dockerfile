FROM python:3

WORKDIR /app

RUN pip install aioredis asyncio

COPY run.py /app

CMD [ "python", "run.py" ]
