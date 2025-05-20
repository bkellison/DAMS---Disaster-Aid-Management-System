<template>
  <div class="auto-match-container">
    <div class="content-box">
      <h1 class="auto-match-header">Initiate Auto Match</h1>
      
      <div v-if="selectedRequest.request_quantity_remaining < 1" class="no-matches-message">
        Request has enough pledges and matches to fulfill.
      </div>
      
      <div v-else>
        <div class="info-section">
          <h3>Request Details</h3>
          <p><strong>Event:</strong> {{ selectedRequest.event_name }}</p>
          <p><strong>Category:</strong> {{ selectedRequest.category_name }}</p>
          <p v-if="selectedRequest.item_name"><strong>Specific Item:</strong> {{ selectedRequest.item_name }}</p>
          <p><strong>Quantity Requested:</strong> {{ selectedRequest.request_quantity }}</p>
          <p><strong>Quantity Remaining:</strong> {{ selectedRequest.request_quantity_remaining }}</p>
          <p v-if="selectedRequest.requester_zipcode"><strong>Recipient Location:</strong> {{ selectedRequest.requester_zipcode }}</p>
          <p v-if="selectedRequest.request_details"><strong>Details:</strong> {{ selectedRequest.request_details }}</p>
        </div>
        
        <div class="form-section">
          <h3>Select Auto-Match Method</h3>
          <p class="helper-text">Choose a matching algorithm to automatically pair this request with available pledges.</p>
          
          <div class="match-options">
            <div v-for="matchType in matchTypes" :key="matchType.match_type_id" class="match-option">
              <button class="match-btn" @click="createAutoMatch(selectedRequest, matchType)">
                <span class="match-name">{{ capitalizeFirstLetter(matchType.name) }}</span>
                <span class="match-description">{{ matchType.description }}</span>
              </button>
            </div>
          </div>
          
          <div class="button-group">
            <button class="cancel-btn" @click="goBack">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const matchTypes = ref([]);
const selectedRequest = ref({});

// Helper function to capitalize first letter
function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

// Get auto-match algorithms
async function getMatchType() {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/api/getAutoMatchType`);
    if (response.data.length > 0) {
      matchTypes.value = response.data;
    }
  } catch (error) {
    console.error('Error getting match types:', error);
  }
}

// Get request details
async function getRequestId(requestId) {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/getRequests?user_id=${authStore.userId}&request_id=${requestId}`);
    if (response.data.length > 0) {
      selectedRequest.value = response.data[0];
    }
  } catch (error) {
    console.error('Error getting request id:', error);
  }
}

// Create auto match
async function createAutoMatch(selectedRequest, matchType) {
  try {
    const matchRequest = {
      request_id: selectedRequest.request_id,
      match_type_name: matchType.name
    };
    
    const response = await axios.post('http://127.0.0.1:5000/api/autoMatch', matchRequest);
    
    if (response.status === 200) {
      alert(response.data.message);
      router.push({ path: `/match-view` });
    }
  } catch (error) {
    console.error('Match Creation Failed', error);
    
    if (error.response) {
      if (error.response.status === 400) {
        alert('No pledges available to match with this request.');
      } else {
        alert(`Error: ${error.response.data.message || 'Failed to create match'}`);
      }
    } else {
      alert('Failed to create match. Please try again.');
    }
    
    router.push({ path: `/respond-to-requests` });
  }
}

// Go back function
const goBack = () => {
  router.back();
};

// Initialize page data
onMounted(() => {
  const requestId = route.params.id;
  getRequestId(requestId);
  getMatchType();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.auto-match-container {
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

.auto-match-header {
  background: #f5e1c5;
  padding: 15px 65px;
  border-radius: 20px;
  display: inline-block;
  font-size: 32px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 30px;
}

.info-section, .form-section {
  background: #ffffff;
  padding: 25px;
  border-radius: 10px;
  margin-bottom: 30px;
  border: 1px solid #d3c0a3;
  text-align: left;
}

.info-section h3, .form-section h3 {
  color: #8B5E3C;
  margin-bottom: 15px;
  font-size: 22px;
}

.no-matches-message {
  background-color: #ffecb3;
  color: #856404;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: 500;
  border: 1px solid #ffeeba;
  text-align: center;
}

.helper-text {
  color: #666;
  margin-bottom: 20px;
  font-size: 16px;
}

.match-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 25px;
}

.match-btn {
  width: 100%;
  padding: 20px;
  background: linear-gradient(to right, #f5e1c5, #f9f3e8);
  border: 1px solid #d3c0a3;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.match-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  background: linear-gradient(to right, #f0d5b0, #f5e1c5);
}

.match-name {
  font-size: 18px;
  font-weight: 600;
  color: #5c4033;
}

.match-description {
  font-size: 14px;
  color: #666;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn {
  padding: 12px 25px;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: background-color 0.3s;
  border: none;
  background: #e0e0e0;
  color: #333;
  min-width: 120px;
}

.cancel-btn:hover {
  background: #d0d0d0;
}

@media (max-width: 768px) {
  .content-box {
    padding: 20px;
  }
  
  .auto-match-header {
    font-size: 24px;
    padding: 12px 30px;
  }
  
  .match-btn {
    padding: 15px;
  }
}
</style>