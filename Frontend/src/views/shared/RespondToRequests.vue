<template>
  <div class="respond-container">
    <div class="content-box">
      <h1 class="respond-header">Respond to Requests</h1>
      <p class="description">Browse the list of disaster relief requests that need your help.</p>
      
      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ totalRequests }}</div>
          <div class="stat-label">Total Requests</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ totalItemsNeeded }}</div>
          <div class="stat-label">Total Items Needed</div>
        </div>
        <div class="stat-card urgent">
          <div class="stat-number">{{ urgentRequests }}</div>
          <div class="stat-label">Urgent Requests</div>
        </div>
        <div class="stat-card donor-stats" v-if="isDonor">
          <div class="stat-number">{{ yourTotalPledges }}</div>
          <div class="stat-label">Your Pledges</div>
        </div>
      </div>

      <!-- Filters and Controls -->
      <div class="controls-section">
        <div class="filters">
          <div class="filter-group">
            <label for="categoryFilter">Filter by Category:</label>
            <select id="categoryFilter" v-model="selectedCategory" @change="filterRequests">
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
                {{ category.category_name }}
              </option>
            </select>
          </div>

          <div class="filter-group">
            <label for="sortBy">Sort by:</label>
            <select id="sortBy" v-model="sortBy" @change="sortRequests">
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="quantity-high">Highest Quantity</option>
              <option value="quantity-low">Lowest Quantity</option>
              <option value="remaining-high">Most Remaining</option>
              <option value="remaining-low">Least Remaining</option>
            </select>
          </div>
        </div>

        <div class="refresh-button">
          <AppButton @click="refreshData" variant="secondary">Refresh</AppButton>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading requests...</p>
      </div>

      <!-- No Requests State -->
      <div v-else-if="filteredRequests.length === 0" class="no-requests">
        <h3>No requests found</h3>
        <p v-if="selectedCategory">Try selecting a different category or clearing the filter.</p>
        <p v-else>There are currently no requests that need responses.</p>
      </div>

      <!-- Requests List -->
      <div v-else class="requests-list">
        <div v-for="request in paginatedRequests" :key="request.request_id" class="request-card">
          <!-- Header with event and category -->
          <div class="card-header">
            <div class="event-info">
              <h3>{{ request.event_name }} - {{ request.category }}</h3>
              <div class="status-badge needs-pledges">Needs Pledges</div>
            </div>
            <div class="location">
              <strong>Location:</strong> {{ request.event_location }}
            </div>
          </div>

          <!-- Request Details -->
          <div class="card-body">
            <div class="request-info">
              <div class="info-row">
                <span class="label">Requested by:</span>
                <span class="value">{{ request.requested_by }}</span>
              </div>
              
              <div class="info-row" v-if="request.item_name">
                <span class="label">Specific Item:</span>
                <span class="value">{{ request.item_name }}</span>
              </div>
              
              <!-- ENHANCED: Available Inventory Display -->
              <div class="info-row inventory-info" v-if="request.item_name">
                <span class="label">Available Inventory:</span>
                <div class="inventory-details">
                  <div class="inventory-breakdown">
                    <span class="inventory-total" :class="getInventoryClass(request.available_inventory)">
                      {{ request.available_inventory || 0 }} available
                    </span>
                    <div class="inventory-sources" v-if="request.inventory_breakdown">
                      <span class="admin-inventory" v-if="request.inventory_breakdown.admin > 0">
                        {{ request.inventory_breakdown.admin }} (admin)
                      </span>
                      <span class="pledge-inventory" v-if="request.inventory_breakdown.pledges > 0">
                        {{ request.inventory_breakdown.pledges }} (pledged)
                      </span>
                    </div>
                  </div>
                  <div class="fulfillment-indicator" v-if="request.available_inventory >= request.request_quantity_remaining">
                    <span class="can-fulfill">✓ Can be fully fulfilled</span>
                  </div>
                  <div class="fulfillment-indicator" v-else-if="request.available_inventory > 0">
                    <span class="partial-fulfill">Can be partially fulfilled</span>
                  </div>
                  <div class="fulfillment-indicator" v-else>
                    <span class="no-fulfill">No inventory available</span>
                  </div>
                </div>
              </div>

              <!-- ENHANCED: Your Pledges Display -->
              <div class="info-row your-pledges-info" v-if="request.your_pledged_quantity > 0">
                <span class="label">Your Pledges:</span>
                <div class="pledge-details">
                  <div class="pledge-summary">
                    <span class="pledge-total">
                      {{ request.your_pledged_quantity }} items pledged by you
                    </span>
                    <div class="pledge-breakdown" v-if="request.your_pledge_breakdown">
                      <span class="allocated-items" v-if="request.your_pledge_breakdown.allocated > 0">
                        {{ request.your_pledge_breakdown.allocated }} allocated
                      </span>
                      <span class="fulfilled-items" v-if="request.your_pledge_breakdown.fulfilled > 0">
                        {{ request.your_pledge_breakdown.fulfilled }} fulfilled
                      </span>
                      <span class="available-items" v-if="request.your_pledge_breakdown.available > 0">
                        {{ request.your_pledge_breakdown.available }} available
                      </span>
                    </div>
                  </div>
                  <div class="pledge-status">
                    <span class="contribution-indicator">
                      You've contributed to this request
                    </span>
                  </div>
                </div>
              </div>

              <div class="info-row">
                <span class="label">Total Requested:</span>
                <span class="value">{{ request.quantity }}</span>
              </div>
              
              <div class="info-row">
                <span class="label">Still Needed:</span>
                <span class="value urgent">{{ request.request_quantity_remaining }}</span>
              </div>
              
              <div class="info-row">
                <span class="label">Preferred Matching:</span>
                <span class="value">{{ request.preferred_match_type_name }}</span>
              </div>
              
              <div class="info-row" v-if="request.details">
                <span class="label">Details:</span>
                <span class="value">{{ request.details }}</span>
              </div>
            </div>

            <!-- Overall Progress Bar -->
            <div class="progress-section">
              <div class="progress-text">
                Overall Progress: {{ request.quantity - request.request_quantity_remaining }} / {{ request.quantity }} fulfilled
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill overall" 
                  :style="{ width: getProgressPercentage(request) + '%' }"
                ></div>
              </div>
              <div class="progress-percentage">{{ getProgressPercentage(request) }}%</div>
            </div>

            <!-- NEW: Your Contribution Progress Bar (for donors only) -->
            <div v-if="isDonor && request.your_pledged_quantity > 0" class="progress-section your-contribution">
              <div class="progress-text donor-contribution">
                Your Contribution: {{ request.your_pledged_quantity }} / {{ request.quantity }} 
                ({{ Math.round((request.your_pledged_quantity / request.quantity) * 100) }}% of total need)
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill donor" 
                  :style="{ width: Math.min((request.your_pledged_quantity / request.quantity) * 100, 100) + '%' }"
                ></div>
              </div>
              <div class="donor-impact">
                <span v-if="request.your_pledged_quantity >= request.quantity" class="full-coverage">
                  You've covered the entire request!
                </span>
                <span v-else-if="request.your_pledged_quantity >= request.request_quantity_remaining" class="covers-remaining">
                  Your pledges cover the remaining need
                </span>
                <span v-else class="partial-coverage">
                  Great contribution! {{ request.request_quantity_remaining - request.your_pledged_quantity }} more needed
                </span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="card-actions">
              <!-- NEW: Pledge Button for Donors -->
              <AppButton 
                v-if="isDonor"
                @click="openPledgeModal(request)" 
                variant="success"
                class="pledge-button"
                :disabled="request.request_quantity_remaining <= 0"
              >
                <span v-if="request.your_pledged_quantity > 0">Add More Pledge</span>
                <span v-else>Create Pledge</span>
              </AppButton>

              <!-- Admin/Advanced Actions -->
              <AppButton 
                v-if="isAdmin"
                @click="navigateToManualMatch(request.request_id)" 
                variant="primary"
                size="small"
              >
                Manual Match
              </AppButton>
              <AppButton 
                v-if="isAdmin"
                @click="navigateToAutoMatch(request.request_id)" 
                variant="secondary"
                size="small"
              >
                Auto Match
              </AppButton>
              
              <!-- View Details Button (for all users) -->
              <AppButton 
                @click="viewRequestDetails(request)" 
                variant="outline"
                size="small"
              >
                View Details
              </AppButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <AppButton 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          variant="outline"
          size="small"
        >
          Previous
        </AppButton>
        
        <span class="page-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        
        <AppButton 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          variant="outline"
          size="small"
        >
          Next
        </AppButton>
      </div>
    </div>

    <!-- NEW: Pledge Modal -->
    <div v-if="showPledgeModal" class="modal-overlay" @click.self="closePledgeModal">
      <div class="pledge-modal">
        <div class="modal-header">
          <h3>Create Pledge for Request</h3>
          <button @click="closePledgeModal" class="close-button">&times;</button>
        </div>
        
        <div class="modal-body" v-if="selectedRequestForPledge">
          <div class="request-summary">
            <h4>{{ selectedRequestForPledge.event_name }} - {{ selectedRequestForPledge.category }}</h4>
            <p><strong>Requested by:</strong> {{ selectedRequestForPledge.requested_by }}</p>
            <p><strong>Item:</strong> {{ selectedRequestForPledge.item_name || 'Any item in category' }}</p>
            <p><strong>Still needed:</strong> {{ selectedRequestForPledge.request_quantity_remaining }}</p>
            <p v-if="selectedRequestForPledge.your_pledged_quantity > 0">
              <strong>You've already pledged:</strong> {{ selectedRequestForPledge.your_pledged_quantity }}
            </p>
          </div>

          <div class="pledge-form">
            <div class="form-group">
              <label for="pledge-quantity">Quantity to Pledge:</label>
              <input 
                type="number" 
                id="pledge-quantity"
                v-model.number="pledgeForm.quantity" 
                :min="1" 
                :max="Math.max(selectedRequestForPledge.request_quantity_remaining, 100)"
                required 
              />
              <div class="quantity-suggestions">
                <button 
                  type="button" 
                  class="suggestion-btn"
                  @click="pledgeForm.quantity = Math.min(selectedRequestForPledge.request_quantity_remaining, 5)"
                  :disabled="selectedRequestForPledge.request_quantity_remaining < 5"
                >
                  {{ Math.min(selectedRequestForPledge.request_quantity_remaining, 5) }}
                </button>
                <button 
                  type="button" 
                  class="suggestion-btn"
                  @click="pledgeForm.quantity = Math.min(selectedRequestForPledge.request_quantity_remaining, 10)"
                  :disabled="selectedRequestForPledge.request_quantity_remaining < 10"
                >
                  {{ Math.min(selectedRequestForPledge.request_quantity_remaining, 10) }}
                </button>
                <button 
                  type="button" 
                  class="suggestion-btn"
                  @click="pledgeForm.quantity = selectedRequestForPledge.request_quantity_remaining"
                >
                  All ({{ selectedRequestForPledge.request_quantity_remaining }})
                </button>
              </div>
            </div>

            <div class="form-group">
              <label for="days-to-ship">Days to Ship (optional):</label>
              <input 
                type="number" 
                id="days-to-ship"
                v-model.number="pledgeForm.daysToShip" 
                :min="1" 
                :max="30"
                placeholder="Leave blank if flexible"
              />
              <div class="help-text">How many days after matching to ship the items</div>
            </div>

            <div class="form-group">
              <label for="pledge-notes">Notes (optional):</label>
              <textarea 
                id="pledge-notes"
                v-model="pledgeForm.notes" 
                rows="3" 
                placeholder="Any additional information about your pledge..."
              ></textarea>
            </div>

            <div class="form-group">
              <div class="auto-match-option">
                <label>
                  <input 
                    type="checkbox" 
                    v-model="pledgeForm.autoMatch"
                  />
                  Request priority matching for this specific request
                </label>
                <div class="help-text">
                  If checked, administrators will be notified to prioritize matching your pledge with this request.
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <AppButton 
            variant="success" 
            @click="submitPledge"
            :disabled="isSubmittingPledge || !pledgeForm.quantity || pledgeForm.quantity < 1"
          >
            {{ isSubmittingPledge ? 'Creating Pledge...' : 'Create Pledge' }}
          </AppButton>
          <AppButton 
            variant="secondary" 
            @click="closePledgeModal"
          >
            Cancel
          </AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();

