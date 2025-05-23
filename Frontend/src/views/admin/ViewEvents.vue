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
            <strong>Start:</strong> {{ formatDate(event.start_date) }} |
            <strong>End:</strong> {{ formatDate(event.end_date) }}
          </p>
          <p><strong>Status:</strong> {{ event.is_active ? 'Active' : 'Inactive' }}</p>

          <div class="button-group">
            <AppButton variant="edit" @click="editEvent(event)">Edit</AppButton>
            <AppButton variant="danger" @click="deleteEvent(event.event_id)">Delete</AppButton>
          </div>
        </li>
      </ul>
    </div>
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
        
        <!-- Updated location editing fields -->
        <div class="location-section">
          <h4 class="section-title">Event Location</h4>
          
          <div class="form-group">
            <label for="event-address">Street Address:</label>
            <input id="event-address" v-model="selectedEvent.address" placeholder="Street Address" required />
          </div>
          
          <div class="form-group">
            <label for="event-city">City:</label>
            <input id="event-city" v-model="selectedEvent.city" placeholder="City" required />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="event-state">State:</label>
              <select id="event-state" v-model="selectedEvent.state" required>
                <option disabled value="">Select State</option>
                <option v-for="state in stateOptions" :key="state.value" :value="state.value">
                  {{ state.label }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="event-zip">ZIP Code:</label>
              <input id="event-zip" v-model="selectedEvent.zipCode" placeholder="ZIP Code" required />
            </div>
          </div>
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
          <AppButton type="submit" variant="save">Save</AppButton>
          <AppButton type="button" variant="cancel" @click="closeModal">Cancel</AppButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const events = ref([])
const categories = ref([])
const selectedEvent = ref(null)

// State options for editing
const stateOptions = [
  { value: 'AL', label: 'Alabama' },
  { value: 'AK', label: 'Alaska' },
  { value: 'AZ', label: 'Arizona' },
  { value: 'AR', label: 'Arkansas' },
  { value: 'CA', label: 'California' },
  { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' },
  { value: 'DE', label: 'Delaware' },
  { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' },
  { value: 'HI', label: 'Hawaii' },
  { value: 'ID', label: 'Idaho' },
  { value: 'IL', label: 'Illinois' },
  { value: 'IN', label: 'Indiana' },
  { value: 'IA', label: 'Iowa' },
  { value: 'KS', label: 'Kansas' },
  { value: 'KY', label: 'Kentucky' },
  { value: 'LA', label: 'Louisiana' },
  { value: 'ME', label: 'Maine' },
  { value: 'MD', label: 'Maryland' },
  { value: 'MA', label: 'Massachusetts' },
  { value: 'MI', label: 'Michigan' },
  { value: 'MN', label: 'Minnesota' },
  { value: 'MS', label: 'Mississippi' },
  { value: 'MO', label: 'Missouri' },
  { value: 'MT', label: 'Montana' },
  { value: 'NE', label: 'Nebraska' },
  { value: 'NV', label: 'Nevada' },
  { value: 'NH', label: 'New Hampshire' },
  { value: 'NJ', label: 'New Jersey' },
  { value: 'NM', label: 'New Mexico' },
  { value: 'NY', label: 'New York' },
  { value: 'NC', label: 'North Carolina' },
  { value: 'ND', label: 'North Dakota' },
  { value: 'OH', label: 'Ohio' },
  { value: 'OK', label: 'Oklahoma' },
  { value: 'OR', label: 'Oregon' },
  { value: 'PA', label: 'Pennsylvania' },
  { value: 'RI', label: 'Rhode Island' },
  { value: 'SC', label: 'South Carolina' },
  { value: 'SD', label: 'South Dakota' },
  { value: 'TN', label: 'Tennessee' },
  { value: 'TX', label: 'Texas' },
  { value: 'UT', label: 'Utah' },
  { value: 'VT', label: 'Vermont' },
  { value: 'VA', label: 'Virginia' },
  { value: 'WA', label: 'Washington' },
  { value: 'WV', label: 'West Virginia' },
  { value: 'WI', label: 'Wisconsin' },
  { value: 'WY', label: 'Wyoming' }
];

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  });
};

