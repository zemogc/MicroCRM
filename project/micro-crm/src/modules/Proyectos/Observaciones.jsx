import { useState } from "react";

function Observaciones({ proyecto, onAddObservacion }) {
  const [texto, setTexto] = useState("");

  const handleAdd = () => {
    if (!texto.trim()) return;
    const nuevaObs = {
      id: Date.now(),
      texto,
      fecha: new Date().toLocaleDateString(),
    };
    onAddObservacion(proyecto.id, nuevaObs);
    setTexto("");
  };

  return (
    <div className="observaciones">
      <h4>Observaciones de {proyecto.nombre}</h4>
      <ul>
        {proyecto.observaciones.length > 0 ? (
          proyecto.observaciones.map((obs) => (
            <li key={obs.id}>
              <strong>{obs.fecha}:</strong> {obs.texto}
            </li>
          ))
        ) : (
          <li>No hay observaciones registradas.</li>
        )}
      </ul>
      <div className="add-observacion">
        <textarea
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Añadir nueva observación..."
        />
        <button onClick={handleAdd}>Agregar</button>
      </div>
    </div>
  );
}

export default Observaciones;