// Check user roles
const isDonor = computed(() => authStore.role === 'Donor');
const isAdmin = computed(() => authStore.role === 'Admin' || authStore.role === 'Admin Observer');

// Reactive data
const requests = ref([]);
const categories = ref([]);
const loading = ref(false);
const selectedCategory = ref('');
const sortBy = ref('newest');
const currentPage = ref(1);
const itemsPerPage = 10;

// NEW: Pledge modal data
const showPledgeModal = ref(false);
const selectedRequestForPledge = ref(null);
const isSubmittingPledge = ref(false);
const pledgeForm = ref({
  quantity: 1,
  daysToShip: null,
  notes: '',
  autoMatch: false
});

// Computed properties
const totalRequests = computed(() => requests.value.length);

const totalItemsNeeded = computed(() => 
  requests.value.reduce((sum, req) => sum + Number(req.request_quantity_remaining || 0), 0)
);

const urgentRequests = computed(() => 
  requests.value.filter(req => Number(req.request_quantity_remaining) === Number(req.quantity)).length
);

// NEW: Calculate total pledges by current user
const yourTotalPledges = computed(() => 
  requests.value.reduce((sum, req) => sum + Number(req.your_pledged_quantity || 0), 0)
);

const filteredRequests = computed(() => {
  let filtered = requests.value;
  
  if (selectedCategory.value) {
    filtered = filtered.filter(req => req.category_id == selectedCategory.value);
  }
  
  return filtered;
});

