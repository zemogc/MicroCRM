import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";
import {
  X,
  Users,
  ListTodo,
  Plus,
  Edit2,
  Trash2,
  UserPlus,
  Clock,
  Calendar,
  CheckCircle,
  Circle,
  Loader,
  AlertCircle,
  Play,
  Eye,
  Send,
  Check
} from "lucide-react";
import "./ProyectoDetalle.css";

function ProyectoDetalle({ proyecto, onClose, onUpdate }) {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("tasks"); // 'tasks' o 'members'
  const [members, setMembers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [allUsers, setAllUsers] = useState([]); // Todos los usuarios para agregar miembros
  const [projectUsers, setProjectUsers] = useState([]); // Solo usuarios del proyecto para asignar tareas
  const [projectRoles, setProjectRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Modales
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [showAddTaskModal, setShowAddTaskModal] = useState(false);
  const [showEditTaskModal, setShowEditTaskModal] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  
  // Formularios
  const [memberForm, setMemberForm] = useState({
    user_id: "",
    project_role_id: "",
    project_id: proyecto.id
  });
  
  const [taskForm, setTaskForm] = useState({
    project_id: proyecto.id,
    title: "",
    description: "",
    status: "pending",
    assigned_to: null,
    due_date: null
  });

  const isOwner = proyecto.id_user === user?.id;

  // Datos editables del proyecto (solo el propietario)
  const [info, setInfo] = useState({ name: proyecto.name, description: proyecto.description || "" });
  const [infoDraft, setInfoDraft] = useState(info);
  const [editingInfo, setEditingInfo] = useState(false);
  const [savingInfo, setSavingInfo] = useState(false);

  const fetchProjectData = useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      
      // Cargar miembros, tareas, usuarios y roles del proyecto en paralelo
      const [membersRes, tasksRes, usersRes, projectRolesRes] = await Promise.all([
        api.get(`/api/project-members/project/${proyecto.id}`),
        api.get(`/api/tasks/project/${proyecto.id}`),
        api.get("/api/users/", { params: { limit: 100 } }),
        api.get(`/api/project-roles/project/${proyecto.id}`)
      ]);
      
      const membersData = membersRes.data || [];
      const allUsersData = usersRes.data.items || [];
      
      // Agregar el creador del proyecto como miembro con rol especial
      const creator = allUsersData.find(u => u.id === proyecto.id_user);
      const creatorAsMember = {
        id: 0, // ID temporal para el creador
        project_id: proyecto.id,
        user_id: proyecto.id_user,
        project_role_id: 0, // Rol especial para creador
        user_name: creator?.name || proyecto.creator_name || "Desconocido",
        user_email: creator?.email || proyecto.creator_email || "",
        role_name: "Creador",
        role_description: "Creador del proyecto",
        created_at: proyecto.created_at,
        isCreator: true // Flag para identificarlo
      };
      
      // Combinar creador con otros miembros
      setMembers([creatorAsMember, ...membersData]);
      setTasks(tasksRes.data);
      setAllUsers(allUsersData);
      // Usar roles del proyecto desde la API
      const projectRolesData = projectRolesRes.data || [];
      setProjectRoles(projectRolesData);
      
      // Crear lista de usuarios del proyecto (para asignar tareas)
      // Incluye al creador y todos los miembros del proyecto
      const allProjectMembers = [creatorAsMember, ...membersData];
      const projectUserIds = allProjectMembers.map(member => member.user_id);
      const projectUsersFiltered = allUsersData.filter(u => projectUserIds.includes(u.id));
      setProjectUsers(projectUsersFiltered);
      
    } catch (err) {
      console.error("Error al cargar datos del proyecto:", err);
      setError("Error al cargar los datos");
    } finally {
      setLoading(false);
    }
  }, [proyecto]);

  useEffect(() => {
    fetchProjectData();
  }, [fetchProjectData]);

  // ============ DATOS DEL PROYECTO ============

  const handleSaveInfo = async (e) => {
    e.preventDefault();
    try {
      setSavingInfo(true);
      const response = await api.put(`/api/projects/${proyecto.id}`, infoDraft);
      setInfo({ name: response.data.name, description: response.data.description || "" });
      setEditingInfo(false);
      onUpdate?.(response.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Error al actualizar el proyecto");
    } finally {
      setSavingInfo(false);
    }
  };

  // ============ GESTIÓN DE MIEMBROS ============
  
  const handleAddMember = async (e) => {
    e.preventDefault();
    try {
      await api.post("/api/project-members/", memberForm);
      await fetchProjectData();
      setShowAddMemberModal(false);
      setMemberForm({
        user_id: "",
        project_role_id: "",
        project_id: proyecto.id
      });
    } catch (err) {
      console.error("Error al agregar miembro:", err);
      alert(err.response?.data?.detail || "Error al agregar miembro");
    }
  };

  const handleDeleteMember = async (memberId) => {
    if (!window.confirm("¿Eliminar este miembro del proyecto?")) return;
    
    try {
      await api.delete(`/api/project-members/${memberId}`);
      await fetchProjectData();
    } catch (err) {
      console.error("Error al eliminar miembro:", err);
      alert("Error al eliminar miembro");
    }
  };

  const handleUpdateMemberRole = async (memberId, newRoleId) => {
    try {
      await api.put(`/api/project-members/${memberId}`, { project_role_id: newRoleId });
      await fetchProjectData();
    } catch (err) {
      console.error("Error al actualizar rol:", err);
      alert("Error al actualizar rol");
    }
  };

  // ============ GESTIÓN DE TAREAS ============
  
  const handleAddTask = async (e) => {
    e.preventDefault();
    try {
      await api.post("/api/tasks/", taskForm);
      await fetchProjectData();
      setShowAddTaskModal(false);
      setTaskForm({
        project_id: proyecto.id,
        title: "",
        description: "",
        status: "pending",
        assigned_to: null,
        due_date: null
      });
    } catch (err) {
      console.error("Error al crear tarea:", err);
      alert(err.response?.data?.detail || "Error al crear tarea");
    }
  };

  const handleEditTask = (task) => {
    setSelectedTask(task);
    setTaskForm({
      project_id: proyecto.id,
      title: task.title,
      description: task.description || "",
      status: task.status,
      assigned_to: task.assigned_to,
      due_date: task.due_date ? task.due_date.split('T')[0] : null
    });
    setShowEditTaskModal(true);
  };

  const handleUpdateTask = async (e) => {
    e.preventDefault();
    try {
      // Si es colaborador, solo enviar el status
      const updateData = isOwner 
        ? taskForm 
        : { status: taskForm.status };
        
      await api.put(`/api/tasks/${selectedTask.id}`, updateData);
      await fetchProjectData();
      setShowEditTaskModal(false);
      setSelectedTask(null);
    } catch (err) {
      console.error("Error al actualizar tarea:", err);
      alert("Error al actualizar tarea");
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("¿Eliminar esta tarea?")) return;
    
    try {
      await api.delete(`/api/tasks/${taskId}`);
      await fetchProjectData();
    } catch (err) {
      console.error("Error al eliminar tarea:", err);
      alert("Error al eliminar tarea");
    }
  };

  // Actualización optimista: la tarjeta cambia de columna al instante y se revierte si la API lo rechaza
  const handleChangeTaskStatus = async (taskId, newStatus) => {
    const previous = tasks;
    setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t)));
    try {
      const response = await api.put(`/api/tasks/${taskId}`, { status: newStatus });
      setTasks((prev) => prev.map((t) => (t.id === taskId ? response.data : t)));
    } catch (err) {
      setTasks(previous);
      alert(err.response?.data?.detail || "Error al cambiar estado");
    }
  };

  // ============ ARRASTRAR Y SOLTAR ============

  const [draggedTask, setDraggedTask] = useState(null);
  const [dropTarget, setDropTarget] = useState(null);

  // Mismas reglas que la API: el propietario mueve cualquier tarea; el colaborador solo las suyas
  // y sin completarlas (eso lo aprueba el propietario). "Atrasado" lo asigna el sistema.
  const COLLABORATOR_TARGETS = ["pending", "in_progress", "in_review"];
  const canDrag = (task) => isOwner || task.assigned_to === user?.id;
  const canDropTo = (task, status) =>
    !!task &&
    task.status !== status &&
    status !== "overdue" &&
    (isOwner || COLLABORATOR_TARGETS.includes(status));

  const handleDragStart = (e, task) => {
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", String(task.id));
    setDraggedTask(task);
  };

  const handleDragEnd = () => {
    setDraggedTask(null);
    setDropTarget(null);
  };

  const handleDragOver = (e, status) => {
    if (!canDropTo(draggedTask, status)) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    if (dropTarget !== status) setDropTarget(status);
  };

  const handleDrop = (e, status) => {
    e.preventDefault();
    const task = draggedTask;
    handleDragEnd();
    if (canDropTo(task, status)) handleChangeTaskStatus(task.id, status);
  };

  // ============ HELPERS ============
  
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
          {editingInfo ? (
            <form className="header-info header-edit-form" onSubmit={handleSaveInfo}>
              <input
                className="form-control"
                value={infoDraft.name}
                onChange={(e) => setInfoDraft({ ...infoDraft, name: e.target.value })}
                maxLength={100}
                required
                aria-label="Nombre del proyecto"
              />
              <input
                className="form-control"
                value={infoDraft.description}
                onChange={(e) => setInfoDraft({ ...infoDraft, description: e.target.value })}
                maxLength={150}
                placeholder="Descripción"
                aria-label="Descripción del proyecto"
              />
              <div className="header-edit-actions">
                <button type="submit" className="btn-add" disabled={savingInfo}>
                  <Check size={16} /> Guardar
                </button>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setEditingInfo(false)}>
                  Cancelar
                </button>
              </div>
            </form>
          ) : (
            <div className="header-info">
              <h2>
                Editar: {info.name}
                {isOwner && (
                  <button
                    className="btn-action btn-edit btn-edit-info"
                    onClick={() => { setInfoDraft(info); setEditingInfo(true); }}
                    title="Editar nombre y descripción"
                  >
                    <Edit2 size={16} />
                  </button>
                )}
              </h2>
              <p>{info.description || "Sin descripción"}</p>
              <span className="badge-owner-detail">Modo Edición</span>
            </div>
          )}
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
            <ListTodo size={20} strokeWidth={2} />
            Tareas ({tasks.length})
          </button>
          <button
            className={`tab-btn ${activeTab === "members" ? "active" : ""}`}
            onClick={() => setActiveTab("members")}
          >
            <Users size={20} strokeWidth={2} />
            Miembros ({members.length})
          </button>
        </div>

        {/* Content */}
        <div className="detalle-content">
          {error && (
            <div className="alert alert-danger">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {/* TAREAS TAB */}
          {activeTab === "tasks" && (
            <div className="tasks-section">
              <div className="section-header">
                <div>
                  <h3>Tareas del Proyecto</h3>
                  <p className="kanban-hint">Arrastra las tarjetas entre columnas para cambiar su estado</p>
                </div>
                {isOwner && (
                  <button className="btn-add" onClick={() => setShowAddTaskModal(true)}>
                    <Plus size={18} strokeWidth={2} />
                    Nueva Tarea
                  </button>
                )}
              </div>

              {/* Kanban Board */}
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
                    <div
                      key={status}
                      className={[
                        "kanban-column",
                        draggedTask && canDropTo(draggedTask, status) ? "can-drop" : "",
                        dropTarget === status ? "is-drop-target" : ""
                      ].join(" ")}
                      onDragOver={(e) => handleDragOver(e, status)}
                      onDragLeave={(e) => {
                        if (!e.currentTarget.contains(e.relatedTarget)) setDropTarget(null);
                      }}
                      onDrop={(e) => handleDrop(e, status)}
                    >
                      <div className="column-header">
                        <h4>{statusLabels[status]}</h4>
                        <span className="task-count">{statusTasks.length}</span>
                      </div>
                      <div className="column-tasks">
                        {statusTasks.map((task) => (
                          <div
                            key={task.id}
                            className={`task-card ${canDrag(task) ? "is-draggable" : ""} ${draggedTask?.id === task.id ? "is-dragging" : ""}`}
                            draggable={canDrag(task)}
                            onDragStart={(e) => handleDragStart(e, task)}
                            onDragEnd={handleDragEnd}
                          >
                            <div className="task-card-header">
                              <h5>{task.title}</h5>
                              <div className="task-actions">
                                {isOwner ? (
                                  <>
                                    <button className="btn-action btn-edit" onClick={() => handleEditTask(task)} title="Editar">
                                      <Edit2 size={18} />
                                    </button>
                                    <button className="btn-action btn-delete" onClick={() => handleDeleteTask(task.id)} title="Eliminar">
                                      <Trash2 size={18} />
                                    </button>
                                  </>
                                ) : (
                                  // Colaborador: solo puede ver/gestionar SUS tareas
                                  task.assigned_to === user?.id && (
                                    <button className="btn-action btn-view" onClick={() => handleEditTask(task)} title="Gestionar mi tarea">
                                      <Eye size={18} />
                                    </button>
                                  )
                                )}
                              </div>
                            </div>
                            {task.description && (
                              <p className="task-description">{task.description}</p>
                            )}
                            <div className="task-meta">
                              {task.assigned_to_email && (
                                <span className="task-assigned">
                                  <Users size={14} />
                                  {task.assigned_to_email}
                                </span>
                              )}
                              {task.due_date && (
                                <span className="task-due-date">
                                  <Calendar size={14} />
                                  {formatDate(task.due_date)}
                                </span>
                              )}
                            </div>
                            {/* Botones de acción según rol */}
                            {status !== "completed" && status !== "cancelled" && (
                              <>
                                {/* Admin/Owner: control total */}
                                {isOwner && (
                                  <div className="task-status-actions">
                                    {status === "pending" && (
                                      <button
                                        className="btn-task-action btn-start"
                                        onClick={() => handleChangeTaskStatus(task.id, "in_progress")}
                                        title="Iniciar tarea"
                                      >
                                        <Play size={14} />
                                        <span>Iniciar</span>
                                      </button>
                                    )}
                                    {status === "in_progress" && (
                                      <>
                                        <button
                                          className="btn-task-action btn-review"
                                          onClick={() => handleChangeTaskStatus(task.id, "in_review")}
                                          title="Enviar a revisión"
                                        >
                                          <Send size={14} />
                                          <span>Revisar</span>
                                        </button>
                                        <button
                                          className="btn-task-action btn-complete"
                                          onClick={() => handleChangeTaskStatus(task.id, "completed")}
                                          title="Completar tarea"
                                        >
                                          <Check size={14} />
                                          <span>Completar</span>
                                        </button>
                                      </>
                                    )}
                                    {(status === "in_review" || status === "overdue") && (
                                      <button
                                        className="btn-task-action btn-approve"
                                        onClick={() => handleChangeTaskStatus(task.id, "completed")}
                                        title="Aprobar tarea"
                                      >
                                        <CheckCircle size={14} />
                                        <span>Aprobar</span>
                                      </button>
                                    )}
                                  </div>
                                )}
                                
                                {/* Colaborador: solo sus tareas asignadas */}
                                {!isOwner && task.assigned_to === user?.id && (
                                  <div className="task-status-actions">
                                    {status === "pending" && (
                                      <button
                                        className="btn-task-action btn-start"
                                        onClick={() => handleChangeTaskStatus(task.id, "in_progress")}
                                        title="Iniciar mi tarea"
                                      >
                                        <Play size={14} />
                                        <span>Iniciar</span>
                                      </button>
                                    )}
                                    {(status === "in_progress" || status === "overdue") && (
                                      <button
                                        className="btn-task-action btn-review"
                                        onClick={() => handleChangeTaskStatus(task.id, "in_review")}
                                        title="Enviar a revisión"
                                      >
                                        <Send size={14} />
                                        <span>Revisar</span>
                                      </button>
                                    )}
                                  </div>
                                )}
                              </>
                            )}
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

          {/* MIEMBROS TAB */}
          {activeTab === "members" && (
            <div className="members-section">
              <div className="section-header">
                <h3>Miembros del Proyecto</h3>
                {isOwner && (
                  <button className="btn-add" onClick={() => setShowAddMemberModal(true)}>
                    <UserPlus size={18} strokeWidth={2} />
                    Agregar Miembro
                  </button>
                )}
              </div>

              <div className="members-list">
                {members.map((member) => (
                  <div key={member.id} className="member-card">
                    <div className="member-avatar">
                      {member.user_name.charAt(0).toUpperCase()}
                    </div>
                    <div className="member-info">
                      <h4>{member.user_name}</h4>
                      <p className="member-added">
                        {member.user_email} · desde {formatDate(member.created_at)}
                      </p>
                    </div>
                    <div className="member-role">
                      {isOwner && !member.isCreator ? (
                        <select
                          value={member.project_role_id}
                          onChange={(e) => handleUpdateMemberRole(member.id, parseInt(e.target.value))}
                          className="role-select"
                        >
                          {projectRoles.map((role) => (
                            <option key={role.id} value={role.id}>
                              {role.name}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span className="role-badge">{member.role_name}</span>
                      )}
                    </div>
                    {isOwner && !member.isCreator && (
                      <button
                        className="btn-action btn-delete"
                        onClick={() => handleDeleteMember(member.id)}
                        title="Eliminar miembro"
                      >
                        <Trash2 size={18} />
                      </button>
                    )}
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

        {/* MODAL: Agregar Miembro - Bootstrap */}
        {showAddMemberModal && (
          <>
            <div className="modal-backdrop fade show" onClick={() => setShowAddMemberModal(false)}></div>
            <div className="modal fade show d-block" tabIndex="-1" style={{ zIndex: 2100 }}>
              <div className="modal-dialog modal-dialog-centered">
                <div className="modal-content">
                  <div className="modal-header">
                    <h5 className="modal-title">
                      <UserPlus size={24} strokeWidth={2.5} />
                      Agregar Miembro
                    </h5>
                    <button 
                      type="button" 
                      className="btn-close" 
                      onClick={() => setShowAddMemberModal(false)}
                      aria-label="Close"
                    >
                      <X size={28} strokeWidth={3} />
                    </button>
                  </div>
                  <form onSubmit={handleAddMember}>
                    <div className="modal-body">
                      <div className="mb-3">
                        <label htmlFor="user_id" className="form-label">
                          Usuario <span className="text-danger">*</span>
                        </label>
                        <select
                          className="form-select"
                          id="user_id"
                          value={memberForm.user_id}
                          onChange={(e) => setMemberForm({ ...memberForm, user_id: parseInt(e.target.value) })}
                          required
                        >
                          <option value="">Seleccionar usuario</option>
                          {allUsers.map((u) => (
                            <option key={u.id} value={u.id}>
                              {u.name} ({u.email})
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="mb-3">
                        <label htmlFor="project_role_id" className="form-label">
                          Rol <span className="text-danger">*</span>
                        </label>
                        <select
                          className="form-select"
                          id="project_role_id"
                          value={memberForm.project_role_id}
                          onChange={(e) => setMemberForm({ ...memberForm, project_role_id: parseInt(e.target.value) })}
                          required
                        >
                          <option value="">Seleccionar rol</option>
                          {projectRoles.map((role) => (
                            <option key={role.id} value={role.id}>
                              {role.name} - {role.description}
                            </option>
                          ))}
                        </select>
                        <small className="form-text text-muted">
                          Define el nivel de acceso del miembro
                        </small>
                      </div>
                    </div>
                    <div className="modal-footer">
                      <button 
                        type="button" 
                        className="btn btn-secondary" 
                        onClick={() => setShowAddMemberModal(false)}
                      >
                        Cancelar
                      </button>
                      <button type="submit" className="btn btn-primary">
                        <UserPlus size={22} strokeWidth={2.5} />
                        Agregar Miembro
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </>
        )}

        {/* MODAL: Agregar/Editar Tarea - Bootstrap */}
        {(showAddTaskModal || showEditTaskModal) && (
          <>
            <div 
              className="modal-backdrop fade show" 
              onClick={() => {
                setShowAddTaskModal(false);
                setShowEditTaskModal(false);
                setSelectedTask(null);
              }}
            ></div>
            <div className="modal fade show d-block" tabIndex="-1" style={{ zIndex: 2100 }}>
              <div className="modal-dialog modal-dialog-centered">
                <div className="modal-content">
                  <div className="modal-header">
                    <h5 className="modal-title">
                      <ListTodo size={24} strokeWidth={2.5} />
                      {showEditTaskModal ? (isOwner ? "Editar Tarea" : "Gestionar Mi Tarea") : "Nueva Tarea"}
                    </h5>
                    <button
                      type="button"
                      className="btn-close"
                      onClick={() => {
                        setShowAddTaskModal(false);
                        setShowEditTaskModal(false);
                        setSelectedTask(null);
                      }}
                      aria-label="Close"
                    >
                      <X size={28} strokeWidth={3} />
                    </button>
                  </div>
                  <form onSubmit={showEditTaskModal ? handleUpdateTask : handleAddTask}>
                    <div className="modal-body">
                      <div className="mb-3">
                        <label htmlFor="title" className="form-label">
                          Título <span className="text-danger">*</span>
                        </label>
                        <input
                          type="text"
                          className="form-control"
                          id="title"
                          value={taskForm.title}
                          onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
                          placeholder="Título de la tarea"
                          required
                          maxLength={150}
                          disabled={!isOwner && showEditTaskModal}
                        />
                      </div>
                      <div className="mb-3">
                        <label htmlFor="description" className="form-label">
                          Descripción
                        </label>
                        <textarea
                          className="form-control"
                          id="description"
                          value={taskForm.description}
                          onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
                          placeholder="Descripción opcional"
                          rows={3}
                          maxLength={150}
                          disabled={!isOwner && showEditTaskModal}
                        ></textarea>
                      </div>
                      <div className="mb-3">
                        <label htmlFor="status" className="form-label">
                          Estado {!isOwner && <small className="text-muted">(solo puedes mover tu tarea)</small>}
                        </label>
                        <select
                          className="form-select"
                          id="status"
                          value={taskForm.status}
                          onChange={(e) => setTaskForm({ ...taskForm, status: e.target.value })}
                        >
                          {isOwner ? (
                            <>
                              <option value="pending">Por hacer</option>
                              <option value="in_progress">En desarrollo</option>
                              <option value="overdue">Atrasado</option>
                              <option value="in_review">En revisión</option>
                              <option value="completed">Hecho</option>
                            </>
                          ) : (
                            <>
                              {taskForm.status === "pending" && (
                                <>
                                  <option value="pending">Por hacer</option>
                                  <option value="in_progress">En desarrollo</option>
                                </>
                              )}
                              {(taskForm.status === "in_progress" || taskForm.status === "overdue") && (
                                <>
                                  <option value="in_progress">En desarrollo</option>
                                  <option value="overdue">Atrasado</option>
                                  <option value="in_review">En revisión</option>
                                </>
                              )}
                              {taskForm.status === "in_review" && (
                                <option value="in_review">En revisión (esperando aprobación)</option>
                              )}
                              {taskForm.status === "completed" && (
                                <option value="completed">Completada</option>
                              )}
                            </>
                          )}
                        </select>
                      </div>
                      <div className="mb-3">
                        <label htmlFor="assigned_to" className="form-label">
                          Asignar a
                        </label>
                        <select
                          className="form-select"
                          id="assigned_to"
                          value={taskForm.assigned_to || ""}
                          onChange={(e) => setTaskForm({ ...taskForm, assigned_to: e.target.value ? parseInt(e.target.value) : null })}
                          disabled={!isOwner && showEditTaskModal}
                        >
                          <option value="">Sin asignar</option>
                          {projectUsers.map((u) => (
                            <option key={u.id} value={u.id}>
                              {u.name}
                            </option>
                          ))}
                        </select>
                        <small className="form-text text-muted">
                          Solo miembros del proyecto
                        </small>
                      </div>
                      <div className="mb-3">
                        <label htmlFor="due_date" className="form-label">
                          Fecha de vencimiento
                        </label>
                        <input
                          type="date"
                          className="form-control"
                          id="due_date"
                          value={taskForm.due_date || ""}
                          onChange={(e) => setTaskForm({ ...taskForm, due_date: e.target.value || null })}
                          disabled={!isOwner && showEditTaskModal}
                        />
                      </div>
                    </div>
                    <div className="modal-footer">
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => {
                          setShowAddTaskModal(false);
                          setShowEditTaskModal(false);
                          setSelectedTask(null);
                        }}
                      >
                        Cancelar
                      </button>
                      <button type="submit" className="btn btn-primary">
                        {showEditTaskModal ? (
                          <>
                            <Edit2 size={22} strokeWidth={2.5} />
                            {isOwner ? "Actualizar" : "Cambiar Estado"}
                          </>
                        ) : (
                          <>
                            <CheckCircle size={22} strokeWidth={2.5} />
                            Crear Tarea
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default ProyectoDetalle;

