export default function ScoreBadge({ score }) {
  const valor = score ?? 0;
  const color =
    valor >= 80
      ? "bg-green-100 text-green-800 border-green-300"
      : "bg-yellow-100 text-yellow-800 border-yellow-300";

  return (
    <span
      className={`inline-flex w-12 h-12 items-center justify-center rounded-full border font-bold text-lg ${color}`}
      title={`Score de relevancia: ${valor}/100`}
    >
      {valor}
    </span>
  );
}
