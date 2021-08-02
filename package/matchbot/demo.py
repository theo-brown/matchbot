from matchbot import Team, User, Match

from random import randint

def fake_steamid():
    return randint(1e17, 1e18)

team1 = Team("Astralis",
                     [User(fake_steamid(), "gla1ve"),
                      User(fake_steamid(), "Magisk"),
                      User(fake_steamid(), "dev1ce"),
                      User(fake_steamid(), "dupreeh"),
                      User(fake_steamid(), "Xyp9x")],
                     tag="AST")

team2 = Team("Natus Vincere",
                     [User(fake_steamid(), "s1mple"),
                      User(fake_steamid(), "Boombl4"),
                      User(fake_steamid(), "electronic"),
                      User(fake_steamid(), "Perfecto"),
                      User(fake_steamid(), "flamie")],
                     tag="NAVI")

match = Match(team1, team2, maps=["de_dust2", "de_inferno", "de_overpass"], sides=["team1_ct", "team2_ct", "knife"])
