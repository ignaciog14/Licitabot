-- Talinay Compras Públicas — esquema inicial
-- Ejecutar en el SQL editor de Supabase.

-- =============================================================
-- Función y trigger para mantener updated_at automáticamente.
-- =============================================================
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- =============================================================
-- Tabla: oportunidades
-- =============================================================
create table if not exists public.oportunidades (
  id                 uuid primary key default gen_random_uuid(),
  codigo             text unique not null,
  tipo               text not null check (tipo in ('compra_agil', 'licitacion')),
  nombre             text not null,
  organismo          text not null,
  monto_disponible   numeric,
  moneda             text default 'CLP',
  fecha_cierre       timestamptz,
  estado             text,
  descripcion        text,
  region             text,
  raw_data           jsonb,
  score_relevancia   integer check (score_relevancia between 0 and 100),
  justificacion_ia   text,
  estado_interno     text default 'pendiente'
                     check (estado_interno in ('pendiente', 'cotizado', 'descartado', 'ganado', 'perdido')),
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);

create index if not exists idx_oportunidades_codigo           on public.oportunidades (codigo);
create index if not exists idx_oportunidades_estado_interno   on public.oportunidades (estado_interno);
create index if not exists idx_oportunidades_score_relevancia on public.oportunidades (score_relevancia desc);
create index if not exists idx_oportunidades_created_at       on public.oportunidades (created_at desc);

drop trigger if exists trg_oportunidades_updated_at on public.oportunidades;
create trigger trg_oportunidades_updated_at
before update on public.oportunidades
for each row execute function public.set_updated_at();

-- =============================================================
-- Tabla: cotizaciones
-- =============================================================
create table if not exists public.cotizaciones (
  id                  uuid primary key default gen_random_uuid(),
  oportunidad_id      uuid not null references public.oportunidades(id) on delete cascade,
  borrador_ia         text,
  borrador_editado    text,
  precio_ofertado     numeric,
  plazo_entrega_dias  integer,
  estado              text not null default 'borrador'
                      check (estado in ('borrador', 'aprobada', 'enviada')),
  pdf_url             text,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);

create index if not exists idx_cotizaciones_oportunidad_id on public.cotizaciones (oportunidad_id);
create index if not exists idx_cotizaciones_estado         on public.cotizaciones (estado);

drop trigger if exists trg_cotizaciones_updated_at on public.cotizaciones;
create trigger trg_cotizaciones_updated_at
before update on public.cotizaciones
for each row execute function public.set_updated_at();

-- =============================================================
-- Tabla: sync_log
-- =============================================================
create table if not exists public.sync_log (
  id                         uuid primary key default gen_random_uuid(),
  tipo                       text not null check (tipo in ('compras_agiles', 'licitaciones')),
  oportunidades_encontradas  integer default 0,
  oportunidades_nuevas       integer default 0,
  errores                    jsonb,
  created_at                 timestamptz not null default now()
);

create index if not exists idx_sync_log_created_at on public.sync_log (created_at desc);

-- =============================================================
-- Row Level Security
-- El service_role bypasea RLS por defecto en Supabase, por lo que
-- todo el acceso desde el backend (con SUPABASE_SERVICE_KEY) funciona
-- sin políticas. No se agregan políticas para anon: el frontend
-- siempre pasa por el backend.
-- =============================================================
alter table public.oportunidades enable row level security;
alter table public.cotizaciones  enable row level security;
alter table public.sync_log      enable row level security;
