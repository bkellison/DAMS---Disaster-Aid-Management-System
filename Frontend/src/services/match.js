import api from './api';

export const matchService = {
  async getMatches(userId) {
    try {
      const response = await api.get(`/getMatches?user_id=${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching matches:', error);
      throw error;
    }
  },

  async createMatch(matchData) {
    try {
      const response = await api.post('/createMatch', matchData);
      return response;
    } catch (error) {
      console.error('Error creating match:', error);
      throw error;
    }
  },

  async autoMatch(matchData) {
    try {
      const response = await api.post('/api/autoMatch', matchData);
      return response;
    } catch (error) {
      console.error('Error creating auto match:', error);
      throw error;
    }
  },

  async getAutoMatchType() {
    try {
      const response = await api.get('/api/getAutoMatchType');
      return response.data;
    } catch (error) {
      console.error('Error getting match types:', error);
      throw error;
    }
  },

  // New method to get all match types for request creation
  async getMatchTypes() {
    try {
      const response = await api.get('/getMatchTypes');
      return response.data;
    } catch (error) {
      console.error('Error getting all match types:', error);
      throw error;
    }
  }
};