const sortedRequests = computed(() => {
  const sorted = [...filteredRequests.value];
  
  switch (sortBy.value) {
    case 'oldest':
      return sorted;
    case 'quantity-high':
      return sorted.sort((a, b) => b.quantity - a.quantity);
    case 'quantity-low':
      return sorted.sort((a, b) => a.quantity - b.quantity);
    case 'remaining-high':
      return sorted.sort((a, b) => b.request_quantity_remaining - a.request_quantity_remaining);
    case 'remaining-low':
      return sorted.sort((a, b) => a.request_quantity_remaining - b.request_quantity_remaining);
    default: // newest
      return sorted.reverse();
  }
});

const paginatedRequests = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return sortedRequests.value.slice(start, end);
});

const totalPages = computed(() => 
  Math.ceil(sortedRequests.value.length / itemsPerPage)
);

// Methods
const getProgressPercentage = (request) => {
  if (request.quantity === 0) return 0;
  const fulfilled = request.quantity - request.request_quantity_remaining;
  return Math.round((fulfilled / request.quantity) * 100);
};

const getInventoryClass = (availableInventory) => {
  if (availableInventory === 0) return 'no-inventory';
  if (availableInventory < 5) return 'low-inventory';
  return 'good-inventory';
};

const navigateToManualMatch = (requestId) => {
  if (!requestId) {
    alert('Error: Invalid request ID');
    return;
  }
  router.push(`/create-match/${requestId}`);
};

