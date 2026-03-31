import { updateTaskStatus, deleteTask } from "../api/client";

const STATUS_NEXT = {
  todo: ["in_progress"],
  in_progress: ["todo", "done"],
  done: ["in_progress"],
};

const PRIORITY_COLOR = {
  low: "#4caf50",
  medium: "#ff9800",
  high: "#f44336",
};

const STATUS_LABEL = {
  todo: "To Do",
  in_progress: "In Progress",
  done: "Done",
};

export default function TaskCard({ task, onUpdated, onDeleted }) {
  const nextStatuses = STATUS_NEXT[task.status] || [];

  const transition = async (status) => {
    try {
      const resp = await updateTaskStatus(task.id, status);
      onUpdated(resp.data);
    } catch (err) {
      alert(err.response?.data?.errors?.status?.[0] || "Failed to update status");
    }
  };

  const remove = async () => {
    if (!confirm(`Delete "${task.title}"?`)) return;
    await deleteTask(task.id);
    onDeleted(task.id);
  };

  return (
    <div style={styles.card}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <span style={{ ...styles.badge, background: PRIORITY_COLOR[task.priority] }}>
            {task.priority}
          </span>
          <span style={styles.statusBadge}>{STATUS_LABEL[task.status]}</span>
        </div>
        <button onClick={remove} style={styles.deleteBtn} title="Delete">✕</button>
      </div>

      <p style={styles.title}>{task.title}</p>
      {task.description && <p style={styles.desc}>{task.description}</p>}
      {task.due_date && (
        <p style={styles.meta}>Due: {task.due_date}</p>
      )}

      {nextStatuses.length > 0 && (
        <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
          {nextStatuses.map((s) => (
            <button key={s} onClick={() => transition(s)} style={styles.transBtn}>
              → {STATUS_LABEL[s]}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  card: {
    background: "#fff",
    borderRadius: 8,
    padding: 14,
    boxShadow: "0 1px 3px rgba(0,0,0,.08)",
    marginBottom: 10,
  },
  badge: {
    display: "inline-block",
    color: "#fff",
    fontSize: 11,
    fontWeight: 600,
    padding: "2px 8px",
    borderRadius: 20,
    textTransform: "uppercase",
    marginRight: 6,
  },
  statusBadge: {
    display: "inline-block",
    background: "#eee",
    color: "#555",
    fontSize: 11,
    fontWeight: 500,
    padding: "2px 8px",
    borderRadius: 20,
  },
  title: { marginTop: 8, fontWeight: 600, fontSize: 15 },
  desc: { marginTop: 4, fontSize: 13, color: "#666" },
  meta: { marginTop: 4, fontSize: 12, color: "#888" },
  deleteBtn: {
    background: "transparent",
    color: "#aaa",
    padding: "2px 6px",
    fontSize: 13,
  },
  transBtn: {
    background: "#f0f4ff",
    color: "#4f6ef7",
    fontSize: 12,
    padding: "4px 10px",
  },
};
