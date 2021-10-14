import matchbot.database
import matchbot.apps
import matchbot.redis
from datetime import datetime


def timestamp():
    return datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
