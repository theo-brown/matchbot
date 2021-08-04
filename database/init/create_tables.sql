CREATE TABLE IF NOT EXISTS users (steam_id     BIGINT      NOT NULL,
                                  discord_id   BIGINT,
                                  display_name VARCHAR(64) NOT NULL,
                                  PRIMARY KEY (steam_id),
                                  CONSTRAINT unique_user UNIQUE (steam_id, discord_id, display_name));

CREATE TABLE IF NOT EXISTS teams (team_id   VARCHAR(32) NOT NULL,
                                  team_name VARCHAR(64) NOT NULL,
                                  team_tag  VARCHAR(15) NOT NULL DEFAULT '',
                                  PRIMARY KEY (team_id));

CREATE TABLE IF NOT EXISTS team_players (team_id  VARCHAR(32) NOT NULL,
                                         steam_id BIGINT      NOT NULL,
                                         PRIMARY KEY (team_id),
                                         CONSTRAINT unique_player UNIQUE (team_id, steam_id));

CREATE TABLE IF NOT EXISTS game_servers (server_token VARCHAR(32) NOT NULL,
                                         ip           INET        NOT NULL,
                                         port         INTEGER     NOT NULL,
                                         gotv_port    INTEGER     NOT NULL,
                                         PRIMARY KEY (server_token));
