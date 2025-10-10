import { Link, NavLink } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
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
    </nav>
  );
}