import { useState, useEffect, useCallback } from "react";
import api from "../../services/api";
import StatusBadge from "../../components/StatusBadge";
import { CLIENT_STATUS } from "../../constants/status";
import { apiErrorMessage, formatDate } from "../../utils/format";
import {
  Users,
  Plus,
  Search,
  Mail,
  Phone,
  Building2,
  Edit2,
  Trash2,
  AlertCircle,
  CheckCircle,
  Loader,
  ChevronLeft,
  ChevronRight,
  Contact
} from "lucide-react";
import "../Proyectos/Proyectos.css";
import "./Clientes.css";

const PAGE_SIZE = 8;

const EMPTY_FORM = {
  name: "",
  company: "",
  email: "",
  phone: "",
  status: "lead",
  notes: ""
};

const STAT_CARDS = [
  { key: "", label: "Total clientes", className: "clientes-total-icon", icon: Contact },
  { key: "lead", label: "Prospectos", className: "clientes-lead-icon", icon: CLIENT_STATUS.lead.icon },
  { key: "active", label: "Activos", className: "clientes-active-icon", icon: CLIENT_STATUS.active.icon },
  { key: "inactive", label: "Inactivos", className: "clientes-inactive-icon", icon: CLIENT_STATUS.inactive.icon },
];

export default function Clientes() {
  const [clientes, setClientes] = useState([]);
  const [total, setTotal] = useState(0);
  const [counts, setCounts] = useState({ lead: 0, active: 0, inactive: 0 });
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Esperar a que el usuario deje de escribir antes de buscar
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search.trim());
      setPage(0);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const fetchClientes = useCallback(async () => {
    try {
      setError("");
      const [listRes, summaryRes] = await Promise.all([
        api.get("/api/clients/", {
          params: {
            skip: page * PAGE_SIZE,
            limit: PAGE_SIZE,
            order_by: "updated_at",
            order_dir: "desc",
            search: debouncedSearch || undefined,
            status: statusFilter || undefined
          }
        }),
        api.get("/api/dashboard/summary")
      ]);
      setClientes(listRes.data.items);
      setTotal(listRes.data.total);
      setCounts(summaryRes.data.clients.by_status);
    } catch (err) {
      setError(apiErrorMessage(err, "Error al cargar los clientes"));
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch, statusFilter]);

  useEffect(() => {
    fetchClientes();
  }, [fetchClientes]);

  const totalClientes = counts.lead + counts.active + counts.inactive;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const handleFilter = (status) => {
    setStatusFilter(status);
    setPage(0);
  };

  const openCreate = () => {
    setEditingId(null);
    setFormData(EMPTY_FORM);
    setFormError("");
    setShowModal(true);
  };

  const openEdit = (cliente) => {
    setEditingId(cliente.id);
    setFormData({
      name: cliente.name,
      company: cliente.company || "",
      email: cliente.email || "",
      phone: cliente.phone || "",
      status: cliente.status,
      notes: cliente.notes || ""
    });
    setFormError("");
    setShowModal(true);
  };

  const closeModal = () => {
    if (!submitting) setShowModal(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setFormError("El nombre del cliente es obligatorio");
      return;
    }

    try {
      setSubmitting(true);
      setFormError("");
      if (editingId) {
        await api.put(`/api/clients/${editingId}`, formData);
      } else {
        await api.post("/api/clients/", formData);
      }
      setShowModal(false);
      await fetchClientes();
    } catch (err) {
      setFormError(apiErrorMessage(err, "No se pudo guardar el cliente"));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (cliente) => {
    if (!window.confirm(`¿Eliminar a "${cliente.name}"? Esta acción no se puede deshacer.`)) return;
    try {
      await api.delete(`/api/clients/${cliente.id}`);
      // Si se borró el último de la página, volver a la anterior
      if (clientes.length === 1 && page > 0) {
        setPage(page - 1);
      } else {
        await fetchClientes();
      }
    } catch (err) {
      setError(apiErrorMessage(err, "No se pudo eliminar el cliente"));
    }
  };

  if (loading) {
    return (
      <div className="proyectos-container">
        <div className="loading-state">
          <Loader size={48} className="spinner" />
          <p>Cargando clientes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="proyectos-container">
      {/* Header */}
      <div className="proyectos-header">
        <div className="header-title">
          <Users size={32} />
          <div>
            <h1>Clientes</h1>
            <p>Tu cartera de clientes y prospectos</p>
          </div>
        </div>
        <button className="btn-primary" onClick={openCreate}>
          <Plus size={20} />
          Nuevo Cliente
        </button>
      </div>

      {error && (
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          <AlertCircle size={20} />
          <span>{error}</span>
          <button type="button" className="btn-close" onClick={() => setError("")} aria-label="Cerrar"></button>
        </div>
      )}

      {/* Stats: también funcionan como filtro rápido */}
      <div className="stats-grid">
        {STAT_CARDS.map(({ key, label, className, icon: Icon }) => (
          <button
            key={label}
            type="button"
            className={`stat-card stat-card-button ${statusFilter === key ? "selected" : ""}`}
            onClick={() => handleFilter(key)}
          >
            <div className={`stat-icon ${className}`}>
              <Icon size={24} />
            </div>
            <div className="stat-info">
              <h3>{key ? counts[key] : totalClientes}</h3>
              <p>{label}</p>
            </div>
          </button>
        ))}
      </div>

      {/* Búsqueda */}
      <div className="clientes-toolbar">
        <div className="search-field">
          <Search size={18} />
          <input
            type="search"
            className="form-control"
            placeholder="Buscar por nombre, empresa o correo"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Buscar clientes"
          />
        </div>
        <select
          className="form-select clientes-status-select"
          value={statusFilter}
          onChange={(e) => handleFilter(e.target.value)}
          aria-label="Filtrar por estado"
        >
          <option value="">Todos los estados</option>
          {Object.entries(CLIENT_STATUS).map(([value, { label }]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      {/* Tabla */}
      <div className="proyectos-table-container">
        {clientes.length === 0 ? (
          <div className="empty-state">
            <Users size={64} />
            {totalClientes === 0 ? (
              <>
                <h3>Aún no tienes clientes</h3>
                <p>Registra tu primer cliente o prospecto para empezar</p>
                <button className="btn-primary" onClick={openCreate}>
                  <Plus size={20} />
                  Registrar Cliente
                </button>
              </>
            ) : (
              <>
                <h3>Sin resultados</h3>
                <p>Ningún cliente coincide con la búsqueda o el filtro</p>
              </>
            )}
          </div>
        ) : (
          <>
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Cliente</th>
                    <th>Contacto</th>
                    <th>Estado</th>
                    <th>Notas</th>
                    <th>Actualizado</th>
                    <th className="text-center">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {clientes.map((cliente) => (
                    <tr key={cliente.id}>
                      <td>
                        <div className="cliente-name">
                          <div className="cliente-avatar">{cliente.name.charAt(0).toUpperCase()}</div>
                          <div>
                            <strong>{cliente.name}</strong>
                            {cliente.company && (
                              <span className="cliente-company">
                                <Building2 size={13} />
                                {cliente.company}
                              </span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="cliente-contact">
                          {cliente.email && (
                            <a href={`mailto:${cliente.email}`}>
                              <Mail size={13} />
                              {cliente.email}
                            </a>
                          )}
                          {cliente.phone && (
                            <span>
                              <Phone size={13} />
                              {cliente.phone}
                            </span>
                          )}
                          {!cliente.email && !cliente.phone && <span className="text-muted">Sin datos</span>}
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={cliente.status} catalog={CLIENT_STATUS} />
                      </td>
                      <td>
                        <span className="cliente-notes" title={cliente.notes || ""}>
                          {cliente.notes || <span className="text-muted">—</span>}
                        </span>
                      </td>
                      <td>
                        <span className="date-text">{formatDate(cliente.updated_at)}</span>
                      </td>
                      <td>
                        <div className="actions-buttons">
                          <button className="btn-action btn-edit" title="Editar" onClick={() => openEdit(cliente)}>
                            <Edit2 size={18} />
                          </button>
                          <button className="btn-action btn-delete" title="Eliminar" onClick={() => handleDelete(cliente)}>
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="clientes-pagination">
              <span>
                Mostrando {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, total)} de {total}
              </span>
              <div>
                <button
                  className="btn-action"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 0}
                  aria-label="Página anterior"
                >
                  <ChevronLeft size={18} />
                </button>
                <span className="clientes-page">{page + 1} / {totalPages}</span>
                <button
                  className="btn-action"
                  onClick={() => setPage(page + 1)}
                  disabled={page + 1 >= totalPages}
                  aria-label="Página siguiente"
                >
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Modal crear / editar */}
      {showModal && (
        <>
          <div className="modal-backdrop fade show" onClick={closeModal}></div>
          <div className="modal fade show d-block" tabIndex="-1">
            <div className="modal-dialog modal-dialog-centered modal-lg">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">
                    <Users size={24} />
                    {editingId ? "Editar Cliente" : "Nuevo Cliente"}
                  </h5>
                  <button type="button" className="btn-close" onClick={closeModal} aria-label="Cerrar"></button>
                </div>
                <form onSubmit={handleSubmit}>
                  <div className="modal-body">
                    {formError && (
                      <div className="alert alert-danger">
                        <AlertCircle size={18} />
                        <span>{formError}</span>
                      </div>
                    )}
                    <div className="row g-3">
                      <div className="col-md-6">
                        <label htmlFor="cliente-name" className="form-label">
                          Nombre <span className="text-danger">*</span>
                        </label>
                        <input id="cliente-name" name="name" className="form-control" value={formData.name}
                          onChange={handleChange} maxLength={100} required placeholder="Ej: Mariana Restrepo" />
                      </div>
                      <div className="col-md-6">
                        <label htmlFor="cliente-company" className="form-label">Empresa</label>
                        <input id="cliente-company" name="company" className="form-control" value={formData.company}
                          onChange={handleChange} maxLength={100} placeholder="Ej: Moda Andina" />
                      </div>
                      <div className="col-md-6">
                        <label htmlFor="cliente-email" className="form-label">Correo</label>
                        <input id="cliente-email" name="email" type="email" className="form-control" value={formData.email}
                          onChange={handleChange} maxLength={150} placeholder="nombre@empresa.com" />
                      </div>
                      <div className="col-md-6">
                        <label htmlFor="cliente-phone" className="form-label">Teléfono</label>
                        <input id="cliente-phone" name="phone" type="tel" className="form-control" value={formData.phone}
                          onChange={handleChange} maxLength={30} placeholder="+57 300 000 0000" />
                      </div>
                      <div className="col-md-6">
                        <label htmlFor="cliente-status" className="form-label">Estado</label>
                        <select id="cliente-status" name="status" className="form-select" value={formData.status} onChange={handleChange}>
                          {Object.entries(CLIENT_STATUS).map(([value, { label }]) => (
                            <option key={value} value={value}>{label}</option>
                          ))}
                        </select>
                      </div>
                      <div className="col-12">
                        <label htmlFor="cliente-notes" className="form-label">Notas</label>
                        <textarea id="cliente-notes" name="notes" className="form-control" rows={3} value={formData.notes}
                          onChange={handleChange} maxLength={500} placeholder="Acuerdos, próximos pasos, intereses..." />
                        <small className="form-text text-muted">{formData.notes.length}/500</small>
                      </div>
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button type="button" className="btn btn-secondary" onClick={closeModal} disabled={submitting}>
                      Cancelar
                    </button>
                    <button type="submit" className="btn btn-primary" disabled={submitting}>
                      {submitting ? <Loader size={18} className="spinner" /> : <CheckCircle size={18} />}
                      {editingId ? "Guardar Cambios" : "Crear Cliente"}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
