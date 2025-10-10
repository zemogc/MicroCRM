import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";
import {
  ListTodo,
  FolderKanban,
  Calendar,
  Clock,
  CheckCircle,
  Circle,
  Play,
  X,
  AlertCircle,
  Loader,
  Eye
} from "lucide-react";
import "./Tareas.css";

function Tareas() {
  const { user } = useAuth();
  const [tareas, setTareas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filterStatus, setFilterStatus] = useState("all"); // all, pending, in_progress, completed

  useEffect(() => {
    fetchUserTasks();
  }, []);

  const fetchUserTasks = async () => {
    try {
      setLoading(true);
      setError("");
      
      // Obtener todas las tareas asignadas al usuario actual
      const response = await api.get(`/api/tasks/user/${user.id}`);
      setTareas(response.data);
      
    } catch (err) {
      console.error("Error al cargar tareas del usuario:", err);
      setError("Error al cargar las tareas");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { label: "Por hacer", color: "#6b7280", icon: Circle },
      in_progress: { label: "En desarrollo", color: "#3b82f6", icon: Play },
      overdue: { label: "Atrasado", color: "#f59e0b", icon: Clock },
      in_review: { label: "En revisión", color: "#8b5cf6", icon: Eye },
      completed: { label: "Hecho", color: "#22c55e", icon: CheckCircle },
      cancelled: { label: "Cancelado", color: "#ef4444", icon: X }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;
    
    return (
      <span className="status-badge" style={{ backgroundColor: `${config.color}20`, color: config.color }}>
        <Icon size={16} strokeWidth={2.5} />
        {config.label}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Sin fecha";
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", { year: "numeric", month: "short", day: "numeric" });
  };

  const filteredTareas = filterStatus === "all" 
    ? tareas 
    : tareas.filter(tarea => tarea.status === filterStatus);

  const getTasksByStatus = (status) => {
    return tareas.filter(t => t.status === status);
  };

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
        <div className="stat-card">
          <div className="stat-icon pending-icon">
            <Circle size={24} />
          </div>
          <div className="stat-info">
            <h3>{getTasksByStatus("pending").length}</h3>
            <p>Por hacer</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon progress-icon">
            <Play size={24} />
          </div>
          <div className="stat-info">
            <h3>{getTasksByStatus("in_progress").length}</h3>
            <p>En desarrollo</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon overdue-icon">
            <Clock size={24} />
          </div>
          <div className="stat-info">
            <h3>{getTasksByStatus("overdue").length}</h3>
            <p>Atrasadas</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon review-icon">
            <Eye size={24} />
          </div>
          <div className="stat-info">
            <h3>{getTasksByStatus("in_review").length}</h3>
            <p>En revisión</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon completed-icon">
            <CheckCircle size={24} />
          </div>
          <div className="stat-info">
            <h3>{getTasksByStatus("completed").length}</h3>
            <p>Completadas</p>
          </div>
        </div>
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
          <button 
            className={`filter-btn ${filterStatus === "pending" ? "active" : ""}`}
            onClick={() => setFilterStatus("pending")}
          >
            Por hacer ({getTasksByStatus("pending").length})
          </button>
          <button 
            className={`filter-btn ${filterStatus === "in_progress" ? "active" : ""}`}
            onClick={() => setFilterStatus("in_progress")}
          >
            En desarrollo ({getTasksByStatus("in_progress").length})
          </button>
          <button 
            className={`filter-btn ${filterStatus === "overdue" ? "active" : ""}`}
            onClick={() => setFilterStatus("overdue")}
          >
            Atrasadas ({getTasksByStatus("overdue").length})
          </button>
          <button 
            className={`filter-btn ${filterStatus === "in_review" ? "active" : ""}`}
            onClick={() => setFilterStatus("in_review")}
          >
            En revisión ({getTasksByStatus("in_review").length})
          </button>
          <button 
            className={`filter-btn ${filterStatus === "completed" ? "active" : ""}`}
            onClick={() => setFilterStatus("completed")}
          >
            Completadas ({getTasksByStatus("completed").length})
          </button>
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
                : `No hay tareas ${filterStatus === "pending" ? "pendientes" : 
                  filterStatus === "in_progress" ? "en desarrollo" : "completadas"}`
              }
            </h3>
            <p>
              {filterStatus === "all" 
                ? "Las tareas que te asignen aparecerán aquí" 
                : "Cambia el filtro para ver otras tareas"
              }
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
                </tr>
              </thead>
              <tbody>
                {filteredTareas.map((tarea) => (
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
                      {getStatusBadge(tarea.status)}
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
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Tareas;
