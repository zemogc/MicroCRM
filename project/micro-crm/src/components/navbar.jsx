import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ThemeToggle from "./ThemeToggle";
import "./Navbar.css";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <Link to="/" className="navbar-title">
          Micro CRM
        </Link>
      </div>

      <div className="navbar-links">
        <NavLink
          to="/clientes"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          Clientes
        </NavLink>
        <NavLink
          to="/proyectos"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          Proyectos
        </NavLink>
        <NavLink
          to="/admin"
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          Administración
        </NavLink>
      </div>

      <div className="navbar-user">
        <div className="user-info">
          <span className="user-name">{user?.name}</span>
          <span className="user-email">{user?.email}</span>
        </div>
        <ThemeToggle />
        <button onClick={handleLogout} className="btn-logout">
          Cerrar Sesión
        </button>
      </div>
    </nav>
  );
}