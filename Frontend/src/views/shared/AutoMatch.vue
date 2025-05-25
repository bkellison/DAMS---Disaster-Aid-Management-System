<template>
  <div class="auto-match-container">
    <div class="content-box">
      <h1 class="auto-match-header">Auto Match</h1>
      
      <!-- Admin Observer Warning -->
      <div v-if="isAdminObserver" class="observer-warning">
        <strong>Admin Observer Mode:</strong> You can view the auto-matching interface but cannot create matches. This is a read-only preview of the automatic matching process.
      </div>
      
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
          
          <p v-if="selectedRequest.preferred_match_type_name">
            <strong>Recipient's Preferred Method:</strong> {{ capitalizeFirstLetter(selectedRequest.preferred_match_type_name) }}
          </p>
        </div>

        <div class="inventory-breakdown">
          <h4>Available Inventory</h4>
          <div class="inventory-stats">
            <div class="inventory-stat">
              <span class="stat-label">Total Available:</span>
              <span class="stat-value">{{ combinedOptions.total_available }} items</span>
            </div>
            <div class="inventory-stat">
              <span class="stat-label">Admin Inventory:</span>
              <span class="stat-value">{{ combinedOptions.base_quantity }} items</span>
            </div>
            <div class="inventory-stat">
              <span class="stat-label">From Pledges:</span>
              <span class="stat-value">{{ combinedOptions.total_from_pledges }} items</span>
            </div>
          </div>
        </div>
        
        <div v-if="combinedOptions.total_available === 0" class="no-pledges-message">
          No inventory or pledges available for this item type. Please check back later or add more pledges.
        </div>
        
        <div v-else-if="combinedOptions.total_available < selectedRequest.request_quantity_remaining" class="partial-match-message">
          <p><strong>Note:</strong> Only {{ combinedOptions.total_available }} items are available of the {{ selectedRequest.request_quantity_remaining }} still needed. 
          This will be a partial match.</p>
        </div>
        
        <div class="form-section" v-if="combinedOptions.total_available > 0">
          <h3>Select Auto-Match Method</h3>
          <p class="helper-text">Choose how you want the system to match this request with available inventory sources.</p>
          
          <div class="priority-selection">
            <h4>Inventory Priority</h4>
            <p class="help-text">Select which inventory source should be prioritized when matching.</p>
            
            <div class="radio-group">
              <div class="radio-option">
                <input 
                  type="radio" 
                  id="priority-admin" 
                  value="admin" 
                  v-model="inventoryPriority"
                  :disabled="combinedOptions.base_quantity === 0 || isAdminObserver"
                  :class="{ 'disabled-field': isAdminObserver }"
                />
                <label for="priority-admin" :class="{ 'disabled-label': isAdminObserver }">Admin Inventory First</label>
                <span class="option-description" :class="{ 'disabled-text': isAdminObserver }">Use admin inventory before donor pledges</span>
              </div>
              
              <div class="radio-option">
                <input 
                  type="radio" 
                  id="priority-pledges" 
                  value="pledges" 
                  v-model="inventoryPriority"
                  :disabled="combinedOptions.total_from_pledges === 0 || isAdminObserver"
                  :class="{ 'disabled-field': isAdminObserver }"
                />
                <label for="priority-pledges" :class="{ 'disabled-label': isAdminObserver }">Donor Pledges First</label>
                <span class="option-description" :class="{ 'disabled-text': isAdminObserver }">Use donor pledges before admin inventory</span>
              </div>
              
              <div class="radio-option">
                <input 
                  type="radio" 
                  id="priority-auto" 
                  value="auto" 
                  v-model="inventoryPriority"
                  :disabled="isAdminObserver"
                  :class="{ 'disabled-field': isAdminObserver }"
                />
                <label for="priority-auto" :class="{ 'disabled-label': isAdminObserver }">Automatic (Recommended)</label>
                <span class="option-description" :class="{ 'disabled-text': isAdminObserver }">Let the system decide the optimal source based on match method</span>
              </div>
            </div>
          </div>
          
          <h4>Match Algorithms</h4>
          <div class="match-options">
            <div v-for="matchType in matchTypes" :key="matchType.match_type_id" class="match-option">
              <button 
                :class="[
                  'match-btn',
                  { 'match-btn-preferred': isPreferredMethod(matchType) },
                  { 'disabled-button': isAdminObserver }
                ]"
                :disabled="isAdminObserver || !canCreateMatches"
                @click="createAutoMatch(selectedRequest, matchType)"
                :title="isAdminObserver ? 'Admin Observers cannot create matches' : `Create auto match using ${matchType.name} algorithm`"
              >
                <span class="match-name">
                  {{ isAdminObserver ? 'View Only - ' : '' }}{{ capitalizeFirstLetter(matchType.name) }}
                </span>
                <span class="match-description">{{ matchType.description }}</span>
                <span v-if="isPreferredMethod(matchType)" class="preferred-badge">Recipient's Preference</span>
              </button>
            </div>
          </div>
          
          <div v-if="isAdminObserver" class="observer-notice">
            <p>Admin Observers can view the auto-matching interface and see all available algorithms and inventory.</p>
            <p>However, you cannot create matches or modify data. This ensures you can monitor the system without making changes.</p>
          </div>
          
          <div class="button-group">
            <AppButton variant="cancel" @click="goBack">{{ isAdminObserver ? 'Back to View' : 'Cancel' }}</AppButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppButton from '@/components/common/AppButton.vue'; 
