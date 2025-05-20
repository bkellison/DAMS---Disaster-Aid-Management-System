<template>
  <div class="create-request-container">
    <div class="content-box">
      <h1 class="create-request-header">Create Request</h1>
      <p>Select an event and specify your needs below.</p>
      <form @submit.prevent="submitRequest">
        <div class="form-group">
          <label>Select Disaster Event:</label>
          <select v-model="selectedEvent" required>
            <option value="" disabled>-- Select an event --</option>
            <option v-for="event in events" :key="event.event_id" :value="event.event_id">
              {{ event.event_name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Select Category:</label>
          <select v-model="selectedCategory" required>
            <option value="" disabled>-- Select a category --</option>
            <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
              {{ category.category_name }}
            </option>
          </select>
        </div>

        <div class="form-group" v-if="items.length > 0">
          <label>Select Specific Item (Optional):</label>
          <select v-model="selectedItem">
            <option value="">-- No specific item --</option>
            <option v-for="item in items" :key="item.item_id" :value="item.item_id">
              {{ item.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Quantity Needed:</label>
          <input type="number" v-model="quantity" min="1" required />
        </div>

        <div class="form-group">
          <label>Additional Details:</label>
          <textarea v-model="details" rows="4" placeholder="Describe your specific needs..."></textarea>
        </div>

        <button type="submit">Submit Request</button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from "@/stores/auth";
import axios from 'axios';

export default {
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    // Form data
    const selectedEvent = ref('');
    const selectedCategory = ref('');
    const selectedItem = ref(null);
    const quantity = ref(1);
    const details = ref('');

    // Available options
    const events = ref([]);
    const categories = ref([]);
    const items = ref([]);

    // Load available events on mount
    onMounted(async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/getActiveEvents');
        events.value = response.data || [];
      } catch (error) {
        console.error('Error fetching events:', error);
      }
    });

    // Load categories when an event is selected
    const fetchCategories = async () => {
      if (!selectedEvent.value) return;

      try {
        const response = await axios.get(`http://127.0.0.1:5000/getEventCategories/${selectedEvent.value}`);
        categories.value = response.data || [];
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };

    // Load items when a category is selected
    const fetchItems = async () => {
      if (!selectedCategory.value) return;

      try {
        const response = await axios.get(`http://127.0.0.1:5000/getItemsByCategory/${selectedCategory.value}`);
        items.value = response.data || [];
      } catch (error) {
        console.error('Error fetching items:', error);
      }
    };

    // Watch for event selection change
    watch(selectedEvent, (newValue) => {
      if (newValue) {
        fetchCategories();
        categories.value = [];
        selectedCategory.value = '';
        items.value = [];
        selectedItem.value = null;
      } else {
        categories.value = [];
        items.value = [];
      }
    });

    // Watch for category selection change
    watch(selectedCategory, (newValue) => {
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
      if (!authStore.userId) {
        alert('You must be logged in to create a request.');
        router.push('/');
        return;
      }

      const requestData = {
        user_id: authStore.userId,
        event_id: selectedEvent.value,
        category_id: selectedCategory.value,
        item_id: selectedItem.value || null, // Include item_id if selected
        quantity: quantity.value,
        details: details.value,
        status: 'pending'
      };

      try {
        const response = await axios.post('http://127.0.0.1:5000/createRequest', requestData);

        if (response.status === 201) {
          alert('Request submitted successfully!');
          if(authStore.role == 'Admin' || authStore.role == 'Donor'){
            router.push('/respond-to-requests');
          }
          else {
            router.push('/request-view');
          }
          
        } else {
          alert(`Error: ${response.data.message || 'An error occurred'}`);
        }
      } catch (error) {
        console.error('Error submitting request:', error);
        alert('Error submitting request. Please try again later.');
      }
    };

    return {
      selectedEvent,
      selectedCategory,
      selectedItem,
      quantity,
      details,
      events,
      categories,
      items,
      submitRequest
    };
  }
};
</script>

<style scoped>
/* Font for text */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

/* Create Request container styling */
.create-request-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C; 
  max-width: 600px;
  margin: auto;
  padding: 50px 20px;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
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
}

/* Button styling */
button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 18px;
  margin-top: 10px;
}

button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}
</style>