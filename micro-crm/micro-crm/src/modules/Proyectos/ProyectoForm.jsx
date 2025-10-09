import { useState } from "react";

function ProyectoForm({ onAddProyecto, clientes }) {
  const [nombre, setNombre] = useState("");
  const [valor, setValor] = useState("");
  const [etapa, setEtapa] = useState("contacto inicial");
  const [cliente, setCliente] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!nombre || !cliente) {
      alert("El nombre del proyecto y el cliente son obligatorios");
      return;
    }

    const nuevoProyecto = {
      id: Date.now(),
      nombre,
      valor,
      etapa,
      cliente,
      observaciones: [], 
    };

    onAddProyecto(nuevoProyecto);
    setNombre("");
    setValor("");
    setEtapa("contacto inicial");
    setCliente("");
  };

  return (
    <form className="form" onSubmit={handleSubmit}>
      <h2>Registrar Proyecto</h2>

      <label>Nombre del proyecto:</label>
      <input type="text" value={nombre} onChange={(e) => setNombre(e.target.value)} required />

      <label>Valor estimado:</label>
      <input type="number" value={valor} onChange={(e) => setValor(e.target.value)} />

      <label>Etapa:</label>
      <select value={etapa} onChange={(e) => setEtapa(e.target.value)}>
        <option value="contacto inicial">Contacto inicial</option>
        <option value="propuesta enviada">Propuesta enviada</option>
        <option value="negociación">Negociación</option>
        <option value="estado positivo">Estado positivo</option>
        <option value="estado negativo">Estado negativo</option>
      </select>

      <label>Cliente asociado:</label>
      <select value={cliente} onChange={(e) => setCliente(e.target.value)} required>
        <option value="">Seleccione un cliente</option>
        {clientes.map((c) => (
          <option key={c.id} value={c.nombre}>
            {c.nombre} - {c.empresa}
          </option>
        ))}
      </select>

      <button type="submit">Guardar Proyecto</button>
    </form>
  );
}

export default ProyectoForm;