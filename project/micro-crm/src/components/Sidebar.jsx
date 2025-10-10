import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ThemeToggle from "./ThemeToggle";
import { 
  LayoutDashboard, 
  Users, 
  FolderKanban, 
  ListTodo,
  Settings, 
  LogOut,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { useState } from "react";
import "./Sidebar.css";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const menuItems = [
    {
      path: "/",
      icon: LayoutDashboard,
      label: "Inicio",
      exact: true
    },
    {
      path: "/clientes",
      icon: Users,
      label: "Clientes"
    },
    {
      path: "/proyectos",
      icon: FolderKanban,
      label: "Proyectos"
    },
    {
      path: "/tareas",
      icon: ListTodo,
      label: "Mis Tareas"
    },
    {
      path: "/admin",
      icon: Settings,
      label: "Administración"
    }
  ];

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      {/* Header del Sidebar */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon">
            <LayoutDashboard size={24} />
          </div>
          {!isCollapsed && <span className="logo-text">MicroCRM</span>}
        </div>
        <button 
          className="toggle-btn" 
          onClick={() => setIsCollapsed(!isCollapsed)}
          title={isCollapsed ? "Expandir" : "Contraer"}
        >
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {/* Navegación */}
      <nav className="sidebar-nav">
        <ul className="nav-list">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.path} className="nav-item">
                <NavLink
                  to={item.path}
                  end={item.exact}
                  className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                  title={isCollapsed ? item.label : ''}
                >
                  <Icon size={20} className="nav-icon" />
                  {!isCollapsed && <span className="nav-label">{item.label}</span>}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer del Sidebar */}
      <div className="sidebar-footer">
        {/* Toggle de Tema */}
        <div className="theme-toggle-wrapper">
          <ThemeToggle className={isCollapsed ? 'collapsed' : ''} />
        </div>

        {/* Información del Usuario */}
        <div className="user-section">
          <div className="user-avatar">
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </div>
          {!isCollapsed && (
            <div className="user-details">
              <span className="user-name">{user?.name}</span>
              <span className="user-email">{user?.email}</span>
            </div>
          )}
        </div>

        {/* Botón de Logout */}
        <button 
          onClick={handleLogout} 
          className="logout-btn"
          title={isCollapsed ? "Cerrar Sesión" : ''}
        >
          <LogOut size={20} />
          {!isCollapsed && <span>Cerrar Sesión</span>}
        </button>
      </div>
    </aside>
  );
}