const navigateToAutoMatch = (requestId) => {
  if (!requestId) {
    alert('Error: Invalid request ID');
    return;
  }
  router.push(`/auto-match/${requestId}`);
};

const viewRequestDetails = (request) => {
  alert(`Request Details:\n\nEvent: ${request.event_name}\nRequested by: ${request.requested_by}\nQuantity: ${request.quantity}\nDetails: ${request.details || 'No additional details'}`);
};

// NEW: Pledge modal functions
const openPledgeModal = (request) => {
  selectedRequestForPledge.value = request;
  // Set default quantity to what's still needed (capped at 10 for UX)
  pledgeForm.value.quantity = Math.min(request.request_quantity_remaining, 10);
  pledgeForm.value.daysToShip = null;
  pledgeForm.value.notes = '';
  pledgeForm.value.autoMatch = false;
  showPledgeModal.value = true;
};

const closePledgeModal = () => {
  showPledgeModal.value = false;
  selectedRequestForPledge.value = null;
  pledgeForm.value = {
    quantity: 1,
    daysToShip: null,
    notes: '',
    autoMatch: false
  };
};

const submitPledge = async () => {
  if (!selectedRequestForPledge.value || !pledgeForm.value.quantity) {
    alert('Please enter a valid quantity.');
    return;
  }

  isSubmittingPledge.value = true;

  try {
    const pledgeData = {
      user_id: authStore.userId,
      selected_category_id: selectedRequestForPledge.value.category_id,
      selected_item_id: selectedRequestForPledge.value.item_id || null,
      item_quantity: pledgeForm.value.quantity,
      days_to_ship: pledgeForm.value.daysToShip || null
    };

    console.log('Creating pledge:', pledgeData);

    const response = await api.post('/createPledge', pledgeData);

    if (response.status === 201) {
      let successMessage = 'Pledge created successfully!';
      
      if (pledgeForm.value.autoMatch) {
        successMessage += ' Administrators have been notified to prioritize matching this pledge.';
      }
      
      alert(successMessage);
      
      // Refresh the requests to show updated data
      await fetchRequests();
      
      closePledgeModal();
    }
  } catch (error) {
    console.error('Error creating pledge:', error);
    
    if (error.response?.data?.error) {
      alert('Error: ' + error.response.data.error);
    } else {
      alert('Error creating pledge. Please try again later.');
    }
  } finally {
    isSubmittingPledge.value = false;
  }
};

