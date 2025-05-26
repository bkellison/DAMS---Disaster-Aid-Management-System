<template> 
  <div class="match-container">
    <div class="content-box">
      <h1 class="match-header">Create Manual Match</h1>
      
      <!-- Admin Observer Warning -->
      <div v-if="isAdminObserver" class="observer-warning">
        <strong>Admin Observer Mode:</strong> You can view the matching interface but cannot create matches. This is a read-only preview of the manual matching process.
      </div>
      
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading match options...</p>
      </div>
      
      <!-- Request Already Fulfilled -->
      <div v-else-if="selectedRequest.request_quantity_remaining < 1" class="no-matches-message">
        Request has enough pledges and matches to fulfill.
        <div class="button-group">
          <app-button variant="cancel" @click="goBack">Back to Requests</app-button>
        </div>
      </div>
      
      <!-- Main Content -->
      <div v-else>
        <div class="info-section">
          <h3>Request Details</h3>
          <p><strong>Event:</strong> {{ selectedRequest.event_name || 'Unknown Event' }}</p>
          <p><strong>Category:</strong> {{ selectedRequest.category_name || 'Unknown Category' }}</p>
          <p v-if="selectedRequest.item_name"><strong>Specific Item:</strong> {{ selectedRequest.item_name }}</p>
          <p><strong>Quantity Requested:</strong> {{ selectedRequest.request_quantity || 0 }}</p>
          <p><strong>Quantity Remaining:</strong> {{ selectedRequest.request_quantity_remaining || 0 }}</p>
          <p v-if="selectedRequest.requester_zipcode"><strong>Recipient Location:</strong> {{ selectedRequest.requester_zipcode }}</p>
          <p v-if="selectedRequest.request_details"><strong>Details:</strong> {{ selectedRequest.request_details }}</p>
        </div>
        
        <!-- No Inventory Available -->
        <div v-if="!hasAnyInventory" class="no-inventory-section">
          <div class="no-pledges-message">
            <h3>No Inventory Available</h3>
            <p>Unfortunately, there are no available items that match this request:</p>
            <ul class="no-inventory-reasons">
              <li v-if="selectedRequest.item_name">No admin inventory or donor pledges for "{{ selectedRequest.item_name }}"</li>
              <li v-else>No admin inventory or donor pledges for items in the "{{ selectedRequest.category_name }}" category</li>
              <li>All existing pledges may already be allocated to other requests</li>
            </ul>
            
            <div class="suggestions">
              <h4>Suggestions:</h4>
              <ul>
                <li>Check back later as new pledges may become available</li>
                <li>Contact donors to request pledges for this specific item</li>
                <li>Consider if a similar item from another category could fulfill this need</li>
              </ul>
            </div>
            
            <div class="button-group">
              <app-button variant="primary" @click="goToRequests">View All Requests</app-button>
              <app-button variant="secondary" @click="goToPledges">View Available Pledges</app-button>
              <app-button variant="cancel" @click="goBack">Back</app-button>
            </div>
          </div>
        </div>
        
        <!-- Inventory Available -->
        <div v-else class="form-section">
          <h3>Match Options</h3>
          
          <div class="inventory-summary">
            <h4>Inventory Summary</h4>
            <div class="inventory-stats">
              <div class="inventory-stat">
                <span class="stat-label">Total Available:</span>
                <span class="stat-value">{{ safeMatchOptions.total_available }} items</span>
              </div>
              <div class="inventory-stat">
                <span class="stat-label">Admin Inventory:</span>
                <span class="stat-value">{{ safeMatchOptions.base_quantity }} items</span>
              </div>
              <div class="inventory-stat">
                <span class="stat-label">Donor Pledges:</span>
                <span class="stat-value">{{ safeMatchOptions.total_from_pledges }} items</span>
              </div>
            </div>
          </div>
          
          <div class="source-tabs">
            <button 
              class="tab-button" 
              :class="{ active: activeTab === 'admin' }"
              @click="setActiveTab('admin')"
              :disabled="!hasAdminInventory || isAdminObserver"
            >
              Admin Inventory ({{ safeMatchOptions.base_quantity }})
            </button>
            <button 
              class="tab-button" 
              :class="{ active: activeTab === 'pledges' }"
              @click="setActiveTab('pledges')"
              :disabled="!hasPledges || isAdminObserver"
            >
              Donor Pledges ({{ safeMatchOptions.total_from_pledges }})
            </button>
          </div>
          
          <!-- Admin Inventory Tab -->
          <div v-if="activeTab === 'admin' && hasAdminInventory" class="tab-content">
            <div class="admin-inventory">
              <h4>Match from Admin Inventory</h4>
              <p class="help-text">This will create a match using items directly from the system inventory.</p>
              
              <div class="form-group">
                <label for="admin-match-quantity">Match Quantity:</label>
                <input 
                  type="number" 
                  id="admin-match-quantity"
                  v-model="adminMatchQuantity" 
                  min="1" 
                  :max="maxAdminQuantity" 
                  :disabled="isAdminObserver"
                  :class="{ 'disabled-field': isAdminObserver }"
                />
              </div>
              
              <button 
                class="match-btn" 
                @click="createAdminMatch(selectedRequest)"
                :disabled="isAdminObserver || !canCreateMatches"
                :class="{ 'disabled-button': isAdminObserver }"
                :title="isAdminObserver ? 'Admin Observers cannot create matches' : 'Create match from admin inventory'"
              >
                {{ isAdminObserver ? 'View Only - Cannot Create Match' : 'Match from Admin Inventory' }}
              </button>
            </div>
          </div>
          
          <!-- Donor Pledges Tab -->
          <div v-if="activeTab === 'pledges' && hasPledges" class="tab-content">
            <div class="pledge-selection">
              <h4>Select a Specific Donor Pledge</h4>
              <p class="help-text">Choose a specific donor pledge to fulfill this request.</p>
              
              <div v-for="pledge in safeAvailablePledges" :key="pledge.pledge_id" class="pledge-option">
                <button 
                  class="pledge-btn" 
                  :class="{ 
                    'selected': selectedPledge && selectedPledge.pledge_id === pledge.pledge_id,
                    'disabled-button': isAdminObserver 
                  }"
                  @click="selectPledge(pledge)"
                  :disabled="isAdminObserver"
                >
                  <div class="pledge-donor">{{ pledge.donor_name || 'Donor #' + pledge.donor_id }}</div>
                  <div class="pledge-details">
                    <span class="pledge-item">{{ pledge.item_name }}</span>
                    <span class="quantity-badge">Available: {{ pledge.available_quantity }}</span>
                  </div>
                  <div class="pledge-meta">
                    <span class="ship-days">{{ pledge.days_to_ship || 'TBD' }} days to ship</span>
                    <span class="donor-location">{{ pledge.donor_zipcode || 'Location TBD' }}</span>
                  </div>
                </button>
              </div>
            </div>
            
            <!-- Match Details (only show if pledge is selected) -->
            <div v-if="selectedPledge" class="match-details">
              <h3>Match Details</h3>
              <p><strong>Selected Donor:</strong> {{ selectedPledge.donor_name || 'Donor #' + selectedPledge.donor_id }}</p>
              <p><strong>Selected Item:</strong> {{ selectedPledge.item_name }}</p>
              
              <div class="form-group">
                <label for="match-quantity">Match Quantity:</label>
                <input 
                  type="number" 
                  id="match-quantity"
                  v-model="pledgeMatchQuantity" 
                  min="1" 
                  :max="maxPledgeQuantity" 
                  :disabled="isAdminObserver"
                  :class="{ 'disabled-field': isAdminObserver }"
                />
              </div>
              
              <button 
                class="match-btn"
                @click="createPledgeMatch(selectedRequest, selectedPledge)"
                :disabled="isAdminObserver || !canCreateMatches"
                :class="{ 'disabled-button': isAdminObserver }"
                :title="isAdminObserver ? 'Admin Observers cannot create matches' : 'Create match from pledge'"
              >
                {{ isAdminObserver ? 'View Only - Cannot Create Match' : 'Create Match from Pledge' }}
              </button>
            </div>
          </div>
          
          <!-- Auto Match Option -->
          <div class="auto-match-option">
            <h3>Or Use Auto Match</h3>
            <p>Let the system automatically match this request with the best available sources.</p>
            <app-button 
              variant="auto-match" 
              @click="goToAutoMatch(selectedRequest.request_id)"
              :disabled="isAdminObserver"
              :class="{ 'disabled-button': isAdminObserver }"
            >
              {{ isAdminObserver ? 'View Only Mode' : `Auto Match (${safeMatchOptions.total_available} available)` }}
            </app-button>
          </div>
          
          <div v-if="isAdminObserver" class="observer-notice">
            <p>Admin Observers can view the matching interface and see all available inventory and pledges.</p>
            <p>However, you cannot create matches or modify data. This ensures you can monitor the system without making changes.</p>
          </div>
          
          <div class="button-group">
            <app-button variant="cancel" @click="goBack">{{ isAdminObserver ? 'Back to View' : 'Cancel' }}</app-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const isAdminObserver = computed(() => authStore.isAdminObserver);
