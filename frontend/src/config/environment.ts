/**
 * Environment Configuration
 * Centralized configuration for different deployment environments
 */

export interface EnvironmentConfig {
  apiBaseUrl: string;
  wsBaseUrl: string;
  environment: 'development' | 'production';
  isProduction: boolean;
  isDevelopment: boolean;
  googleClientId: string;
}

const getEnvironmentConfig = (): EnvironmentConfig => {
  const isProduction = process.env.NODE_ENV === 'production' || window.location.hostname !== 'localhost';
  const isDevelopment = !isProduction;

  let apiBaseUrl: string;
  let wsBaseUrl: string;

  if (isProduction) {
    // Production: Use same domain (Railway deployment)
    apiBaseUrl = window.location.origin;
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    wsBaseUrl = `${wsProtocol}//${window.location.host}`;
  } else {
    // Development: Use localhost backend
    apiBaseUrl = 'http://localhost:8001';
    wsBaseUrl = 'ws://localhost:8001';
  }

  return {
    apiBaseUrl,
    wsBaseUrl,
    environment: isProduction ? 'production' : 'development',
    isProduction,
    isDevelopment,
    googleClientId: process.env.REACT_APP_GOOGLE_CLIENT_ID || process.env.GOOGLE_CLIENT_ID || ''
  };
};

export const config = getEnvironmentConfig();

// Log configuration for debugging
console.log('🔧 Environment Configuration:', {
  environment: config.environment,
  apiBaseUrl: config.apiBaseUrl,
  wsBaseUrl: config.wsBaseUrl,
  hostname: window.location.hostname,
  protocol: window.location.protocol
});

export default config;