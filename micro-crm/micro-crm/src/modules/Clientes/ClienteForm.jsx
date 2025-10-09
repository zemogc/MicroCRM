import { useState, useEffect } from "react";

export default function ClienteForm({ clientes = [], editClient = null, onSave, onCancelEdit }) {
  const [nombre, setNombre] = useState("");
  const [empresa, setEmpresa] = useState("");
  const [correo, setCorreo] = useState("");
  const [telefono, setTelefono] = useState("");
  const [direccion, setDireccion] = useState("");
  const [projNombre, setProjNombre] = useState("");
  const [projValor, setProjValor] = useState("");
  const [projEtapa, setProjEtapa] = useState("contacto inicial");

  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    if (editClient) {
      setNombre(editClient.nombre || "");
      setEmpresa(editClient.empresa || "");
      setCorreo(editClient.correo || "");
      setTelefono(editClient.telefono || "");
      setDireccion(editClient.direccion || "");
    
    } else {
      setNombre(""); setEmpresa(""); setCorreo(""); setTelefono(""); setDireccion("");
      setProjNombre(""); setProjValor(""); setProjEtapa("contacto inicial");
    }
  }, [editClient]);

  const validarCorreo = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const esDuplicado = (email) => {
    return clientes.some(c => c.correo?.toLowerCase() === email.toLowerCase() && c.id !== editClient?.id);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Validaciones
    if (!nombre.trim() || !empresa.trim() || !correo.trim() || !direccion.trim()) {
      setMensaje("Por favor complete todos los campos obligatorios (nombre, empresa, correo, dirección).");
      return;
    }
    if (!validarCorreo(correo)) {
      setMensaje("Correo electrónico inválido.");
      return;
    }
    if (esDuplicado(correo)) {
      setMensaje("Ya existe un cliente con ese correo.");
      return;
    }

    // construimos el objeto cliente (sin id: parent lo generará o usará el existente)
    const clientePayload = {
      nombre: nombre.trim(),
      empresa: empresa.trim(),
      correo: correo.trim(),
      telefono: telefono.trim(),
      direccion: direccion.trim()
    };

    // creamos proyecto opcional solo si se escribio nombre de proyecto
    let proyectoPayload = null;
    if (projNombre.trim()) {
      proyectoPayload = {
        nombre: projNombre.trim(),
        valor: projValor ? Number(projValor) : 0,
        etapa: projEtapa
      };
    }

    onSave(clientePayload, proyectoPayload);
    setMensaje(editClient ? "Cliente actualizado." : "Cliente registrado.");

    // limpiar formulario
    if (!editClient) {
      setNombre(""); setEmpresa(""); setCorreo(""); setTelefono(""); setDireccion("");
      setProjNombre(""); setProjValor(""); setProjEtapa("contacto inicial");
    }
    // limpiar mensaje
    setTimeout(() => setMensaje(""), 3000);
  };

  return (
    <div className="card">
      {mensaje && <div style={{padding:8, marginBottom:12, borderRadius:6, backgroundColor: mensaje.includes("registrado") || mensaje.includes("actualizado") ? "#e6ffed" : "#ffecec", color: mensaje.includes("registrado") || mensaje.includes("actualizado") ? "green" : "crimson"}}>{mensaje}</div>}
      <form onSubmit={handleSubmit}>
        <h3>{editClient ? "Editar Cliente" : "Registrar Cliente"}</h3>

        <label>Nombre *</label>
        <input value={nombre} onChange={e => setNombre(e.target.value)} />

        <label>Empresa *</label>
        <input value={empresa} onChange={e => setEmpresa(e.target.value)} />

        <label>Correo *</label>
        <input type="email" value={correo} onChange={e => setCorreo(e.target.value)} />

        <label>Teléfono</label>
        <input value={telefono} onChange={e => setTelefono(e.target.value)} />

        <label>Dirección *</label>
        <input value={direccion} onChange={e => setDireccion(e.target.value)} />

        <hr style={{margin:"12px 0"}} />

        <h4>Información de proyecto (opcional)</h4><br></br>

        <label>Nombre del proyecto</label>
        <input value={projNombre} onChange={e => setProjNombre(e.target.value)} />

        <label>Valor estimado</label>
        <input type="number" value={projValor} onChange={e => setProjValor(e.target.value)} />

        <label>Etapa</label><br></br>
        <select value={projEtapa} onChange={e => setProjEtapa(e.target.value)}>
          <option value="contacto inicial">Contacto inicial</option>
          <option value="propuesta enviada">Propuesta enviada</option>
          <option value="negociación">Negociación</option>
          <option value="estado positivo">Estado positivo</option>
          <option value="estado negativo">Estado negativo</option>
        </select>

        <div style={{marginTop:12}}>
          <button className="btn" type="submit">{editClient ? "Actualizar Cliente" : "Registrar Cliente"}</button>
          {editClient && <button type="button" style={{marginLeft:10}} className="btn" onClick={onCancelEdit}>Cancelar</button>}
        </div>
      </form>
    </div>
  );
}