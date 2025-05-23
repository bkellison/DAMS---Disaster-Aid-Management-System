<template>
  <div class="shipping-container">
    <div class="shipping-wrapper">
      <h1 class="shipping-header">Shipping Information</h1>
      
      <div v-if="shippingInfo" class="shipping-details">
        <div class="info-section">
          <h3>Match Details</h3>
          <p><strong>Event:</strong> {{ shippingInfo.event_name }}</p>
          <p><strong>Recipient:</strong> {{ shippingInfo.recipient_name }}</p>
          <p><strong>Shipping To:</strong> {{ shippingInfo.recipient_zip }}</p>
          <p><strong>Status:</strong> {{ shippingInfo.shipping_status }}</p>
        </div>
        
        <!-- Show form for pending items or shipped items (for admin) -->
        <div class="info-section" v-if="canEditShipping">
          <h3>Update Shipping Information</h3>
          <form @submit.prevent="updateShipping">
            <div class="form-group">
              <label v-if="!isRecipient" >Shipping Address:</label>
              <textarea v-if="!isRecipient"  v-model="shippingAddress" rows="3" required></textarea>
            </div>
            
            <div v-if="!isRecipient"  class="form-group">
              <label>Tracking Number:</label>
              <input type="text" v-model="trackingNumber" />
            </div>
            
            <div v-if="!isRecipient" class="form-group">
              <label>Shipping Date:</label>
              <input type="date" v-model="shippingDate" required />
            </div>
            
            <div class="form-group">
              <label>Status:</label>
              <select v-model="shippingStatus" required>
                <option value="pending">Pending</option>
                <option v-if="!isRecipient" value="shipped">Shipped</option>
                <!-- Only show delivered option for admin users -->
                <option v-if="isRecipient || isAdmin" value="delivered">Delivered</option>
              </select>
            </div>
            
            <AppButton type="submit" variant="primary">Update Shipping</AppButton>
          </form>
        </div>
        
        <div class="info-section" v-else>
          <h3>Shipping Information</h3>
          <p><strong>Address:</strong> {{ shippingInfo.shipping_address }}</p>
          <p><strong>Tracking Number:</strong> {{ shippingInfo.tracking_number }}</p>
          <p><strong>Shipping Date:</strong> {{ shippingInfo.shipping_date }}</p>
          
          <!-- Admin button to update delivered items -->
          <AppButton 
            v-if="isAdmin && shippingInfo.shipping_status === 'delivered'" 
            variant="edit"
            @click="enableEditing">
            Edit Shipping Info
          </AppButton>
        </div>
      </div>
      
      <div v-else-if="loading">
        <p>Loading shipping information...</p>
      </div>
      
      <div v-else class="error">
        <p>Unable to load shipping information.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppButton from '@/components/common/AppButton.vue'
import axios from 'axios'
import api from '@/services/api';

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const shippingInfo = ref(null)
const loading = ref(true)
const editMode = ref(false)

// Form fields
const shippingAddress = ref('')
const trackingNumber = ref('')
const shippingDate = ref('')
const shippingStatus = ref('pending')

// Check if user is admin
const isAdmin = computed(() => authStore.role === 'Admin')
const isRecipient = computed(() => authStore.role === 'Recipient')
const isDonor = computed(() => authStore.role === 'Donor')

// Determine if editing is allowed
const canEditShipping = computed(() => {
  if (!shippingInfo.value) return false
  
  // Allow editing for pending items by anyone
  if (shippingInfo.value.shipping_status === 'pending') return true
  
  // Allow editing for shipped items by admin
  if (shippingInfo.value.shipping_status === 'shipped' && isAdmin.value) return true
  
  // Allow editing for delivered items by admin if editMode is enabled
  if (shippingInfo.value.shipping_status === 'delivered' && isAdmin.value && editMode.value) return true
  
  return false
})

// Enable editing for delivered items (admin only)
function enableEditing() {
  editMode.value = true
}

async function fetchShippingInfo() {
  try {
    const matchId = route.params.id
    console.log('Fetching shipping info for match ID:', matchId)
    const response = await api.get(`/api/getShippingInfo/${matchId}`)
    console.log('Response:', response.data)
    shippingInfo.value = response.data
    
    // Initialize form fields if data exists
    if (response.data.shipping_address) {
      shippingAddress.value = response.data.shipping_address
    }
    if (response.data.tracking_number) {
      trackingNumber.value = response.data.tracking_number
    }
    if (response.data.shipping_date) {
      shippingDate.value = response.data.shipping_date
    }
    shippingStatus.value = response.data.shipping_status
    
  } catch (error) {
    console.error('Error fetching shipping info:', error.response || error)
    console.error('Status:', error.response?.status)
    console.error('Data:', error.response?.data)
  } finally {
    loading.value = false
  }
}

async function updateShipping() {
    try {
      const matchId = route.params.id
      const data = {
        match_id: matchId,
        shipping_status: shippingStatus.value,
        tracking_number: trackingNumber.value,
        shipping_date: shippingDate.value,
        shipping_address: shippingAddress.value,
        user_id: authStore.userId
      }
      
      await api.post('/api/updateShippingStatus', data)
      alert('Shipping information updated successfully!')
      await fetchShippingInfo() // Refresh data
      
    } catch (error) {
      console.error('Error updating shipping info:', error.response?.data || error)
      if (error.response && error.response.status === 403) {
        if (authStore.role === 'Donor') {
          alert('You can only mark items as shipped. Only admins can mark items as delivered.')
        } else {
          alert(error.response.data.error || 'You do not have permission to perform this action.')
        }
      } else {
        alert('Failed to update shipping information')
      }
    }
  }

onMounted(() => {
  fetchShippingInfo()
})
</script>

<style scoped>
.shipping-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C;
  max-width: 800px;
  margin: auto;
  padding: 50px 20px;
}

.shipping-wrapper {
  background-color: #f5e1c5;
  padding: 30px;
  border-radius: 12px;
}

.shipping-header {
  background: #8B5E3C;
  color: white;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 25px;
}

.shipping-details {
  text-align: left;
}

.info-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.info-section h3 {
  color: #8B5E3C;
  margin-bottom: 15px;
  font-size: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #5c4033;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

.error {
  color: red;
  font-weight: bold;
}
</style>