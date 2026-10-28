import { TASK_STATUS } from "../constants/status";
import "./StatusBadge.css";

export default function StatusBadge({ status, catalog = TASK_STATUS, size = 14 }) {
  const config = catalog[status] || Object.values(catalog)[0];
  const Icon = config.icon;
  return (
    <span className="status-badge" style={{ backgroundColor: `${config.color}20`, color: config.color }}>
      <Icon size={size} strokeWidth={2.5} />
      {config.label}
    </span>
  );
}