const canCreateMatches = computed(() => authStore.canCreateMatches);

// State variables
const isLoading = ref(true);
const selectedRequest = ref({});
const matchOptions = ref({
  base_quantity: 0,
  total_from_pledges: 0,
  total_available: 0,
  available_pledges: [],
  available_sources: []
});
const activeTab = ref('admin');
const selectedPledge = ref(null);
const adminMatchQuantity = ref(1);
const pledgeMatchQuantity = ref(1);

// Safe computed properties to prevent crashes
const safeMatchOptions = computed(() => ({
  base_quantity: matchOptions.value?.base_quantity || 0,
  total_from_pledges: matchOptions.value?.total_from_pledges || 0,
  total_available: matchOptions.value?.total_available || 0,
  available_pledges: matchOptions.value?.available_pledges || [],
  available_sources: matchOptions.value?.available_sources || []
}));

const safeAvailablePledges = computed(() => {
  return safeMatchOptions.value.available_pledges.filter(pledge => 
    pledge && pledge.pledge_id && pledge.available_quantity > 0
  );
});

const hasAdminInventory = computed(() => safeMatchOptions.value.base_quantity > 0);
const hasPledges = computed(() => safeAvailablePledges.value.length > 0);
const hasAnyInventory = computed(() => hasAdminInventory.value || hasPledges.value);

