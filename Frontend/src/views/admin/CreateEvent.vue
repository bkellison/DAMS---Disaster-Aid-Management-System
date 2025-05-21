<template>
  <div class="event-container">
    <div class="content-box">
      <h2 class="event-header">Create Disaster Event</h2>
      <p>Please fill in the details below to register a new disaster event.</p>
      <form @submit.prevent="submitEvent">
        <input v-model="event.name" placeholder="Event Name" required />
        
        <select v-model="event.type" required>
          <option disabled value="">Select Disaster Type</option>
          <option>Hurricane</option>
          <option>Earthquake</option>
          <option>Tornado</option>
          <option>Flood</option>
        </select>

        <input v-model="event.location" placeholder="Location (City/State or Lat/Long)" required />
        <label class="field-label">Start Date:</label>
        <input type="date" v-model="event.startDate" required />

        <label class="field-label">End Date:</label>
        <input type="date" v-model="event.endDate" required />

        <label class="field-label">Select Categories:</label>
        <select v-model="event.categoryIds" multiple>
          <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
            {{ cat.category_name }}
          </option>
        </select>
        <p class="help-text">Hold Ctrl/Cmd to select multiple categories</p>

        <button type="submit">Create Event</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { RouterView, useRoute, useRouter } from 'vue-router';

const router = useRouter();

const event = ref({
  name: '',
  type: '',
  location: '',
  startDate: '',
  endDate: '',
  categoryIds: [] // For multiple selection
})

const categories = ref([])

const fetchCategories = async () => {
  const res = await axios.get('/api/categories')
  categories.value = res.data
}

const submitEvent = async () => {
  try {
    // Ensure IDs are numbers (optional, depending on backend expectations)
    const formattedEvent = {
      ...event.value,
      categoryIds: event.value.categoryIds.map(id => parseInt(id))
    }

    await axios.post('/api/admin/events', formattedEvent)
    alert('Event created successfully!')
    router.push({ path: '/admin/view-events' })
  } catch (error) {
    alert('Error creating event: ' + error.message)
  }
}

onMounted(fetchCategories)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.event-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C;
  max-width: 500px;
  margin: auto;
  padding: 50px 20px;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
  width: 500px
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

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

input,
select {
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  background-color: white;
}

.field-label {
  text-align: left;
  margin-bottom: -10px;
  font-weight: 500;
  color: #5c4033;
}

.help-text {
  font-size: 14px;
  margin-top: -5px;
  color: #6A3E2B;
  text-align: left;
  font-style: italic;
}

button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 18px;
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  margin-top: 10px;
}

button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}
</style>