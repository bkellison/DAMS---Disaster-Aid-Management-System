import api from './api';

export const pledgeService = {
  async getPledges(userId) {
    try {
      const response = await api.get(`/getPledges?user_id=${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching pledges:', error);
      throw error;
    }
  },

  async createPledge(pledgeData) {
    try {
      const response = await api.post('/createPledge', pledgeData);
      return response;
    } catch (error) {
      console.error('Error creating pledge:', error);
      throw error;
    }
  },

  async updatePledge(pledgeData) {
    try {
      const response = await api.post('/updatePledge', pledgeData);
      return response;
    } catch (error) {
      console.error('Error updating pledge:', error);
      throw error;
    }
  },

  async cancelPledge(pledgeId) {
    try {
      const response = await api.post(`/cancelPledge/${pledgeId}`);
      return response;
    } catch (error) {
      console.error('Error canceling pledge:', error);
      throw error;
    }
  }
};