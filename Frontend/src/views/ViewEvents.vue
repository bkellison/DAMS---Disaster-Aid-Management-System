<template>
  <div class="event-view-container">
    <div class="content-box">
      <h2 class="event-header">All Disaster Events</h2>
      <p class="description">Browse the list of all created disaster events below.</p>

      <div v-if="events.length === 0" class="no-events">No events found.</div>

      <ul class="event-list">
        <li v-for="event in events" :key="event.event_id" class="event-card">
          <h3 class="event-title">{{ event.name }}</h3>
          <p><strong>Categories:</strong> {{ event.categories.join(', ') }}</p>
          <p><strong>Location:</strong> {{ event.location }}</p>
          <p>
            <strong>Start:</strong> {{ event.start_date }} |
            <strong>End:</strong> {{ event.end_date }}
          </p>
          <p><strong>Status:</strong> {{ event.is_active ? 'Active' : 'Inactive' }}</p>

          <div class="button-group">
            <button @click="editEvent(event)" class="edit-btn">Edit</button>
            <button @click="deleteEvent(event.event_id)" class="delete-btn">Delete</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
  
  <!-- Edit Event Modal -->
  <div v-if="selectedEvent" class="modal-overlay">
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
          <button type="button" class="cancel-btn" @click="selectedEvent = null">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const events = ref([])
const categories = ref([])
const selectedEvent = ref(null)

const fetchEvents = async () => {
  try {
    const res = await axios.get('/api/admin/events')
    events.value = res.data
  } catch (error) {
    console.error('Error fetching events:', error)
  }
}

const fetchCategories = async () => {
  try {
    const res = await axios.get('/api/categories')
    categories.value = res.data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

const deleteEvent = async (id) => {
  if (confirm("Are you sure you want to delete this event?")) {
    try {
      await axios.delete(`/api/admin/events/${id}`);
      await fetchEvents(); // Refresh list
    } catch (err) {
      alert("Failed to delete event: " + err.message);
    }
  }
};

const editEvent = async (event) => {
  try {
    // Get category IDs for this event
    const categoryRes = await axios.get(`/api/admin/events/${event.event_id}/categories`)
    const categoryIds = categoryRes.data.map(cat => cat.category_id)

    selectedEvent.value = {
      ...event,
      categoryIds
    }
  } catch (error) {
    console.error('Error fetching event categories:', error)
    alert('Could not load event categories')
  }
}

const updateEvent = async () => {
  try {
    await axios.put(`/api/admin/events/${selectedEvent.value.event_id}`, selectedEvent.value)
    await fetchEvents()
    selectedEvent.value = null
    alert('Event updated successfully!')
  } catch (error) {
    alert('Update failed: ' + error.message)
  }
}

onMounted(() => {
  fetchEvents()
  fetchCategories()
})
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

.no-events {
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
.delete-btn {
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

.save-btn,
.cancel-btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease, 0.3s ease;
  min-width: 120px;
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
</style>
