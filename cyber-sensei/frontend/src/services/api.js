import axios from 'axios';

// Determine the API URL based on environment
export const getApiUrl = () => {
  // In development Vite will proxy /api to the backend
  // In production, the backend runs on the same host or you set VITE_API_URL
  const apiUrl = import.meta.env.VITE_API_URL;
  if (apiUrl) {
    return apiUrl;
  }
  // Default: use /api for local development (proxied) or full URL for production
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return '/api'; // Uses proxy in Vite dev
  }
  return `http://${window.location.hostname}:8000/api`; // Production
};

const api = axios.create({
  baseURL: getApiUrl(),
  timeout: 30000,
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only log in development
    if (import.meta.env.DEV) {
      console.error('API Error:', error);
    }
    
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message || 'Unknown error';
      
      if (status === 401) {
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        return Promise.reject(new Error('Session expired. Please login again.'));
      } else if (status === 403) {
        return Promise.reject(new Error('Access forbidden.'));
      } else if (status === 404) {
        return Promise.reject(new Error(detail || 'Resource not found'));
      } else if (status === 400) {
        return Promise.reject(new Error(detail || 'Invalid request'));
      } else if (status === 413) {
        return Promise.reject(new Error('File too large. Please upload a smaller file.'));
      } else if (status === 429) {
        return Promise.reject(new Error('Too many requests. Please try again later.'));
      } else if (status >= 500) {
        return Promise.reject(new Error(detail || 'Server error. Please try again later.'));
      }
      return Promise.reject(new Error(detail));
    } else if (error.request) {
      // Request made but no response
      return Promise.reject(new Error('Network error. Please check your connection.'));
    } else {
      // Error in request setup
      return Promise.reject(new Error(error.message || 'An unexpected error occurred'));
    }
  }
);

// Attach auth token to requests when present
api.interceptors.request.use((config) => {
  try {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (err) {
    // localStorage may not be available in some environments
  }
  return config;
});

// --- User API ---
export const getUserDashboard = (username) => 
  api.get(`/users/${username}/dashboard`);

export const createUser = (userData) => 
  api.post(`/users`, userData);

export const getUser = (username) => 
  api.get(`/users/${username}`);

// --- Learning API ---
export const getNextLearningStep = (username) => 
  api.get(`/learning/${username}/next-step`);

export const submitQuiz = (username, submission) => 
  api.post(`/learning/${username}/submit-quiz`, submission);

export const getTopicContent = (topicId) => 
  api.get(`/learning/topic/${topicId}`);

export const getTopicQuiz = (topicId) =>
  api.get(`/learning/topic/${topicId}/quiz`);

export const markTopicAsComplete = (username, topicId) => 
  api.post(`/learning/${username}/topic/${topicId}/complete`);

// --- Knowledge Base API ---
export const addDocument = (payload) => 
  api.post(`/knowledge-base/add-document`, payload);

const uploadClient = () =>
  axios.create({
    baseURL: getApiUrl(),
    timeout: 300000,
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const uploadDocumentFile = (formData) =>
  uploadClient().post(`/knowledge-base/upload-document`, formData);

export const uploadVideo = (formData) =>
  uploadClient().post(`/knowledge-base/upload-video`, formData);

export const getKnowledgeBaseItems = () => 
  api.get(`/knowledge-base`);

export const deleteKnowledgeBaseItem = (itemId) => 
  api.delete(`/knowledge-base/${itemId}`);

// --- Lab API ---
export const getLabInstructions = (labId) => 
  api.get(`/labs/${labId}/instructions`);

export const executeLabCommand = (labId, command) => 
  api.post(`/labs/${labId}/execute`, { command });

export const getLabModules = () => 
  api.get(`/labs/modules`);

export const getLabTopics = (moduleId) => 
  api.get(`/labs/modules/${moduleId}/topics`);

// --- Health Check ---
export const healthCheck = () => 
  api.get(`/health`);

// Export axios instance for direct calls (e.g., login)
export { api };