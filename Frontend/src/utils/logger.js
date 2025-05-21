import { LOGGING_CONFIG } from '@/config';

/**
 * Logger utility for consistent logging throughout the application
 */
class Logger {
  constructor(source) {
    this.source = source;
    this.logLevel = this._getLogLevel();
    this.persist = LOGGING_CONFIG.PERSIST;
  }

  /**
   * Convert log level string to numeric value for comparison
   */
  _getLogLevel() {
    const levels = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3
    };
    
    return levels[LOGGING_CONFIG.LEVEL] || levels.error;
  }

  /**
   * Format log message with timestamp and source
   */
  _formatMessage(message) {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${this.source}] ${message}`;
  }

  /**
   * Persist log to storage if enabled
   */
  _persistLog(level, message, data) {
    if (!this.persist) return;
    
    try {
      const logs = JSON.parse(localStorage.getItem('app_logs') || '[]');
      logs.push({
        timestamp: new Date().toISOString(),
        level,
        source: this.source,
        message,
        data: data ? JSON.stringify(data) : undefined
      });
      
      // Keep only the last 100 logs
      while (logs.length > 100) {
        logs.shift();
      }
      
      localStorage.setItem('app_logs', JSON.stringify(logs));
    } catch (e) {
      // Silently fail if localStorage is not available
      console.error('Failed to persist log:', e);
    }
  }

  /**
   * Debug level log
   */
  debug(message, data) {
    if (this.logLevel <= 0) {
      console.debug(this._formatMessage(message), data);
      this._persistLog('debug', message, data);
    }
  }

  /**
   * Info level log
   */
  info(message, data) {
    if (this.logLevel <= 1) {
      console.info(this._formatMessage(message), data);
      this._persistLog('info', message, data);
    }
  }

  /**
   * Warning level log
   */
  warn(message, data) {
    if (this.logLevel <= 2) {
      console.warn(this._formatMessage(message), data);
      this._persistLog('warn', message, data);
    }
  }

  /**
   * Error level log
   */
  error(message, error) {
    if (this.logLevel <= 3) {
      console.error(this._formatMessage(message), error);
      this._persistLog('error', message, error);
    }
  }

  /**
   * Get all persisted logs
   */
  static getLogs() {
    try {
      return JSON.parse(localStorage.getItem('app_logs') || '[]');
    } catch (e) {
      return [];
    }
  }

  /**
   * Clear all persisted logs
   */
  static clearLogs() {
    try {
      localStorage.removeItem('app_logs');
    } catch (e) {
      // Silently fail
    }
  }
}

/**
 * Create a logger instance
 */
export function createLogger(source) {
  return new Logger(source || 'App');
}

export default Logger;