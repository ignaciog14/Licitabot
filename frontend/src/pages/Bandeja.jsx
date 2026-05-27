import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import api from "../lib/api.js";
import FilterBar from "../components/FilterBar.jsx";
import OpportunityRow from "../components/OpportunityRow.jsx";
import { tiempoRelativoDesde } from "../lib/format.js";

const POR_PAGINA = 20;
const SCORE_DEFAULT = "50";

export default function Bandeja() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const filters = {
    estado: searchParams.get("estado") || "",
    minScore: searchParams.get("min_score") || SCORE_DEFAULT,
    tipo: searchParams.get("tipo") || "",
    q: searchParams.get("q") || "",
  };

  const [page, setPage] = useState(1);
  const [toast, setToast] = useState(null);
  const [ultimoSync, setUltimoSync] = useState(null);

  const handleFilterChange = (next) => {
    const params = {};
    if (next.estado) params.estado = next.estado;
    if (next.minScore && next.minScore !== SCORE_DEFAULT)
      params.min_score = next.minScore;
    if (next.tipo) params.tipo = next.tipo;
    if (next.q) params.q = next.q;
    setSearchParams(params, { replace: true });
    setPage(1);
  };

  const {
    data: oportunidades = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["oportunidades", filters.minScore],
    queryFn: async () => {
      const { data } = await api.get("/oportunidades", {
        params: { min_score: filters.minScore },
      });
      return data;
    },
  });

  const filtradas = useMemo(() => {
    const q = filters.q.trim().toLowerCase();
    return oportunidades.filter((op) => {
      if (filters.estado && op.estado_interno !== filters.estado) return false;
      if (filters.tipo && op.tipo !== filters.tipo) return false;
      if (q) {
        const nombre = (op.nombre || "").toLowerCase();
        const organismo = (op.organismo || "").toLowerCase();
        if (!nombre.includes(q) && !organismo.includes(q)) return false;
      }
      return true;
    });
  }, [oportunidades, filters.estado, filters.tipo, filters.q]);

  const totalPages = Math.max(1, Math.ceil(filtradas.length / POR_PAGINA));
  const paginadas = filtradas.slice(
    (page - 1) * POR_PAGINA,
    page * POR_PAGINA
  );

  const syncMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post("/sync/compras-agiles");
      return data;
    },
    onSuccess: (result) => {
      setUltimoSync(new Date());
      if (result.nuevas > 0) {
        setToast({
          type: "success",
          msg: `Se encontraron ${result.nuevas} ${
            result.nuevas === 1 ? "nueva oportunidad" : "nuevas oportunidades"
          }`,
        });
      } else {
        setToast({ type: "info", msg: "Sin novedades" });
      }
      queryClient.invalidateQueries({ queryKey: ["oportunidades"] });
    },
    onError: (err) => {
      const detalle = err?.response?.data?.detail || err.message || "desconocido";
      setToast({ type: "error", msg: `Error al sincronizar: ${detalle}` });
    },
  });

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 4000);
    return () => clearTimeout(t);
  }, [toast]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Bandeja de oportunidades
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            {isLoading
              ? "Cargando..."
              : `${filtradas.length} ${
                  filtradas.length === 1 ? "oportunidad" : "oportunidades"
                }`}
          </p>
        </div>
        <div className="text-right">
          <button
            type="button"
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending}
            className="rounded-md bg-talinay px-4 py-2 text-sm font-medium text-white hover:bg-talinay-dark disabled:cursor-not-allowed disabled:opacity-60"
          >
            {syncMutation.isPending ? (
              <span>
                <span className="mr-2 inline-block animate-spin">↻</span>
                Buscando nuevas oportunidades...
              </span>
            ) : (
              "Sincronizar ahora"
            )}
          </button>
          <p className="mt-1 text-xs text-slate-500">
            Última sync:{" "}
            {ultimoSync ? tiempoRelativoDesde(ultimoSync) : "nunca en esta sesión"}
          </p>
        </div>
      </div>

      <FilterBar filters={filters} onChange={handleFilterChange} />

      {error && (
        <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800">
          Error cargando oportunidades:{" "}
          {error?.response?.data?.detail || error.message}
        </div>
      )}

      {isLoading && (
        <div className="rounded-lg border border-slate-200 bg-white p-12 text-center text-slate-500">
          Cargando oportunidades...
        </div>
      )}

      {!isLoading && filtradas.length === 0 && !error && (
        <div className="rounded-lg border border-slate-200 bg-white p-12 text-center">
          <p className="text-slate-500">
            No hay oportunidades que coincidan con los filtros.
          </p>
          <p className="mt-2 text-xs text-slate-400">
            Probá sincronizar o relajar los filtros.
          </p>
        </div>
      )}

      {filtradas.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          {paginadas.map((op) => (
            <OpportunityRow key={op.id} oportunidad={op} />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            type="button"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="rounded border border-slate-300 bg-white px-3 py-1 text-sm disabled:opacity-50"
          >
            ←
          </button>
          <span className="text-sm text-slate-600">
            Página {page} de {totalPages}
          </span>
          <button
            type="button"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded border border-slate-300 bg-white px-3 py-1 text-sm disabled:opacity-50"
          >
            →
          </button>
        </div>
      )}

      {toast && (
        <div
          className={`fixed right-4 top-20 z-50 max-w-md rounded-md px-4 py-3 text-sm font-medium shadow-lg ${
            toast.type === "success"
              ? "bg-green-600 text-white"
              : toast.type === "error"
                ? "bg-red-600 text-white"
                : "bg-slate-800 text-white"
          }`}
          role="status"
        >
          {toast.msg}
        </div>
      )}
    </div>
  );
}
