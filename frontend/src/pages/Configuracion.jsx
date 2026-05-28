import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api.js";

export default function Configuracion() {
  const queryClient = useQueryClient();
  const [input, setInput] = useState("");
  const [toast, setToast] = useState(null);

  const { data, isLoading } = useQuery({
    queryKey: ["keywords"],
    queryFn: async () => {
      const { data } = await api.get("/configuracion/keywords");
      return data.keywords;
    },
  });

  const keywords = data || [];

  const saveMutation = useMutation({
    mutationFn: (keywords) => api.put("/configuracion/keywords", { keywords }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["keywords"] });
      showToast("success", "Palabras clave guardadas");
    },
    onError: () => showToast("error", "Error al guardar"),
  });

  const recalcularMutation = useMutation({
    mutationFn: () => api.post("/oportunidades/recalcular-scores"),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["oportunidades"] });
      showToast("success", `${res.data.actualizadas} oportunidades recalculadas`);
    },
    onError: () => showToast("error", "Error al recalcular"),
  });

  const showToast = (type, msg) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 3000);
  };

  const agregar = () => {
    const candidatas = input
      .split(",")
      .map((k) => k.trim().toLowerCase())
      .filter((k) => k.length > 0);

    if (!candidatas.length) return;

    const duplicadas = candidatas.filter((k) => keywords.includes(k));
    const nuevas = candidatas.filter((k) => !keywords.includes(k));

    if (duplicadas.length > 0 && nuevas.length === 0) {
      showToast("error", `Ya existe: ${duplicadas.join(", ")}`);
      return;
    }

    saveMutation.mutate([...keywords, ...nuevas]);
    setInput("");
  };

  const eliminar = (kw) => {
    saveMutation.mutate(keywords.filter((k) => k !== kw));
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") agregar();
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Palabras clave</h1>
        <p className="mt-1 text-sm text-slate-600">
          Las oportunidades se califican según cuántas palabras clave aparecen en su nombre
          y descripción. A mayor coincidencia, mayor score.
        </p>
      </div>

      {/* Input para agregar */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="ej: pintura, tampón, fieltro  (separar con comas)"
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-talinay focus:outline-none focus:ring-1 focus:ring-talinay"
        />
        <button
          type="button"
          onClick={agregar}
          disabled={!input.trim() || saveMutation.isPending}
          className="rounded-md bg-talinay px-4 py-2 text-sm font-medium text-white hover:bg-talinay-dark disabled:opacity-50"
        >
          Agregar
        </button>
      </div>

      {/* Lista de keywords */}
      <div className="rounded-lg border border-slate-200 bg-white p-4">
        {isLoading ? (
          <p className="text-sm text-slate-500">Cargando...</p>
        ) : keywords.length === 0 ? (
          <p className="text-sm text-slate-500">No hay palabras clave configuradas.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {keywords.map((kw) => (
              <span
                key={kw}
                className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-700 border border-blue-200"
              >
                {kw}
                <button
                  type="button"
                  onClick={() => eliminar(kw)}
                  className="ml-1 text-blue-400 hover:text-blue-700 font-bold leading-none"
                  title="Eliminar"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
        <p className="mt-3 text-xs text-slate-400">{keywords.length} palabras clave activas</p>
      </div>

      <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4">
        <div>
          <p className="text-sm font-medium text-slate-800">Recalcular oportunidades existentes</p>
          <p className="text-xs text-slate-500 mt-0.5">Aplica las keywords actuales a todas las oportunidades en la bandeja</p>
        </div>
        <button
          type="button"
          onClick={() => recalcularMutation.mutate()}
          disabled={recalcularMutation.isPending}
          className="rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
        >
          {recalcularMutation.isPending ? "Recalculando..." : "Recalcular ahora"}
        </button>
      </div>

      {toast && (
        <div
          className={`fixed right-4 top-20 z-50 rounded-md px-4 py-3 text-sm font-medium shadow-lg ${
            toast.type === "success" ? "bg-green-600 text-white" : "bg-red-600 text-white"
          }`}
        >
          {toast.msg}
        </div>
      )}
    </div>
  );
}
