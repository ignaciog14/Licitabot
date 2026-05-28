-- Tabla de configuración general del sistema.
create table if not exists public.configuracion (
  clave   text primary key,
  valor   jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.configuracion enable row level security;

-- Semilla: keywords por defecto de Talinay
insert into public.configuracion (clave, valor) values (
  'keywords',
  '["librería","artículos de oficina","insumos escolares","papelería","tinta","tampón","sello","plumón","lápiz","cuaderno","pintura","acrílica","tempera","pintura tela","pintura género","brocha","rodillo","barniz","manualidades","materiales didácticos","materiales escolares","útiles escolares","poliestireno","plumavit","foam","espuma","corte a medida","fieltro","disco de pulir","paño industrial","silicona","aceite industrial","emulsión","lubricante"]'
) on conflict (clave) do nothing;

-- keywords_matched: qué palabras matchearon en esta oportunidad
alter table public.oportunidades
  add column if not exists keywords_matched jsonb;
