<template>
  <div class="response-detail-container">
    <div class="content-box">
      <h1 class="response-detail-header">{{ isEditing ? 'Edit Pledge' : 'Create Pledge for Request' }}</h1>
      <p class="description">Please review the request details and create a pledge to help.</p>
      
      <div v-if="requestDetails" class="request-info">
        <div class="info-section">
          <h3>{{ requestDetails.event_name }} - {{ requestDetails.category }}</h3>
          <p><strong>Requested by:</strong> {{ requestDetails.requested_by }}</p>
          <p><strong>Event Location:</strong> {{ requestDetails.event_location || 'Location not specified' }}</p>
          <p><strong>Total Quantity Requested:</strong> {{ requestDetails.quantity }}</p>
          <p><strong>Quantity Still Needed:</strong> {{ requestDetails.request_quantity_remaining }}</p>
          <p v-if="requestDetails.item_name"><strong>Specific Item:</strong> {{ requestDetails.item_name }}</p>
          <p v-if="requestDetails.preferred_match_type_name">
            <strong>Preferred Matching:</strong> {{ requestDetails.preferred_match_type_name }}
            <span class="help-text"> - {{ requestDetails.preferred_match_type_description }}</span>
          </p>
          <p v-if="requestDetails.details"><strong>Details:</strong> {{ requestDetails.details }}</p>
        </div>
        
        <div v-if="requestDetails.is_locked" class="locked-notice">
          <p>This request has been fully matched and cannot receive additional pledges.</p>
        </div>
        
        <div v-else-if="requestDetails.request_quantity_remaining <= 0" class="fulfilled-notice">
          <p>This request has been fully pledged and no additional quantity is needed.</p>
        </div>
        
        <div v-else class="form-section">
          <h4>Create Your Pledge</h4>
          <p class="pledge-explanation">
            By creating a pledge, you commit to providing these items for this disaster relief effort. 
            Your pledge will be available for administrators to match with this and other similar requests.
          </p>

          <div class="form-group">
            <label for="pledgeQuantity">Quantity to pledge:</label>
            <input 
              type="number" 
              v-model.number="pledgeQuantity" 
              id="pledgeQuantity" 
              :max="Math.max(requestDetails.request_quantity_remaining, 1)" 
              :min="1" 
              required 
            />
            <div class="help-text">
              You can pledge more than what's currently needed - it will help with future similar requests.
            </div>
          </div>

          <div class="form-group">
            <label for="daysToShip">Days to ship (optional):</label>
            <input 
              type="number" 
              v-model.number="daysToShip" 
              id="daysToShip" 
              :min="1" 
              :max="30"
              placeholder="How many days to ship after matching"
            />
            <div class="help-text">
              Leave blank if shipping time is flexible. This helps with priority matching.
            </div>
          </div>

          <div class="form-group">
            <label for="pledgeNotes">Additional Notes (optional):</label>
            <textarea 
              v-model="pledgeNotes" 
              id="pledgeNotes" 
              rows="3" 
              placeholder="Any additional information about your pledge..."></textarea>
          </div>

          <div class="form-group">
            <div class="auto-match-option">
              <label>
                <input 
                  type="checkbox" 
                  v-model="autoMatchRequested"
                />
                Request automatic matching for this specific request
              </label>
              <div class="help-text">
                If checked, administrators will be notified to prioritize matching your pledge with this specific request.
              </div>
            </div>
          </div>

          <div class="button-row">
            <AppButton 
              variant="primary" 
              @click="createPledge"
              :disabled="isSubmitting">
              {{ isSubmitting ? 'Creating Pledge...' : 'Create Pledge' }}
            </AppButton>
            
            <AppButton 
              variant="secondary" 
              @click="createPledgeAndMatch"
              :disabled="isSubmitting || !authStore.isAdmin">
              Create Pledge & Auto-Match
            </AppButton>
            
            <AppButton 
              variant="cancel" 
              @click="goBack">
              Cancel
            </AppButton>
          </div>
        </div>

        <!-- Show existing pledges for this item if any -->
        <div v-if="existingPledges.length > 0" class="existing-pledges">
          <h4>Your Existing Pledges for {{ requestDetails.item_name || requestDetails.category }}</h4>
          <div class="pledge-list">
            <div v-for="pledge in existingPledges" :key="pledge.pledge_id" class="pledge-item">
              <div class="pledge-info">
                <strong>{{ pledge.item_name }}</strong> - 
                Pledged: {{ pledge.item_quantity }} | 
                Available: {{ pledge.items_left }} |
                Status: {{ pledge.pledge_status }}
              </div>
              <AppButton 
                variant="edit" 
                size="small"
                @click="editExistingPledge(pledge.pledge_id)"
                :disabled="pledge.items_left === 0">
                {{ pledge.items_left === 0 ? 'Fully Used' : 'Edit Pledge' }}
              </AppButton>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="loading">
        <div class="spinner"></div>
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
const pledgeQuantity = ref(1)
const daysToShip = ref(null)
const pledgeNotes = ref('')
const autoMatchRequested = ref(false)
const isSubmitting = ref(false)
const existingPledges = ref([])

// Fetch request details and check for existing pledges
onMounted(async () => {
  const requestId = route.params.id
  
  try {
    // Fetch request details
    const response = await api.get(`/getRequestDetails/${requestId}`)
    requestDetails.value = response.data
    
    // Set default pledge quantity to what's still needed (but allow more)
    if (requestDetails.value.request_quantity_remaining > 0) {
      pledgeQuantity.value = Math.min(requestDetails.value.request_quantity_remaining, 10) // Cap at 10 for UX
    }

    // If there's a specific item, check for existing pledges from this donor
    if (requestDetails.value.item_name && authStore.userId) {
      await fetchExistingPledges()
    }
  } catch (error) {
    console.error('Error fetching request details:', error)
    alert('Error loading request details. Please try again.')
  }
})

