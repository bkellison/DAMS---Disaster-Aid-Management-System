// src/stores/auth.js
import { defineStore } from 'pinia';
import api from '@/services/api'; // Make sure this points to your single API instance
import Cookies from 'js-cookie';

export const useAuthStore = defineStore("auth", {
  state: () => ({
    userId: null,
    username: null,
    role: null,
    isAuthenticated: false
  }),

    getters: {
    isAdmin: (state) => {
      console.log('Checking isAdmin:', state.role === 'Admin', 'Current role:', state.role);
      return state.role === 'Admin';
    },
    isDonor: (state) => {
      console.log('Checking isDonor:', state.role === 'Donor', 'Current role:', state.role);
      return state.role === 'Donor';
    },
    isRecipient: (state) => {
      console.log('Checking isRecipient:', state.role === 'Recipient', 'Current role:', state.role);
      return state.role === 'Recipient';
    },
    isAdminObserver: (state) => {
      console.log('Checking isAdminObserver:', state.role === 'Admin Observer', 'Current role:', state.role);
      return state.role === 'Admin Observer';
    },
    // Permission-based getters
    canEdit: (state) => {
      return state.role === 'Admin'; // Only full admins can edit
    },
    canView: (state) => {
      return ['Admin', 'Admin Observer'].includes(state.role); // Both can view admin pages
    },
    canCreateRequests: (state) => {
      return state.role !== 'Admin Observer'; // Admin Observer cannot create requests
    },
    canManageEvents: (state) => {
      return state.role === 'Admin'; // Only full admins can manage events
    },
    canManageItems: (state) => {
      return state.role === 'Admin'; // Only full admins can manage donation items
    },
    canCreateMatches: (state) => {
      return state.role === 'Admin'; // Only full admins can create matches
    },
    canUpdatePledges: (state) => {
      return ['Admin', 'Donor'].includes(state.role) && state.role !== 'Admin Observer';
    }
  },

  actions: {
    // State management actions
    setUserData(userData) {
      console.log('=== SET USER DATA CALLED ===');
      console.log('Input userData:', userData);
      
      if (!userData) {
        console.error('Error: setUserData called with null or undefined data');
        return;
      }

      // Check if all required fields are present
      if (!userData.user_id || !userData.username || !userData.role) {
        console.error('Error: userData is missing required fields', userData);
        return;
      }

      try {
        // Update state
        this.userId = userData.user_id;
        this.username = userData.username;
        this.role = userData.role;
        this.isAuthenticated = true;

        console.log('State after update:', {
          userId: this.userId,
          username: this.username,
          role: this.role,
          isAuthenticated: this.isAuthenticated
        });

        // Store in cookie for persistence
        const cookieData = { 
          userId: userData.user_id, 
          username: userData.username, 
          role: userData.role 
        };
        
        console.log('Saving to cookie:', cookieData);
        Cookies.set('authUser', JSON.stringify(cookieData), { expires: 1 / 24 });
        
        const savedCookie = Cookies.get('authUser');
        console.log('Cookie verification - saved cookie:', savedCookie);
        
        if (savedCookie) {
          try {
            const parsedCookie = JSON.parse(savedCookie);
            console.log('Parsed cookie data:', parsedCookie);
          } catch (e) {
            console.error('Error parsing saved cookie:', e);
          }
        } else {
          console.warn('Warning: Cookie was not saved successfully');
        }
        
        console.log('=== SET USER DATA COMPLETED ===');
      } catch (err) {
        console.error('Error in setUserData:', err);
      }
    },

    loadUserDataFromCookie() {
      console.log('=== LOADING USER DATA FROM COOKIE ===');
      const cookie = Cookies.get('authUser');
      console.log('Raw cookie data:', cookie);
      
      if (cookie) {
        try {
          console.log('Attempting to parse cookie...');
          const userData = JSON.parse(cookie);
          console.log('Parsed cookie data:', userData);

          // Validate the data
          if (!userData.userId || !userData.username || !userData.role) {
            console.error('Cookie data is missing required fields', userData);
            this.logout();
            return;
          }

          this.userId = userData.userId;
          this.username = userData.username;
          this.role = userData.role;
          this.isAuthenticated = true;

          console.log('Auth state after loading from cookie:', {
            userId: this.userId,
            username: this.username,
            role: this.role,
            isAuthenticated: this.isAuthenticated
          });
        } catch (err) {
          console.error('Invalid auth cookie:', err);
          this.logout();
        }
      } else {
        console.log('No auth cookie found, user is not authenticated');
      }
      console.log('=== LOAD FROM COOKIE COMPLETED ===');
    },

    logout() {
      console.log('=== LOGOUT CALLED ===');
      console.log('Auth state before logout:', {
        userId: this.userId,
        username: this.username,
        role: this.role,
        isAuthenticated: this.isAuthenticated
      });

      this.userId = null;
      this.username = null;
      this.role = null;
      this.isAuthenticated = false;
      
      console.log('Removing auth cookie...');
      Cookies.remove('authUser');
      
      const cookieAfterRemoval = Cookies.get('authUser');
      console.log('Cookie after removal:', cookieAfterRemoval);
      
      console.log('Auth state after logout:', {
        userId: this.userId,
        username: this.username,
        role: this.role,
        isAuthenticated: this.isAuthenticated
      });
      console.log('=== LOGOUT COMPLETED ===');
    },

    // API actions
    async login(username, password) {
      console.log('=== LOGIN CALLED ===');
      console.log('Login attempt for username:', username);
      
      try {
        console.log('Making API request to /login endpoint...');
        const response = await api.post('/login', { username, password });
        
        console.log('Login response status:', response.status);
        console.log('Login response headers:', response.headers);
        console.log('Login response data:', response.data);
        
        if (response.status === 200) {
          if (response.data) {
            console.log('Login successful, data received:', response.data);
            
            // Check data structure
            if (typeof response.data === 'object') {
              if (response.data.user_id && response.data.username && response.data.role) {
                console.log('Data has expected fields, calling setUserData');
                this.setUserData(response.data);
              } else {
                console.error('Login response missing required fields:', response.data);
              }
            } else {
              console.error('Login response data is not an object:', typeof response.data);
            }
          } else {
            console.error('Login response has no data despite 200 status');
          }
        } else {
          console.warn('Login response status is not 200:', response.status);
        }
        
        console.log('Auth state after login attempt:', {
          userId: this.userId,
          username: this.username,
          role: this.role,
          isAuthenticated: this.isAuthenticated
        });
        
        console.log('=== LOGIN COMPLETED ===');
        return response;
      } catch (error) {
        console.error('=== LOGIN ERROR ===');
        console.error('Login request failed:', error);
        
        if (error.response) {
          console.error('Error response status:', error.response.status);
          console.error('Error response data:', error.response.data);
        } else if (error.request) {
          console.error('No response received:', error.request);
        } else {
          console.error('Error setting up request:', error.message);
        }
        
        console.error('=== LOGIN ERROR DETAILS END ===');
        throw error;
      }
    },

    async requestAccount(userData) {
      console.log('=== REQUEST ACCOUNT CALLED ===');
      console.log('Account request data:', { ...userData, password: '***REDACTED***' });
      
      try {
        console.log('Making API request to /requestNewAccount endpoint...');
        const response = await api.post('/requestNewAccount', userData);
        
        console.log('Request account response:', {
          status: response.status,
          data: response.data
        });
        
        console.log('=== REQUEST ACCOUNT COMPLETED ===');
        return response;
      } catch (error) {
        console.error('=== REQUEST ACCOUNT ERROR ===');
        console.error('Account request failed:', error);
        
        if (error.response) {
          console.error('Error response status:', error.response.status);
          console.error('Error response data:', error.response.data);
        }
        
        console.error('=== REQUEST ACCOUNT ERROR DETAILS END ===');
        throw error;
      }
    },

    async resetPassword(resetData) {
      console.log('=== RESET PASSWORD CALLED ===');
      console.log('Reset data:', { ...resetData, new_password: '***REDACTED***' });
      
      try {
        console.log('Making API request to /resetForgottenPassword endpoint...');
        const response = await api.post('/resetForgottenPassword', resetData);
        
        console.log('Reset password response:', {
          status: response.status,
          data: response.data
        });
        
        console.log('=== RESET PASSWORD COMPLETED ===');
        return response;
      } catch (error) {
        console.error('=== RESET PASSWORD ERROR ===');
        console.error('Password reset failed:', error);
        
        if (error.response) {
          console.error('Error response status:', error.response.status);
          console.error('Error response data:', error.response.data);
        }
        
        console.error('=== RESET PASSWORD ERROR DETAILS END ===');
        throw error;
      }
    }
  }
});