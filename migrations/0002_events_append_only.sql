CREATE OR REPLACE FUNCTION prevent_event_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'events table is append-only';
END;
$$;

CREATE TRIGGER events_no_update_delete
BEFORE UPDATE OR DELETE ON events
FOR EACH ROW
EXECUTE FUNCTION prevent_event_mutation();