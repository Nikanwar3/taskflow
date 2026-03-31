import { useEffect, useState } from "react";
import { getTasks, getProjects } from "./api/client";
import TaskForm from "./components/TaskForm";
import TaskCard from "./components/TaskCard";
import ProjectPanel from "./components/ProjectPanel";

const STATUSES = ["todo", "in_progress", "done"];
const STATUS_LABEL = { todo: "To Do", in_progress: "In Progress", done: "Done" };

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [filterStatus, setFilterStatus] = useState("");
  const [filterPriority, setFilterPriority] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      getTasks(),
      getProjects(),
    ])
      .then(([tasksResp, projectsResp]) => {
        setTasks(tasksResp.data);
        setProjects(projectsResp.data);
      })
      .catch(() => setError("Failed to load data. Is the backend running?"))
      .finally(() => setLoading(false));
  }, []);

  const fetchTasks = async () => {
    const params = {};
    if (filterStatus) params.status = filterStatus;
    if (filterPriority) params.priority = filterPriority;
    const resp = await getTasks(params);
    setTasks(resp.data);
  };

  useEffect(() => { fetchTasks(); }, [filterStatus, filterPriority]);

  const onTaskCreated = (task) => setTasks((prev) => [task, ...prev]);
  const onTaskUpdated = (task) =>
    setTasks((prev) => prev.map((t) => (t.id === task.id ? task : t)));
  const onTaskDeleted = (id) => setTasks((prev) => prev.filter((t) => t.id !== id));

  const onProjectCreated = (p) => setProjects((prev) => [...prev, p].sort((a, b) => a.name.localeCompare(b.name)));
  const onProjectDeleted = (id) => setProjects((prev) => prev.filter((p) => p.id !== id));

  if (loading) return <div style={styles.center}>Loading…</div>;
  if (error) return <div style={{ ...styles.center, color: "#d32f2f" }}>{error}</div>;

  const filtered = tasks.filter((t) => {
    if (filterStatus && t.status !== filterStatus) return false;
    if (filterPriority && t.priority !== filterPriority) return false;
    return true;
  });

  return (
    <div style={styles.root}>
      <header style={styles.header}>
        <h1 style={styles.logo}>TaskFlow</h1>
      </header>

      <div style={styles.layout}>
        <aside style={styles.sidebar}>
          <ProjectPanel
            projects={projects}
            onCreated={onProjectCreated}
            onDeleted={onProjectDeleted}
          />
          <TaskForm
            projects={projects}
            onCreated={onTaskCreated}
          />
        </aside>

        <main style={styles.main}>
          <div style={styles.filters}>
            <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} style={styles.filterSelect}>
              <option value="">All statuses</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>{STATUS_LABEL[s]}</option>
              ))}
            </select>
            <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)} style={styles.filterSelect}>
              <option value="">All priorities</option>
              {["low", "medium", "high"].map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
            <span style={styles.count}>{filtered.length} task{filtered.length !== 1 ? "s" : ""}</span>
          </div>

          {filtered.length === 0 ? (
            <p style={styles.empty}>No tasks found. Add one on the left.</p>
          ) : (
            filtered.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onUpdated={onTaskUpdated}
                onDeleted={onTaskDeleted}
              />
            ))
          )}
        </main>
      </div>
    </div>
  );
}

const styles = {
  root: { minHeight: "100vh" },
  center: { display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", fontSize: 16 },
  header: {
    background: "#4f6ef7",
    color: "#fff",
    padding: "14px 24px",
    boxShadow: "0 2px 6px rgba(0,0,0,.15)",
  },
  logo: { fontSize: 20, fontWeight: 700, letterSpacing: "-0.5px" },
  layout: { display: "flex", gap: 24, padding: 24, maxWidth: 1100, margin: "0 auto" },
  sidebar: { width: 280, flexShrink: 0 },
  main: { flex: 1 },
  filters: { display: "flex", gap: 10, alignItems: "center", marginBottom: 16 },
  filterSelect: { width: "auto", flex: "0 0 auto" },
  count: { marginLeft: "auto", fontSize: 13, color: "#888" },
  empty: { color: "#999", fontSize: 14, textAlign: "center", marginTop: 40 },
};
