-- Owner-only migration. Runtime uses a separate login granted learngraph_runtime.
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'learngraph_runtime') THEN
        CREATE ROLE learngraph_runtime NOLOGIN;
    END IF;
END $$;

CREATE SCHEMA IF NOT EXISTS learngraph;
REVOKE ALL ON SCHEMA learngraph FROM PUBLIC;
GRANT USAGE ON SCHEMA learngraph TO learngraph_runtime;

CREATE TABLE IF NOT EXISTS learngraph.releases (
    id text PRIMARY KEY,
    content_hash text NOT NULL CHECK (length(content_hash) = 64),
    payload jsonb NOT NULL,
    published_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE learngraph.releases ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS runtime_release_read ON learngraph.releases;
CREATE POLICY runtime_release_read ON learngraph.releases
    FOR SELECT TO learngraph_runtime USING (true);
GRANT SELECT ON learngraph.releases TO learngraph_runtime;

CREATE OR REPLACE FUNCTION learngraph.reject_release_mutation()
RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
    RAISE EXCEPTION 'Published releases are immutable; publish a new version';
END;
$$;
REVOKE ALL ON FUNCTION learngraph.reject_release_mutation() FROM PUBLIC;
DROP TRIGGER IF EXISTS release_immutable ON learngraph.releases;
CREATE TRIGGER release_immutable BEFORE UPDATE OR DELETE ON learngraph.releases
    FOR EACH ROW EXECUTE FUNCTION learngraph.reject_release_mutation();

CREATE TABLE IF NOT EXISTS learngraph.quota_buckets (
    key text PRIMARY KEY,
    requests integer NOT NULL DEFAULT 0 CHECK (requests >= 0),
    expires_at timestamptz NOT NULL
);
CREATE INDEX IF NOT EXISTS quota_expiry_idx ON learngraph.quota_buckets (expires_at);
ALTER TABLE learngraph.quota_buckets ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON learngraph.quota_buckets FROM learngraph_runtime, PUBLIC;

CREATE OR REPLACE FUNCTION learngraph.reserve_budget(p_namespace text, p_client text)
RETURNS TABLE(allowed boolean, retry_after integer)
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE
    moment timestamptz := clock_timestamp();
    minute_start timestamptz := date_trunc('minute', moment);
    day_start timestamptz := date_trunc('day', moment, 'UTC');
    day_key text;
    client_key text;
    day_count integer;
    client_count integer;
BEGIN
    IF length(p_namespace) NOT BETWEEN 1 AND 40 OR p_client !~ '^[a-f0-9]{64}$' THEN
        RAISE EXCEPTION 'Invalid quota identifier';
    END IF;
    -- One tiny serialized reservation protects both budgets atomically at this demo scale.
    PERFORM pg_advisory_xact_lock(hashtextextended('learngraph:' || p_namespace, 0));
    day_key := p_namespace || ':day:' || extract(epoch FROM day_start)::bigint;
    client_key := p_namespace || ':client:' || p_client || ':' || extract(epoch FROM minute_start)::bigint;
    SELECT requests INTO day_count FROM learngraph.quota_buckets WHERE key = day_key;
    SELECT requests INTO client_count FROM learngraph.quota_buckets WHERE key = client_key;
    IF coalesce(day_count, 0) >= 1000 THEN
        RETURN QUERY SELECT false, greatest(1, ceil(extract(epoch FROM day_start + interval '1 day' - moment))::integer);
        RETURN;
    END IF;
    IF coalesce(client_count, 0) >= 10 THEN
        RETURN QUERY SELECT false, greatest(1, ceil(extract(epoch FROM minute_start + interval '1 minute' - moment))::integer);
        RETURN;
    END IF;
    INSERT INTO learngraph.quota_buckets(key, requests, expires_at) VALUES
        (day_key, 1, day_start + interval '2 days'),
        (client_key, 1, minute_start + interval '2 days')
    ON CONFLICT (key) DO UPDATE SET requests = learngraph.quota_buckets.requests + 1;
    -- Bounded opportunistic cleanup; no paid cron or public delete privilege.
    DELETE FROM learngraph.quota_buckets WHERE key IN (
        SELECT key FROM learngraph.quota_buckets WHERE expires_at <= moment
        ORDER BY expires_at LIMIT 20
    );
    RETURN QUERY SELECT true, 0;
END;
$$;
REVOKE ALL ON FUNCTION learngraph.reserve_budget(text, text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION learngraph.reserve_budget(text, text) TO learngraph_runtime;
