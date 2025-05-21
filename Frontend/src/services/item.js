import api from './api';

export const itemService = {
  async getItems() {
    try {
      const response = await api.get('/getItems');
      return response.data;
    } catch (error) {
      console.error('Error fetching items:', error);
      throw error;
    }
  },

  async getCategories() {
    try {
      const response = await api.get('/getCategories');
      return response.data;
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  },

  async getItemsByCategory(categoryId) {
    try {
      const response = await api.get(`/getItemsByCategory/${categoryId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching items by category:', error);
      throw error;
    }
  },

  async createItem(itemData) {
    try {
      const response = await api.post('/api/admin/items', itemData);
      return response;
    } catch (error) {
      console.error('Error creating item:', error);
      throw error;
    }
  },

  async updateItem(itemId, itemData) {
    try {
      const response = await api.put(`/api/admin/items/${itemId}`, itemData);
      return response;
    } catch (error) {
      console.error('Error updating item:', error);
      throw error;
    }
  },

  async deleteItem(itemId) {
    try {
      const response = await api.delete(`/api/admin/items/${itemId}`);
      return response;
    } catch (error) {
      console.error('Error deleting item:', error);
      throw error;
    }
  }
};