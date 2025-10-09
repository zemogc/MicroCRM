export default function ClienteList({ clientes = [], onEdit, onDelete }) {
  if (!clientes.length) return <p>No se han registrado clientes.</p>;

  return (
    <div style={{marginTop:16}} className="card">
      <h3>Clientes Registrados</h3>
      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Empresa</th>
            <th>Correo</th>
            <th>Teléfono</th>
            <th>Dirección</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {clientes.map(c => (
            <tr key={c.id}>
              <td>{c.nombre}</td>
              <td>{c.empresa}</td>
              <td>{c.correo}</td>
              <td>{c.telefono}</td>
              <td>{c.direccion}</td>
              <td>
                <button className="btn" style={{backgroundColor:"#ffc107", marginRight:8}} onClick={() => onEdit(c.id)}>Editar</button>
                <button className="btn" style={{backgroundColor:"#dc3545"}} onClick={() => onDelete(c.id)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}