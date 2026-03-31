import { useState } from "react";
import { createTask } from "../api/client";

const PRIORITIES = ["low", "medium", "high"];

export default function TaskForm({ projects, onCreated }) {
  const [form, setForm] = useState({
    title: "",
    description: "",
    priority: "medium",
    due_date: "",
    project_id: "",
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const set = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setErrors({});
    setSubmitting(true);
    const payload = {
      title: form.title,
      priority: form.priority,
      description: form.description || undefined,
      due_date: form.due_date || undefined,
      project_id: form.project_id ? Number(form.project_id) : undefined,
    };
    try {
      const resp = await createTask(payload);
      onCreated(resp.data);
      setForm({ title: "", description: "", priority: "medium", due_date: "", project_id: "" });
    } catch (err) {
      if (err.response?.status === 422) {
        setErrors(err.response.data.errors || {});
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} style={styles.form}>
      <h3 style={{ marginBottom: 12, fontSize: 15, fontWeight: 600 }}>New Task</h3>

      <div style={styles.field}>
        <label>Title *</label>
        <input value={form.title} onChange={set("title")} placeholder="Task title" />
        {errors.title && <p className="error-text">{errors.title[0]}</p>}
      </div>

      <div style={styles.field}>
        <label>Description</label>
        <textarea value={form.description} onChange={set("description")} rows={2} />
      </div>

      <div style={{ display: "flex", gap: 10 }}>
        <div style={{ ...styles.field, flex: 1 }}>
          <label>Priority *</label>
          <select value={form.priority} onChange={set("priority")}>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        <div style={{ ...styles.field, flex: 1 }}>
          <label>Due Date</label>
          <input type="date" value={form.due_date} onChange={set("due_date")} />
          {errors.due_date && <p className="error-text">{errors.due_date[0]}</p>}
        </div>
      </div>

      <div style={styles.field}>
        <label>Project</label>
        <select value={form.project_id} onChange={set("project_id")}>
          <option value="">No project</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      <button type="submit" disabled={submitting} style={styles.btn}>
        {submitting ? "Adding…" : "Add Task"}
      </button>
    </form>
  );
}

const styles = {
  form: {
    background: "#fff",
    borderRadius: 10,
    padding: 18,
    boxShadow: "0 1px 4px rgba(0,0,0,.08)",
    marginBottom: 20,
  },
  field: { marginBottom: 10 },
  btn: {
    background: "#4f6ef7",
    color: "#fff",
    padding: "8px 18px",
    marginTop: 4,
    fontSize: 14,
  },
};
