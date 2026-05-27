import { useParams } from "react-router-dom";

export default function Detalle() {
  const { id } = useParams();

  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900">
        Detalle de oportunidad
      </h1>
      <p className="mt-2 text-slate-600">ID: {id}</p>
    </div>
  );
}
