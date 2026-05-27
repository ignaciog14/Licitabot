import { Link, useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import api from "../lib/api.js";
import CotizacionEditor from "../components/CotizacionEditor.jsx";
import CountdownTimer from "../components/CountdownTimer.jsx";
import ScoreBadge from "../components/ScoreBadge.jsx";
import { formatCLP } from "../lib/format.js";

export default function Detalle() {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    data: op,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["oportunidad", id],
    queryFn: async () => {
      const { data } = await api.get(`/oportunidades/${id}`);
      return data;
    },
  });

  if (isLoading) {
    return <div className="text-slate-500">Cargando oportunidad...</div>;
  }

  if (error) {
    return (
      <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800">
        Error: {error?.response?.data?.detail || error.message}
      </div>
    );
  }

  if (!op) {
    return <div className="text-slate-500">Oportunidad no encontrada.</div>;
  }

  const raw = op.raw_data || {};
  const unidad =
    raw.unidad ||
    raw.unidadCompradora ||
    raw.unidad_compradora ||
    null;
  const productos = raw.productos || raw.items || raw.lineas || null;
  const direccionEntrega =
    raw.direccion_entrega || raw.direccionEntrega || raw.direccion || null;
  const urlMP =
    raw.url ||
    raw.urlFicha ||
    `https://www.mercadopublico.cl/CompraAgil/Modules/CA/DetailsAcquisition.aspx?qs=${op.codigo}`;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="text-talinay hover:underline"
        >
          ← Volver
        </button>
        <span className="text-slate-300">·</span>
        <Link to="/" className="text-slate-600 hover:underline">
          Bandeja
        </Link>
        <span className="text-slate-400">›</span>
        <span className="max-w-md truncate text-slate-900">{op.nombre}</span>
      </div>

      <div className="flex items-start gap-4">
        <ScoreBadge score={op.score_relevancia} />
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold text-slate-900">
            {op.nombre || "(sin nombre)"}
          </h1>
          <p className="text-slate-600">{op.organismo || "—"}</p>
          {unidad && (
            <p className="text-sm text-slate-500">Unidad: {unidad}</p>
          )}
          <p className="mt-1 text-xs text-slate-400">Código: {op.codigo}</p>
        </div>
        <a
          href={urlMP}
          target="_blank"
          rel="noopener noreferrer"
          className="whitespace-nowrap text-sm text-talinay hover:underline"
        >
          Ver en mercadopublico.cl ↗
        </a>
      </div>

      {op.justificacion_ia && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
          <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-blue-800">
            Análisis de la IA · Categoría: {op.categoria || "—"}
          </p>
          <p className="text-sm text-blue-900">{op.justificacion_ia}</p>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Tarjeta label="Monto disponible">
          <span className="text-xl font-bold text-slate-900">
            {formatCLP(op.monto_disponible)}
          </span>
        </Tarjeta>
        <Tarjeta label="Cierre">
          <CountdownTimer fechaCierre={op.fecha_cierre} />
        </Tarjeta>
        <Tarjeta label="Región">
          <span className="text-slate-900">{op.region || "—"}</span>
        </Tarjeta>
      </div>

      <Bloque titulo="Descripción">
        <p className="whitespace-pre-wrap text-sm text-slate-700">
          {op.descripcion || "(sin descripción)"}
        </p>
      </Bloque>

      {productos && (
        <Bloque titulo="Productos requeridos">
          {Array.isArray(productos) ? (
            <ul className="list-inside list-disc space-y-1 text-sm text-slate-700">
              {productos.map((p, i) => (
                <li key={i}>
                  {typeof p === "string" ? p : JSON.stringify(p)}
                </li>
              ))}
            </ul>
          ) : (
            <p className="whitespace-pre-wrap text-sm text-slate-700">
              {String(productos)}
            </p>
          )}
        </Bloque>
      )}

      {direccionEntrega && (
        <Bloque titulo="Dirección de entrega">
          <p className="text-sm text-slate-700">{direccionEntrega}</p>
        </Bloque>
      )}

      <CotizacionEditor
        oportunidadId={op.id}
        scoreRelevancia={op.score_relevancia}
      />
    </div>
  );
}

function Tarjeta({ label, children }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <div>{children}</div>
    </div>
  );
}

function Bloque({ titulo, children }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <h2 className="mb-2 text-sm font-semibold text-slate-700">{titulo}</h2>
      {children}
    </div>
  );
}
