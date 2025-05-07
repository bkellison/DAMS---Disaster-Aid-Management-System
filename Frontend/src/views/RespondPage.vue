<template>
  <div class="response-detail-container">
    <h1 class="response-detail-header">{{ isEditing ? 'Edit Response' : 'Respond to Request' }}</h1>
    <div v-if="requestDetails">
      <h3>{{ requestDetails.event_name }} - {{ requestDetails.category_name }}</h3>
      <p>Quantity Requested: {{ requestDetails.quantity }}</p>
      <p>Details: {{ requestDetails.details }}</p>
      
      <div v-if="requestDetails.is_locked" class="locked-notice">
        <p>This response has been locked and cannot be edited.</p>
      </div>
      
      <div v-else>
        <div class="form-group">
          <label for="responseQuantity">Quantity left to donate:</label>
          <input 
            type="number" 
            v-model="responseQuantity" 
            id="responseQuantity" 
            :max="requestDetails.request_quantity_remaining" 
            :min="1" 
            required 
          />
        </div>

        <div class="form-group">
          <label for="responseDetails">Response Details:</label>
          <textarea v-model="responseDetails" id="responseDetails" rows="4" placeholder="Describe your response..."></textarea>
        </div>

        <button @click="submitResponse">
          {{ isEditing ? 'Update Response' : 'Submit Response' }}
        </button>
      </div>
    </div>
    <div v-else>
      <p>Loading request details...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from "@/stores/auth"
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const requestDetails = ref(null)
const responseDetails = ref('')
const responseQuantity = ref(1)
const isEditing = ref(false)
const responseId = ref(null)

// Fetch request details or existing response
onMounted(async () => {
  const requestId = route.params.id
  
  try {
    // Check if this is an edit operation (if responseId is in query params)
    if (route.query.responseId) {
      isEditing.value = true
      responseId.value = route.query.responseId
      
      // Fetch existing response data
      const responseData = await axios.get(`http://127.0.0.1:5000/getResponseDetails/${responseId.value}`)
      responseDetails.value = responseData.data.message
      responseQuantity.value = responseData.data.quantity
      requestDetails.value = responseData.data.request
    } else {
      // Fetch request details for new response
      const response = await axios.get(`http://127.0.0.1:5000/getRequestDetails/${requestId}`)
      requestDetails.value = response.data
      responseQuantity.value = response.data.quantity
    }
  } catch (error) {
    console.error('Error fetching details:', error)
  }
})

// Submit or update the response
const submitResponse = async () => {
  const requestId = route.params.id
  
  try {
    if (isEditing.value) {
      // Update existing response
      const updateData = {
        response_id: responseId.value,
        quantity: responseQuantity.value,
        message: responseDetails.value
      }
      
      const response = await axios.post('http://127.0.0.1:5000/updateResponse', updateData)
      
      if (response.status === 200) {
        alert('Response updated successfully!')
        router.push('/donor')
      } else {
        alert('Error updating response: ' + response.data.error)
      }
    } else {
      // Create new response
      const responseData = {
        request_id: requestId,
        donor_id: authStore.userId,
        quantity: responseQuantity.value,
        message: responseDetails.value
      }
      
      const response = await axios.post('http://127.0.0.1:5000/submitResponse', responseData)
      
      if (response.status === 200 || response.status === 201) {
        alert('Response submitted successfully!')
        router.push('/donor')
      } else {
        alert('Error submitting response.')
      }
    }
  } catch (error) {
    console.error('Error:', error)
    if (error.response && error.response.status === 403) {
      alert('This response is locked and cannot be edited.')
    } else {
      alert('Error ' + (isEditing.value ? 'updating' : 'submitting') + ' response. Please try again later.')
    }
  }
}
</script>

<style scoped>
.response-detail-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C;
  max-width: 800px;
  margin: auto;
  padding: 50px 20px;
}

.response-detail-header {
  background: #f5e1c5;
  padding: 15px 65px;
  border-radius: 20px;
  display: inline-block;
  font-size: 32px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
}

.form-group label {
  text-align: left;
  margin-bottom: 5px;
  font-weight: 500;
}

input, textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
}

button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: transform 0.2s ease-in-out, background-color 0.3s;
}

button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}
</style>