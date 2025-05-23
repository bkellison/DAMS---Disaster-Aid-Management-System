<template>
  <div class="response-detail-container">
    <div class="content-box">
      <h1 class="response-detail-header">{{ isEditing ? 'Edit Response' : 'Respond to Request' }}</h1>
      <p class="description">Please review the request details and provide your response.</p>
      
      <div v-if="requestDetails" class="request-info">
        <div class="info-section">
          <h3>{{ requestDetails.event_name }} - {{ requestDetails.category }}</h3>
          <p><strong>Quantity Requested:</strong> {{ requestDetails.quantity }}</p>
          <p v-if="requestDetails.item_name"><strong>Specific Item:</strong> {{ requestDetails.item_name }}</p>
          <p v-if="requestDetails.details"><strong>Details:</strong> {{ requestDetails.details }}</p>
        </div>
        
        <div v-if="requestDetails.is_locked" class="locked-notice">
          <p>This response has been locked and cannot be edited.</p>
        </div>
        
        <div v-else class="form-section">
          <div class="form-group">
            <label for="responseQuantity">Quantity to donate:</label>
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
            <textarea 
              v-model="responseDetails" 
              id="responseDetails" 
              rows="4" 
              placeholder="Describe your response..."></textarea>
          </div>

          <div class="button-row">
            <AppButton 
              variant="primary" 
              @click="submitResponse">
              {{ isEditing ? 'Update Response' : 'Submit Response' }}
            </AppButton>
            
            <AppButton 
              variant="cancel" 
              @click="goBack">
              Cancel
            </AppButton>
          </div>
        </div>
      </div>
      <div v-else class="loading">
        <p>Loading request details...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

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
      const responseData = await api.get(`/getResponseDetails/${responseId.value}`)
      responseDetails.value = responseData.data.message
      responseQuantity.value = responseData.data.quantity
      requestDetails.value = responseData.data.request
    } else {
      // Fetch request details for new response
      const response = await api.get(`/getRequestDetails/${requestId}`)
      requestDetails.value = response.data
      responseQuantity.value = 1
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
      
      const response = await api.post('/updateResponse', updateData)
      
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
      
      const response = await api.post('/submitResponse', responseData)
      
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

// Go back to previous page
const goBack = () => {
  router.back()
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.response-detail-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #5c4033;
  max-width: 1000px;
  margin: auto;
  padding: 50px 20px;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
}

.response-detail-header {
  background: #f5e1c5;
  padding: 15px 65px;
  border-radius: 20px;
  display: inline-block;
  font-size: 32px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 15px;
}

.description {
  color: #6c757d;
  margin-bottom: 30px;
  text-align: left;
}

.request-info {
  text-align: left;
}

.info-section {
  background: #ffffff;
  padding: 25px;
  border-radius: 10px;
  margin-bottom: 30px;
  border: 1px solid #d3c0a3;
}

.info-section h3 {
  color: #8B5E3C;
  margin-bottom: 15px;
  font-size: 22px;
}

.form-section {
  background: #ffffff;
  padding: 25px;
  border-radius: 10px;
  margin-bottom: 20px;
  border: 1px solid #d3c0a3;
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
  margin-bottom: 8px;
  font-weight: 500;
  color: #5c4033;
  font-size: 16px;
}

.button-row {
  display: flex;
  gap: 15px;
}

input, textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  background-color: #fcfcfc;
}

.loading {
  padding: 40px;
  text-align: center;
  font-size: 18px;
  color: #8B5E3C;
}

.locked-notice {
  background-color: #ffe9e3;
  color: #d32f2f;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: 500;
  border: 1px solid #ffccbc;
}
</style>