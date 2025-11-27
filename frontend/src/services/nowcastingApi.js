import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    // Get token from axios defaults (set by AuthContext)
    const token = axios.defaults.headers.common['Authorization'];
    if (token) {
      config.headers.Authorization = token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const getNowcasts = async (forecastTime) => {
  try {
    const response = await apiClient.get(`/nowcast/${forecastTime}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching nowcasts:", error);
    throw error;
  }
};

export const getWarnings = async () => {
  try {
    const response = await apiClient.get('/warnings/active');
    return response.data;
  } catch (error) {
    console.error("Error fetching warnings:", error);
    throw error;
  }
};

// Training API functions
export const uploadRadarData = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/training/upload-radar-data', formData);
    return response.data;
  } catch (error) {
    console.error("Error uploading radar data:", error);
    throw error;
  }
};

export const uploadLabels = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/training/upload-labels', formData);
    return response.data;
  } catch (error) {
    console.error("Error uploading labels:", error);
    throw error;
  }
};

export const startTraining = async () => {
  try {
    const response = await apiClient.post('/training/start-training');
    return response.data;
  } catch (error) {
    console.error("Error starting training:", error);
    throw error;
  }
};

export const getTrainingStatus = async () => {
  try {
    const response = await apiClient.get('/training/training-status');
    return response.data;
  } catch (error) {
    console.error("Error fetching training status:", error);
    throw error;
  }
};

export const getTrainingDataStatus = async () => {
  try {
    const response = await apiClient.get('/training/training-data-status');
    return response.data;
  } catch (error) {
    console.error("Error fetching training data status:", error);
    throw error;
  }
};

export const getUploadedDatasets = async () => {
  try {
    const response = await apiClient.get('/training/datasets');
    return response.data;
  } catch (error) {
    console.error("Error fetching uploaded datasets:", error);
    throw error;
  }
};

export const deleteDataset = async (datasetId) => {
  try {
    const response = await apiClient.delete(`/training/delete-dataset/${datasetId}`);
    return response.data;
  } catch (error) {
    console.error("Error deleting dataset:", error);
    throw error;
  }
};

export const startMonitoring = async (adminEmail, adminPhone) => {
  try {
    const response = await apiClient.post('/training/start-monitoring', {
      admin_email: adminEmail,
      admin_phone: adminPhone
    });
    return response.data;
  } catch (error) {
    console.error("Error starting monitoring:", error);
    throw error;
  }
};