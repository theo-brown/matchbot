import matchbot.database as db
from matchbot.redis import EventHandler
from typing import Coroutine


class MatchbotBaseApp:
    def __init__(self,
                 db_host: str, db_port: int, db_user: str, db_password: str, db_name: str,
                 redis_host: str, redis_port: int):
        self._db_host = db_host
        self._db_port = db_port
        self._db_user = db_user
        self._db_password = db_password
        self._db_name = db_name
        self._redis_host = redis_host
        self._redis_port = redis_port

        self.event_handlers = {}

        self.engine = db.new_engine(self._db_host, self._db_port,
                                    self._db_user, self._db_password, self._db_name)

    def new_session(self) -> db.functions.AsyncSession:
        return db.new_session(self.engine)

    def new_event_handler(self, channel: str, callback: Coroutine):
        self.event_handlers[channel] = EventHandler(channel, callback, host=self._redis_host, port=self._redis_port)
        self.start_event_handler(channel)

    def start_event_handler(self, channel):
        self.event_handlers[channel].start()

    def stop_event_handler(self, channel):
        self.event_handlers[channel].stop()
