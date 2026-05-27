import { useEffect, useState } from "react";

function calcular(target) {
  const diff = new Date(target).getTime() - Date.now();
  if (Number.isNaN(diff) || diff <= 0) return null;
  const dias = Math.floor(diff / 86_400_000);
  const horas = Math.floor((diff % 86_400_000) / 3_600_000);
  const minutos = Math.floor((diff % 3_600_000) / 60_000);
  return { dias, horas, minutos };
}

export default function CountdownTimer({ fechaCierre }) {
  const [tiempo, setTiempo] = useState(() => calcular(fechaCierre));

  useEffect(() => {
    if (!fechaCierre) return;
    const tick = () => setTiempo(calcular(fechaCierre));
    tick();
    const id = setInterval(tick, 60_000);
    return () => clearInterval(id);
  }, [fechaCierre]);

  if (!fechaCierre) {
    return <span className="text-slate-500">Sin fecha de cierre</span>;
  }
  if (!tiempo) {
    return <span className="font-semibold text-red-600">Cerrada</span>;
  }

  const partes = [];
  if (tiempo.dias) {
    partes.push(`${tiempo.dias} ${tiempo.dias === 1 ? "día" : "días"}`);
  }
  if (tiempo.horas) {
    partes.push(`${tiempo.horas} ${tiempo.horas === 1 ? "hora" : "horas"}`);
  }
  if (!tiempo.dias && tiempo.minutos) {
    partes.push(`${tiempo.minutos} min`);
  }

  const urgente = tiempo.dias === 0;
  return (
    <span
      className={
        urgente ? "font-semibold text-orange-600" : "font-medium text-slate-800"
      }
    >
      Cierra en {partes.join(", ") || "menos de un minuto"}
    </span>
  );
}
