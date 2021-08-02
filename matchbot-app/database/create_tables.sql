CREATE TABLE IF NOT EXISTS users (steam_id     BIGINT      UNSIGNED NOT NULL,
                                  discord_id   BIGINT      UNSIGNED NOT NULL,
                                  display_name VARCHAR(64)          NOT NULL,
                                  PRIMARY KEY (steam_id),
                                  CONSTRAINT unique_user UNIQUE (steam_id, discord_id, display_name));

CREATE TABLE IF NOT EXISTS teams (team_id           VARCHAR(32)          NOT NULL,
                                  team_name         VARCHAR(64)          NOT NULL,
                                  team_tag          VARCHAR(15)          NOT NULL DEFAULT '',
                                  number_of_players TINYINT     UNSIGNED NOT NULL,
                                  steamid_p1        BIGINT      UNSIGNED          DEFAULT NULL,
                                  steamid_p2        BIGINT      UNSIGNED          DEFAULT NULL,
                                  steamid_p3        BIGINT      UNSIGNED          DEFAULT NULL,
                                  steamid_p4        BIGINT      UNSIGNED          DEFAULT NULL,
                                  steamid_p5        BIGINT      UNSIGNED          DEFAULT NULL,
                                  PRIMARY KEY (team_id));
