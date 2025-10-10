import { useState, useEffect } from "react";
import "./ClienteForm.css";

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
      setProjNombre("");
      setProjValor("");
      setProjEtapa("contacto inicial");
    } else {
      setNombre(""); setEmpresa(""); setCorreo(""); setTelefono(""); setDireccion("");
      setProjNombre(""); setProjValor(""); setProjEtapa("contacto inicial");
    }
  }, [editClient]);

  const validarCorreo = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const esDuplicado = (email) =>
    clientes.some(c => c.correo?.toLowerCase() === email.toLowerCase() && c.id !== editClient?.id);

  const handleSubmit = (e) => {
    e.preventDefault();
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

    const clientePayload = {
      nombre: nombre.trim(),
      empresa: empresa.trim(),
      correo: correo.trim(),
      telefono: telefono.trim(),
      direccion: direccion.trim()
    };

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

    if (!editClient) {
      setNombre(""); setEmpresa(""); setCorreo(""); setTelefono(""); setDireccion("");
      setProjNombre(""); setProjValor(""); setProjEtapa("contacto inicial");
    }
    setTimeout(() => setMensaje(""), 3000);
  };

  return (
    <section className="cliente-form">
      {mensaje && (
        <div
          className={`cliente-form__alert ${
            mensaje.includes("registrado") || mensaje.includes("actualizado")
              ? "cliente-form__alert--ok"
              : "cliente-form__alert--err"
          }`}
          role="status"
        >
          {mensaje}
        </div>
      )}

      <form onSubmit={handleSubmit} className="cliente-form__form">
        <h3 className="cliente-form__title">
          {editClient ? "Editar Cliente" : "Registrar Cliente"}
        </h3>

        <div className="cliente-form__grid">
          <div className="field">
            <label htmlFor="cf-nombre">Nombre *</label>
            <input id="cf-nombre" value={nombre} onChange={e => setNombre(e.target.value)} />
          </div>

          <div className="field">
            <label htmlFor="cf-empresa">Empresa *</label>
            <input id="cf-empresa" value={empresa} onChange={e => setEmpresa(e.target.value)} />
          </div>

          <div className="field">
            <label htmlFor="cf-correo">Correo *</label>
            <input id="cf-correo" type="email" value={correo} onChange={e => setCorreo(e.target.value)} />
          </div>

          <div className="field">
            <label htmlFor="cf-telefono">Teléfono</label>
            <input id="cf-telefono" value={telefono} onChange={e => setTelefono(e.target.value)} />
          </div>

          <div className="field field--full">
            <label htmlFor="cf-direccion">Dirección *</label>
            <input id="cf-direccion" value={direccion} onChange={e => setDireccion(e.target.value)} />
          </div>
        </div>

        <fieldset className="cliente-form__fieldset">
          <legend>Información de proyecto (opcional)</legend>

          <div className="cliente-form__grid">
            <div className="field">
              <label htmlFor="cf-proj-nombre">Nombre del proyecto</label>
              <input id="cf-proj-nombre" value={projNombre} onChange={e => setProjNombre(e.target.value)} />
            </div>

            <div className="field">
              <label htmlFor="cf-proj-valor">Valor estimado</label>
              <input id="cf-proj-valor" type="number" value={projValor} onChange={e => setProjValor(e.target.value)} />
            </div>

            <div className="field field--full">
              <label htmlFor="cf-proj-etapa">Etapa</label>
              <select id="cf-proj-etapa" value={projEtapa} onChange={e => setProjEtapa(e.target.value)}>
                <option value="contacto inicial">Contacto inicial</option>
                <option value="propuesta enviada">Propuesta enviada</option>
                <option value="negociación">Negociación</option>
                <option value="estado positivo">Estado positivo</option>
                <option value="estado negativo">Estado negativo</option>
              </select>
            </div>
          </div>
        </fieldset>

        <div className="cliente-form__actions">
          <button className="btn" type="submit">
            {editClient ? "Actualizar Cliente" : "Registrar Cliente"}
          </button>

          {editClient && (
            <button type="button" className="btn btn--ghost" onClick={onCancelEdit}>
              Cancelar
            </button>
          )}
        </div>
      </form>
    </section>
  );
}
