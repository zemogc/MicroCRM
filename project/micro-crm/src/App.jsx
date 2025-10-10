import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/navbar";
import Inicio from "./modules/Inicio/Inicio";
import Clientes from "./modules/Clientes/Clientes";
import Proyectos from "./modules/Proyectos/Proyectos";
import Administracion from "./modules/Administracion/Administracion";
import "./styles/global.css";
import "./App.css"; // importa los ajustes de App
import { useState } from "react";

function App() {
  const [clientes, setClientes] = useState([]);

  return (
    <Router>
      <Navbar />
      {/* OJO: ya NO usamos className="container" para evitar el choque */}
      <main className="app-shell">
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/clientes" element={<Clientes setClientes={setClientes} />} />
          <Route path="/proyectos" element={<Proyectos clientes={clientes} />} />
          <Route path="/admin" element={<Administracion />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
