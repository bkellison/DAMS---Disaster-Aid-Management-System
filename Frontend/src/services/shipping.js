import api from './api';

export const shippingService = {
  async getShippingInfo(matchId) {
    try {
      const response = await api.get(`/api/getShippingInfo/${matchId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching shipping info:', error);
      throw error;
    }
  },

  async updateShippingStatus(shippingData) {
    try {
      const response = await api.post('/api/updateShippingStatus', shippingData);
      return response;
    } catch (error) {
      console.error('Error updating shipping status:', error);
      throw error;
    }
  }
};