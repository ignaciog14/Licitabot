const ESTILOS = {
  pendiente: "bg-slate-100 text-slate-700",
  cotizado: "bg-blue-100 text-blue-800",
  descartado: "bg-red-100 text-red-700",
  ganado: "bg-green-100 text-green-800",
  perdido: "bg-stone-100 text-stone-700",
};

const ETIQUETAS = {
  pendiente: "Pendiente",
  cotizado: "Cotizado",
  descartado: "Descartado",
  ganado: "Ganado",
  perdido: "Perdido",
};

export default function StatusBadge({ estado }) {
  const key = estado || "pendiente";
  const classes = ESTILOS[key] || ESTILOS.pendiente;
  const label = ETIQUETAS[key] || key;

  return (
    <span
      className={`inline-flex px-2 py-1 rounded text-xs font-medium ${classes}`}
    >
      {label}
    </span>
  );
}
