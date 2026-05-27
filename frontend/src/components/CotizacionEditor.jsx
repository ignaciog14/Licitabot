import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import api from "../lib/api.js";
import { formatCLP } from "../lib/format.js";

const SCORE_UMBRAL = 50;

export default function CotizacionEditor({ oportunidadId, scoreRelevancia }) {
  const queryClient = useQueryClient();

  const cotizacionQuery = useQuery({
    queryKey: ["cotizacion", oportunidadId],
    queryFn: async () => {
      try {
        const { data } = await api.get(
          `/oportunidades/${oportunidadId}/cotizacion`
        );
        return data;
      } catch (err) {
        if (err?.response?.status === 404) return null;
        throw err;
      }
    },
  });

  const cotizacion = cotizacionQuery.data;

  const [borrador, setBorrador] = useState("");
  const [precio, setPrecio] = useState("");
  const [plazo, setPlazo] = useState("");
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (!cotizacion) return;
    setBorrador(cotizacion.borrador_editado ?? cotizacion.borrador_ia ?? "");
    setPrecio(cotizacion.precio_ofertado ?? "");
    setPlazo(cotizacion.plazo_entrega_dias ?? "");
    setDirty(false);
  }, [cotizacion?.id, cotizacion?.estado, cotizacion?.borrador_ia]);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["cotizacion", oportunidadId] });
    queryClient.invalidateQueries({ queryKey: ["oportunidad", oportunidadId] });
    queryClient.invalidateQueries({ queryKey: ["oportunidades"] });
  };

  const generarMutation = useMutation({
    mutationFn: async ({ force = false } = {}) => {
      const { data } = await api.post(
        `/oportunidades/${oportunidadId}/generar-cotizacion`,
        null,
        { params: force ? { force: true } : {} }
      );
      return data;
    },
    onSuccess: invalidate,
  });

  const guardarMutation = useMutation({
    mutationFn: async (payload) => {
      const { data } = await api.patch(
        `/cotizaciones/${cotizacion.id}`,
        payload
      );
      return data;
    },
    onSuccess: invalidate,
  });

  if (cotizacionQuery.isLoading) {
    return (
      <Card>
        <p className="text-sm text-slate-500">Cargando cotización...</p>
      </Card>
    );
  }

  if (!cotizacion) {
    return (
      <Card>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">
          Cotización
        </h2>
        {(scoreRelevancia ?? 0) < SCORE_UMBRAL ? (
          <p className="text-sm text-slate-500">
            Score {scoreRelevancia ?? 0} bajo el umbral ({SCORE_UMBRAL}). Esta
            oportunidad no parece relevante para Talinay.
          </p>
        ) : generarMutation.isPending ? (
          <div className="flex items-center gap-3 text-talinay">
            <span className="inline-block animate-spin text-xl">↻</span>
            <span className="text-sm">
              La IA está preparando tu cotización...
            </span>
          </div>
        ) : (
          <>
            <p className="mb-4 text-sm text-slate-600">
              No hay cotización todavía. Generemos un borrador con Claude.
            </p>
            <button
              type="button"
              onClick={() => generarMutation.mutate({})}
              className="rounded-md bg-talinay px-4 py-2 text-sm font-medium text-white hover:bg-talinay-dark"
            >
              Generar cotización con IA
            </button>
          </>
        )}
        <ErrorMessage error={generarMutation.error} />
      </Card>
    );
  }

  const aprobada = cotizacion.estado === "aprobada";

  return (
    <Card>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-900">Cotización</h2>
        <EstadoFlujo estado={cotizacion.estado} tienePdf={!!cotizacion.pdf_url} />
      </div>

      {aprobada ? (
        <div className="space-y-4">
          <div className="rounded-md border border-green-200 bg-green-50 p-3 text-sm font-medium text-green-800">
            ✓ Cotización aprobada · no se puede modificar
          </div>
          <pre className="whitespace-pre-wrap rounded-md border border-slate-200 bg-slate-50 p-4 text-sm text-slate-800">
            {cotizacion.borrador_editado || cotizacion.borrador_ia}
          </pre>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-slate-500">Precio ofertado:</span>{" "}
              <strong className="text-slate-900">
                {formatCLP(cotizacion.precio_ofertado)}
              </strong>
            </div>
            <div>
              <span className="text-slate-500">Plazo:</span>{" "}
              <strong className="text-slate-900">
                {cotizacion.plazo_entrega_dias ?? "—"} días hábiles
              </strong>
            </div>
          </div>
          {cotizacion.pdf_url ? (
            <a
              href={cotizacion.pdf_url}
              download
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex rounded-md bg-talinay px-4 py-2 text-sm font-medium text-white hover:bg-talinay-dark"
            >
              Descargar PDF
            </a>
          ) : (
            <div className="inline-flex items-center gap-2 text-sm text-slate-500">
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-slate-400" />
              Generando PDF...
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <textarea
            value={borrador}
            onChange={(e) => {
              setBorrador(e.target.value);
              setDirty(true);
            }}
            className="min-h-[300px] w-full resize-y rounded-md border border-slate-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-talinay"
          />
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Precio ofertado (CLP)
              </label>
              <input
                type="number"
                min="0"
                value={precio}
                onChange={(e) => {
                  setPrecio(e.target.value);
                  setDirty(true);
                }}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-talinay"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Plazo de entrega (días hábiles)
              </label>
              <input
                type="number"
                min="0"
                value={plazo}
                onChange={(e) => {
                  setPlazo(e.target.value);
                  setDirty(true);
                }}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-talinay"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2 border-t border-slate-100 pt-3">
            <button
              type="button"
              onClick={() =>
                guardarMutation.mutate({
                  borrador_editado: borrador,
                  precio_ofertado: precio === "" ? null : Number(precio),
                  plazo_entrega_dias: plazo === "" ? null : Number(plazo),
                })
              }
              disabled={!dirty || guardarMutation.isPending}
              className="rounded-md bg-talinay px-4 py-2 text-sm font-medium text-white hover:bg-talinay-dark disabled:cursor-not-allowed disabled:opacity-50"
            >
              {guardarMutation.isPending ? "Guardando..." : "Guardar cambios"}
            </button>
            <button
              type="button"
              onClick={() => {
                if (
                  !window.confirm(
                    "¿Aprobar esta cotización? Una vez aprobada no podrás editarla."
                  )
                )
                  return;
                guardarMutation.mutate({
                  borrador_editado: borrador,
                  precio_ofertado: precio === "" ? null : Number(precio),
                  plazo_entrega_dias: plazo === "" ? null : Number(plazo),
                  estado: "aprobada",
                });
              }}
              disabled={guardarMutation.isPending}
              className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
            >
              Aprobar cotización
            </button>
            <button
              type="button"
              onClick={() => {
                if (
                  !window.confirm(
                    "¿Regenerar el borrador con IA? Perderás tus ediciones actuales."
                  )
                )
                  return;
                generarMutation.mutate({ force: true });
              }}
              disabled={generarMutation.isPending}
              className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              {generarMutation.isPending ? "Regenerando..." : "Regenerar"}
            </button>
            <button
              type="button"
              onClick={() => {
                if (
                  !window.confirm(
                    "¿Descartar esta oportunidad? Se sacará de la bandeja."
                  )
                )
                  return;
                guardarMutation.mutate({ estado_oportunidad: "descartado" });
              }}
              disabled={guardarMutation.isPending}
              className="rounded-md border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
            >
              Descartar oportunidad
            </button>
          </div>

          <ErrorMessage error={guardarMutation.error || generarMutation.error} />
        </div>
      )}
    </Card>
  );
}

function Card({ children }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      {children}
    </div>
  );
}

function EstadoFlujo({ estado, tienePdf }) {
  const pasos = [
    { key: "borrador", label: "Borrador", activo: true },
    { key: "aprobada", label: "Aprobada", activo: estado === "aprobada" },
    { key: "pdf", label: "PDF listo", activo: tienePdf },
  ];
  return (
    <div className="flex items-center gap-2 text-xs">
      {pasos.map((p, i) => (
        <span key={p.key} className="flex items-center gap-2">
          <span
            className={`rounded px-2 py-1 ${
              p.activo
                ? "bg-talinay text-white"
                : "bg-slate-100 text-slate-500"
            }`}
          >
            {p.label}
          </span>
          {i < pasos.length - 1 && <span className="text-slate-400">→</span>}
        </span>
      ))}
    </div>
  );
}

function ErrorMessage({ error }) {
  if (!error) return null;
  const detalle =
    error?.response?.data?.detail || error?.message || "desconocido";
  return (
    <p className="mt-2 text-sm text-red-600">
      Error: {detalle}
    </p>
  );
}
