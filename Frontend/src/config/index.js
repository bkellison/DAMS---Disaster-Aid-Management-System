/**
 * Application configuration
 * This file centralizes all configuration variables from environment files
 */

// API configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000',
  TIMEOUT: 30000 // 30 seconds
};

// Authentication configuration
export const AUTH_CONFIG = {
  COOKIE_NAME: import.meta.env.VITE_AUTH_COOKIE_NAME || 'authUser',
  COOKIE_EXPIRY: parseInt(import.meta.env.VITE_AUTH_COOKIE_EXPIRY || '1', 10), // in hours
  COOKIE_SECURE: window.location.protocol === 'https:',
  COOKIE_SAME_SITE: 'Strict'
};

// Application settings
export const APP_CONFIG = {
  DEBUG_MODE: import.meta.env.VITE_DEBUG_MODE === 'true',
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  ENABLE_MOCKS: import.meta.env.VITE_ENABLE_MOCKS === 'true'
};

// Feature settings
export const FEATURES = {
  AUTO_MATCH: true,
  SHIPPING_TRACKING: true,
  ADVANCED_REPORTING: false
};

// Logging configuration
export const LOGGING_CONFIG = {
  LEVEL: APP_CONFIG.DEBUG_MODE ? 'debug' : 'error',
  PERSIST: APP_CONFIG.DEBUG_MODE
};

// Centralized error messages
export const ERROR_MESSAGES = {
  GENERIC: 'An unexpected error occurred. Please try again later.',
  NETWORK: 'Network error. Please check your connection and try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  VALIDATION: 'Please check your input and try again.',
  SERVER: 'Server error. Our team has been notified.',
  TIMEOUT: 'The request timed out. Please try again.'
};

// Define regex patterns
export const REGEX_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  ZIPCODE: /^\d{5}(-\d{4})?$/,
  PHONE: /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/
};

// Export default config
export default {
  api: API_CONFIG,
  auth: AUTH_CONFIG,
  app: APP_CONFIG,
  features: FEATURES,
  logging: LOGGING_CONFIG,
  errors: ERROR_MESSAGES,
  regex: REGEX_PATTERNS
};