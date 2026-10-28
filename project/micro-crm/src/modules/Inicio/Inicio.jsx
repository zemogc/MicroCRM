import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Users,
  FolderKanban,
  ListTodo,
  TrendingUp,
  CalendarClock,
  ArrowRight,
  AlertCircle,
  Loader,
  PartyPopper
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";
import StatusBadge from "../../components/StatusBadge";
import { TASK_STATUS } from "../../constants/status";
import { apiErrorMessage, daysUntil, formatDate, relativeDue } from "../../utils/format";
import "./Inicio.css";

const greeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return "Buenos días";
  if (hour < 19) return "Buenas tardes";
  return "Buenas noches";
};

export default function Inicio() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/api/dashboard/summary")
      .then((res) => setSummary(res.data))
      .catch((err) => setError(apiErrorMessage(err, "No se pudo cargar el resumen")));
  }, []);

  const firstName = user?.name?.split(" ")[0] || "";
  const today = new Date().toLocaleDateString("es-ES", { weekday: "long", day: "numeric", month: "long" });

  if (error) {
    return (
      <div className="dash">
        <div className="alert alert-danger"><AlertCircle size={20} /> {error}</div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="dash dash-loading">
        <Loader size={48} className="spinner" />
        <p>Cargando tu resumen...</p>
      </div>
    );
  }

  const { projects, tasks, clients, due_soon: dueSoon, recent_projects: recentProjects } = summary;
  const distribution = Object.entries(tasks.by_status).filter(([, count]) => count > 0);

  const kpis = [
    {
      to: "/proyectos", icon: FolderKanban, className: "kpi-projects",
      value: projects.total, label: "Proyectos",
      detail: `${projects.owned} propios · ${projects.collaborating} como colaborador`
    },
    {
      to: "/tareas", icon: ListTodo, className: "kpi-tasks",
      value: tasks.open, label: "Tareas abiertas",
      detail: tasks.by_status.overdue > 0
        ? `${tasks.by_status.overdue} ${tasks.by_status.overdue === 1 ? "atrasada" : "atrasadas"}`
        : "Ninguna atrasada",
      alert: tasks.by_status.overdue > 0
    },
    {
      to: "/tareas", icon: TrendingUp, className: "kpi-progress",
      value: `${tasks.completion_rate}%`, label: "Avance",
      detail: `${tasks.by_status.completed} de ${tasks.assigned} tareas completadas`,
      progress: tasks.completion_rate
    },
    {
      to: "/clientes", icon: Users, className: "kpi-clients",
      value: clients.total, label: "Clientes",
      detail: `${clients.by_status.active} activos · ${clients.by_status.lead} prospectos`
    }
  ];

  return (
    <div className="dash">
      <header className="dash-hero">
        <div>
          <p className="dash-date">{today.charAt(0).toUpperCase() + today.slice(1)}</p>
          <h1>{greeting()}, {firstName}</h1>
          <p className="dash-subtitle">Este es el estado de tus proyectos, tareas y clientes.</p>
        </div>
      </header>

      <section className="dash-kpis" aria-label="Indicadores">
        {kpis.map(({ to, icon: Icon, className, value, label, detail, alert, progress }) => (
          <Link to={to} key={label} className={`dash-kpi ${className}`}>
            <div className="dash-kpi-icon"><Icon size={22} /></div>
            <div className="dash-kpi-body">
              <span className="dash-kpi-label">{label}</span>
              <strong className="dash-kpi-value">{value}</strong>
              {progress !== undefined && (
                <div className="dash-progress" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
                  <span style={{ width: `${progress}%` }} />
                </div>
              )}
              <span className={`dash-kpi-detail ${alert ? "is-alert" : ""}`}>{detail}</span>
            </div>
          </Link>
        ))}
      </section>

      <div className="dash-grid">
        <section className="dash-panel">
          <div className="dash-panel-header">
            <h2><CalendarClock size={20} /> Próximos vencimientos</h2>
            <Link to="/tareas" className="dash-link">Ver tareas <ArrowRight size={16} /></Link>
          </div>
          {dueSoon.length === 0 ? (
            <div className="dash-empty">
              <PartyPopper size={36} />
              <p>No tienes tareas por vencer esta semana.</p>
            </div>
          ) : (
            <ul className="dash-due-list">
              {dueSoon.map((task) => (
                <li key={task.id} className={daysUntil(task.due_date) < 0 ? "is-late" : ""}>
                  <div className="dash-due-main">
                    <strong>{task.title}</strong>
                    <span><FolderKanban size={13} /> {task.project_name}</span>
                  </div>
                  <div className="dash-due-meta">
                    <StatusBadge status={task.status} size={12} />
                    <span className="dash-due-when" title={formatDate(task.due_date)}>{relativeDue(task.due_date)}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="dash-panel">
          <div className="dash-panel-header">
            <h2><ListTodo size={20} /> Mis tareas por estado</h2>
          </div>
          {distribution.length === 0 ? (
            <div className="dash-empty">
              <ListTodo size={36} />
              <p>Aún no tienes tareas asignadas.</p>
            </div>
          ) : (
            <>
              <div className="dash-stacked" aria-hidden="true">
                {distribution.map(([status, count]) => (
                  <span
                    key={status}
                    style={{ flexGrow: count, background: TASK_STATUS[status].color }}
                    title={`${TASK_STATUS[status].label}: ${count}`}
                  />
                ))}
              </div>
              <ul className="dash-legend">
                {Object.entries(tasks.by_status).map(([status, count]) => (
                  <li key={status}>
                    <span className="dash-dot" style={{ background: TASK_STATUS[status].color }} />
                    <span>{TASK_STATUS[status].label}</span>
                    <strong>{count}</strong>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>

        <section className="dash-panel dash-panel-wide">
          <div className="dash-panel-header">
            <h2><FolderKanban size={20} /> Proyectos recientes</h2>
            <Link to="/proyectos" className="dash-link">Ver proyectos <ArrowRight size={16} /></Link>
          </div>
          {recentProjects.length === 0 ? (
            <div className="dash-empty">
              <FolderKanban size={36} />
              <p>Crea tu primer proyecto para empezar a organizar el trabajo.</p>
              <Link to="/proyectos" className="dash-link">Ir a proyectos <ArrowRight size={16} /></Link>
            </div>
          ) : (
            <ul className="dash-projects">
              {recentProjects.map((project) => (
                <li key={project.id}>
                  <div className="dash-project-icon"><FolderKanban size={18} /></div>
                  <div className="dash-project-main">
                    <strong>{project.name}</strong>
                    <span>{project.description || "Sin descripción"}</span>
                  </div>
                  <span className={project.id_user === user?.id ? "badge-owner" : "badge-collaborator"}>
                    {project.id_user === user?.id ? "Propietario" : "Colaborador"}
                  </span>
                  <span className="dash-project-date">Actualizado {formatDate(project.updated_at)}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
