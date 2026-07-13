# Migraciones CrediBot v2

## Orden de ejecución

1. `supabase/schema.sql` — esquema v1 base
2. `supabase/migrations/001_v2_schema.sql` — tablas y columnas v2
3. `supabase/migrations/002_validation_failures.sql` — contador de fallos
4. `supabase/migrations/003_rag_vector_search.sql` — función `match_rag_chunks`
5. `supabase/seed_credit_profiles.sql` — perfiles ficticios (idempotente)

## Rollback

Las migraciones v2 son aditivas. Para revertir en staging:

```sql
drop table if exists rag_chunks cascade;
drop table if exists rag_documents cascade;
drop table if exists inbound_events cascade;
drop table if exists tool_audit_logs cascade;
drop table if exists credit_history_events cascade;
drop table if exists credit_profiles cascade;
```

No eliminar columnas añadidas a `users` o `credit_requests` en producción sin backup.