const maxAdminQuantity = computed(() => {
  return Math.min(
    safeMatchOptions.value.base_quantity,
    selectedRequest.value?.request_quantity_remaining || 1
  );
});

const maxPledgeQuantity = computed(() => {
  if (!selectedPledge.value) return 1;
  return Math.min(
    selectedPledge.value.available_quantity || 1,
    selectedRequest.value?.request_quantity_remaining || 1
  );
});

// Safe tab switching
const setActiveTab = (tab) => {
  if (isAdminObserver.value) return;
  
  // Only allow switching to tabs that have content
  if (tab === 'admin' && !hasAdminInventory.value) return;
  if (tab === 'pledges' && !hasPledges.value) return;
  
  activeTab.value = tab;
  
  // Clear selected pledge when switching tabs
  if (tab === 'admin') {
    selectedPledge.value = null;
  }
};

// Select a pledge with validation
const selectPledge = (pledge) => {
  if (isAdminObserver.value || !pledge || !pledge.pledge_id) return;
  
  selectedPledge.value = pledge;
  
  // Set safe default match quantity
  pledgeMatchQuantity.value = Math.min(
    pledge.available_quantity || 1,
    selectedRequest.value?.request_quantity_remaining || 1
  );
};

// Navigation functions
const goBack = () => router.back();
const goToRequests = () => router.push('/respond-to-requests');
const goToPledges = () => router.push('/pledge-view');
const goToAutoMatch = (requestId) => router.push(`/auto-match/${requestId}`);

// Get specific request by ID with error handling
async function getRequestDetails(requestId) {
  try {
    if (!requestId) {
      throw new Error('No request ID provided');
    }

    const response = await api.get(`/getRequests?user_id=${authStore.userId}&request_id=${requestId}`);
    
    if (!response.data || response.data.length === 0) {
      throw new Error('Request not found');
    }

    selectedRequest.value = response.data[0];
    
    // Validate required properties
    if (!selectedRequest.value.request_id) {
      throw new Error('Invalid request data');
    }

    // Get match options
    await getMatchOptions(requestId);
    
  } catch (error) {
    console.error('Error getting request details:', error);
    
    // Set safe defaults
    selectedRequest.value = {
      request_id: requestId,
      event_name: 'Unknown Event',
      category_name: 'Unknown Category',
      request_quantity: 0,
      request_quantity_remaining: 0
    };
    
    // Show user-friendly error
    alert('Error loading request details: ' + error.message);
  }
}

// Get combined match options with comprehensive error handling
async function getMatchOptions(requestId) {
  try {
    const response = await api.get(`/getCombinedMatchOptions?request_id=${requestId}`);
    
    if (response.data) {
      matchOptions.value = {
        base_quantity: response.data.base_quantity || 0,
        total_from_pledges: response.data.total_from_pledges || 0,
        total_available: response.data.total_available || 0,
        available_pledges: response.data.available_pledges || [],
        available_sources: response.data.available_sources || []
      };
    } else {
      throw new Error('No match options data received');
    }
    
    // Set appropriate default tab
    await nextTick(); // Wait for computed properties to update
    
    if (hasAdminInventory.value) {
      activeTab.value = 'admin';
      adminMatchQuantity.value = Math.min(
        matchOptions.value.base_quantity,
        selectedRequest.value?.request_quantity_remaining || 1
      );
    } else if (hasPledges.value) {
      activeTab.value = 'pledges';
    }
    
    // Clear any selected pledge
    selectedPledge.value = null;
    
  } catch (error) {
    console.error('Error getting match options:', error);
    
    // Set safe empty state
    matchOptions.value = {
      base_quantity: 0,
      total_from_pledges: 0,
      total_available: 0,
      available_pledges: [],
      available_sources: []
    };
  }
}

