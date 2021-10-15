import aioredis
import asyncio
from typing import Optional, Union, Callable, Coroutine
import matchbot.log


def connect(host="localhost", port=6379, decode_responses=True) -> aioredis.Redis:
    if host is None:
        host = "localhost"
    if port is None:
        port = 6379
    if decode_responses is None:
        decode_responses = True
    return aioredis.Redis.from_url(
        f"redis://{host}:{port}", decode_responses=decode_responses)


class BlockingFIFOQueue(matchbot.log.LoggedClass):
    def __init__(self,
                 channel: str,
                 *args,
                 redis: Optional[aioredis.client.Redis] = None,
                 host="localhost",
                 port=6379,
                 decode_responses=True,
                 **kwargs):
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


class EventHandler(matchbot.log.LoggedClass):
    def __init__(self,
                 channel: str,
                 callback: Coroutine,
                 *args,
                 loop: asyncio.AbstractEventLoop = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = BlockingFIFOQueue(channel, **kwargs)
        self.callback = callback
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop
        self._running = False

    async def _run(self):
        while True:
            self.logger.debug(f"Waiting for value in channel '{self.queue.channel}'")
            value = await self.queue.pop()
            self.logger.debug(f"Received value {value} in channel '{self.queue.channel}'")
            self._loop.create_task(self.callback(value))

    def start(self):
        self.logger.debug(f"Starting EventHandler on '{self.queue.channel}'")
        self._loop.create_task(self._run())

        if not self._loop.is_running():
            self.logger.debug(f"Starting EventHandler event loop for '{self.queue.channel}'")
            self._loop.run_forever()

    # TODO: add close nicely on force quit
    def stop(self):
        self.logger.debug(f"Stopping EventHandler on '{self.queue.channel}'")
        if self._loop.is_running():
            self._loop.stop()
            self._running = False
        else:
            raise RuntimeError("event loop not running")
