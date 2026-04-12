import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

export const predict      = (data)       => api.post('/predict', data);
export const predictBatch = (data)       => api.post('/predict/batch', { applicants: data });
export const getMetrics   = ()           => api.get('/metrics');
export const getHealth    = ()           => api.get('/health');
export const getHistory   = (limit = 50) => api.get(`/history?limit=${limit}`);