import api from './api';

export const eventService = {
  async getActiveEvents() {
    try {
      const response = await api.get('/getActiveEvents');
      return response.data;
    } catch (error) {
      console.error('Error fetching events:', error);
      throw error;
    }
  },

  async getEventCategories(eventId) {
    try {
      const response = await api.get(`/getEventCategories/${eventId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching event categories:', error);
      throw error;
    }
  },

  async getAllCategories() {
    try {
      const response = await api.get('/api/categories');
      return response.data;
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  },

  async createEvent(eventData) {
    try {
      const response = await api.post('/api/admin/events', eventData);
      return response.data;
    } catch (error) {
      console.error('Error creating event:', error);
      throw error;
    }
  },

  async updateEvent(eventId, eventData) {
    try {
      const response = await api.put(`/api/admin/events/${eventId}`, eventData);
      return response.data;
    } catch (error) {
      console.error('Error updating event:', error);
      throw error;
    }
  },

  async deleteEvent(eventId) {
    try {
      const response = await api.delete(`/api/admin/events/${eventId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting event:', error);
      throw error;
    }
  }
};