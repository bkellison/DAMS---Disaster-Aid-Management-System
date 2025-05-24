<template>
  <div class="event-container">
    <div class="content-box">
      <h2 class="event-header">Create Disaster Event</h2>
      <p class="description">Please fill in the details below to register a new disaster event.</p>
      
      <!-- Admin Observer Warning -->
      <div v-if="isAdminObserver" class="observer-warning">
        <strong>Admin Observer Mode:</strong> You can view this form but cannot create events. This is a read-only preview of the event creation process.
      </div>
      
      <form @submit.prevent="submitEvent">
        <input 
          v-model="event.name" 
          placeholder="Event Name (e.g., Earthquake Relief)" 
          required 
          :disabled="isAdminObserver"
          :class="{ 'disabled-field': isAdminObserver }"
        />
        
        <select 
          v-model="event.type" 
          required
          :disabled="isAdminObserver"
          :class="{ 'disabled-field': isAdminObserver }"
        >
          <option disabled value="">Select Disaster Type</option>
          <option>Hurricane</option>
          <option>Earthquake</option>
          <option>Tornado</option>
          <option>Flood</option>
          <option>Wildfire</option>
          <option>Winter Storm</option>
          <option>Other</option>
        </select>

        <!-- Updated location fields -->
        <div class="location-section">
          <h3 class="section-title">Event Location</h3>
          
          <input 
            v-model="event.address" 
            placeholder="Street Address (e.g., 123 Main St)" 
            required 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          />
          
          <input 
            v-model="event.city" 
            placeholder="City (e.g., Los Angeles)" 
            required 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          />
          
          <div class="form-row">
            <select 
              v-model="event.state" 
              required 
              class="state-select"
              :disabled="isAdminObserver"
              :class="{ 'disabled-field': isAdminObserver }"
            >
              <option disabled value="">Select State</option>
              <option v-for="state in stateOptions" :key="state.value" :value="state.value">
                {{ state.label }}
              </option>
            </select>
            
            <input 
              v-model="event.zipCode" 
              placeholder="ZIP Code" 
              pattern="[0-9]{5}(-[0-9]{4})?" 
              title="Please enter a valid ZIP code (e.g., 12345 or 12345-6789)"
              required 
              :disabled="isAdminObserver"
              :class="{ 'disabled-field': isAdminObserver }"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label class="field-label">Start Date:</label>
          <input 
            type="date" 
            v-model="event.startDate" 
            required 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          />
        </div>

        <div class="form-group">
          <label class="field-label">End Date:</label>
          <input 
            type="date" 
            v-model="event.endDate" 
            required 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          />
        </div>

        <div class="form-group">
          <label class="field-label">Select Categories:</label>
          <select 
            v-model="event.categoryIds" 
            multiple
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          >
            <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
              {{ cat.category_name }}
            </option>
          </select>
          <p class="help-text">Hold Ctrl/Cmd to select multiple categories</p>
        </div>

        <div class="auth-actions">
          <AppButton 
            type="submit" 
            variant="primary"
            :disabled="isAdminObserver || !canManageEvents"
            :class="{ 'disabled-button': isAdminObserver }"
          >
            {{ isAdminObserver ? 'View Only Mode - Cannot Create' : 'Create Event' }}
          </AppButton>
          
          <div v-if="isAdminObserver" class="observer-notice">
            <p>Admin Observers can view all forms but cannot create events or modify existing data.</p>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();

const isAdminObserver = computed(() => authStore.isAdminObserver);
const canManageEvents = computed(() => authStore.canManageEvents);

const event = ref({
  name: '',
  type: '',
  address: '',
  city: '',
  state: '',
  zipCode: '',
  startDate: '',
  endDate: '',
  categoryIds: []
})

const categories = ref([])

// State options for select dropdown
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

const fetchCategories = async () => {
  const res = await api.get('/api/categories')
  categories.value = res.data
}

const submitEvent = async () => {
  if (isAdminObserver.value || !canManageEvents.value) {
    alert('Admin Observers cannot create events. This is a view-only mode.');
    return;
  }
  
  try {
    // Combine location fields into a single location string
    const locationString = `${event.value.address}, ${event.value.city}, ${event.value.state} ${event.value.zipCode}`;
    
    // Ensure IDs are numbers
    const formattedEvent = {
      name: event.value.name,
      type: event.value.type,
      location: locationString,
      startDate: event.value.startDate,
      endDate: event.value.endDate,
      categoryIds: event.value.categoryIds.map(id => parseInt(id)),
      // Store individual location components for future use
      address: event.value.address,
      city: event.value.city,
      state: event.value.state,
      zipCode: event.value.zipCode,
      user_id: authStore.userId // Add user ID for permission checking
    }

    await api.post('/api/admin/events', formattedEvent)
    alert('Event created successfully!')
    router.push({ path: '/admin/view-events' })
  } catch (error) {
    if (error.response && error.response.status === 403) {
      alert('You do not have permission to create events.');
    } else {
      alert('Error creating event: ' + error.message)
    }
  }
}

onMounted(fetchCategories)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.event-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #5c4033;
  max-width: 750px;
  margin: auto;
  padding: 50px 20px;
  display: flex;
  justify-content: center;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
  width: 100%; 
  max-width: 750px; 
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

.description {
  color: #6c757d;
  margin-bottom: 30px;
  text-align: left; 
}

/* Observer warning styling */
.observer-warning {
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  border: 2px solid #2196f3;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
  color: #1565c0;
  text-align: center;
  font-size: 16px;
  box-shadow: 0 4px 8px rgba(33, 150, 243, 0.1);
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.location-section {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #e0e0e0;
  margin: 10px 0;
}

.section-title {
  color: #5c4033;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
  text-align: left;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .state-select {
  flex: 2;
}

.form-row input {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
}

input,
select {
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  background-color: white;
  width: 100%;
  transition: all 0.3s ease;
}

/* Disabled field styling */
.disabled-field,
input:disabled, 
select:disabled {
  background-color: #f8f9fa !important;
  color: #6c757d !important;
  cursor: not-allowed !important;
  opacity: 0.8 !important;
  border-color: #dee2e6 !important;
}

.field-label {
  text-align: left;
  margin-bottom: 8px;
  font-weight: 500;
  color: #5c4033;
}

.help-text {
  font-size: 14px;
  margin-top: 5px;
  color: #6A3E2B;
  text-align: left;
  font-style: italic;
}

.auth-actions {
  margin-top: 30px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.disabled-button {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
  background-color: #cccccc !important;
  color: #666666 !important;
}

.disabled-button:hover {
  transform: none !important;
  box-shadow: none !important;
}

.observer-notice {
  background: linear-gradient(135deg, #fff3e0, #fce4ec);
  border: 2px solid #ff9800;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  color: #e65100;
  max-width: 500px;
}

.observer-notice p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

/* Responsive design */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
  }
  
  .form-row .state-select,
  .form-row input {
    flex: none;
  }

  .event-container {
    padding: 30px 15px;
  }

  .content-box {
    padding: 25px;
  }

  .event-header {
    font-size: 24px;
    padding: 12px 25px;
  }

  .observer-warning,
  .observer-notice {
    font-size: 14px;
    padding: 15px;
  }
}
</style>