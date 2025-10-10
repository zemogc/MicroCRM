import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";
import { 
  Plus, 
  FolderKanban, 
  Users, 
  Calendar, 
  Edit2, 
  Trash2,
  Eye,
  AlertCircle,
  CheckCircle,
  Loader
} from "lucide-react";
import ProyectoVer from "./ProyectoVer";
import ProyectoDetalle from "./ProyectoDetalle";
import "./Proyectos.css";

function Proyectos() {
  const { user } = useAuth();
  const [proyectos, setProyectos] = useState([]);
  const [proyectosComoColaborador, setProyectosComoColaborador] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    crated_by: user?.id || 0
  });
  const [submitting, setSubmitting] = useState(false);
  const [selectedProyecto, setSelectedProyecto] = useState(null);
  const [modoEdicion, setModoEdicion] = useState(false);

  // Cargar proyectos del usuario
  useEffect(() => {
    if (user?.id) {
      fetchProyectos();
      fetchRoles();
    }
  }, [user?.id]);

  const fetchProyectos = async () => {
    if (!user?.id) {
      console.error("Usuario no disponible");
      return;
    }
    
    try {
      setLoading(true);
      setError("");
      
      // Obtener todos los proyectos y membresías del usuario
      const [projectsRes, membershipRes] = await Promise.all([
        api.get("/api/projects/", {
          params: {
            limit: 100,
            order_by: "updated_at",
            order_dir: "desc"
          }
        }),
        // Obtener proyectos donde soy miembro (colaborador)
        api.get(`/api/project-members/user/${user.id}`)
      ]);
      
      const allProjects = projectsRes.data.items || [];
      const membership = membershipRes.data || [];
      
      // IDs de proyectos donde soy miembro (colaborador)
      const collaboratorProjectIds = membership.map(m => m.project_id);
      
      // FILTRAR: Solo mostrar proyectos donde:
      // 1. Soy el creador (crated_by === user.id), O
      // 2. Soy miembro (está en project_members)
      const myProjects = allProjects.filter(p => 
        p.crated_by === user.id || collaboratorProjectIds.includes(p.id)
      );
      
      // Proyectos donde soy colaborador (no creador)
      const collaboratorProjects = myProjects.filter(p => 
        collaboratorProjectIds.includes(p.id) && p.crated_by !== user.id
      );
      
      setProyectos(myProjects); // Solo MIS proyectos
      setProyectosComoColaborador(collaboratorProjects);
    } catch (err) {
      console.error("Error al cargar proyectos:", err);
      setError("Error al cargar los proyectos. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await api.get("/api/roles/");
      setRoles(response.data || []); // Los roles vienen directamente, no en .items
    } catch (err) {
      console.error("Error al cargar roles:", err);
    }
  };

  const handleOpenModal = () => {
    setShowModal(true);
    setFormData({
      name: "",
      description: "",
      crated_by: user?.id || 0
    });
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setFormData({
      name: "",
      description: "",
      crated_by: user?.id || 0
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError("El nombre del proyecto es obligatorio");
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      
      const response = await api.post("/api/projects/", {
        ...formData,
        crated_by: user.id
      });
      
      // Agregar el nuevo proyecto a la lista
      setProyectos(prev => [response.data, ...prev]);
      
      // Cerrar modal
      handleCloseModal();
      
    } catch (err) {
      console.error("Error al crear proyecto:", err);
      setError(err.response?.data?.detail || "Error al crear el proyecto");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (projectId) => {
    if (!window.confirm("¿Estás seguro de eliminar este proyecto?")) {
      return;
    }

    try {
      await api.delete(`/api/projects/${projectId}`);
      setProyectos(prev => prev.filter(p => p.id !== projectId));
    } catch (err) {
      console.error("Error al eliminar proyecto:", err);
      alert("Error al eliminar el proyecto");
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric"
    });
  };

  if (loading) {
    return (
      <div className="proyectos-container">
        <div className="loading-state">
          <Loader size={48} className="spinner" />
          <p>Cargando proyectos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="proyectos-container">
      {/* Header */}
      <div className="proyectos-header">
        <div className="header-title">
          <FolderKanban size={32} />
          <div>
            <h1>Mis Proyectos</h1>
            <p>Gestiona tus proyectos y colaboraciones</p>
          </div>
        </div>
        <button className="btn-primary" onClick={handleOpenModal}>
          <Plus size={20} />
          Nuevo Proyecto
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          <AlertCircle size={20} />
          <span>{error}</span>
          <button 
            type="button" 
            className="btn-close" 
            onClick={() => setError("")}
            aria-label="Close"
          ></button>
        </div>
      )}

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon proyectos-icon">
            <FolderKanban size={24} />
          </div>
          <div className="stat-info">
            <h3>{proyectos.length}</h3>
            <p>Total Proyectos</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon creados-icon">
            <CheckCircle size={24} />
          </div>
          <div className="stat-info">
            <h3>{proyectos.filter(p => p.crated_by === user?.id).length}</h3>
            <p>Creados por mí</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon colaborador-icon">
            <Users size={24} />
          </div>
          <div className="stat-info">
            <h3>{proyectosComoColaborador.length}</h3>
            <p>Como colaborador</p>
          </div>
        </div>
      </div>

      {/* Tabla de Proyectos */}
      <div className="proyectos-table-container">
        {proyectos.length === 0 ? (
          <div className="empty-state">
            <FolderKanban size={64} />
            <h3>No tienes proyectos</h3>
            <p>Crea tu primer proyecto para comenzar</p>
            <button className="btn-primary" onClick={handleOpenModal}>
              <Plus size={20} />
              Crear Proyecto
            </button>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>Proyecto</th>
                  <th>Descripción</th>
                  <th>Creador</th>
                  <th>Creado</th>
                  <th>Actualizado</th>
                  <th className="text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {proyectos.map((proyecto) => (
                  <tr key={proyecto.id}>
                    <td>
                      <div className="proyecto-name">
                        <FolderKanban size={18} />
                        <strong>{proyecto.name}</strong>
                        {proyecto.crated_by === user?.id && (
                          <span className="badge-owner">Propietario</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="text-muted">
                        {proyecto.description || "Sin descripción"}
                      </span>
                    </td>
                    <td>
                      <span className="creator-email">
                        {proyecto.creator_email || "Desconocido"}
                      </span>
                    </td>
                    <td>
                      <span className="date-text">
                        <Calendar size={14} />
                        {formatDate(proyecto.created_at)}
                      </span>
                    </td>
                    <td>
                      <span className="date-text">
                        {formatDate(proyecto.updated_at)}
                      </span>
                    </td>
                    <td>
                      <div className="actions-buttons">
                        <button 
                          className="btn-action btn-view" 
                          title="Ver detalles"
                          onClick={() => {
                            setSelectedProyecto(proyecto);
                            setModoEdicion(false);
                          }}
                        >
                          <Eye size={18} />
                        </button>
                        {/* Botón de editar/gestionar - Owner o Colaborador */}
                        <button 
                          className="btn-action btn-edit" 
                          title={proyecto.crated_by === user?.id ? "Editar" : "Gestionar mis tareas"}
                          onClick={() => {
                            setSelectedProyecto(proyecto);
                            setModoEdicion(true);
                          }}
                        >
                          <Edit2 size={18} />
                        </button>
                        {/* Solo el owner puede eliminar */}
                        {proyecto.crated_by === user?.id && (
                          <button 
                            className="btn-action btn-delete" 
                            title="Eliminar"
                            onClick={() => handleDelete(proyecto.id)}
                          >
                            <Trash2 size={18} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal de Nuevo Proyecto */}
      {showModal && (
        <>
          <div className="modal-backdrop fade show" onClick={handleCloseModal}></div>
          <div className="modal fade show d-block" tabIndex="-1">
            <div className="modal-dialog modal-dialog-centered">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">
                    <FolderKanban size={24} />
                    Nuevo Proyecto
                  </h5>
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={handleCloseModal}
                    aria-label="Close"
                  ></button>
                </div>
                <form onSubmit={handleSubmit}>
                  <div className="modal-body">
                    <div className="mb-3">
                      <label htmlFor="name" className="form-label">
                        Nombre del Proyecto <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Ej: Sistema de Gestión"
                        required
                        maxLength={100}
                      />
                    </div>
                    <div className="mb-3">
                      <label htmlFor="description" className="form-label">
                        Descripción
                      </label>
                      <textarea
                        className="form-control"
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        placeholder="Describe brevemente el proyecto"
                        rows={3}
                        maxLength={150}
                      ></textarea>
                      <small className="form-text text-muted">
                        Máximo 150 caracteres
                      </small>
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button 
                      type="button" 
                      className="btn btn-secondary" 
                      onClick={handleCloseModal}
                      disabled={submitting}
                    >
                      Cancelar
                    </button>
                    <button 
                      type="submit" 
                      className="btn btn-primary"
                      disabled={submitting}
                    >
                      {submitting ? (
                        <>
                          <Loader size={18} className="spinner" />
                          Creando...
                        </>
                      ) : (
                        <>
                          <CheckCircle size={18} />
                          Crear Proyecto
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

      {/* Modales de Proyecto */}
      {selectedProyecto && !modoEdicion && (
        <ProyectoVer
          proyecto={selectedProyecto}
          onClose={() => {
            setSelectedProyecto(null);
            setModoEdicion(false);
          }}
        />
      )}

      {selectedProyecto && modoEdicion && (
        <ProyectoDetalle
          proyecto={selectedProyecto}
          onClose={() => {
            setSelectedProyecto(null);
            setModoEdicion(false);
          }}
          onUpdate={fetchProyectos}
        />
      )}
    </div>
  );
}

export default Proyectos;
