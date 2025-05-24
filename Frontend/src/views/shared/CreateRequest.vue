<template>
  <div class="create-request-container">
    <div class="content-box">
      <h1 class="create-request-header">Create Request</h1>
      <p class="description">Select an event and specify your needs below.</p>
      
      <!-- Show warning for Admin Observer -->
      <div v-if="isAdminObserver" class="observer-warning">
        <strong>Admin Observer Mode:</strong> You can view this form but cannot submit requests. This is a read-only preview of the request creation process.
      </div>
      
      <form @submit.prevent="submitRequest">
        <div class="form-group">
          <label>Select Disaster Event:</label>
          <select 
            v-model="selectedEvent" 
            required 
            @change="onEventChange" 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          >
            <option value="" disabled>-- Select an event --</option>
            <option v-for="event in events" :key="event.event_id" :value="event.event_id">
              {{ event.event_name }}
            </option>
          </select>
          
          <!-- Display event location when an event is selected -->
          <div v-if="selectedEventDetails" class="event-location-display">
            <div class="location-header">
              <strong>Event Location:</strong>
            </div>
            <div class="location-details">
              {{ selectedEventDetails.location || 'Location not specified' }}
            </div>
            <div class="event-dates">
              <strong>Duration:</strong> 
              {{ formatDate(selectedEventDetails.start_date) }} - {{ formatDate(selectedEventDetails.end_date) }}
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Select Category:</label>
          <select 
            v-model="selectedCategory" 
            required 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          >
            <option value="" disabled>-- Select a category --</option>
            <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
              {{ category.category_name }}
            </option>
          </select>
        </div>

        <div class="form-group" v-if="items.length > 0">
          <label>Select Specific Item (Optional):</label>
          <select 
            v-model="selectedItem" 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          >
            <option value="">-- No specific item --</option>
            <option v-for="item in items" :key="item.item_id" :value="item.item_id">
              {{ item.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Quantity Needed:</label>
          <input 
            type="number" 
            v-model="quantity" 
            min="1" 
            required 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }" 
          />
        </div>

        <div class="form-group">
          <label>Preferred Matching Method:</label>
          <select 
            v-model="preferredMatchType" 
            required 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          >
            <option value="" disabled>-- Select matching preference --</option>
            <option v-for="matchType in matchTypes" :key="matchType.match_type_id" :value="matchType.match_type_id">
              {{ matchType.name }} - {{ matchType.description }}
            </option>
          </select>
          <p class="help-text">
            This helps administrators know your preference when automatically matching your request with available donations.
          </p>
        </div>

        <div class="form-group">
          <label>Additional Details:</label>
          <textarea 
            v-model="details" 
            rows="4" 
            placeholder="Describe your specific needs..." 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          ></textarea>
        </div>

        <div class="auth-actions">
          <AppButton 
            type="submit" 
            variant="primary" 
            :disabled="isAdminObserver || !canCreateRequests"
            :class="{ 'disabled-button': isAdminObserver }"
          >
            {{ isAdminObserver ? 'View Only Mode - Cannot Submit' : 'Submit Request' }}
          </AppButton>
          
          <div v-if="isAdminObserver" class="observer-notice">
            <p>Admin Observers can view all forms and data but cannot create new requests or modify existing data.</p>
            <p>This ensures you can monitor the system without accidentally making changes.</p>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

export default {
  components: {
    AppButton
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    // Form data
    const selectedEvent = ref('');
    const selectedCategory = ref('');
    const selectedItem = ref(null);
    const quantity = ref(1);
    const details = ref('');
    const preferredMatchType = ref('');

    // Available options
    const events = ref([]);
    const categories = ref([]);
    const items = ref([]);
    const matchTypes = ref([]);

    // Admin Observer and permission checks
    const isAdminObserver = computed(() => {
      console.log('Checking isAdminObserver:', authStore.isAdminObserver, 'Role:', authStore.role);
      return authStore.isAdminObserver;
    });

    const canCreateRequests = computed(() => {
      console.log('Checking canCreateRequests:', authStore.canCreateRequests, 'Role:', authStore.role);
      return authStore.canCreateRequests;
    });

    // Get details of the selected event
    const selectedEventDetails = computed(() => {
      if (!selectedEvent.value) return null;
      return events.value.find(event => event.event_id == selectedEvent.value);
    });

    // Format date for display
    const formatDate = (dateString) => {
      if (!dateString) return 'Not specified';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    };

    // Handle event selection change
    const onEventChange = () => {
      console.log('Event selection changed, isAdminObserver:', isAdminObserver.value);
      
      // Allow Admin Observer to view changes but don't fetch data
      if (isAdminObserver.value) {
        console.log('Admin Observer detected, not fetching categories');
        return;
      }
      
      // Clear categories and items when event changes
      categories.value = [];
      selectedCategory.value = '';
      items.value = [];
      selectedItem.value = null;
      
      // Fetch categories for the selected event
      if (selectedEvent.value) {
        fetchCategories();
      }
    };

    // Load available events and match types on mount
    onMounted(async () => {
      console.log('Component mounted, loading initial data...');
      try {
        // Load events (everyone can see events)
        const eventsResponse = await api.get('/getActiveEvents');
        events.value = eventsResponse.data || [];
        console.log('Loaded events:', events.value.length);

        // Load match types (everyone can see match types)
        const matchTypesResponse = await api.get('/getMatchTypes');
        matchTypes.value = matchTypesResponse.data || [];
        console.log('Loaded match types:', matchTypes.value.length);

        // For demo purposes, if Admin Observer, pre-select first event to show form
        if (isAdminObserver.value && events.value.length > 0) {
          selectedEvent.value = events.value[0].event_id;
          // Don't fetch categories, just show the form structure
        }
      } catch (error) {
        console.error('Error fetching initial data:', error);
        alert('Failed to load form data. Please refresh the page.');
      }
    });

    // Load categories when an event is selected
    const fetchCategories = async () => {
      if (!selectedEvent.value) return;
      
      // Admin Observer can't fetch dynamic data, but we can show them sample data
      if (isAdminObserver.value) {
        console.log('Admin Observer - not fetching categories');
        return;
      }

      console.log('Fetching categories for event:', selectedEvent.value);
      try {
        const response = await api.get(`/getEventCategories/${selectedEvent.value}`);
        categories.value = response.data || [];
        console.log('Loaded categories:', categories.value.length);
      } catch (error) {
        console.error('Error fetching categories:', error);
        alert('Failed to load categories. Please try again.');
      }
    };

    // Load items when a category is selected
    const fetchItems = async () => {
      if (!selectedCategory.value) return;
      
      // Admin Observer can't fetch dynamic data
      if (isAdminObserver.value) {
        console.log('Admin Observer - not fetching items');
        return;
      }

      console.log('Fetching items for category:', selectedCategory.value);
      try {
        const response = await api.get(`/getItemsByCategory/${selectedCategory.value}`);
        items.value = response.data || [];
        console.log('Loaded items:', items.value.length);
      } catch (error) {
        console.error('Error fetching items:', error);
        alert('Failed to load items. Please try again.');
      }
    };

    // Watch for category selection change
    watch(selectedCategory, (newValue) => {
      console.log('Category changed to:', newValue, 'isAdminObserver:', isAdminObserver.value);
      
      if (isAdminObserver.value) {
        console.log('Admin Observer - skipping item fetch');
        return;
      }
      
      if (newValue) {
        fetchItems();
        selectedItem.value = null;
      } else {
        items.value = [];
        selectedItem.value = null;
      }
    });

    // Submit the request
    const submitRequest = async () => {
      console.log('Submit request called');
      console.log('isAdminObserver:', isAdminObserver.value);
      console.log('canCreateRequests:', canCreateRequests.value);
      console.log('authStore.role:', authStore.role);

      // Check if user is Admin Observer
      if (isAdminObserver.value) {
        alert('Admin Observers cannot create requests. This is a view-only mode.');
        return;
      }

      // Check general permission
      if (!canCreateRequests.value) {
        alert('You do not have permission to create requests.');
        return;
      }

      if (!authStore.userId) {
        alert('You must be logged in to create a request.');
        router.push('/');
        return;
      }

      // Validate required fields
      if (!selectedEvent.value || !selectedCategory.value || !preferredMatchType.value) {
        alert('Please fill in all required fields.');
        return;
      }

      if (!quantity.value || quantity.value < 1) {
        alert('Please enter a valid quantity.');
        return;
      }

      const requestData = {
        user_id: authStore.userId,
        event_id: selectedEvent.value,
        category_id: selectedCategory.value,
        item_id: selectedItem.value || null,
        quantity: quantity.value,
        details: details.value,
        status: 'pending',
        preferred_match_type_id: preferredMatchType.value
      };

      console.log('Submitting request data:', requestData);

      try {
        const response = await api.post('/createRequest', requestData);

        if (response.status === 201) {
          alert('Request submitted successfully!');
          
          // Redirect based on user role
          if (authStore.role === 'Admin' || authStore.role === 'Donor') {
            router.push('/respond-to-requests');
          } else {
            router.push('/request-view');
          }
        } else {
          alert(`Error: ${response.data.message || 'An error occurred'}`);
        }
      } catch (error) {
        console.error('Error submitting request:', error);
        if (error.response && error.response.data && error.response.data.error) {
          alert(`Error: ${error.response.data.error}`);
        } else {
          alert('Error submitting request. Please try again later.');
        }
      }
    };

    return {
      selectedEvent,
      selectedCategory,
      selectedItem,
      quantity,
      details,
      preferredMatchType,
      events,
      categories,
      items,
      matchTypes,
      selectedEventDetails,
      formatDate,
      onEventChange,
      submitRequest,
      isAdminObserver,
      canCreateRequests
    };
  }
};
</script>

<style scoped>
/* Font for text */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.create-request-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C; 
  max-width: 100%; 
  padding: 50px 20px;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
  width: 700px;
  margin: 0 auto;
}

