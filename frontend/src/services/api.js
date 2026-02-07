/**
 * API Service for Emergency Triage System
 * Handles all HTTP requests to the backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Triage API
 */
export const triageAPI = {
  /**
   * Process an emergency message
   * @param {Object} message - Emergency message data
   * @returns {Promise} Triage response with extracted info and matches
   */
  processMessage: async (message) => {
    const response = await api.post('/triage', message);
    return response.data;
  },

  /**
   * Confirm dispatcher decision
   * @param {Object} confirmation - Confirmation data
   * @returns {Promise} Confirmation response
   */
  confirmDispatch: async (confirmation) => {
    const response = await api.post('/confirm', confirmation);
    return response.data;
  },

  /**
   * Get list of emergency requests
   * @param {Object} params - Query parameters
   * @returns {Promise} Array of emergency requests
   */
  getRequests: async (params = {}) => {
    const response = await api.get('/requests', { params });
    return response.data;
  },

  /**
   * Get specific request details
   * @param {string} requestId - Request ID
   * @returns {Promise} Emergency request details
   */
  getRequest: async (requestId) => {
    const response = await api.get(`/requests/${requestId}`);
    return response.data;
  },
};

/**
 * Resources API
 */
export const resourcesAPI = {
  /**
   * Get list of resources
   * @param {Object} params - Query parameters
   * @returns {Promise} Array of resources
   */
  getResources: async (params = {}) => {
    const response = await api.get('/resources', { params });
    return response.data;
  },

  /**
   * Create new resource
   * @param {Object} resource - Resource data
   * @returns {Promise} Created resource
   */
  createResource: async (resource) => {
    const response = await api.post('/resources', resource);
    return response.data;
  },

  /**
   * Update resource
   * @param {string} resourceId - Resource ID
   * @param {Object} updates - Updates to apply
   * @returns {Promise} Update confirmation
   */
  updateResource: async (resourceId, updates) => {
    const response = await api.put(`/resources/${resourceId}`, updates);
    return response.data;
  },
};

/**
 * Dashboard API
 */
export const dashboardAPI = {
  /**
   * Get dashboard statistics
   * @returns {Promise} Dashboard stats
   */
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
};

/**
 * Health Check
 */
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
