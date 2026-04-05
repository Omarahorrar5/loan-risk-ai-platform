import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})

export const predict      = (data)  => api.post('/predict', data);
export const predictBatch = (data)  => api.post('/predict/batch', { applicants: data });
export const getMetrics   = ()      => api.get('/metrics');
export const getHealth    = ()      => api.get('/health');