// El backend guarda fechas en UTC sin zona horaria; se marcan como UTC al leerlas
const parseDate = (value) => new Date(/[zZ]|[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`);

export const formatDate = (value, fallback = "Sin fecha") => {
  if (!value) return fallback;
  return parseDate(value).toLocaleDateString("es-ES", { year: "numeric", month: "short", day: "numeric" });
};

// Días hasta la fecha (negativo si ya pasó)
export const daysUntil = (value) => {
  const startOfDay = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const diff = startOfDay(parseDate(value)) - startOfDay(new Date());
  return Math.round(diff / 86400000);
};

export const relativeDue = (value) => {
  const days = daysUntil(value);
  if (days === 0) return "Vence hoy";
  if (days === 1) return "Vence mañana";
  if (days < 0) return `Venció hace ${-days} ${days === -1 ? "día" : "días"}`;
  return `Vence en ${days} días`;
};

// Mensaje legible a partir de un error de axios
export const apiErrorMessage = (error, fallback = "Ocurrió un error inesperado") => {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join("; ");
  return fallback;
};