import api from '@/services/api';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const isAdminObserver = computed(() => authStore.isAdminObserver);
const canCreateMatches = computed(() => authStore.canCreateMatches);

const matchTypes = ref([]);
const selectedRequest = ref({});
const combinedOptions = ref({
  base_quantity: 0,
  total_from_pledges: 0,
  total_available: 0,
  available_pledges: []
});
const inventoryPriority = ref('auto'); // Default to auto

// Check if a match type is the preferred one
const isPreferredMethod = (matchType) => {
  return selectedRequest.value.preferred_match_type_id === matchType.match_type_id;
};

// Helper function to capitalize first letter
function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

// Get auto-match algorithms
async function getMatchType() {
  try {
    const response = await api.get(`/api/getAutoMatchType`);
    if (response.data.length > 0) {
      matchTypes.value = response.data;
    }
  } catch (error) {
    console.error('Error getting match types:', error);
  }
}

// Get request details
async function getRequestDetails(requestId) {
  try {
    const response = await api.get(`/getRequests?user_id=${authStore.userId}&request_id=${requestId}`);
    if (response.data.length > 0) {
      selectedRequest.value = response.data[0];
      
      // Now fetch the combined inventory options
      await getCombinedOptions(requestId);
    }
  } catch (error) {
    console.error('Error getting request details:', error);
  }
}

// Get combined inventory options (admin + pledges)
async function getCombinedOptions(requestId) {
  try {
    const response = await api.get(`/getCombinedMatchOptions?request_id=${requestId}`);
    combinedOptions.value = response.data;
    
    // Set the default inventory priority based on what's available
    if (combinedOptions.value.base_quantity === 0) {
      inventoryPriority.value = 'pledges';
    } else if (combinedOptions.value.total_from_pledges === 0) {
      inventoryPriority.value = 'admin';
    }
  } catch (error) {
    console.error('Error getting combined inventory options:', error);
    
    // Fallback with empty data if API call fails
    combinedOptions.value = {
      base_quantity: 0,
      total_from_pledges: 0,
      total_available: 0,
      available_pledges: []
    };
  }
}

