-- Migración 002: contador de fallos de validación en conversaciones
alter table conversations add column if not exists validation_failures integer default 0;
