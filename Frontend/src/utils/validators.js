import { REGEX_PATTERNS } from '@/config';

/**
 * Validation utilities for forms
 */
export const validators = {
  required: (message = 'This field is required') => {
    return (value) => {
      if (value === null || value === undefined || value === '') {
        return message;
      }
      
      if (Array.isArray(value) && value.length === 0) {
        return message;
      }
      
      return true;
    };
  },
  
  minLength: (min, message = `Must be at least ${min} characters`) => {
    return (value) => {
      if (!value || value.length < min) {
        return message;
      }
      
      return true;
    };
  },
  
  maxLength: (max, message = `Must be no more than ${max} characters`) => {
    return (value) => {
      if (value && value.length > max) {
        return message;
      }
      
      return true;
    };
  },
  
  email: (message = 'Please enter a valid email address') => {
    return (value) => {
      if (!value) return true;
      
      if (!REGEX_PATTERNS.EMAIL.test(value)) {
        return message;
      }
      
      return true;
    };
  },
  
  zipcode: (message = 'Please enter a valid ZIP code') => {
    return (value) => {
      if (!value) return true;
      
      if (!REGEX_PATTERNS.ZIPCODE.test(value)) {
        return message;
      }
      
      return true;
    };
  },
  
  phone: (message = 'Please enter a valid phone number') => {
    return (value) => {
      if (!value) return true;
      
      if (!REGEX_PATTERNS.PHONE.test(value)) {
        return message;
      }
      
      return true;
    };
  },
  
  password: (message = 'Password must contain at least 8 characters, including uppercase, lowercase and numbers') => {
    return (value) => {
      if (!value) return true;
      
      if (!REGEX_PATTERNS.PASSWORD.test(value)) {
        return message;
      }
      
      return true;
    };
  },
  
  match: (field, fieldName = 'fields', message) => {
    return (value, formValues) => {
      if (!value) return true;
      
      if (value !== formValues[field]) {
        return message || `The ${fieldName} do not match`;
      }
      
      return true;
    };
  },
  
  number: (message = 'Please enter a valid number') => {
    return (value) => {
      if (!value) return true;
      
      if (isNaN(Number(value))) {
        return message;
      }
      
      return true;
    };
  },
  
  min: (min, message = `Value must be at least ${min}`) => {
    return (value) => {
      if (!value) return true;
      
      if (Number(value) < min) {
        return message;
      }
      
      return true;
    };
  },
  
  max: (max, message = `Value must be no more than ${max}`) => {
    return (value) => {
      if (!value) return true;
      
      if (Number(value) > max) {
        return message;
      }
      
      return true;
    };
  }
};

export default validators;