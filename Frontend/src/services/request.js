import api from './api';

export const requestService = {
  async getRequests(userId, requestId = null) {
    try {
      let url = `/getRequests?user_id=${userId}`;
      if (requestId) {
        url += `&request_id=${requestId}`;
      }
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching requests:', error);
      throw error;
    }
  },

  async getRequestsForResponse() {
    try {
      const response = await api.get('/getRequestsForResponse');
      return response.data;
    } catch (error) {
      console.error('Error fetching requests for response:', error);
      throw error;
    }
  },

  async getRequestDetails(requestId) {
    try {
      const response = await api.get(`/getRequestDetails/${requestId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching request details:', error);
      throw error;
    }
  },

  async createRequest(requestData) {
    try {
      const response = await api.post('/createRequest', requestData);
      return response;
    } catch (error) {
      console.error('Error creating request:', error);
      throw error;
    }
  },

  async submitResponse(responseData) {
    try {
      const response = await api.post('/submitResponse', responseData);
      return response;
    } catch (error) {
      console.error('Error submitting response:', error);
      throw error;
    }
  },

  async updateResponse(responseData) {
    try {
      const response = await api.post('/updateResponse', responseData);
      return response;
    } catch (error) {
      console.error('Error updating response:', error);
      throw error;
    }
  }
};