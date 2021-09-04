CREATE OR REPLACE FUNCTION get_users_by_team(select_team_id VARCHAR(32))
    RETURNS TABLE(steam_id INTEGER, discord_id INTEGER, display_name VARCHAR(32))
    AS $$
    SELECT steam_id, discord_id, display_name FROM users
        WHERE steam_id = ANY(SELECT steam_id from team_players WHERE team_id = select_team_id)
    $$
    LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_maps_by_match(select_match_id VARCHAR(32))
    RETURNS TABLE(map_id VARCHAR(32), side VARCHAR(32))
    AS $$
    SELECT map_id, side FROM match_maps
        WHERE match_id = select_match_id;
    $$
    LANGUAGE SQL;

