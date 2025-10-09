import Observaciones from "./Observaciones";

function ProyectoList({ proyectos, onAddObservacion }) {
  return (
    <div className="list">
      <h2>Listado de Proyectos</h2>
      {proyectos.length === 0 ? (
        <p>No hay proyectos registrados.</p>
      ) : (
        proyectos.map((p) => (
          <div key={p.id} className="proyecto-card">
            <h3>{p.nombre}</h3>
            <p><strong>Cliente:</strong> {p.cliente}</p>
            <p><strong>Valor:</strong> {p.valor}</p>
            <p><strong>Etapa:</strong> {p.etapa}</p>

            <Observaciones proyecto={p} onAddObservacion={onAddObservacion} />
          </div>
        ))
      )}
    </div>
  );
}

export default ProyectoList;