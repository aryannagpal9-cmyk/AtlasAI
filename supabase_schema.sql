-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Clients Table
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    tax_profile JSONB DEFAULT '{}'::jsonb,
    behavioural_profile JSONB DEFAULT '{}'::jsonb,
    vulnerability_score NUMERIC DEFAULT 0.0,
    vulnerability_category TEXT,
    vulnerability_notes TEXT,
    last_proactive_check TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Market Snapshots (UK Specific)
CREATE TABLE IF NOT EXISTS market_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ DEFAULT now(),
    ftse_100_value NUMERIC,
    ftse_250_value NUMERIC,
    sector_performance JSONB NOT NULL, -- e.g., {"Financials": -0.02, "Energy": 0.01}
    raw_data JSONB
);

-- Client Portfolios
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    holdings JSONB NOT NULL, -- List of assets and quantities
    total_value_gbp NUMERIC NOT NULL,
    cash_balance_gbp NUMERIC DEFAULT 0,
    current_risk_score NUMERIC DEFAULT 5.0,
    target_risk_score NUMERIC DEFAULT 5.0,
    last_updated TIMESTAMPTZ DEFAULT now()
);

-- Immutable Portfolio Snapshots
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    snapshot_timestamp TIMESTAMPTZ DEFAULT now(),
    holdings_snapshot JSONB NOT NULL,
    total_value_snapshot NUMERIC NOT NULL,
    market_snapshot_id UUID REFERENCES market_snapshots(id),
    trigger_event_id UUID -- Link to the risk event that triggered this snapshot if any
);

-- Risk Events (Append-Only)
CREATE TABLE IF NOT EXISTS risk_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- market_risk, tax_opportunity, compliance_exposure
    urgency TEXT CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    deterministic_classification JSONB NOT NULL, -- The "Why" from the reasoning engine
    ai_interpretation JSONB, -- JSON output from RiskInterpretationAgent
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'auto_resolved', 'adviser_resolved', 'dismissed')),
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

COMMENT ON COLUMN risk_events.event_type IS 'Categories: market_risk, tax_opportunity, compliance_exposure, pension_allowance, iht_pulse, isa_optimization, cgt_exposure, vulnerability_alert';

-- Behavioural Memory (Vector)
CREATE TABLE IF NOT EXISTS behavioural_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding VECTOR(384), -- Assuming HuggingFace embeddings (all-MiniLM-L6-v2)
    source_reference TEXT, -- e.g., "Meeting 2024-05-10"
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Meeting Briefs
CREATE TABLE IF NOT EXISTS meeting_briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    meeting_timestamp TIMESTAMPTZ NOT NULL,
    brief_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Draft Actions
CREATE TABLE IF NOT EXISTS draft_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_event_id UUID REFERENCES risk_events(id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL, -- email, letter, notification
    draft_content JSONB NOT NULL, -- {subject, body, tone}
    compliance_check_status TEXT DEFAULT 'pending',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'sent')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Heartbeat Logs (Sweep Tracking)
CREATE TABLE IF NOT EXISTS heartbeat_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sweep_type TEXT NOT NULL, -- 'book_sweep', 'mandate_check', 'feed_sync'
    portfolios_scanned INTEGER DEFAULT 0,
    risks_found INTEGER DEFAULT 0,
    result_summary TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Action Logs (Audit Trail)
CREATE TABLE IF NOT EXISTS action_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    adviser_id UUID, -- For future multi-adviser support
    action_type TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- e.g., 'risk_event', 'draft_action'
    entity_id UUID NOT NULL,
    decision TEXT NOT NULL, -- 'approved', 'dismissed', etc.
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Market Impact Reports
CREATE TABLE IF NOT EXISTS market_impact_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ DEFAULT now(),
    market_snapshot_id UUID REFERENCES market_snapshots(id),
    global_outlook TEXT NOT NULL,
    sector_impact_map JSONB NOT NULL,
    vulnerable_clients_alert JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- pgvector Similarity Search RPC
CREATE OR REPLACE FUNCTION match_memory (
  query_embedding vector(384),
  match_threshold float,
  match_count int,
  client_id_filter uuid
)
RETURNS TABLE (
  id uuid,
  content text,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  select
    behavioural_memory.id,
    behavioural_memory.content,
    1 - (behavioural_memory.embedding <=> query_embedding) as similarity
  from behavioural_memory
  where 
    behavioural_memory.client_id = client_id_filter
    and 1 - (behavioural_memory.embedding <=> query_embedding) > match_threshold
  order by (behavioural_memory.embedding <=> query_embedding) asc
  limit match_count;
$$;
