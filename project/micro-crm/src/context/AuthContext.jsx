import { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Verificar si hay un usuario autenticado al cargar la aplicación
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = authService.getToken();
        if (token) {
          const storedUser = authService.getStoredUser();
          setUser(storedUser);
          
          // Opcionalmente, verificar el token con el backend
          try {
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
            localStorage.setItem('user', JSON.stringify(currentUser));
          } catch (err) {
            // Si el token es inválido, limpiar
            authService.logout();
            setUser(null);
          }
        }
      } catch (err) {
        console.error('Error al inicializar autenticación:', err);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Función de login
  const login = async (credentials) => {
    try {
      setError(null);
      const data = await authService.login(credentials);
      setUser(data.user);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    }
  };

  // Función de registro
  const register = async (userData) => {
    try {
      setError(null);
      const data = await authService.register(userData);
      setUser(data.user);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    }
  };

  // Función de logout
  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;

