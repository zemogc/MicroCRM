import { useState, useEffect } from "react";
import ClienteForm from "./ClienteForm";
import ClienteList from "./ClienteList";

const genId = () => `${Date.now().toString(36)}-${Math.random().toString(36).slice(2,9)}`;

export default function Clientes() {
  const [clientes, setClientes] = useState([]);
  const [proyectos, setProyectos] = useState([]);
  const [editClient, setEditClient] = useState(null);

  // Cargar y migrar
  useEffect(() => {
    const rawClients = JSON.parse(localStorage.getItem("clientes")) || [];
    const migratedClients = rawClients.map(c => c.id ? c : {...c, id: genId()});
    setClientes(migratedClients);
    if (migratedClients.length && rawClients.length && !rawClients[0].id) {
      localStorage.setItem("clientes", JSON.stringify(migratedClients));
    }

    const rawProjects = JSON.parse(localStorage.getItem("proyectos")) || [];
    const migratedProjects = rawProjects.map(p => p.id ? p : {...p, id: genId(), clientId: p.clientId || null});
    setProyectos(migratedProjects);
    if (migratedProjects.length && rawProjects.length && !rawProjects[0].id) {
      localStorage.setItem("proyectos", JSON.stringify(migratedProjects));
    }
  }, []);

  // Persistir en localStorage cuando cambian
  useEffect(() => {
    localStorage.setItem("clientes", JSON.stringify(clientes));
  }, [clientes]);

  useEffect(() => {
    localStorage.setItem("proyectos", JSON.stringify(proyectos));
  }, [proyectos]);

  // Guardar cliente
  const handleSave = (clientePayload, proyectoPayload) => {
    if (editClient) {
      const updatedClients = clientes.map(c => c.id === editClient.id ? { ...clientePayload, id: editClient.id } : c);
      setClientes(updatedClients);
      setEditClient(null);
      return;
    }

    // crear cliente
    const newClientId = genId();
    const newClient = { ...clientePayload, id: newClientId };
    setClientes(prev => [...prev, newClient]);

    // si hay proyecto opcional asociarlo
    if (proyectoPayload && proyectoPayload.nombre) {
      const newProj = {
        ...proyectoPayload,
        id: genId(),
        clientId: newClientId,
        createdAt: new Date().toISOString()
      };
      setProyectos(prev => [...prev, newProj]);
    }
  };

  const handleEdit = (clientId) => {
    const c = clientes.find(x => x.id === clientId);
    if (c) setEditClient(c);
  };

  const handleDelete = (clientId) => {
    if (!confirm("¿Eliminar cliente? Esto también eliminará los proyectos asociados.")) return;
    setClientes(prev => prev.filter(c => c.id !== clientId));
    // elimina proyectos conectados
    setProyectos(prev => prev.filter(p => p.clientId !== clientId));
  };

  return (
    <div>
      <ClienteForm
        clientes={clientes}
        editClient={editClient}
        onSave={handleSave}
        onCancelEdit={() => setEditClient(null)}
      />
      <ClienteList
        clientes={clientes}
        onEdit={(indexOrId) => {
          handleEdit(indexOrId);
        }}
        onDelete={(id) => handleDelete(id)}
      />
    </div>
  );
}