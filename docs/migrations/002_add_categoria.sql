-- HU-07: agregar columna `categoria` a oportunidades para almacenar
-- la categoría que la IA detecta (librería / pinturas / etc.).
alter table public.oportunidades
  add column if not exists categoria text;

create index if not exists idx_oportunidades_categoria
  on public.oportunidades (categoria);