// Create auto match
async function createAutoMatch(selectedRequest, matchType) {
  if (isAdminObserver.value) {
    alert('Admin Observers cannot create matches.');
    return;
  }
  
  try {
    const matchRequest = {
      request_id: selectedRequest.request_id,
      match_type_name: matchType.name,
      inventory_priority: inventoryPriority.value
    };
    
    const response = await api.post('/api/autoMatch', matchRequest);
    
    if (response.status === 200) {
      alert(response.data.message || 'Match created successfully!');
      router.push({ path: `/match-view` });
    }
  } catch (error) {
    console.error('Match Creation Failed', error);
    
    if (error.response) {
      if (error.response.status === 400) {
        alert('No inventory or pledges available to match with this request.');
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
  getRequestDetails(requestId);
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
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 28px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 30px;
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

.preferred-match-info {
  background-color: #f5e1c5;
  border-radius: 8px;
  padding: 15px;
  margin: 15px 0;
  border: 1px solid #d3c0a3;
}

.inventory-breakdown {
  background-color: #e6f7ef;
  border: 1px solid #8fcea5;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 25px;
}

.inventory-breakdown h4 {
  color: #2e8b57;
  margin-bottom: 15px;
  text-align: center;
  font-size: 18px;
}

.inventory-stats {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 15px;
}

.inventory-stat {
  flex: 1;
  min-width: 150px;
  background-color: rgba(255, 255, 255, 0.7);
  padding: 12px;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #5c4033;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #2e8b57;
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

.partial-match-message {
  background-color: #fff3cd;
  color: #856404;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: left;
}

.helper-text {
  color: #666;
  margin-bottom: 20px;
  font-size: 16px;
}

.help-text {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
  font-style: italic;
}

.priority-selection {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.priority-selection h4 {
  color: #5c4033;
  margin-bottom: 10px;
  font-size: 18px;
}

.radio-group {
  margin-top: 15px;
}

.radio-option {
  margin-bottom: 15px;
  padding: 12px;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e0d4c3;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transition: all 0.3s ease;
}

.radio-option input[type="radio"] {
  margin-right: 10px;
}

.radio-option label {
  font-weight: 600;
  color: #5c4033;
  margin-left: 24px;
  margin-top: -20px;
  display: block;
  margin-bottom: 5px;
  transition: color 0.3s ease;
}

.option-description {
  font-size: 14px;
  color: #666;
  margin-left: 24px;
  transition: color 0.3s ease;
}

/* Disabled radio option styling */
.radio-option input[type="radio"]:disabled + label,
.radio-option input[type="radio"]:disabled ~ .option-description {
  color: #aaa;
}

.disabled-field {
  opacity: 0.6;
  cursor: not-allowed;
}

.disabled-label {
  color: #aaa !important;
  cursor: not-allowed;
}

.disabled-text {
  color: #ccc !important;
  cursor: not-allowed;
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
  position: relative;
}

.match-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  background: linear-gradient(to right, #f0d5b0, #f5e1c5);
}

.match-btn-preferred {
  background: linear-gradient(to right, #d4b896, #c9a876) !important;
  border: 2px solid #a88b5a !important;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15) !important;
}

.match-btn-preferred:hover:not(:disabled) {
  background: linear-gradient(to right, #c9a876, #b8975c) !important;
  transform: translateY(-4px) !important;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2) !important;
}

/* Disabled button styling */
.disabled-button,
.match-btn:disabled {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
  background: #cccccc !important;
  color: #666666 !important;
}

.disabled-button:hover,
.match-btn:disabled:hover {
  transform: none !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
  background: #cccccc !important;
}

.match-name {
  font-size: 18px;
  font-weight: 600;
  color: #5c4033;
}

.disabled-button .match-name,
.match-btn:disabled .match-name {
  color: #666666 !important;
}

.match-description {
  font-size: 14px;
  color: #666;
}

.disabled-button .match-description,
.match-btn:disabled .match-description {
  color: #999999 !important;
}

.preferred-badge {
  background-color: #28a745;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 5px;
  display: inline-block;
}

.disabled-button .preferred-badge,
.match-btn:disabled .preferred-badge {
  background-color: #999999 !important;
}

.observer-notice {
  background: linear-gradient(135deg, #fff3e0, #fce4ec);
  border: 2px solid #ff9800;
  border-radius: 10px;
  padding: 20px;
  margin-top: 30px;
  text-align: center;
  color: #e65100;
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

.button-group {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
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
  
  .inventory-stats {
    flex-direction: column;
  }
  
  .inventory-stat {
    min-width: auto;
  }

  .observer-warning,
  .observer-notice {
    font-size: 14px;
    padding: 15px;
  }
}
</style>