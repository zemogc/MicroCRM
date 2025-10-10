import api from './api';

// Servicio de autenticación
const authService = {
  // Registro de usuario
  register: async (userData) => {
    try {
      const response = await api.post('/api/auth/register', userData);
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Error al registrar usuario';
    }
  },

  // Login de usuario
  login: async (credentials) => {
    try {
      const response = await api.post('/api/auth/login', credentials);
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Error al iniciar sesión';
    }
  },

  // Logout
  logout: () => {
    // Limpiar solo los datos de autenticación
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Opcional: Limpiar también los datos temporales de la aplicación
    // (estos datos deberían venir del backend, no de localStorage)
    localStorage.removeItem('clientes');
    localStorage.removeItem('proyectos');
    localStorage.removeItem('usuarios');
  },

  // Obtener información del usuario actual
  getCurrentUser: async () => {
    try {
      const response = await api.get('/api/auth/me');
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Error al obtener usuario';
    }
  },

  // Obtener token almacenado
  getToken: () => {
    return localStorage.getItem('token');
  },

  // Obtener usuario almacenado
  getStoredUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  // Verificar si el usuario está autenticado
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
};

export default authService;