// Create admin match with validation
const createAdminMatch = async (request) => {
  if (isAdminObserver.value) {
    alert('Admin Observers cannot create matches from admin inventory.');
    return;
  }
  
  if (!adminMatchQuantity.value || adminMatchQuantity.value < 1) {
    alert('Please enter a valid quantity');
    return;
  }
  
  if (!request?.request_id) {
    alert('Invalid request data');
    return;
  }
  
  try {
    const matchRequest = {
      requestId: request.request_id,
      adminQuantity: adminMatchQuantity.value,
      isAdminSource: true
    };
    
    await api.post('/createAdminMatch', matchRequest);
    alert('Match created successfully from admin inventory!');
    router.push('/match-view');
  } catch (error) {
    console.error('Error creating admin match:', error);
    alert('Failed to create match from admin inventory. Please try again.');
  }
};

// Create pledge match with comprehensive validation
const createPledgeMatch = async (request, pledge) => {
  if (isAdminObserver.value) {
    alert('Admin Observers cannot create matches from donor pledges.');
    return;
  }
  
  if (!pledgeMatchQuantity.value || pledgeMatchQuantity.value < 1) {
    alert('Please enter a valid quantity');
    return;
  }
  
  if (!request?.request_id || !pledge?.pledge_id) {
    alert('Invalid request or pledge data');
    return;
  }
  
  try {
    const matchRequest = {
      requestId: request.request_id,
      pledgeId: pledge.pledge_id,
      matchQuantity: Number(pledgeMatchQuantity.value)
    };
    
    // Validate data
    if (isNaN(matchRequest.matchQuantity) || matchRequest.matchQuantity <= 0) {
      alert('Invalid match quantity');
      return;
    }
    
    const response = await api.post('/createMatch', matchRequest);
    
    if (response.status === 201 || response.status === 200) {
      alert('Match created successfully from donor pledge!');
      router.push('/match-view');
    } else {
      alert('Unexpected response from server');
    }
    
  } catch (error) {
    console.error('Error creating pledge match:', error);
    
    if (error.response?.data?.error) {
      alert('Error: ' + error.response.data.error);
    } else {
      alert('Failed to create match from donor pledge. Please try again.');
    }
  }
};

// Watchers with null checks
watch(adminMatchQuantity, (value) => {
  if (!value || value < 1) {
    adminMatchQuantity.value = 1;
  } else if (value > maxAdminQuantity.value) {
    adminMatchQuantity.value = maxAdminQuantity.value;
  }
});

watch(pledgeMatchQuantity, (value) => {
  if (!value || value < 1) {
    pledgeMatchQuantity.value = 1;
  } else if (value > maxPledgeQuantity.value) {
    pledgeMatchQuantity.value = maxPledgeQuantity.value;
  }
});

