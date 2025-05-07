<template>
  <div class="event-view-container">
    <h2 class="event-header">All Disaster Events</h2>
    <p>Browse the list of all created disaster events below.</p>

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
          <button class="edit-btn" @click="editEvent(event)">Edit</button>
          <button class="delete-btn" @click="deleteEvent(event.event_id)">Delete</button>
        </div>
      </li>
    </ul>
  </div>
  <div v-if="selectedEvent" class="modal-overlay">
  <div class="modal">
    <h3>Edit Event</h3>
    <form @submit.prevent="updateEvent">
      <input v-model="selectedEvent.name" placeholder="Event Name" required />
      <label>Requested Item Categories:</label>
      <select v-model="selectedEvent.categoryIds" multiple>
        <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
          {{ cat.category_name }}
        </option>
      </select>
      <input v-model="selectedEvent.location" placeholder="Location" required />
      <input type="date" v-model="selectedEvent.start_date" required />
      <input type="date" v-model="selectedEvent.end_date" required />

      <div class="modal-buttons">
        <button type="submit">Save Changes</button>
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
  const res = await axios.get('/api/admin/events')
  events.value = res.data
}

const fetchCategories = async () => {
  const res = await axios.get('/api/categories')
  categories.value = res.data
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
  // Get category IDs for this event (you could fetch from backend or use stored data)
  const categoryRes = await axios.get(`/api/admin/events/${event.event_id}/categories`)
  const categoryIds = categoryRes.data.map(cat => cat.category_id)

  selectedEvent.value = {
    ...event,
    categoryIds
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
  color: #8B5E3C;
  max-width: 800px;
  margin: auto;
  padding: 50px 20px;
  text-align: center;
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
}

.event-list {
  list-style: none;
  padding: 0;
  margin-top: 30px;
}

.event-card {
  background: #f9f9f9;
  border: 1px solid #d3c0a3;
  padding: 20px;
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
  margin-bottom: 10px;
}

.button-group {
  margin-top: 15px;
}

.edit-btn,
.delete-btn {
  font-size: 14px;
  padding: 8px 14px;
  margin-right: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.edit-btn {
  background-color: #007bff;
  color: white;
}

.edit-btn:hover {
  background-color: #0056b3;
}

.delete-btn {
  background-color: #e63946;
  color: white;
}

.delete-btn:hover {
  background-color: #c82333;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal {
  background: white;
  padding: 30px;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
  font-family: 'Poppins', sans-serif;
  color: #5c4033;
}

.modal input,
.modal select {
  width: 100%;
  margin-bottom: 12px;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.modal button {
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: bold;
  border: none;
  cursor: pointer;
}

.modal button[type="submit"] {
  background-color: #8B5E3C;
  color: white;
}

.cancel-btn {
  background-color: #ccc;
}


</style>
