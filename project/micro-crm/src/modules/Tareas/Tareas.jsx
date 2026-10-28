import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";
import StatusBadge from "../../components/StatusBadge";
import { TASK_STATUS } from "../../constants/status";
import { apiErrorMessage, formatDate } from "../../utils/format";
import {
  ListTodo,
  FolderKanban,
  Calendar,
  Clock,
  CheckCircle,
  Circle,
  Play,
  AlertCircle,
  Loader,
  Eye,
  Send
} from "lucide-react";
import "./Tareas.css";

const STAT_CARDS = [
  { status: "pending", label: "Por hacer", icon: Circle, className: "pending-icon" },
  { status: "in_progress", label: "En desarrollo", icon: Play, className: "progress-icon" },
  { status: "overdue", label: "Atrasadas", icon: Clock, className: "overdue-icon" },
  { status: "in_review", label: "En revisión", icon: Eye, className: "review-icon" },
  { status: "completed", label: "Completadas", icon: CheckCircle, className: "completed-icon" },
];

// Siguiente paso que puede dar quien tiene la tarea asignada
const NEXT_STEP = {
  pending: { status: "in_progress", label: "Iniciar", icon: Play, className: "btn-start" },
  in_progress: { status: "in_review", label: "A revisión", icon: Send, className: "btn-review" },
  overdue: { status: "in_review", label: "A revisión", icon: Send, className: "btn-review" },
};

function Tareas() {
  const { user } = useAuth();
  const [tareas, setTareas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [updatingId, setUpdatingId] = useState(null);

  const fetchUserTasks = useCallback(async () => {
    try {
      setError("");
      // Obtener todas las tareas asignadas al usuario actual
      const response = await api.get(`/api/tasks/user/${user.id}`);
      setTareas(response.data);
    } catch (err) {
      setError(apiErrorMessage(err, "Error al cargar las tareas"));
    } finally {
      setLoading(false);
    }
  }, [user.id]);

  useEffect(() => {
    fetchUserTasks();
  }, [fetchUserTasks]);

  const handleAdvance = async (tarea) => {
    const next = NEXT_STEP[tarea.status];
    try {
      setUpdatingId(tarea.id);
      const response = await api.put(`/api/tasks/${tarea.id}`, { status: next.status });
      setTareas((prev) => prev.map((t) => (t.id === tarea.id ? response.data : t)));
    } catch (err) {
      setError(apiErrorMessage(err, "No se pudo actualizar la tarea"));
    } finally {
      setUpdatingId(null);
    }
  };

  const getTasksByStatus = (status) => tareas.filter((t) => t.status === status);

  const filteredTareas = filterStatus === "all" ? tareas : getTasksByStatus(filterStatus);

  if (loading) {
    return (
      <div className="tareas-container">
        <div className="tareas-loading">
          <Loader size={48} className="spinner" />
          <p>Cargando tus tareas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="tareas-container">
      {/* Header */}
      <div className="tareas-header">
        <div className="header-title">
          <ListTodo size={32} />
          <h1>Mis Tareas</h1>
        </div>
        <p className="header-subtitle">
          Gestiona todas tus tareas asignadas de todos los proyectos
        </p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon total-icon">
            <ListTodo size={24} />
          </div>
          <div className="stat-info">
            <h3>{tareas.length}</h3>
            <p>Total</p>
          </div>
        </div>
        {STAT_CARDS.map(({ status, label, icon: Icon, className }) => (
          <div className="stat-card" key={status}>
            <div className={`stat-icon ${className}`}>
              <Icon size={24} />
            </div>
            <div className="stat-info">
              <h3>{getTasksByStatus(status).length}</h3>
              <p>{label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Filtros */}
      <div className="filters-section">
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterStatus === "all" ? "active" : ""}`}
            onClick={() => setFilterStatus("all")}
          >
            Todas ({tareas.length})
          </button>
          {STAT_CARDS.map(({ status, label }) => (
            <button
              key={status}
              className={`filter-btn ${filterStatus === status ? "active" : ""}`}
              onClick={() => setFilterStatus(status)}
            >
              {label} ({getTasksByStatus(status).length})
            </button>
          ))}
        </div>
      </div>

      {/* Lista de Tareas */}
      <div className="tareas-content">
        {error && (
          <div className="alert alert-danger">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {filteredTareas.length === 0 ? (
          <div className="empty-state">
            <ListTodo size={64} />
            <h3>
              {filterStatus === "all"
                ? "No tienes tareas asignadas"
                : `No hay tareas en "${TASK_STATUS[filterStatus].label}"`}
            </h3>
            <p>
              {filterStatus === "all"
                ? "Las tareas que te asignen aparecerán aquí"
                : "Cambia el filtro para ver otras tareas"}
            </p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>Tarea</th>
                  <th>Proyecto</th>
                  <th>Estado</th>
                  <th>Fecha de Vencimiento</th>
                  <th>Creada</th>
                  <th className="text-center">Acción</th>
                </tr>
              </thead>
              <tbody>
                {filteredTareas.map((tarea) => {
                  const next = NEXT_STEP[tarea.status];
                  const NextIcon = next?.icon;
                  return (
                    <tr key={tarea.id}>
                      <td>
                        <div className="tarea-name">
                          <ListTodo size={18} />
                          <div className="tarea-info">
                            <strong>{tarea.title}</strong>
                            {tarea.description && (
                              <span className="tarea-description">
                                {tarea.description}
                              </span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="project-info">
                          <FolderKanban size={16} strokeWidth={2} />
                          <span className="project-name">{tarea.project_name}</span>
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={tarea.status} size={16} />
                      </td>
                      <td>
                        {tarea.due_date ? (
                          <span className="date-text">
                            <Calendar size={14} />
                            {formatDate(tarea.due_date)}
                          </span>
                        ) : (
                          <span className="text-muted">Sin fecha</span>
                        )}
                      </td>
                      <td>
                        <span className="date-text">
                          <Clock size={14} />
                          {formatDate(tarea.created_at)}
                        </span>
                      </td>
                      <td className="text-center">
                        {next ? (
                          <button
                            className={`btn-task-step ${next.className}`}
                            onClick={() => handleAdvance(tarea)}
                            disabled={updatingId === tarea.id}
                          >
                            {updatingId === tarea.id ? <Loader size={14} className="spinner" /> : <NextIcon size={14} />}
                            {next.label}
                          </button>
                        ) : (
                          <span className="text-muted">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Tareas;