// Load initial data with comprehensive error handling
onMounted(async () => {
  try {
    isLoading.value = true;
    
    const requestId = route.params.id;
    if (!requestId) {
      throw new Error('No request ID in route parameters');
    }
    
    await getRequestDetails(requestId);
    
  } catch (error) {
    console.error('Error in onMounted:', error);
    alert('Error loading page: ' + error.message);
    
    // Redirect back to requests list on critical error
    router.push('/respond-to-requests');
  } finally {
    isLoading.value = false;
  }
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
  width: 100%; 
}

.match-header {
  background: #f5e1c5;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 28px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 30px;
}

/* Loading state */
.loading-state {
  text-align: center;
  padding: 50px;
  color: #8B5E3C;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #8B5E3C;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.no-matches-message {
  background-color: #ffecb3;
  color: #856404;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: 500;
  border: 1px solid #ffeeba;
  text-align: center;
}

/* No inventory section */
.no-inventory-section {
  text-align: left;
}

.no-pledges-message {
  padding: 30px;
  background-color: #fff3cd;
  color: #856404;
  border-radius: 12px;
  border: 1px solid #ffeeba;
  margin: 20px 0;
}

.no-pledges-message h3 {
  color: #d32f2f;
  margin-bottom: 15px;
  text-align: center;
}

.no-inventory-reasons {
  margin: 15px 0;
  padding-left: 20px;
}

.no-inventory-reasons li {
  margin-bottom: 8px;
  color: #856404;
}

.suggestions {
  margin-top: 25px;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
}

.suggestions h4 {
  color: #2e8b57;
  margin-bottom: 10px;
}

.suggestions ul {
  margin: 10px 0;
  padding-left: 20px;
}

.suggestions li {
  margin-bottom: 8px;
  color: #2e8b57;
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

.inventory-summary {
  background-color: #e6f7ef;
  border: 1px solid #8fcea5;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.inventory-summary h4 {
  color: #2e8b57;
  margin-bottom: 10px;
  text-align: center;
}

.inventory-stats {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.inventory-stat {
  padding: 8px 12px;
  background-color: rgba(255, 255, 255, 0.6);
  border-radius: 6px;
  flex-grow: 1;
  text-align: center;
}

.stat-label {
  font-weight: bold;
  display: block;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  color: #2e8b57;
}

.help-text {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
  font-style: italic;
}

.source-tabs {
  display: flex;
  border-bottom: 2px solid #d3c0a3;
  margin-bottom: 20px;
}

.tab-button {
  padding: 10px 20px;
  background: none;
  border: none;
  color: #5c4033;
  cursor: pointer;
  position: relative;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tab-button:disabled {
  color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.tab-button.active {
  font-weight: 600;
}

.tab-button.active:after {
  content: '';
  position: absolute;
  width: 100%;
  height: 3px;
  background-color: #8B5E3C;
  bottom: -2px;
  left: 0;
}

.tab-content {
  padding: 20px 0;
}

.pledge-selection {
  margin: 20px 0;
}

.pledge-option {
  margin-bottom: 10px;
}

.pledge-btn, .match-btn {
  width: 100%;
  padding: 15px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  background-color: #f9f3e8;
  color: #5c4033;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  display: block;
}

.match-btn {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  color: white;
  text-align: center;
  font-weight: 600;
  margin-top: 20px;
}

.pledge-btn:hover, .match-btn:hover {
  background-color: #f5e1c5;
  transform: translateY(-2px);
}

.pledge-btn.selected {
  background-color: #8B5E3C;
  color: white;
  border-color: #6A3E2B;
}

.match-btn:hover {
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}

/* Disabled button styling */
.disabled-button,
.pledge-btn:disabled,
.match-btn:disabled {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
  background-color: #cccccc !important;
  color: #666666 !important;
}

.disabled-button:hover,
.pledge-btn:disabled:hover,
.match-btn:disabled:hover {
  transform: none !important;
  box-shadow: none !important;
  background-color: #cccccc !important;
}

/* Disabled field styling */
.disabled-field,
input:disabled {
  background-color: #f8f9fa !important;
  color: #6c757d !important;
  cursor: not-allowed !important;
  opacity: 0.8 !important;
  border-color: #dee2e6 !important;
}

.pledge-donor {
  font-weight: 600;
  margin-bottom: 5px;
}

.pledge-details {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.pledge-meta {
  font-size: 14px;
  color: #666;
  display: flex;
  justify-content: space-between;
}

.pledge-btn.selected .pledge-meta {
  color: rgba(255, 255, 255, 0.8);
}

.quantity-badge {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

.pledge-btn.selected .quantity-badge {
  background-color: rgba(255, 255, 255, 0.2);
}

.match-details, .admin-inventory {
  background: #f9f3e8;
  padding: 25px;
  border-radius: 10px;
  margin-top: 20px;
  border: 1px solid #d3c0a3;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #5c4033;
}

input {
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  width: 100%;
  max-width: 200px;
  transition: all 0.3s ease;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.auto-match-option {
  margin-top: 30px;
  text-align: center;
  padding: 20px;
  background-color: #f5e1c5;
  border-radius: 8px;
}

.auto-match-option h3 {
  margin-bottom: 10px;
}

.auto-match-option p {
  margin-bottom: 15px;
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

@media (max-width: 768px) {
  .content-box {
    padding: 20px;
  }
  
  .match-header {
    font-size: 24px;
    padding: 12px 20px;
  }
  
  .info-section, .form-section, .match-details {
    padding: 15px;
  }
  
  .inventory-stats {
    flex-direction: column;
  }

  .observer-warning,
  .observer-notice {
    font-size: 14px;
    padding: 15px;
  }
  
  .button-group {
    flex-direction: column;
    align-items: center;
  }
  
  .no-pledges-message {
    padding: 20px;
  }
}
</style>