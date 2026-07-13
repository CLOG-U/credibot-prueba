-- CrediBot v2 — Migración 001
-- Ejecutar después de schema.sql v1

create extension if not exists "uuid-ossp";
create extension if not exists vector;

alter table users add column if not exists cedula varchar(10) unique;
alter table users add column if not exists consent_given boolean default false;
alter table users add column if not exists consent_at timestamptz;

create table if not exists credit_profiles (
    id uuid primary key default uuid_generate_v4(),
    cedula varchar(10) not null unique,
    full_name text not null,
    credit_score integer not null check (credit_score between 1 and 999),
    score_category text not null check (
        score_category in ('excelente', 'aceptable', 'regular', 'alto_riesgo')
    ),
    active_credits integer default 0,
    total_debt numeric(12, 2) default 0,
    monthly_debt_payment numeric(12, 2) default 0,
    has_delinquency boolean default false,
    delinquency_days integer default 0,
    is_blacklisted boolean default false,
    no_credit_history boolean default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists credit_history_events (
    id uuid primary key default uuid_generate_v4(),
    credit_profile_id uuid not null references credit_profiles(id) on delete cascade,
    event_type text not null,
    description text,
    event_date date,
    created_at timestamptz not null default now()
);

alter table credit_requests add column if not exists cedula varchar(10);
alter table credit_requests add column if not exists credit_score integer;
alter table credit_requests add column if not exists score_category text;
alter table credit_requests add column if not exists employment_type text;
alter table credit_requests add column if not exists monthly_expenses numeric(12, 2);
alter table credit_requests add column if not exists loan_purpose text;
alter table credit_requests add column if not exists max_amount numeric(12, 2);
alter table credit_requests add column if not exists annual_rate numeric(6, 4);
alter table credit_requests add column if not exists eligibility_status text;
alter table credit_requests add column if not exists rejection_reasons jsonb;
alter table credit_requests add column if not exists rules_version text default 'v2.0';

create table if not exists tool_audit_logs (
    id uuid primary key default uuid_generate_v4(),
    conversation_id uuid references conversations(id) on delete set null,
    trace_id text,
    tool_name text not null,
    input_payload jsonb,
    output_payload jsonb,
    success boolean default true,
    error_code text,
    latency_ms integer,
    created_at timestamptz not null default now()
);

create table if not exists inbound_events (
    id uuid primary key default uuid_generate_v4(),
    provider text not null,
    external_message_id text not null,
    phone text,
    payload jsonb,
    processed_at timestamptz not null default now(),
    unique (provider, external_message_id)
);

create table if not exists rag_documents (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    source_path text,
    created_at timestamptz not null default now()
);

create table if not exists rag_chunks (
    id uuid primary key default uuid_generate_v4(),
    document_id uuid references rag_documents(id) on delete cascade,
    content text not null,
    embedding vector(1536),
    metadata jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_credit_profiles_cedula on credit_profiles(cedula);
create index if not exists idx_credit_profiles_category on credit_profiles(score_category);
create index if not exists idx_tool_audit_conversation on tool_audit_logs(conversation_id);
create index if not exists idx_inbound_events_provider on inbound_events(provider, external_message_id);
create index if not exists idx_rag_chunks_document on rag_chunks(document_id);
