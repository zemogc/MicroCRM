import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Mail, Lock, Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';
import ThemeToggle from '../../components/ThemeToggle';
import './Auth.css';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(formData);
      navigate('/');
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Error al iniciar sesión. Verifica tus credenciales.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      {/* Botón de tema flotante */}
      <ThemeToggle className="floating" />
      
      {/* Columna izquierda - Ilustración (auth-cover-left) */}
      <div className="auth-illustration">
        <div className="card">
          <div className="card-body">
            <img 
              src="/src/assets/login-cover.svg" 
              className="img-fluid"
              width="650"
              alt="Login Illustration"
            />
          </div>
        </div>
      </div>

      {/* Columna derecha - Formulario (auth-cover-right) */}
      <div className="auth-form-section">
        <div className="card">
          <div className="auth-form-wrapper">
            {/* Header */}
            <div className="auth-header">
              <div className="auth-logo">
                <div style={{
                  width: '60px',
                  height: '60px',
                  background: 'linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%)',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto'
                }}>
                  <LogIn size={28} color="white" />
                </div>
              </div>
              <h5>MicroCRM Admin</h5>
              <p>Por favor inicia sesión en tu cuenta</p>
            </div>

            {/* Error Alert */}
            {error && (
              <div className="auth-alert">
                <AlertCircle size={20} />
                <span>{error}</span>
              </div>
            )}

            {/* Form */}
            <div className="form-body">
              <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                  <label htmlFor="inputEmailAddress" className="form-label">Correo Electrónico</label>
                  <input
                    type="email"
                    className="form-control"
                    id="inputEmailAddress"
                    name="email"
                    placeholder="juan@ejemplo.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    autoComplete="email"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="inputChoosePassword" className="form-label">Contraseña</label>
                  <div className="input-group" id="show_hide_password">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      className="form-control border-end-0"
                      id="inputChoosePassword"
                      name="password"
                      placeholder="Ingresa tu contraseña"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      autoComplete="current-password"
                    />
                    <button
                      type="button"
                      className="input-group-text bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>

                <div className="form-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div className="form-check form-switch">
                      <input className="form-check-input" type="checkbox" id="flexSwitchCheckChecked" />
                      <label className="form-check-label" htmlFor="flexSwitchCheckChecked">Recordarme</label>
                    </div>
                    <a href="#" style={{ textAlign: 'right' }}>¿Olvidaste tu contraseña?</a>
                  </div>
                </div>

                <div className="form-group">
                  <div className="d-grid">
                    <button 
                      type="submit" 
                      className="auth-button"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <div className="spinner"></div>
                          Iniciando sesión...
                        </>
                      ) : (
                        'Iniciar Sesión'
                      )}
                    </button>
                  </div>
                </div>

                <div className="form-group">
                  <div className="text-center">
                    <p className="mb-0">
                      ¿No tienes una cuenta?{' '}
                      <Link to="/register" className="auth-link">
                        Regístrate aquí
                      </Link>
                    </p>
                  </div>
                </div>
              </form>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

