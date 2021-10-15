from matchbot.apps.matchstarter import MatchStarter
from os import getenv
import matchbot.log

logger = matchbot.log.console_logger('MatchStarter', matchbot.log.DEBUG)

matchstarter = MatchStarter(db_host=getenv("POSTGRES_HOST"),
                            db_port=int(getenv("POSTGRES_PORT")),
                            db_user=getenv("POSTGRES_USER"),
                            db_password=getenv("POSTGRES_PASSWORD"),
                            db_name=getenv("POSTGRES_DB"),
                            redis_host=getenv("REDIS_HOST"),
                            redis_port=int(getenv("REDIS_PORT")))

matchstarter.start_event_handler('match_queue')
