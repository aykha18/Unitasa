import axios from 'axios';

// API Configuration - Use environment variable or detect environment
const getApiBaseUrl = () => {
  // If REACT_APP_API_URL is set and it's not the placeholder, use it
  if (process.env.REACT_APP_API_URL && 
      !process.env.REACT_APP_API_URL.includes('your-backend-service.railway.app')) {
    return process.env.REACT_APP_API_URL;
  }
  
  // If we're in production (Railway), use relative URLs for same-service deployment
  if (process.env.NODE_ENV === 'production' || window.location.hostname !== 'localhost') {
    // Backend and frontend are on the same Railway service
    return ''; // Relative URLs will use the same domain
  }
  
  // Development default
  return 'http://localhost:8001';
};

const API_BASE_URL = getApiBaseUrl();
console.log('API Base URL:', API_BASE_URL);
console.log('Environment:', process.env.NODE_ENV);
console.log('Hostname:', window.location.hostname);
console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
