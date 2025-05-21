<template>
  <div class="event-view-container">
    <div class="content-box">
      <h2 class="event-header">All Disaster Events</h2>
      <p class="description">Browse the list of all created disaster events below.</p>

      <div class="action-button-container">
        <button @click="goToCreateEvent" class="create-btn">+ Create New Event</button>
      </div>

      <div v-if="loading" class="loading-indicator">
        Loading events...
      </div>

      <div v-else-if="events.length === 0" class="no-events">No events found.</div>

      <ul v-else class="event-list">
        <li v-for="event in events" :key="event.event_id" class="event-card">
          <h3 class="event-title">{{ event.name }}</h3>
          <p><strong>Categories:</strong> {{ getEventCategories(event) }}</p>
          <p><strong>Location:</strong> {{ event.location }}</p>
          <p>
            <strong>Start:</strong> {{ formatDate(event.start_date) }} |
            <strong>End:</strong> {{ formatDate(event.end_date) }}
          </p>
          <p><strong>Status:</strong> {{ event.is_active ? 'Active' : 'Inactive' }}</p>

          <div class="button-group">
            <button @click="editEvent(event)" class="edit-btn">Edit</button>
            <button @click="confirmDelete(event)" class="delete-btn">Delete</button>
          </div>
        </li>
      </ul>
    </div>
  
    <!-- Edit Event Modal -->
    <div v-if="selectedEvent" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>Edit Event</h3>
        <form @submit.prevent="updateEvent">
          <div class="form-group">
            <label for="event-name">Event Name:</label>
            <input id="event-name" v-model="selectedEvent.name" placeholder="Event Name" required />
          </div>
          
          <div class="form-group">
            <label for="event-location">Location:</label>
            <input id="event-location" v-model="selectedEvent.location" placeholder="Location" required />
          </div>
          
          <div class="form-group date-group">
            <div>
              <label for="start-date">Start Date:</label>
              <input id="start-date" type="date" v-model="selectedEvent.start_date" required />
            </div>
            <div>
              <label for="end-date">End Date:</label>
              <input id="end-date" type="date" v-model="selectedEvent.end_date" required />
            </div>
          </div>
          
          <div class="form-group">
            <label>Categories:</label>
            <select v-model="selectedEvent.categoryIds" multiple>
              <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
                {{ cat.category_name }}
              </option>
            </select>
            <p class="help-text">Hold Ctrl/Cmd to select multiple categories</p>
          </div>

          <div class="modal-buttons">
            <button type="submit" class="save-btn">Save Changes</button>
            <button type="button" class="cancel-btn" @click="closeModal">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal confirm-modal">
        <h3>Confirm Delete</h3>
        <p>Are you sure you want to delete the event "{{ eventToDelete?.name }}"?</p>
        <p class="warning-text">This action cannot be undone.</p>
        
        <div class="modal-buttons">
          <button @click="confirmDeleteAction" class="delete-btn">Delete</button>
          <button @click="cancelDelete" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'ViewEvents',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    
    // State
    const events = ref([]);
    const categories = ref([]);
    const selectedEvent = ref(null);
    const showDeleteConfirm = ref(false);
    const eventToDelete = ref(null);
    const loading = ref(true);
    
    // Format date for display
    const formatDate = (dateStr) => {
      if (!dateStr) return 'N/A';
      return new Date(dateStr).toLocaleDateString();
    };
    
    // Get comma-separated list of categories
    const getEventCategories = (event) => {
      if (!event.categories || !event.categories.length) return 'None';
      return event.categories.join(', ');
    };
    
    // Close modal and reset selected event
    const closeModal = () => {
      selectedEvent.value = null;
    };
    
    // Navigate to create event page
    const goToCreateEvent = () => {
      router.push('/admin/create-event');
    };
    
    // Fetch events from API
    const fetchEvents = async () => {
      try {
        console.log('Fetching events with auth role:', authStore.role);
        loading.value = true;
        
        let url = '/api/admin/events';
        if (authStore.isAdmin) {
          console.log('Using admin endpoint');
        }
        
        const res = await axios.get(url);
        console.log('Admin events fetched:', res.data);
        events.value = res.data;
      } catch (error) {
        console.error('Error fetching events:', error);
        if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
        }
      } finally {
        loading.value = false;
      }
    };
    
    // Fetch categories for event editing
    const fetchCategories = async () => {
      try {
        const res = await axios.get('/api/categories');
        categories.value = res.data;
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };
    
    // Handle delete event
    const confirmDelete = (event) => {
      eventToDelete.value = event;
      showDeleteConfirm.value = true;
    };
    
    const cancelDelete = () => {
      eventToDelete.value = null;
      showDeleteConfirm.value = false;
    };
    
    const confirmDeleteAction = async () => {
      if (!eventToDelete.value) return;
      
      try {
        await axios.delete(`/api/admin/events/${eventToDelete.value.event_id}`);
        await fetchEvents(); // Refresh list
        cancelDelete(); // Close modal
      } catch (err) {
        console.error('Failed to delete event:', err);
        alert('Failed to delete event: ' + (err.response?.data?.error || err.message));
      }
    };
    
    // Handle edit event
    const editEvent = async (event) => {
      try {
        // Get category IDs for this event
        const categoryRes = await axios.get(`/api/admin/events/${event.event_id}/categories`);
        const categoryIds = categoryRes.data.map(cat => cat.category_id);
    
        selectedEvent.value = {
          ...event,
          categoryIds
        };
      } catch (error) {
        console.error('Error fetching event categories:', error);
        alert('Could not load event categories');
      }
    };
    
    const updateEvent = async () => {
      try {
        await axios.put(`/api/admin/events/${selectedEvent.value.event_id}`, selectedEvent.value);
        await fetchEvents();
        selectedEvent.value = null;
        alert('Event updated successfully!');
      } catch (error) {
        console.error('Update failed:', error);
        alert('Update failed: ' + (error.response?.data?.error || error.message));
      }
    };
    
    // Handle escape key to close modals
    const handleEscKey = (e) => {
      if (e.key === 'Escape') {
        if (selectedEvent.value) closeModal();
        if (showDeleteConfirm.value) cancelDelete();
      }
    };
    
    // Set up event listeners on mount
    onMounted(() => {
      console.log('ViewEvents component mounted');
      fetchEvents();
      fetchCategories();
      document.addEventListener('keydown', handleEscKey);
    });
    
    // Clean up event listeners when component is unmounted
    onBeforeUnmount(() => {
      document.removeEventListener('keydown', handleEscKey);
    });
    
    return {
      events,
      categories,
      selectedEvent,
      showDeleteConfirm,
      eventToDelete,
      loading,
      formatDate,
      getEventCategories,
      closeModal,
      goToCreateEvent,
      confirmDelete,
      cancelDelete,
      confirmDeleteAction,
      editEvent,
      updateEvent
    };
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.event-view-container {
  font-family: 'Poppins', sans-serif;
  color: #5c4033;
  max-width: 1000px;
  margin: auto;
  padding: 50px 20px;
  text-align: center;
}

.description {
  color: #8B5E3C; 
  font-size: 16px;
  margin-bottom: 20px;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
}

.event-header {
  background: #f5e1c5;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 28px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
}

.action-button-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.create-btn {
  background: #2e8b57;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.create-btn:hover {
  background: #236b43;
}

.no-events, .loading-indicator {
  font-size: 18px;
  color: #777;
  margin-top: 20px;
  padding: 40px;
  background: #f5f5f5;
  border-radius: 8px;
}

.event-list {
  list-style: none;
  padding: 0;
  margin-top: 30px;
}

.event-card {
  background: #ffffff;
  border: 2px solid #d3c0a3;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 20px;
  text-align: left;
  transition: box-shadow 0.3s ease;
}

.event-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.event-title {
  font-size: 22px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 15px;
}

.event-card p {
  margin: 10px 0;
  line-height: 1.5;
}

.button-group {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.edit-btn,
.delete-btn,
.save-btn,
.cancel-btn {
  font-size: 16px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.3s ease, transform 0.2s ease;
}

.edit-btn {
  background-color: #4a90e2;
  color: white;
}

.edit-btn:hover {
  background-color: #3a7bc8;
  transform: scale(1.05);
}

.delete-btn {
  background-color: #e63946;
  color: white;
}

.delete-btn:hover {
  background-color: #c82333;
  transform: scale(1.05);
}

/* Modal Styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal {
  background: #f9f3e8;
  padding: 30px;
  border-radius: 15px;
  max-width: 550px;
  width: 90%;
  font-family: 'Poppins', sans-serif;
  color: #5c4033;
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}

.modal h3 {
  font-size: 24px;
  text-align: center;
  margin-bottom: 20px;
  color: #5c4033;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #5c4033;
}

.date-group {
  display: flex;
  gap: 15px;
}

.date-group > div {
  flex: 1;
}

.modal input,
.modal select {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #d3c0a3;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
}

.modal select[multiple] {
  height: 120px;
}

.help-text {
  font-size: 14px;
  color: #777;
  margin-top: 5px;
  font-style: italic;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 25px;
}

.save-btn {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  color: white;
}

.save-btn:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}

.cancel-btn {
  background: #e0e0e0;
  color: #333;
}

.cancel-btn:hover {
  background: #d0d0d0;
}

.confirm-modal {
  max-width: 400px;
  text-align: center;
}

.warning-text {
  color: #e63946;
  margin-top: 10px;
  font-weight: 500;
}
</style>