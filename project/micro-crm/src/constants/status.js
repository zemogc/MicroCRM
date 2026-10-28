import { Circle, Play, Clock, Eye, CheckCircle, X, Sparkles, BadgeCheck, PauseCircle } from "lucide-react";

// Estados de tarea (deben coincidir con TASK_STATUSES del backend)
export const TASK_STATUS = {
  pending: { label: "Por hacer", color: "#6b7280", icon: Circle },
  in_progress: { label: "En desarrollo", color: "#3b82f6", icon: Play },
  overdue: { label: "Atrasado", color: "#f59e0b", icon: Clock },
  in_review: { label: "En revisión", color: "#8b5cf6", icon: Eye },
  completed: { label: "Hecho", color: "#22c55e", icon: CheckCircle },
  cancelled: { label: "Cancelado", color: "#ef4444", icon: X },
};

// Estados de cliente (deben coincidir con CLIENT_STATUSES del backend)
export const CLIENT_STATUS = {
  lead: { label: "Prospecto", color: "#f59e0b", icon: Sparkles },
  active: { label: "Activo", color: "#22c55e", icon: BadgeCheck },
  inactive: { label: "Inactivo", color: "#6b7280", icon: PauseCircle },
};
