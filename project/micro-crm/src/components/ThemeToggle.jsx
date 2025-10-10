import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon } from 'lucide-react';
import './ThemeToggle.css';

const ThemeToggle = ({ className = '' }) => {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
        <button
          className={`theme-toggle ${className}`}
          onClick={toggleTheme}
          title={`Cambiar a tema ${isDark ? 'claro' : 'oscuro'}`}
          aria-label={`Cambiar a tema ${isDark ? 'claro' : 'oscuro'}`}
        >
          {isDark ? (
            <Sun size={28} strokeWidth={3} />
          ) : (
            <Moon size={28} strokeWidth={3} />
          )}
        </button>
  );
};

export default ThemeToggle;
