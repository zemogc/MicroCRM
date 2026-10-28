// Separador ";" porque Excel en español (coma decimal) lo usa para abrir el CSV en columnas
const SEPARATOR = ";";

const escapeCell = (value) => {
  if (value === null || value === undefined) return "";
  const text = String(value);
  return /[";\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
};

// columns: [{ header: "Nombre", value: (row) => row.name }, ...]
export const toCsv = (columns, rows) => {
  const lines = [columns.map((c) => escapeCell(c.header)).join(SEPARATOR)];
  for (const row of rows) {
    lines.push(columns.map((c) => escapeCell(c.value(row))).join(SEPARATOR));
  }
  return lines.join("\r\n");
};

export const downloadCsv = (filename, columns, rows) => {
  // BOM para que Excel reconozca UTF-8 (tildes y eñes)
  const blob = new Blob(["﻿" + toCsv(columns, rows)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${filename}-${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};
