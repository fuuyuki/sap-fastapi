-- Adds optional Android camera evidence to medlogs.
-- Safe to run on an existing database (fresh installs already get these
-- columns from db/init.sql).
--
-- Apply with:
--   docker compose exec -T db psql -U fauxpg -d sapdb < db/migrations/002_medlog_evidence.sql

ALTER TABLE public.medlogs
    ADD COLUMN IF NOT EXISTS verification_method character varying(30),
    ADD COLUMN IF NOT EXISTS verification_confidence double precision,
    ADD COLUMN IF NOT EXISTS verified_at timestamp with time zone,
    ADD COLUMN IF NOT EXISTS evidence_key character varying(255);
