import aioredis
import asyncio
from typing import Optional, Union, Callable, Coroutine


def connect(host="localhost", port=6379, decode_responses=True) -> aioredis.Redis:
    if host is None:
        host = "localhost"
    if port is None:
        port = 6379
    if decode_responses is None:
        decode_responses = True
    return aioredis.Redis.from_url(
        f"redis://{host}:{port}", decode_responses=decode_responses)


class BlockingFIFOQueue:
    def __init__(self,
                 channel: str,
                 redis: Optional[aioredis.client.Redis] = None,
                 host="localhost",
                 port=6379,
                 decode_responses=True):
        if redis is not None:
            self.redis = redis
        else:
            self.redis = connect(host, port, decode_responses)
        self.channel = channel

    async def push(self, value):
        await self.redis.lpush(self.channel, value)

    async def pop(self) -> str:
        channel, value = await self.redis.brpop(self.channel, 0)
        return value


class EventHandler:
    def __init__(self,
                 channel: str,
                 callback: Coroutine,
                 loop: asyncio.AbstractEventLoop = None,
                 **kwargs):
        self.queue = BlockingFIFOQueue(channel, **kwargs)
        self.callback = callback
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop
        self._running = False

    async def _run(self):
        while True:
            print(f"Waiting for value in queue {self.queue.channel}")
            value = await self.queue.pop()
            print(f"Received value {value} from queue {self.queue.channel}")
            self._loop.create_task(self.callback(value))

    def start(self):
        print("Creating task")
        self._loop.create_task(self._run())

        if not self._loop.is_running():
            print("Starting event loop")
            self._loop.run_forever()

    def stop(self):
        if self._loop.is_running():
            self._loop.stop()
            self._running = False
        else:
            raise RuntimeError("event loop not running")
