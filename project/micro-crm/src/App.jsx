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
import Equipo from "./modules/Equipo/Equipo";
import "./styles/global.css";
import "./App.css";

// Rutas privadas: requieren autenticación y comparten el layout con sidebar
const PRIVATE_ROUTES = [
  { path: "/", element: <Inicio /> },
  { path: "/clientes", element: <Clientes /> },
  { path: "/proyectos", element: <Proyectos /> },
  { path: "/tareas", element: <Tareas /> },
  { path: "/equipo", element: <Equipo /> },
];

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <Routes>
            {/* Rutas públicas */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {PRIVATE_ROUTES.map(({ path, element }) => (
              <Route
                key={path}
                path={path}
                element={
                  <PrivateRoute>
                    <Layout>{element}</Layout>
                  </PrivateRoute>
                }
              />
            ))}

            {/* Ruta por defecto */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
