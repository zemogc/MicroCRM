import { Link } from "react-router-dom";
import "./Inicio.css";

export default function Inicio() {
  return (
    <main className="inicio">
      <div className="container">
        <header className="hero">
          <h1 className="hero__title">
            <span className="hero__strip">Bienvenido a nuestro CRM</span>
          </h1>
          <p className="hero__subtitle">¿A qué módulo deseas ingresar?</p>
        </header>

        <section className="grid" aria-label="Módulos del sistema">
          <Link to="/clientes" className="card card--clientes">
            <div className="card__icon" aria-hidden>👥</div>
            <h2 className="card__title">Clientes</h2>
            <p className="card__desc">Registrar y gestionar tus clientes.</p>
          </Link>

          <Link to="/proyectos" className="card card--proyectos">
            <div className="card__icon" aria-hidden>📁</div>
            <h2 className="card__title">Proyectos</h2>
            <p className="card__desc">Controla los proyectos activos y su estado.</p>
          </Link>

          <Link to="/admin" className="card card--admin">
            <div className="card__icon" aria-hidden>⚙️</div>
            <h2 className="card__title">Administración</h2>
            <p className="card__desc">Gestión de usuarios y roles del sistema.</p>
          </Link>
        </section>
      </div>
    </main>
  );
}
