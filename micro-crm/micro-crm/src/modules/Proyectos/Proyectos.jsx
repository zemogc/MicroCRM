import { useState, useEffect } from "react";
import ProyectoForm from "./ProyectoForm";
import ProyectoList from "./ProyectoList";

function Proyectos({ clientes = [] }) {
  const [proyectos, setProyectos] = useState([]);

  // Cargar proyectos al iniciar
  useEffect(() => {
    try {
      const proyectosGuardados = localStorage.getItem("proyectos");
      if (proyectosGuardados) {
        setProyectos(JSON.parse(proyectosGuardados));
      }
    } catch (error) {
      console.error("Error al cargar proyectos:", error);
    }
  }, []);

  // Guardar cada vez que se actualiza el proyectos
  useEffect(() => {
    localStorage.setItem("proyectos", JSON.stringify(proyectos));
  }, [proyectos]);

  // Agregar proyecto nuevo
  const handleAddProyecto = (nuevoProyecto) => {
    const proyectoConID = {
      ...nuevoProyecto,
      id: Date.now(),
      observaciones: [],
    };
    setProyectos([...proyectos, proyectoConID]);
  };

  // Agregar observación
  const handleAddObservacion = (idProyecto, nuevaObs) => {
    setProyectos((prev) =>
      prev.map((p) =>
        p.id === idProyecto
          ? { ...p, observaciones: [...(p.observaciones || []), nuevaObs] }
          : p
      )
    );
  };

  return (
    <div className="modulo">
      <ProyectoForm onAddProyecto={handleAddProyecto} clientes={clientes} />
      <ProyectoList proyectos={proyectos} onAddObservacion={handleAddObservacion} />
    </div>
  );
}

export default Proyectos;