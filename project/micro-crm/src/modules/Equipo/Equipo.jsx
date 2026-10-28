import { useState, useEffect } from "react";
import { UserCog, Save, KeyRound, Users, Search, CheckCircle, AlertCircle, Loader } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";
import { apiErrorMessage, formatDate } from "../../utils/format";
import "../Proyectos/Proyectos.css";
import "./Equipo.css";

const EMPTY_PASSWORDS = { current_password: "", new_password: "", confirm: "" };

function Feedback({ message }) {
  if (!message) return null;
  const Icon = message.type === "success" ? CheckCircle : AlertCircle;
  return (
    <div className={`equipo-feedback is-${message.type}`} role="status">
      <Icon size={18} />
      <span>{message.text}</span>
    </div>
  );
}

export default function Equipo() {
  const { user, updateUser } = useAuth();

  const [profile, setProfile] = useState({ name: user.name, email: user.email });
  const [profileMsg, setProfileMsg] = useState(null);
  const [savingProfile, setSavingProfile] = useState(false);

  const [passwords, setPasswords] = useState(EMPTY_PASSWORDS);
  const [passwordMsg, setPasswordMsg] = useState(null);
  const [savingPassword, setSavingPassword] = useState(false);

  const [search, setSearch] = useState("");
  const [members, setMembers] = useState([]);
  const [membersTotal, setMembersTotal] = useState(0);
  const [loadingMembers, setLoadingMembers] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      api.get("/api/users/", { params: { limit: 50, order_by: "name", order_dir: "asc", search: search.trim() || undefined } })
        .then((res) => {
          setMembers(res.data.items);
          setMembersTotal(res.data.total);
        })
        .catch(() => setMembers([]))
        .finally(() => setLoadingMembers(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    try {
      setSavingProfile(true);
      setProfileMsg(null);
      const res = await api.put(`/api/users/${user.id}`, profile);
      updateUser(res.data);
      setProfileMsg({ type: "success", text: "Perfil actualizado" });
    } catch (err) {
      setProfileMsg({ type: "error", text: apiErrorMessage(err, "No se pudo actualizar el perfil") });
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwords.new_password !== passwords.confirm) {
      setPasswordMsg({ type: "error", text: "Las contraseñas nuevas no coinciden" });
      return;
    }
    try {
      setSavingPassword(true);
      setPasswordMsg(null);
      await api.post("/api/auth/change-password", {
        current_password: passwords.current_password,
        new_password: passwords.new_password
      });
      setPasswords(EMPTY_PASSWORDS);
      setPasswordMsg({ type: "success", text: "Contraseña actualizada" });
    } catch (err) {
      setPasswordMsg({ type: "error", text: apiErrorMessage(err, "No se pudo cambiar la contraseña") });
    } finally {
      setSavingPassword(false);
    }
  };

  const profileChanged = profile.name.trim() !== user.name || profile.email.trim() !== user.email;

  return (
    <div className="proyectos-container">
      <div className="proyectos-header">
        <div className="header-title">
          <UserCog size={32} />
          <div>
            <h1>Equipo y cuenta</h1>
            <p>Tu perfil, tu seguridad y las personas con las que colaboras</p>
          </div>
        </div>
      </div>

      <div className="equipo-grid">
        {/* Perfil */}
        <section className="equipo-panel">
          <div className="equipo-profile-head">
            <div className="equipo-avatar">{user.name.charAt(0).toUpperCase()}</div>
            <div>
              <h2>{user.name}</h2>
              <span>Miembro desde {formatDate(user.created_at)}</span>
            </div>
          </div>
          <form onSubmit={handleProfileSubmit}>
            <label htmlFor="perfil-nombre" className="form-label">Nombre</label>
            <input id="perfil-nombre" className="form-control mb-3" value={profile.name} maxLength={100} required
              onChange={(e) => setProfile({ ...profile, name: e.target.value })} />
            <label htmlFor="perfil-correo" className="form-label">Correo</label>
            <input id="perfil-correo" type="email" className="form-control mb-3" value={profile.email} maxLength={150} required
              onChange={(e) => setProfile({ ...profile, email: e.target.value })} />
            <Feedback message={profileMsg} />
            <button type="submit" className="btn btn-primary equipo-submit" disabled={savingProfile || !profileChanged}>
              {savingProfile ? <Loader size={18} className="spinner" /> : <Save size={18} />}
              Guardar perfil
            </button>
          </form>
        </section>

        {/* Seguridad */}
        <section className="equipo-panel">
          <h2 className="equipo-panel-title"><KeyRound size={20} /> Cambiar contraseña</h2>
          <form onSubmit={handlePasswordSubmit}>
            <label htmlFor="pass-actual" className="form-label">Contraseña actual</label>
            <input id="pass-actual" type="password" className="form-control mb-3" autoComplete="current-password" required
              value={passwords.current_password}
              onChange={(e) => setPasswords({ ...passwords, current_password: e.target.value })} />
            <label htmlFor="pass-nueva" className="form-label">Nueva contraseña</label>
            <input id="pass-nueva" type="password" className="form-control" autoComplete="new-password" required
              value={passwords.new_password}
              onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })} />
            <small className="form-text text-muted d-block mb-3">
              Mínimo 8 caracteres, con mayúscula, minúscula y número.
            </small>
            <label htmlFor="pass-confirmar" className="form-label">Confirmar nueva contraseña</label>
            <input id="pass-confirmar" type="password" className="form-control mb-3" autoComplete="new-password" required
              value={passwords.confirm}
              onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })} />
            <Feedback message={passwordMsg} />
            <button type="submit" className="btn btn-primary equipo-submit" disabled={savingPassword}>
              {savingPassword ? <Loader size={18} className="spinner" /> : <KeyRound size={18} />}
              Actualizar contraseña
            </button>
          </form>
        </section>

        {/* Directorio */}
        <section className="equipo-panel equipo-panel-wide">
          <div className="equipo-directory-head">
            <h2 className="equipo-panel-title"><Users size={20} /> Directorio ({membersTotal})</h2>
            <div className="search-field equipo-search">
              <Search size={18} />
              <input type="search" className="form-control" placeholder="Buscar por nombre o correo"
                value={search} onChange={(e) => setSearch(e.target.value)} aria-label="Buscar personas" />
            </div>
          </div>
          <p className="equipo-hint">
            Agrega a estas personas como colaboradores desde la pestaña <strong>Miembros</strong> de cada proyecto.
          </p>
          {loadingMembers ? (
            <div className="loading-state"><Loader size={32} className="spinner" /></div>
          ) : members.length === 0 ? (
            <p className="text-muted text-center py-4">No se encontraron personas.</p>
          ) : (
            <ul className="equipo-directory">
              {members.map((member) => (
                <li key={member.id}>
                  <div className="equipo-avatar is-small">{member.name.charAt(0).toUpperCase()}</div>
                  <div className="equipo-member">
                    <strong>{member.name}{member.id === user.id && <span className="equipo-you">Tú</span>}</strong>
                    <span>{member.email}</span>
                  </div>
                  <span className={`equipo-state ${member.active ? "is-active" : ""}`}>
                    {member.active ? "Activo" : "Inactivo"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
