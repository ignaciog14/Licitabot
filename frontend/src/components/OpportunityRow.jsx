import { Link } from "react-router-dom";

import ScoreBadge from "./ScoreBadge.jsx";
import StatusBadge from "./StatusBadge.jsx";
import { formatCLP, tiempoRelativoCierre } from "../lib/format.js";

export default function OpportunityRow({ oportunidad }) {
  return (
    <Link
      to={`/oportunidad/${oportunidad.id}`}
      className="block border-b border-slate-200 bg-white last:border-b-0 hover:bg-slate-50 transition-colors"
    >
      <div className="flex items-center gap-4 px-4 py-3">
        <ScoreBadge score={oportunidad.score_relevancia} />

        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-medium text-slate-900">
            {oportunidad.nombre || "(sin nombre)"}
          </h3>
          <p className="truncate text-xs text-slate-500">
            {oportunidad.organismo || "(sin organismo)"}
          </p>
        </div>

        <div className="hidden sm:block min-w-[120px] text-right text-sm text-slate-700">
          {formatCLP(oportunidad.monto_disponible)}
        </div>

        <div className="hidden md:block min-w-[120px] text-right text-sm text-slate-600">
          {tiempoRelativoCierre(oportunidad.fecha_cierre)}
        </div>

        <StatusBadge estado={oportunidad.estado_interno} />
      </div>
    </Link>
  );
}
