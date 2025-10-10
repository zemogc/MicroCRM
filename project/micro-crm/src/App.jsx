import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import PrivateRoute from "./components/PrivateRoute";
import Navbar from "./components/navbar";
import Login from "./modules/Auth/Login";
import Register from "./modules/Auth/Register";
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
      <ThemeProvider>
        <AuthProvider>
          <Routes>
          {/* Rutas públicas */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Rutas privadas - requieren autenticación */}
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Navbar />
                {/* OJO: usamos className="app-shell" para evitar el choque */}
                <main className="app-shell">
                  <Inicio />
                </main>
              </PrivateRoute>
            }
          />
          <Route
            path="/clientes"
            element={
              <PrivateRoute>
                <Navbar />
                <main className="app-shell">
                  <Clientes setClientes={setClientes} />
                </main>
              </PrivateRoute>
            }
          />
          <Route
            path="/proyectos"
            element={
              <PrivateRoute>
                <Navbar />
                <main className="app-shell">
                  <Proyectos clientes={clientes} />
                </main>
              </PrivateRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <PrivateRoute>
                <Navbar />
                <main className="app-shell">
                  <Administracion />
                </main>
              </PrivateRoute>
            }
          />

          {/* Ruta por defecto */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
