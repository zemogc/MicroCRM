import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";
import {
  X,
  Users,
  ListTodo,
  Calendar,
  Loader,
  AlertCircle,
  Circle,
  Play,
  CheckCircle,
  Clock,
  Eye
} from "lucide-react";
import "./ProyectoDetalle.css";

function ProyectoVer({ proyecto, onClose }) {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("tasks");
  const [members, setMembers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const isOwner = proyecto.crated_by === user?.id;

  useEffect(() => {
    fetchProjectData();
  }, [proyecto.id]);

  const fetchProjectData = async () => {
    try {
      setLoading(true);
      setError("");
      
      const [membersRes, tasksRes, usersRes] = await Promise.all([
        api.get(`/api/project-members/project/${proyecto.id}`),
        api.get(`/api/tasks/project/${proyecto.id}`),
        api.get("/api/users/", { params: { limit: 100 } })
      ]);
      
      const membersData = membersRes.data;
      const allUsersData = usersRes.data.items || [];
      
      // Encontrar el creador del proyecto
      const creator = allUsersData.find(u => u.id === proyecto.crated_by);
      
      // Agregar el creador a la lista de miembros como "Admin" (rol 1)
      const creatorAsMember = {
        id: 0, // ID temporal para el creador
        project_id: proyecto.id,
        user_id: proyecto.crated_by,
        role_id: 1, // Admin
        user_name: creator?.name || proyecto.creator_email || "Desconocido",
        role_name: "Admin (Creador)",
        added_by_name: "Sistema",
        created_at: proyecto.created_at,
        isCreator: true // Flag para identificarlo
      };
      
      // Combinar creador + miembros del proyecto
      const allMembers = [creatorAsMember, ...membersData];
      
      setMembers(allMembers);
      setTasks(tasksRes.data);
    } catch (err) {
      console.error("Error al cargar datos del proyecto:", err);
      setError("Error al cargar los datos");
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
        <Icon size={18} strokeWidth={2.5} />
        {config.label}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Sin fecha";
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", { year: "numeric", month: "short", day: "numeric" });
  };

  const getTasksByStatus = (status) => {
    return tasks.filter(t => t.status === status);
  };

  if (loading) {
    return (
      <div className="proyecto-detalle-overlay">
        <div className="proyecto-detalle-modal loading">
          <Loader size={48} className="spinner" />
          <p>Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="proyecto-detalle-overlay" onClick={onClose}>
      <div className="proyecto-detalle-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="detalle-header">
          <div className="header-info">
            <h2>{proyecto.name}</h2>
            <p>{proyecto.description || "Sin descripción"}</p>
            {isOwner && <span className="badge-owner-detail">Eres el propietario</span>}
          </div>
          <button className="btn-close-modal" onClick={onClose}>
            <X size={36} strokeWidth={3} />
          </button>
        </div>

        {/* Tabs */}
        <div className="detalle-tabs">
          <button
            className={`tab-btn ${activeTab === "tasks" ? "active" : ""}`}
            onClick={() => setActiveTab("tasks")}
          >
            <ListTodo size={24} strokeWidth={2.5} />
            Tareas ({tasks.length})
          </button>
          <button
            className={`tab-btn ${activeTab === "members" ? "active" : ""}`}
            onClick={() => setActiveTab("members")}
          >
            <Users size={24} strokeWidth={2.5} />
            Miembros ({members.length})
          </button>
        </div>

        {/* Content */}
        <div className="detalle-content">
          {error && (
            <div className="alert alert-danger">
              <AlertCircle size={24} strokeWidth={2.5} />
              {error}
            </div>
          )}

          {/* TAREAS TAB - SOLO LECTURA */}
          {activeTab === "tasks" && (
            <div className="tasks-section">
              <div className="section-header">
                <h3>Tareas del Proyecto</h3>
              </div>

              {/* Kanban Board - Solo visualización */}
              <div className="kanban-board">
                {["pending", "in_progress", "overdue", "in_review", "completed"].map((status) => {
                  const statusTasks = getTasksByStatus(status);
                  const statusLabels = {
                    pending: "Por hacer",
                    in_progress: "En desarrollo",
                    overdue: "Atrasado",
                    in_review: "En revisión",
                    completed: "Hecho"
                  };
                  
                  return (
                    <div key={status} className="kanban-column">
                      <div className="column-header">
                        <h4>{statusLabels[status]}</h4>
                        <span className="task-count">{statusTasks.length}</span>
                      </div>
                      <div className="column-tasks">
                        {statusTasks.map((task) => (
                          <div key={task.id} className="task-card task-card-readonly">
                            <div className="task-card-header">
                              <h5>{task.title}</h5>
                            </div>
                            {task.description && (
                              <p className="task-description">{task.description}</p>
                            )}
                            <div className="task-meta">
                              {task.assigned_to_email && (
                                <span className="task-assigned">
                                  <Users size={18} strokeWidth={2.5} />
                                  {task.assigned_to_email}
                                </span>
                              )}
                              {task.due_date && (
                                <span className="task-due-date">
                                  <Calendar size={18} strokeWidth={2.5} />
                                  {formatDate(task.due_date)}
                                </span>
                              )}
                            </div>
                            <div className="task-status-display">
                              {getStatusBadge(task.status)}
                            </div>
                          </div>
                        ))}
                        {statusTasks.length === 0 && (
                          <div className="empty-column">
                            <p>Sin tareas</p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* MIEMBROS TAB - SOLO LECTURA */}
          {activeTab === "members" && (
            <div className="members-section">
              <div className="section-header">
                <h3>Miembros del Proyecto</h3>
              </div>

              <div className="members-list">
                {members.map((member) => (
                  <div key={member.id} className="member-card member-card-readonly">
                    <div className="member-avatar">
                      {member.user_name.charAt(0).toUpperCase()}
                    </div>
                    <div className="member-info">
                      <h4>{member.user_name}</h4>
                      <p className="member-added">
                        Agregado por {member.added_by_name}
                      </p>
                    </div>
                    <div className="member-role">
                      <span className="role-badge">{member.role_name}</span>
                    </div>
                  </div>
                ))}
                {members.length === 0 && (
                  <div className="empty-state-members">
                    <Users size={48} />
                    <p>No hay miembros asignados</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProyectoVer;

