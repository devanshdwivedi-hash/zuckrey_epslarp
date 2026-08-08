-- Migration Script: Add missing columns if tables already existed
BEGIN;

-- 1. Ensure published_posts exists and has all required columns
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

-- Add created_at if table was created previously without it
ALTER TABLE public.published_posts 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE public.published_posts 
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE public.published_posts 
ADD COLUMN IF NOT EXISTS vector_embedding JSONB;

-- Indexes for published_posts
CREATE INDEX IF NOT EXISTS idx_published_posts_created_at ON public.published_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_published_posts_source_url ON public.published_posts(source_url);


-- 2. Ensure rejected_posts exists and has all required columns
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

-- Add created_at if table was created previously without it
ALTER TABLE public.rejected_posts 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE public.rejected_posts 
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW();

-- Indexes for rejected_posts
CREATE INDEX IF NOT EXISTS idx_rejected_posts_created_at ON public.rejected_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rejected_posts_source_url ON public.rejected_posts(source_url);

COMMIT;
