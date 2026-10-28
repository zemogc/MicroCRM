import api from "./api";

// Recorre todas las páginas de /api/clients (la API devuelve máximo 100 por página)
export const fetchAllClients = async (params = {}) => {
  const rows = [];
  for (let skip = 0; ; skip += 100) {
    const res = await api.get("/api/clients/", {
      params: { order_by: "name", order_dir: "asc", ...params, skip, limit: 100 }
    });
    rows.push(...res.data.items);
    if (!res.data.has_more) return rows;
  }
};