const fetchRequests = async () => {
  loading.value = true;
  try {
    const response = await api.get('/getRequestsForResponse');
    
    // Enhanced: Fetch inventory data and user pledges for each request
    const requestsWithInventory = await Promise.all(
      response.data.map(async (request) => {
        // Initialize default values
        request.available_inventory = 0;
        request.inventory_breakdown = { admin: 0, pledges: 0 };
        request.your_pledged_quantity = 0;
        request.your_pledge_breakdown = { allocated: 0, fulfilled: 0, available: 0 };

        // Get available inventory for this specific item
        if (request.item_name) {
          try {
            const inventoryResponse = await api.get('/getItemAvailability');
            const itemInventory = inventoryResponse.data.find(
              item => item.name === request.item_name
            );
            
            if (itemInventory) {
              request.available_inventory = itemInventory.available_combined || 0;
              request.inventory_breakdown = {
                admin: itemInventory.base_quantity || 0,
                pledges: itemInventory.available_pledged || 0
              };
            }
          } catch (error) {
            console.error('Error fetching inventory for item:', request.item_name, error);
          }
        }

        // Get user's pledges for this specific item
        if (authStore.userId && request.item_name) {
          try {
            const pledgesResponse = await api.get(`/getPledges?user_id=${authStore.userId}`);
            
            // Find pledges for this specific item
            const userPledgesForItem = pledgesResponse.data.filter(
              pledge => pledge.item_name === request.item_name
            );
            
            if (userPledgesForItem.length > 0) {
              // Calculate totals across all pledges for this item
              const totalPledged = userPledgesForItem.reduce((sum, pledge) => sum + (pledge.item_quantity || 0), 0);
              const totalAllocated = userPledgesForItem.reduce((sum, pledge) => sum + (pledge.allocated_quantity || 0), 0);
              const totalFulfilled = userPledgesForItem.reduce((sum, pledge) => sum + (pledge.fulfilled_quantity || 0), 0);
              const totalAvailable = userPledgesForItem.reduce((sum, pledge) => sum + (pledge.items_left || 0), 0);
              
              request.your_pledged_quantity = totalPledged;
              request.your_pledge_breakdown = {
                allocated: totalAllocated,
                fulfilled: totalFulfilled,
                available: totalAvailable
              };
            }
          } catch (error) {
            console.error('Error fetching user pledges for item:', request.item_name, error);
          }
        }
        
        return request;
      })
    );
    
    requests.value = requestsWithInventory;
  } catch (error) {
    console.error('Error fetching requests:', error);
    alert('Failed to load requests. Please try again.');
  } finally {
    loading.value = false;
  }
};

