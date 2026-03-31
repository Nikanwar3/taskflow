import { useState } from "react";
import { createProject, deleteProject } from "../api/client";

export default function ProjectPanel({ projects, onCreated, onDeleted }) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const resp = await createProject({ name });
      onCreated(resp.data);
      setName("");
    } catch (err) {
      const msg = err.response?.data?.errors?.name?.[0] || "Failed to create project";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const remove = async (project) => {
    if (!confirm(`Delete project "${project.name}"? Tasks will be unassigned.`)) return;
    await deleteProject(project.id);
    onDeleted(project.id);
  };

  return (
    <div style={styles.panel}>
      <h3 style={styles.heading}>Projects</h3>

      <form onSubmit={submit} style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Project name"
          style={{ flex: 1 }}
        />
        <button type="submit" disabled={submitting} style={styles.addBtn}>
          Add
        </button>
      </form>
      {error && <p className="error-text" style={{ marginBottom: 8 }}>{error}</p>}

      {projects.length === 0 ? (
        <p style={styles.empty}>No projects yet.</p>
      ) : (
        projects.map((p) => (
          <div key={p.id} style={styles.projectRow}>
            <span style={styles.dot} />
            <span style={{ flex: 1, fontSize: 14 }}>{p.name}</span>
            <button onClick={() => remove(p)} style={styles.deleteBtn}>✕</button>
          </div>
        ))
      )}
    </div>
  );
}

const styles = {
  panel: {
    background: "#fff",
    borderRadius: 10,
    padding: 18,
    boxShadow: "0 1px 4px rgba(0,0,0,.08)",
    marginBottom: 20,
  },
  heading: { fontSize: 15, fontWeight: 600, marginBottom: 12 },
  addBtn: { background: "#4f6ef7", color: "#fff", whiteSpace: "nowrap" },
  projectRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "6px 0",
    borderBottom: "1px solid #f0f0f0",
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: "#4f6ef7",
    flexShrink: 0,
  },
  deleteBtn: {
    background: "transparent",
    color: "#bbb",
    padding: "2px 6px",
    fontSize: 13,
  },
  empty: { fontSize: 13, color: "#999" },
};
