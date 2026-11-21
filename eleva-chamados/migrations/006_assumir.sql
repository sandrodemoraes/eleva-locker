alter table chamados add column if not exists assumido_por text not null default '';
alter table chamados add column if not exists assumido_em timestamptz;