const fetchCategories = async () => {
  try {
    const response = await api.get('/getCategories');
    categories.value = response.data;
  } catch (error) {
    console.error('Error fetching categories:', error);
  }
};

const refreshData = () => {
  fetchRequests();
  fetchCategories();
};

const filterRequests = () => {
  currentPage.value = 1;
};

const sortRequests = () => {
  currentPage.value = 1;
};

// Watchers
watch(() => filteredRequests.value.length, () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = Math.max(1, totalPages.value);
  }
});

// Lifecycle
onMounted(() => {
  fetchRequests();
  fetchCategories();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.respond-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Poppins', sans-serif;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
}

.respond-header {
  background: #f5e1c5;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 32px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
}

.description {
  color: #6c757d;
  margin-bottom: 30px;
  font-size: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 2px solid #e0d4c3;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card.urgent {
  border-color: #d3c0a3;
  background: linear-gradient(135deg,  #f9f3e8, #f5e9db);
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #5c4033;
  margin-bottom: 5px;
}

.stat-card.urgent .stat-number {
  color: #5c4033;
}

.stat-card.donor-stats {
  border-color: #4caf50;
  background: linear-gradient(135deg, #f1f8e9, #e8f5e8);
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #5c4033;
  margin-bottom: 5px;
}

.stat-card.urgent .stat-number {
  color: #d32f2f;
}

.stat-card.donor-stats .stat-number {
  color: #2e7d32;
}

.stat-label {
  font-size: 14px;
  color: #8B5E3C;
  font-weight: 500;
}

.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 30px;
  gap: 20px;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #5c4033;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #d3c0a3;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  min-width: 150px;
}

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

.no-requests {
  text-align: center;
  padding: 50px;
  color: #8B5E3C;
}

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.request-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e0d4c3;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.request-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.card-header {
  background: linear-gradient(135deg, #f5e1c5, #f0d4b8);
  padding: 15px 20px;
  border-bottom: 1px solid #e0d4c3;
}

.event-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.event-info h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #5c4033;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.needs-pledges {
  background: #ffebee;
  color: #5c4033;;
  border: 1px solid #ffcdd2;
}

.location {
  font-size: 14px;
  color: #5c4033;
}

.card-body {
  padding: 20px;
}

.request-info {
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
   gap: 8px;
}

.info-row .label {
  font-weight: 500;
  color: #5c4033;
  min-width: 140px;
  flex-shrink: 0;
}

.info-row .value {
  color: #6c757d;
  flex: 1;
}

.info-row .value.urgent {
  color: #5c4033;;
  font-weight: 600;
}

.inventory-info {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  margin: 10px 0;
}

.inventory-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.inventory-breakdown {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.inventory-total {
  font-weight: 600;
  font-size: 16px;
}

.inventory-total.no-inventory {
  color: #5c4033;;
}

.inventory-total.low-inventory {
  color: #5c4033;;
}

.inventory-total.good-inventory {
  color: #5c4033;;
}

.inventory-sources {
  display: flex;
  gap: 8px;
  font-size: 13px;
  color: #5c4033;
}

.admin-inventory,
.pledge-inventory {
  background: #f9f3e8;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #e0d4c3;
  color: #5c4033;
}

.fulfillment-indicator {
  font-size: 13px;
  font-weight: 500;
}

.can-fulfill {
  color: #5c4033;;
}

.partial-fulfill {
  color: #5c4033;;
}

.no-fulfill {
  color: #5c4033;;
}

.your-pledges-info {
  background: linear-gradient(135deg, #f9f3e8, #f5e9db);
  border-radius: 8px;
  padding: 12px;
  margin: 10px 0;
  border-left: 4px solid #c8b59c;
}

.pledge-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pledge-summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pledge-total {
  font-weight: 600;
  font-size: 16px;
  color: #5c4033;
}

.pledge-breakdown {
  display: flex;
  gap: 8px;
  font-size: 13px;
  flex-wrap: wrap;
}

.allocated-items,
.fulfilled-items,
.available-items {
  background: #f9f3e8;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #e0d4c3;
  color: #5c4033;
}

.pledge-status {
  font-size: 13px;
}

.contribution-indicator {
  color: #5c4033;
  font-weight: 500;
}

.progress-section {
  margin-bottom: 20px;
}

.progress-section.your-contribution {
  background: linear-gradient(135deg, #f1f8e9, #e8f5e8);
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #4caf50;
}

.progress-text {
  font-size: 14px;
  color: #5c4033;
  margin-bottom: 8px;
}

.progress-text.donor-contribution {
  color: #2e7d32;
  font-weight: 600;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.progress-fill.overall {
  background: linear-gradient(90deg, #4caf50, #66bb6a);
}

.progress-fill.donor {
  background: linear-gradient(90deg, #2e7d32, #4caf50);
}

.progress-percentage {
  font-size: 14px;
  font-weight: 600;
  color: #5c4033;
  text-align: right;
}

.donor-impact {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 500;
}

.full-coverage {
  color: #2e7d32;
}

.covers-remaining {
  color: #388e3c;
}

.partial-coverage {
  color: #1976d2;
}

/* Action Buttons */
.card-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pledge-button {
  background: linear-gradient(135deg, #4caf50, #2e7d32) !important;
  font-weight: 600;
}

.pledge-button:hover {
  background: linear-gradient(135deg, #388e3c, #1b5e20) !important;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.page-info {
  font-size: 14px;
  color: #5c4033;
  font-weight: 500;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.pledge-modal {
  background: white;
  border-radius: 15px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px 25px;
  border-bottom: 1px solid #e0d4c3;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f5e1c5, #f0d4b8);
}

.modal-header h3 {
  margin: 0;
  color: #5c4033;
  font-size: 24px;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #5c4033;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: rgba(92, 64, 51, 0.1);
}

.modal-body {
  padding: 25px;
}

.request-summary {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #8B5E3C;
}

.request-summary h4 {
  margin: 0 0 10px 0;
  color: #5c4033;
}

.request-summary p {
  margin: 5px 0;
  color: #6c757d;
}

.pledge-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #5c4033;
  font-size: 16px;
}

.form-group input,
.form-group textarea {
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #8B5E3C;
  box-shadow: 0 0 0 2px rgba(139, 94, 60, 0.2);
}

.quantity-suggestions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.suggestion-btn {
  background: #f5e1c5;
  border: 1px solid #d3c0a3;
  color: #5c4033;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.suggestion-btn:hover:not(:disabled) {
  background: #8B5E3C;
  color: white;
}

.suggestion-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.help-text {
  font-size: 14px;
  color: #666;
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

.modal-footer {
  padding: 20px 25px;
  border-top: 1px solid #e0d4c3;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  background: #f8f9fa;
}

/* Responsive Design */
@media (max-width: 768px) {
  .respond-container {
    padding: 10px;
  }
  
  .content-box {
    padding: 20px;
  }
  
  .controls-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    justify-content: center;
  }
  
  .event-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .card-actions {
    justify-content: center;
  }
  
  .inventory-sources {
    flex-direction: column;
    gap: 4px;
  }

  .pledge-breakdown {
    flex-direction: column;
    gap: 4px;
  }

  .pledge-modal {
    width: 95%;
    margin: 10px;
  }

  .modal-footer {
    flex-direction: column;
  }

  .quantity-suggestions {
    flex-wrap: wrap;
  }
}
</style>