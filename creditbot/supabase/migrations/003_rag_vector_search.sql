-- Migración 003: búsqueda vectorial RAG en pgvector
create or replace function match_rag_chunks(
    query_embedding vector(1536),
    match_threshold float default 0.35,
    match_count int default 3
)
returns table (
    chunk_id uuid,
    content text,
    source_path text,
    title text,
    similarity float
)
language sql stable
as $$
    select
        rc.id as chunk_id,
        rc.content,
        rd.source_path,
        rd.title,
        1 - (rc.embedding <=> query_embedding) as similarity
    from rag_chunks rc
    join rag_documents rd on rd.id = rc.document_id
    where rc.embedding is not null
      and 1 - (rc.embedding <=> query_embedding) >= match_threshold
    order by rc.embedding <=> query_embedding
    limit match_count;
$$;