/* Create Request Header Styling */
.create-request-header {
  background: #f5e1c5; 
  padding: 15px 65px; 
  border-radius: 20px;
  display: inline-block;
  font-size: 32px; 
  font-weight: 600;
  color: #5c4033; 
  margin-bottom: 20px;
  text-align: left;
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

/* Event location display styling */
.event-location-display {
  margin-top: 15px;
  padding: 20px;
  background: linear-gradient(135deg, #e8f5e8, #f0f8f0);
  border-radius: 12px;
  border: 2px solid #2e8b57;
  text-align: left;
}

.location-header {
  font-size: 16px;
  color: #2e8b57;
  font-weight: 600;
  margin-bottom: 8px;
}

.location-details {
  font-size: 18px;
  color: #1a5c3a;
  font-weight: 500;
  margin-bottom: 10px;
  line-height: 1.4;
}

.event-dates {
  font-size: 14px;
  color: #2e8b57;
  font-style: italic;
  padding-top: 8px;
  border-top: 1px solid #c8e6c9;
}

/* Form styling */
form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: left;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Label styling */
label {
  font-size: 16px;
  font-weight: 500;
  color: #5c4033;
}

/* Input fields */
input, select, textarea {
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  background-color: white;
  width: 100%;
  transition: all 0.3s ease;
}

/* Disabled field styling */
.disabled-field,
input:disabled, 
select:disabled, 
textarea:disabled {
  background-color: #f8f9fa !important;
  color: #6c757d !important;
  cursor: not-allowed !important;
  opacity: 0.8 !important;
  border-color: #dee2e6 !important;
}

.help-text {
  font-size: 14px;
  color: #6A3E2B;
  font-style: italic;
  margin-top: 5px;
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
  margin: 8px 0;
  font-size: 14px;
  line-height: 1.5;
}

.observer-notice p:first-child {
  font-weight: 600;
  font-size: 15px;
}

/* Responsive design */
@media (max-width: 768px) {
  .content-box {
    width: 95%;
    padding: 20px;
  }
  
  .create-request-header {
    font-size: 24px;
    padding: 12px 30px;
  }
  
  .event-location-display {
    padding: 15px;
  }
  
  .location-details {
    font-size: 16px;
  }

  .observer-warning,
  .observer-notice {
    font-size: 14px;
    padding: 15px;
  }
}
</style>