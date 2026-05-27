const clpFormatter = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
  maximumFractionDigits: 0,
});

export function formatCLP(monto) {
  if (monto == null || monto === "") return "—";
  return clpFormatter.format(monto);
}

export function tiempoRelativoCierre(fechaCierre) {
  if (!fechaCierre) return "Sin fecha";
  const cierre = new Date(fechaCierre);
  if (Number.isNaN(cierre.getTime())) return "Sin fecha";

  const diffMs = cierre.getTime() - Date.now();
  if (diffMs < 0) return "Cerrada";

  const diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDias === 0) return "Cierra hoy";
  if (diffDias === 1) return "Cierra mañana";
  return `Cierra en ${diffDias} días`;
}

export function tiempoRelativoDesde(fecha) {
  if (!fecha) return "nunca";
  const d = fecha instanceof Date ? fecha : new Date(fecha);
  if (Number.isNaN(d.getTime())) return "nunca";

  const diffMin = Math.floor((Date.now() - d.getTime()) / 60000);
  if (diffMin < 1) return "hace segundos";
  if (diffMin < 60) return `hace ${diffMin} min`;

  const horas = Math.floor(diffMin / 60);
  if (horas < 24) return `hace ${horas} h`;

  const dias = Math.floor(horas / 24);
  return `hace ${dias} d`;
}
