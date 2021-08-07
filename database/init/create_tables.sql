CREATE TABLE IF NOT EXISTS server_tokens (server_token VARCHAR(32) NOT NULL,
                                          PRIMARY KEY (server_token));

CREATE TABLE IF NOT EXISTS maps (map_id   VARCHAR(32) NOT NULL,
                                 map_name VARCHAR(32) NOT NULL,
                                 PRIMARY KEY (map_id));

INSERT INTO maps(map_id, map_name) VALUES ('de_ancient', 'Ancient'),
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

CREATE TABLE IF NOT EXISTS teams (team_id   VARCHAR(32) NOT NULL,
                                  team_name VARCHAR(64) NOT NULL,
                                  team_tag  VARCHAR(15) NOT NULL DEFAULT '',
                                  PRIMARY KEY (team_id));

CREATE TABLE IF NOT EXISTS team_players (team_id  VARCHAR(32) NOT NULL REFERENCES teams(team_id),
                                         steam_id BIGINT      NOT NULL REFERENCES users(steam_id),
                                         CONSTRAINT unique_player UNIQUE (team_id, steam_id));

CREATE TABLE IF NOT EXISTS matches (match_id  VARCHAR(32) NOT NULL,
                                    server_id VARCHAR(32)            DEFAULT NULL,
                                    team1_id  VARCHAR(32) NOT NULL,
                                    team2_id  VARCHAR(32) NOT NULL,
                                    PRIMARY KEY (match_id));

CREATE TABLE IF NOT EXISTS match_maps (match_id VARCHAR(32) NOT NULL REFERENCES matches(match_id),
                                       map_id   VARCHAR(32) NOT NULL REFERENCES maps(map_id),
                                       side     VARCHAR(32) NOT NULL,
                                       CONSTRAINT unique_map UNIQUE (match_id, map_id));