// Fetch existing pledges for this item from current user
const fetchExistingPledges = async () => {
  try {
    const response = await api.get(`/getPledges?user_id=${authStore.userId}`)
    existingPledges.value = response.data.filter(pledge => 
      pledge.item_id === requestDetails.value.item_id && 
      pledge.items_left > 0 // Only show pledges with available quantity
    )
  } catch (error) {
    console.error('Error fetching existing pledges:', error)
  }
}

// Create the pledge
const createPledge = async () => {
  if (!validateForm()) return
  
  isSubmitting.value = true
  
  try {
    const pledgeData = {
      user_id: authStore.userId,
      selected_category_id: requestDetails.value.category_id,
      selected_item_id: requestDetails.value.item_id,
      item_quantity: pledgeQuantity.value,
      days_to_ship: daysToShip.value
    }
    
    const response = await api.post('/createPledge', pledgeData)
    
    if (response.status === 201) {
      let successMessage = 'Pledge created successfully!'
      
      if (autoMatchRequested.value) {
        successMessage += ' Administrators have been notified to prioritize matching this pledge.'
      }
      
      alert(successMessage)
      
      // Redirect based on user role
      if (authStore.isAdmin) {
        router.push('/respond-to-requests')
      } else {
        router.push('/pledge-view')
      }
    } else {
      alert('Error creating pledge: ' + (response.data?.error || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error creating pledge:', error)
    if (error.response?.data?.error) {
      alert('Error: ' + error.response.data.error)
    } else {
      alert('Error creating pledge. Please try again later.')
    }
  } finally {
    isSubmitting.value = false
  }
}

// Create pledge and attempt auto-match (Admin only)
const createPledgeAndMatch = async () => {
  if (!authStore.isAdmin) {
    alert('Only administrators can use auto-matching.')
    return
  }
  
  if (!validateForm()) return
  
  isSubmitting.value = true
  
  try {
    // First create the pledge
    const pledgeData = {
      user_id: authStore.userId,
      selected_category_id: requestDetails.value.category_id,
      selected_item_id: requestDetails.value.item_id,
      item_quantity: pledgeQuantity.value,
      days_to_ship: daysToShip.value
    }
    
    const pledgeResponse = await api.post('/createPledge', pledgeData)
    
    if (pledgeResponse.status === 201) {
      // Then attempt auto-match
      const autoMatchData = {
        request_id: route.params.id,
        match_type_name: requestDetails.value.preferred_match_type_name || 'fulfillment',
        inventory_priority: 'pledges' // Prioritize the pledge we just created
      }
      
      try {
        const matchResponse = await api.post('/api/autoMatch', autoMatchData)
        alert('Pledge created and auto-match completed successfully!')
      } catch (matchError) {
        console.error('Auto-match failed:', matchError)
        alert('Pledge created successfully, but auto-match failed. Please manually match the pledge.')
      }
      
      router.push('/respond-to-requests')
    } else {
      alert('Error creating pledge: ' + (pledgeResponse.data?.error || 'Unknown error'))
    }
  } catch (error) {
    console.error('Error creating pledge:', error)
    if (error.response?.data?.error) {
      alert('Error: ' + error.response.data.error)
    } else {
      alert('Error creating pledge. Please try again later.')
    }
  } finally {
    isSubmitting.value = false
  }
}

// Edit an existing pledge
const editExistingPledge = (pledgeId) => {
  router.push(`/pledge-view?edit=${pledgeId}`)
}

// Form validation
const validateForm = () => {
  if (!pledgeQuantity.value || pledgeQuantity.value < 1) {
    alert('Please enter a valid quantity (at least 1).')
    return false
  }
  
  if (daysToShip.value && (daysToShip.value < 1 || daysToShip.value > 30)) {
    alert('Days to ship must be between 1 and 30.')
    return false
  }
  
  if (!authStore.userId) {
    alert('You must be logged in to create a pledge.')
    return false
  }
  
  return true
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

.form-section h4 {
  color: #5c4033;
  margin-bottom: 15px;
  font-size: 18px;
}

.pledge-explanation {
  background-color: #e8f4fd;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #007bff;
  font-size: 14px;
  color: #0056b3;
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

.help-text {
  font-size: 13px;
  color: #666;
  margin-top: 5px;
  font-style: italic;
}

.auto-match-option {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auto-match-option label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  cursor: pointer;
}

.auto-match-option input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.button-row {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(139, 94, 60, 0.3);
  border-radius: 50%;
  border-top-color: #8B5E3C;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.locked-notice,
.fulfilled-notice {
  background-color: #ffe9e3;
  color: #d32f2f;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: 500;
  border: 1px solid #ffccbc;
}

.fulfilled-notice {
  background-color: #e8f5e8;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.existing-pledges {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  margin-top: 30px;
  border: 1px solid #e9ecef;
}

.existing-pledges h4 {
  color: #5c4033;
  margin-bottom: 15px;
}

.pledge-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pledge-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #d3c0a3;
}

.pledge-info {
  flex: 1;
  color: #5c4033;
  font-size: 14px;
}

/* Responsive design */
@media (max-width: 768px) {
  .button-row {
    flex-direction: column;
  }
  
  .pledge-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .response-detail-header {
    font-size: 24px;
    padding: 12px 30px;
  }
}
</style>