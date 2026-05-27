const ESTADOS = [
  { value: "", label: "Todos" },
  { value: "pendiente", label: "Pendiente" },
  { value: "cotizado", label: "Cotizado" },
  { value: "ganado", label: "Ganado" },
  { value: "descartado", label: "Descartado" },
];

const SCORES = [
  { value: "50", label: "50+" },
  { value: "70", label: "70+" },
  { value: "90", label: "90+" },
];

const TIPOS = [
  { value: "", label: "Todos" },
  { value: "compra_agil", label: "Compra Ágil" },
  { value: "licitacion", label: "Licitación" },
];

export default function FilterBar({ filters, onChange }) {
  const update = (key, value) => onChange({ ...filters, [key]: value });

  const selectClass =
    "border border-slate-300 rounded px-2 py-1.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-talinay";

  return (
    <div className="flex flex-wrap items-end gap-3 rounded-lg border border-slate-200 bg-white p-4">
      <div>
        <label className="mb-1 block text-xs font-medium text-slate-600">
          Estado
        </label>
        <select
          value={filters.estado}
          onChange={(e) => update("estado", e.target.value)}
          className={selectClass}
        >
          {ESTADOS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-slate-600">
          Score mínimo
        </label>
        <select
          value={filters.minScore}
          onChange={(e) => update("minScore", e.target.value)}
          className={selectClass}
        >
          {SCORES.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-slate-600">
          Tipo
        </label>
        <select
          value={filters.tipo}
          onChange={(e) => update("tipo", e.target.value)}
          className={selectClass}
        >
          {TIPOS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="min-w-[200px] flex-1">
        <label className="mb-1 block text-xs font-medium text-slate-600">
          Búsqueda
        </label>
        <input
          type="text"
          placeholder="Nombre u organismo..."
          value={filters.q}
          onChange={(e) => update("q", e.target.value)}
          className="w-full rounded border border-slate-300 bg-white px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-talinay"
        />
      </div>
    </div>
  );
}
