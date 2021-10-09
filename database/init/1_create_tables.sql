CREATE TABLE IF NOT EXISTS maps (id   VARCHAR(32) NOT NULL,
                                 name VARCHAR(32) NOT NULL,
                                 PRIMARY KEY (id));

CREATE TABLE IF NOT EXISTS server_tokens (token VARCHAR(32) NOT NULL,
                                          PRIMARY KEY (token));

CREATE TABLE IF NOT EXISTS users (steam_id     BIGINT      NOT NULL,
                                  discord_id   BIGINT               DEFAULT NULL,
                                  display_name VARCHAR(64) NOT NULL,
                                  PRIMARY KEY (steam_id),
                                  CONSTRAINT unique_user UNIQUE (steam_id, discord_id, display_name));

CREATE TABLE IF NOT EXISTS teams (id   UUID NOT NULL,
                                  name VARCHAR(64) NOT NULL,
                                  tag  VARCHAR(15) NOT NULL DEFAULT '',
                                  PRIMARY KEY (id));

CREATE TABLE IF NOT EXISTS team_members (team_id  UUID NOT NULL REFERENCES teams(id),
                                         steam_id BIGINT      NOT NULL REFERENCES users(steam_id),
                                         PRIMARY KEY (team_id, steam_id));

CREATE TYPE match_status AS ENUM ('CREATED', 'QUEUED', 'LIVE', 'FINISHED');

CREATE TABLE IF NOT EXISTS matches (id                 UUID         NOT NULL,
                                    status             match_status NOT NULL DEFAULT 'CREATED',
                                    created_timestamp  TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                    live_timestamp     TIMESTAMPTZ           DEFAULT NULL,
                                    finished_timestamp TIMESTAMPTZ           DEFAULT NULL,
                                    team1_id           UUID         NOT NULL REFERENCES teams(id),
                                    team2_id           UUID         NOT NULL REFERENCES teams(id),
                                    PRIMARY KEY (id));

CREATE TYPE map_side AS ENUM ('knife', 'team1_ct', 'team1_t', 'team2_ct', 'team2_t');

CREATE TABLE IF NOT EXISTS match_maps (match_id UUID        NOT NULL REFERENCES matches(id),
                                       number   INTEGER     NOT NULL,
                                       id       VARCHAR(32) NOT NULL REFERENCES maps(id),
                                       side     map_side    NOT NULL DEFAULT 'knife',
                                       PRIMARY KEY (match_id, number));

CREATE TABLE IF NOT EXISTS servers (id            UUID        NOT NULL,
                                    token         VARCHAR(32) NOT NULL UNIQUE REFERENCES server_tokens(token),
                                    ip            INET,
                                    port          INTEGER     UNIQUE,
                                    gotv_port     INTEGER     UNIQUE,
                                    password      VARCHAR(32) DEFAULT NULL,
                                    gotv_password VARCHAR(32) DEFAULT NULL,
                                    rcon_password VARCHAR(32) DEFAULT NULL,
                                    match_id      UUID        DEFAULT NULL REFERENCES matches(id),
                                    PRIMARY KEY (id));
