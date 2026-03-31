import axios from "axios";

const api = axios.create({ baseURL: "/" });

export const getTasks = (params) => api.get("/tasks/", { params });
export const createTask = (data) => api.post("/tasks/", data);
export const updateTask = (id, data) => api.put(`/tasks/${id}`, data);
export const updateTaskStatus = (id, status) =>
  api.patch(`/tasks/${id}/status`, { status });
export const deleteTask = (id) => api.delete(`/tasks/${id}`);

export const getProjects = () => api.get("/projects/");
export const createProject = (data) => api.post("/projects/", data);
export const deleteProject = (id) => api.delete(`/projects/${id}`);
