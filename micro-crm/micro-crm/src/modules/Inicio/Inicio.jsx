import { Link } from "react-router-dom";
import "./Inicio.css";

export default function Inicio() {
  return (
    <div className="inicio-container">
      <h1>Bienvenido a nuestro CRM</h1>
      <p>a que módulo que deseas ingresar:</p>

      <div className="modulos-grid">
        <Link to="/clientes" className="modulo-card clientes">
          <h2>👥 Clientes</h2>
          <p>Registrar y gestionar tus clientes.</p>
        </Link>

        <Link to="/proyectos" className="modulo-card proyectos">
          <h2>📁 Proyectos</h2>
          <p>Controla los proyectos activos y su estado.</p>
        </Link>

        <Link to="/admin" className="modulo-card admin">
          <h2>⚙️ Administración</h2>
          <p>Gestión de usuarios y roles del sistema.</p>
        </Link>
      </div>
    </div>
  );
}