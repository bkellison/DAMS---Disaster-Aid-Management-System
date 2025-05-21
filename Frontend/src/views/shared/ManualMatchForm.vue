<template>
  <div class="match-container">
    <div class="content-box">
      <h1 class="match-header">Create Manual Match</h1>
      
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
          <h3>Select a Pledge to Match</h3>
          
          <!-- No matching pledges message -->
          <div v-if="matchingPledges.length === 0" class="no-pledges-message">
            No pledges match the requested item.
          </div>
          
          <!-- Pledge selection -->
          <div v-else class="pledge-selection">
            <div v-for="pledge in matchingPledges" :key="pledge.pledge_id" class="pledge-option">
              <button 
                class="pledge-btn" 
                :class="{ 'selected': selectedPledge && selectedPledge.pledge_id === pledge.pledge_id }"
                @click="selectPledge(pledge)"
              >
                {{ pledge.item_name }} 
                <span class="quantity-badge">Available: {{ pledge.items_left }}</span>
              </button>
            </div>
          </div>
          
          <!-- Match quantity section (only shown when a pledge is selected) -->
          <div v-if="selectedPledge" class="match-details">
            <h3>Match Details</h3>
            <p><strong>Selected Item:</strong> {{ selectedPledge.item_name }}</p>
            
            <div class="form-group">
              <label for="match-quantity">Match Quantity:</label>
              <input 
                type="number" 
                id="match-quantity"
                v-model="selectedPledgeMatchCount" 
                min="1" 
                :max="Math.min(selectedPledge.items_left, selectedRequest.request_quantity_remaining)" 
              />
            </div>
            
            <div class="button-group">
              <button class="submit-btn" @click="createManualMatch(selectedRequest)">Create Match</button>
              <button class="cancel-btn" @click="goBack">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const selectedRequest = ref({});
const pledges = ref([]);
const selectedPledge = ref(null);
const selectedPledgeMatchCount = ref(1);

// Compute matching pledges - only show pledges for the requested item
const matchingPledges = computed(() => {
  return pledges.value.filter(p => p.item_id == selectedRequest.value.item_id && p.items_left > 0);
});

// Select a pledge
const selectPledge = (pledge) => {
  selectedPledge.value = pledge;
  // Set default match count to either all remaining in the request or all available in the pledge (whichever is smaller)
  selectedPledgeMatchCount.value = Math.min(
    pledge.items_left, 
    selectedRequest.value.request_quantity_remaining || 1
  );
};

// Get all pledges
async function getPledges() {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/getPledges?user_id=${authStore.userId}`);
    pledges.value = response.data.filter(i => i.items_left > 0);
  } catch (error) {
    console.error('Error getting pledges:', error);
  }
}

// Get specific request by ID
async function getRequestId(requestId) {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/getRequests?user_id=${authStore.userId}&request_id=${requestId}`);
    if(response.data.length > 0) {
      selectedRequest.value = response.data[0];
    }
  } catch (error) {
    console.error('Error getting request details:', error);
  }
}

// Create the match
async function createManualMatch(selectedRequest) {
  if (!selectedPledge.value) {
    alert('Please select a pledge first');
    return;
  }
  
  if (!selectedPledgeMatchCount.value || selectedPledgeMatchCount.value < 1) {
    alert('Please enter a valid quantity');
    return;
  }
  
  try {
    const matchRequest = {
      requestId: selectedRequest.request_id,
      pledgeId: selectedPledge.value.pledge_id,
      matchQuantity: selectedPledgeMatchCount.value
    };
    
    await axios.post('http://127.0.0.1:5000/createMatch', matchRequest);
    alert('Match created successfully!');
    router.push({ path: `/match-view` });
  } catch (error) {
    console.error('Match Creation Failed', error);
    alert('Failed to create match. Please try again.');
  }
}

// Go back to previous page
const goBack = () => {
  router.back();
};

// Ensure match count is valid
watch(selectedPledgeMatchCount, (value) => {
  const num = parseInt(value);
  
  if (!value || isNaN(num) || num < 1) {
    selectedPledgeMatchCount.value = 1;
  } else if (selectedPledge.value && num > selectedPledge.value.items_left) {
    selectedPledgeMatchCount.value = selectedPledge.value.items_left;
  } else if (selectedRequest.value && num > selectedRequest.value.request_quantity_remaining) {
    selectedPledgeMatchCount.value = selectedRequest.value.request_quantity_remaining;
  }
});

// Load initial data
onMounted(() => {
  const requestId = route.params.id;
  getRequestId(requestId);
  getPledges();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.match-container {
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

.match-header {
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

.info-section h3, .form-section h3, .match-details h3 {
  color: #8B5E3C;
  margin-bottom: 15px;
  font-size: 22px;
}

.no-matches-message, .no-pledges-message {
  background-color: #ffecb3;
  color: #856404;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: 500;
  border: 1px solid #ffeeba;
  text-align: center;
}

.pledge-selection {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.pledge-option {
  flex: 1 0 calc(50% - 10px);
  min-width: 200px;
}

.pledge-btn {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  background-color: #f9f3e8;
  color: #5c4033;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pledge-btn:hover {
  background-color: #f5e1c5;
  transform: translateY(-2px);
}

.pledge-btn.selected {
  background-color: #8B5E3C;
  color: white;
  border-color: #6A3E2B;
}

.quantity-badge {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 14px;
  white-space: nowrap;
}

.pledge-btn.selected .quantity-badge {
  background-color: rgba(255, 255, 255, 0.2);
}

.match-details {
  background: #ffffff;
  padding: 25px;
  border-radius: 10px;
  margin-top: 20px;
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

input {
  width: 100%;
  max-width: 200px;
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  background-color: #fcfcfc;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.submit-btn, .cancel-btn {
  padding: 12px 25px;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  border: none;
}

.submit-btn {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  color: white;
}

.submit-btn:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}

.cancel-btn {
  background: #e0e0e0;
  color: #333;
}

.cancel-btn:hover {
  background: #d0d0d0;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .pledge-option {
    flex: 1 0 100%;
  }
  
  .content-box {
    padding: 20px;
  }
  
  .match-header {
    font-size: 24px;
    padding: 12px 30px;
  }
}
</style>