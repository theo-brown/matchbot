from typing import Iterable, Optional
import datetime
from uuid import uuid4

MATCH_CREATED = "CREATED"
MATCH_QUEUED = "QUEUED"
MATCH_LIVE = "LIVE"
MATCH_FINISHED = "FINISHED"


class Match:
    global MATCH_CREATED
    global MATCH_QUEUED
    global MATCH_LIVE
    global MATCH_FINISHED

    def __init__(self,
                 team1_id: str, team2_id: str,
                 maps: Iterable[str],
                 sides: Iterable[str],
                 id: Optional[str] = None,
                 status: str = MATCH_CREATED,
                 created_timestamp: Optional[datetime.datetime] = None,
                 live_timestamp: Optional[datetime.datetime] = None,
                 finished_timestamp: Optional[datetime.datetime] = None):
        self.team_ids = [team1, team2]
        self.maps = maps
        self.sides = sides
        self.id = id if id else uuid4.hex()
        self.created_timestamp = created_timestamp if created_timestamp else datetime.datetime.now()
        self.live_timestamp = live_timestamp
        self.finished_timestamp = finished_timestamp
        if status in [MATCH_CREATED, MATCH_INITIALISING, MATCH_LIVE, MATCH_FINISHED]:
            self.status = status
        else:
            raise ValueError(f"status must be one of {MATCH_CREATED, MATCH_READY, MATCH_LIVE, MATCH_FINISHED},"
                             f"got {status}.")

    def __str__(self):
        return ("Match:\n"
                f"\tID: {self.id}\n"
                f"\tStatus: {self.status}\n"
                f"\tTeam 1: {self.team_ids[0]}\n"
                f"\tTeam 2: {self.team_ids[1]}\n"
                f"\tMaps:\n {self.maps}\n"
                f"\tSides:\n {self.sides}\n"
                f"\tCreated at: {self.created_timestamp}\n"
                f"\tLive at: {self.live_timestamp}\n"
                f"\tFinished at: {self.finished_timestamp}\n")

# class MatchesTable