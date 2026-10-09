CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(768),
    metadata JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_documents_metadata
    ON documents USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_documents_embedding
    ON documents USING hnsw (embedding vector_cosine_ops);

-- Audit log for security events
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    doc_id UUID,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);