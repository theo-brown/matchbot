CREATE TABLE IF NOT EXISTS server_tokens (server_token VARCHAR(32) NOT NULL,
                                          PRIMARY KEY (server_token));

CREATE TABLE IF NOT EXISTS maps (id   VARCHAR(32) NOT NULL,
                                 name VARCHAR(32) NOT NULL,
                                 PRIMARY KEY (id));

INSERT INTO maps(id, name) VALUES ('de_ancient', 'Ancient'),
                                          ('de_calavera', 'Calavera'),
                                          ('de_cbble', 'Cobblestone'),
                                          ('de_dust2', 'Dust 2'),
                                          ('de_inferno', 'Inferno'),
                                          ('de_mirage', 'Mirage'),
                                          ('de_nuke', 'Nuke'),
                                          ('de_overpass', 'Overpass'),
                                          ('de_pitstop', 'Pitstop'),
                                          ('de_shortdust', 'Shortdust'),
                                          ('de_shortnuke', 'Nuke'),
                                          ('de_train', 'Train'),
                                          ('de_vertigo', 'Vertigo');

CREATE TABLE IF NOT EXISTS users (steam_id     BIGINT      NOT NULL,
                                  discord_id   BIGINT,
                                  display_name VARCHAR(64) NOT NULL,
                                  PRIMARY KEY (steam_id),
                                  CONSTRAINT unique_user UNIQUE (steam_id, discord_id, display_name));

CREATE TABLE IF NOT EXISTS teams (id   VARCHAR(32) NOT NULL,
                                  name VARCHAR(64) NOT NULL,
                                  tag  VARCHAR(15) NOT NULL DEFAULT '',
                                  PRIMARY KEY (id));

CREATE TABLE IF NOT EXISTS team_players (team_id  VARCHAR(32) NOT NULL REFERENCES teams(id),
                                         steam_id BIGINT      NOT NULL REFERENCES users(steam_id),
                                         PRIMARY KEY (team_id, steam_id));

CREATE TABLE IF NOT EXISTS matches (id        VARCHAR(32) NOT NULL,
                                    status    INTEGER     NOT NULL DEFAULT 0,
                                    live_timestamp TIMESTAMP   NOT NULL,
                                    team1_id  VARCHAR(32) NOT NULL REFERENCES teams(id),
                                    team2_id  VARCHAR(32) NOT NULL REFERENCES teams(id),
                                    PRIMARY KEY (id));

CREATE TABLE IF NOT EXISTS match_maps (match_id VARCHAR(32) NOT NULL REFERENCES matches(id),
                                       map_id   VARCHAR(32) NOT NULL REFERENCES maps(id),
                                       side     VARCHAR(32) NOT NULL,
                                       PRIMARY KEY (match_id, map_id));

