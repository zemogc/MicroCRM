import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme debe ser usado dentro de un ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Obtener el tema guardado en localStorage o usar 'light' por defecto
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Aplicar el tema inmediatamente al DOM para evitar flash
    if (typeof document !== 'undefined') {
      document.body.setAttribute('data-bs-theme', savedTheme);
      document.documentElement.setAttribute('data-bs-theme', savedTheme);
    }
    
    return savedTheme;
  });

  useEffect(() => {
    // Aplicar el tema al body del documento
    document.body.setAttribute('data-bs-theme', theme);
    document.documentElement.setAttribute('data-bs-theme', theme);
    
    // Guardar el tema en localStorage
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  const value = {
    theme,
    toggleTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light'
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
