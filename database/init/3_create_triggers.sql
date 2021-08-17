CREATE OR REPLACE FUNCTION notify_match_status()
  RETURNS TRIGGER AS
    $$
    DECLARE
        payload TEXT;
    BEGIN
        payload := json_build_object('id', NEW.id,
                                     'status', NEW.status);
        PERFORM pg_notify('match_status', payload);
        RETURN NULL;
    END
    $$
  LANGUAGE plpgsql;

CREATE TRIGGER update_match_status
    AFTER UPDATE OF status ON matches
    FOR EACH ROW
    EXECUTE PROCEDURE notify_match_status();

CREATE TRIGGER new_match_status
    AFTER INSERT ON matches
    FOR EACH ROW
    EXECUTE PROCEDURE notify_match_status();
