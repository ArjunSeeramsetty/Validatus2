/**
 * Fixed API configuration with HTTPS
 */
const API_BASE_URL = 'https://validatus-backend-ssivkqhvhq-uc.a.run.app';

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  ENDPOINTS: {
    HEALTH: '/health',
    TOPICS: '/api/v3/topics',
    CREATE_TOPIC: '/api/v3/topics/create',
    TOPIC_DETAIL: '/api/v3/topics',
  },
  TIMEOUT: 30000,
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
} as const;

export default API_CONFIG;
