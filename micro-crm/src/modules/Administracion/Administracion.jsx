import { useState, useEffect } from "react";

export default function Administracion() {
  const [usuarios, setUsuarios] = useState([]);
  const [nombre, setNombre] = useState("");
  const [correo, setCorreo] = useState("");
  const [rol, setRol] = useState("consultor");
  const [editIndex, setEditIndex] = useState(null);

  // Cargar desde localStorage al iniciar
  useEffect(() => {
    const data = JSON.parse(localStorage.getItem("usuarios")) || [];
    setUsuarios(data);
  }, []);

  // Guardar automáticamente cada vez que cambia la lista
  useEffect(() => {
    localStorage.setItem("usuarios", JSON.stringify(usuarios));
  }, [usuarios]);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!nombre || !correo) {
      alert("Por favor completa todos los campos.");
      return;
    }

    const nuevoUsuario = { nombre, correo, rol };

    if (editIndex !== null) {
      // Editar usuario existente
      const actualizados = usuarios.map((u, i) =>
        i === editIndex ? nuevoUsuario : u
      );
      setUsuarios(actualizados);
      setEditIndex(null);
    } else {
      // Crear nuevo usuario
      setUsuarios([...usuarios, nuevoUsuario]);
    }

    setNombre("");
    setCorreo("");
    setRol("consultor");
  };

  const handleEdit = (index) => {
    const usuario = usuarios[index];
    setNombre(usuario.nombre);
    setCorreo(usuario.correo);
    setRol(usuario.rol);
    setEditIndex(index);
  };

  const handleDelete = (index) => {
    if (confirm("¿Seguro que deseas eliminar este usuario?")) {
      setUsuarios(usuarios.filter((_, i) => i !== index));
    }
  };

  return (
    <div className="card">
      <h2>Gestión de Usuarios</h2>

      <form onSubmit={handleSubmit}>
        <label>Nombre</label>
        <input
          type="text"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          placeholder="Ej. Juan Pérez"
        />

        <label>Correo</label>
        <input
          type="email"
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
          placeholder="Ej. juan@empresa.com"
        />

        <label>Rol</label>
        <select value={rol} onChange={(e) => setRol(e.target.value)}>
          <option value="consultor">Consultor</option>
          <option value="gerente">Gerente</option>
          <option value="administrador">Administrador</option>
        </select>

        <button className="btn" type="submit">
          {editIndex !== null ? "Actualizar Usuario" : "Registrar Usuario"}
        </button>
      </form>

      <h3>Usuarios Registrados</h3>
      {usuarios.length === 0 ? (
        <p>No hay usuarios registrados.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((u, index) => (
              <tr key={index}>
                <td>{u.nombre}</td>
                <td>{u.correo}</td>
                <td>{u.rol}</td>
                <td>
                  <button
                    className="btn"
                    style={{ backgroundColor: "#ffc107", marginRight: "8px" }}
                    onClick={() => handleEdit(index)}
                  >
                    Editar
                  </button>
                  <button
                    className="btn"
                    style={{ backgroundColor: "#dc3545" }}
                    onClick={() => handleDelete(index)}
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}