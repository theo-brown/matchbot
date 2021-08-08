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

CREATE TABLE IF NOT EXISTS sides (side VARCHAR(32) NOT NULL,
                                  PRIMARY KEY (side));

INSERT INTO sides(side) VALUES ('knife'),
                               ('team1_ct'),
                               ('team1_t'),
                               ('team2_ct'),
                               ('team2_t');

CREATE TABLE IF NOT EXISTS server_tokens (token VARCHAR(32) NOT NULL,
                                          PRIMARY KEY (token));

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

CREATE TABLE IF NOT EXISTS match_maps (match_id   VARCHAR(32) NOT NULL REFERENCES matches(id),
                                       map_number INTEGER     NOT NULL,
                                       map_id     VARCHAR(32) NOT NULL REFERENCES maps(id),
                                       side       VARCHAR(32) NOT NULL REFERENCES sides(side),
                                       PRIMARY KEY (match_id, map_number));

CREATE TABLE IF NOT EXISTS servers (id            VARCHAR(32) NOT NULL UNIQUE,
                                    token         VARCHAR(32) NOT NULL UNIQUE,
                                    ip            INET,
                                    port          INTEGER     UNIQUE,
                                    gotv_port     INTEGER     UNIQUE,
                                    password      VARCHAR(32) DEFAULT NULL,
                                    gotv_password VARCHAR(32) DEFAULT NULL,
                                    rcon_password VARCHAR(32) DEFAULT NULL,
                                    match_id      VARCHAR(32) DEFAULT NULL REFERENCES matches(id),
                                    PRIMARY KEY (id));
