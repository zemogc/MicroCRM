import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import PrivateRoute from "./components/PrivateRoute";
import Layout from "./components/Layout";
import Login from "./modules/Auth/Login";
import Register from "./modules/Auth/Register";
import Inicio from "./modules/Inicio/Inicio";
import Clientes from "./modules/Clientes/Clientes";
import Proyectos from "./modules/Proyectos/Proyectos";
import Tareas from "./modules/Tareas/Tareas";
import Administracion from "./modules/Administracion/Administracion";
import "./styles/global.css";
import "./App.css";
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
                <Layout>
                  <Inicio />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/clientes"
            element={
              <PrivateRoute>
                <Layout>
                  <Clientes setClientes={setClientes} />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/proyectos"
            element={
              <PrivateRoute>
                <Layout>
                  <Proyectos />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/tareas"
            element={
              <PrivateRoute>
                <Layout>
                  <Tareas />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <PrivateRoute>
                <Layout>
                  <Administracion />
                </Layout>
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
