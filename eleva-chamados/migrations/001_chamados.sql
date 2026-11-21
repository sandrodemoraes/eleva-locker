create table if not exists chamados (
  id text primary key,
  cliente text not null default '',
  telefone text not null default '',
  endereco text not null default '',
  servico text not null default '',
  urgencia text not null default 'normal',
  descricao text not null default '',
  transcricao text not null default '',
  status text not null default 'aguardando_nota',
  criado_por text not null default '',
  criado_por_nome text not null default '',
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists chamados_status_idx on chamados (status);
create index if not exists chamados_criado_em_idx on chamados (criado_em desc);
