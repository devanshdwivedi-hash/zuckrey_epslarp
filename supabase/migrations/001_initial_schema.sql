-- ==========================================================
-- Migration 001: Initial Schema Setup
-- File: supabase/migrations/001_initial_schema.sql
-- ==========================================================

BEGIN;

CREATE TABLE IF NOT EXISTS public.published_posts (
    id                SERIAL PRIMARY KEY,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    timestamp         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    title             VARCHAR(512) NOT NULL,
    content           TEXT NOT NULL,
    selection_reason  TEXT NOT NULL,
    why_relevant_now  TEXT NOT NULL,
    sources           JSONB,
    vector_embedding  JSONB,
    embedding         JSONB,
    source_url        VARCHAR(1024),
    source_name       VARCHAR(256),
    persona_name      VARCHAR(256),
    score             INTEGER
);

CREATE INDEX IF NOT EXISTS idx_published_posts_created_at ON public.published_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_published_posts_source_url ON public.published_posts(source_url);

CREATE TABLE IF NOT EXISTS public.rejected_posts (
    id                SERIAL PRIMARY KEY,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    timestamp         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    title             VARCHAR(512) NOT NULL,
    rejection_reason  TEXT NOT NULL,
    score             INTEGER,
    source_url        VARCHAR(1024),
    source_name       VARCHAR(256)
);

CREATE INDEX IF NOT EXISTS idx_rejected_posts_created_at ON public.rejected_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rejected_posts_source_url ON public.rejected_posts(source_url);

COMMIT;
