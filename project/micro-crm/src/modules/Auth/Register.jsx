import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { User, Mail, Lock, Eye, EyeOff, UserPlus, AlertCircle, CheckCircle } from 'lucide-react';
import ThemeToggle from '../../components/ThemeToggle';
import './Auth.css';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const validateForm = () => {
    if (!formData.name || !formData.email || !formData.password) {
      setError('Todos los campos son obligatorios');
      return false;
    }

    if (formData.password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('El correo electrónico no es válido');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const { confirmPassword, ...registerData } = formData;
      await register(registerData);
      navigate('/');
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Error al registrar usuario. Intenta con otro correo.');
    } finally {
      setLoading(false);
    }
  };

  const passwordStrength = formData.password.length >= 6;
  const passwordsMatch = formData.password === formData.confirmPassword && formData.confirmPassword.length > 0;

  return (
    <div className="auth-container">
      {/* Botón de tema flotante */}
      <ThemeToggle className="floating" />
      
      {/* Columna izquierda - Ilustración (auth-cover-left) */}
      <div className="auth-illustration">
        <div className="card">
          <div className="card-body">
            <img 
              src="/src/assets/register-cover.svg" 
              className="img-fluid"
              width="650"
              alt="Register Illustration"
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
                  <UserPlus size={28} color="white" />
                </div>
              </div>
              <h5>MicroCRM Admin</h5>
              <p>Crea tu cuenta</p>
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
                  <label htmlFor="inputName" className="form-label">Nombre Completo</label>
                  <input
                    type="text"
                    className="form-control"
                    id="inputName"
                    name="name"
                    placeholder="Juan Pérez"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    autoComplete="name"
                  />
                </div>

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
                  <label htmlFor="inputPassword" className="form-label">Contraseña</label>
                  <div className="input-group">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      className="form-control border-end-0"
                      id="inputPassword"
                      name="password"
                      placeholder="Ingresa tu contraseña"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      autoComplete="new-password"
                      minLength={6}
                    />
                    <button
                      type="button"
                      className="input-group-text bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  <div className="validation-text">
                    {passwordStrength ? (
                      <>
                        <CheckCircle size={16} className="success-icon" />
                        <span className="success-text">Contraseña válida (mínimo 8 caracteres)</span>
                      </>
                    ) : (
                      <span className="hint-text">Mínimo 8 caracteres</span>
                    )}
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="inputConfirmPassword" className="form-label">Confirmar Contraseña</label>
                  <div className="input-group">
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      className="form-control border-end-0"
                      id="inputConfirmPassword"
                      name="confirmPassword"
                      placeholder="Confirma tu contraseña"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                      autoComplete="new-password"
                    />
                    <button
                      type="button"
                      className="input-group-text bg-transparent"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  {formData.confirmPassword.length > 0 && (
                    <div className="validation-text">
                      {passwordsMatch ? (
                        <>
                          <CheckCircle size={16} className="success-icon" />
                          <span className="success-text">Las contraseñas coinciden</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle size={16} className="error-icon" />
                          <span className="error-text">Las contraseñas no coinciden</span>
                        </>
                      )}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <div className="d-grid">
                    <button 
                      type="submit" 
                      className="auth-button"
                      disabled={loading || !passwordStrength || !passwordsMatch}
                    >
                      {loading ? (
                        <>
                          <div className="spinner"></div>
                          Creando cuenta...
                        </>
                      ) : (
                        'Crear Cuenta'
                      )}
                    </button>
                  </div>
                </div>

                <div className="form-group">
                  <div className="text-center">
                    <p className="mb-0">
                      ¿Ya tienes una cuenta?{' '}
                      <Link to="/login" className="auth-link">
                        Inicia sesión aquí
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

export default Register;