// Parse location string into components
const parseLocationString = (locationString) => {
  if (!locationString) {
    return { address: '', city: '', state: '', zipCode: '' };
  }
  
  // Try to parse "Address, City, State ZipCode" format
  const parts = locationString.split(', ');
  if (parts.length >= 3) {
    const address = parts[0];
    const city = parts[1];
    const stateZipPart = parts[2];
    
    // Extract state and zip from "State ZipCode"
    const stateZipMatch = stateZipPart.match(/^([A-Z]{2})\s+(.+)$/);
    if (stateZipMatch) {
      return {
        address: address,
        city: city,
        state: stateZipMatch[1],
        zipCode: stateZipMatch[2]
      };
    }
  }
  
  // Fallback - just use the full string as address
  return {
    address: locationString,
    city: '',
    state: '',
    zipCode: ''
  };
};

// Close modal and reset selected event
const closeModal = () => {
  selectedEvent.value = null;
}

const fetchEvents = async () => {
  try {
    const res = await api.get('/api/admin/events')
    events.value = res.data
  } catch (error) {
    console.error('Error fetching events:', error)
  }
}

const fetchCategories = async () => {
  try {
    const res = await api.get('/api/categories')
    categories.value = res.data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

const deleteEvent = async (id) => {
  if (confirm("Are you sure you want to delete this event?")) {
    try {
      await api.delete(`/api/admin/events/${id}`);
      await fetchEvents(); // Refresh list
    } catch (err) {
      alert("Failed to delete event: " + err.message);
    }
  }
};

const editEvent = async (event) => {
  try {
    // Get category IDs for this event
    const categoryRes = await api.get(`/api/admin/events/${event.event_id}/categories`)
    const categoryIds = categoryRes.data.map(cat => cat.category_id)

    // Parse the location string into components
    const locationComponents = parseLocationString(event.location);

    selectedEvent.value = {
      ...event,
      categoryIds,
      ...locationComponents
    }
  } catch (error) {
    console.error('Error fetching event categories:', error)
    alert('Could not load event categories')
  }
}

const updateEvent = async () => {
  try {
    // Combine location fields back into a single string
    const locationString = `${selectedEvent.value.address}, ${selectedEvent.value.city}, ${selectedEvent.value.state} ${selectedEvent.value.zipCode}`;
    
    const updateData = {
      ...selectedEvent.value,
      location: locationString
    };
    
    await api.put(`/api/admin/events/${selectedEvent.value.event_id}`, updateData)
    await fetchEvents()
    selectedEvent.value = null
    alert('Event updated successfully!')
  } catch (error) {
    alert('Update failed: ' + error.message)
  }
}

// Handle escape key to close modal
const handleEscKey = (e) => {
  if (e.key === 'Escape' && selectedEvent.value) {
    closeModal();
  }
}

// Clean up any event listeners when component is unmounted
onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleEscKey);
});

onMounted(() => {
  fetchEvents()
  fetchCategories()
  document.addEventListener('keydown', handleEscKey);
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
  color: #6c757d;
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
  gap: 15px; 
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
  max-width: 650px;
  width: 90%;
  font-family: 'Poppins', sans-serif;
  color: #5c4033;
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  font-size: 24px;
  text-align: center;
  margin-bottom: 20px;
  color: #5c4033;
}

.location-section {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
  border: 1px solid #e0e0e0;
}

.section-title {
  color: #5c4033;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #5c4033;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
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
  gap: 15px;
}

/* Responsive design */
@media (max-width: 768px) {
  .form-row,
  .date-group {
    flex-direction: column;
  }
  
  .modal {
    max-width: 95%;
    padding: 20px;
  }
}
</style>