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
                <span class="label">Available Inventory: </span>
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
                    <span class="partial-fulfill">⚠ Can be partially fulfilled</span>
                  </div>
                  <div class="fulfillment-indicator" v-else>
                    <span class="no-fulfill">⚠ No inventory available</span>
                  </div>
                </div>
              </div>

              <!-- ENHANCED: Your Pledges Display -->
              <div class="info-row your-pledges-info" v-if="request.your_pledged_quantity > 0">
                <span class="label">Your Pledges: </span>
                <div class="pledge-details">
                  <div class="pledge-summary">
                    <span class="pledge-total">
                      {{ request.your_pledged_quantity }} items pledged by you </span>
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
                <span class="label">Preferred Matching: </span>
                <span class="value">{{ request.preferred_match_type_name }}</span>
              </div>
              
              <div class="info-row" v-if="request.details">
                <span class="label">Details:</span>
                <span class="value">{{ request.details }}</span>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="progress-section">
              <div class="progress-text">
                Progress: {{ request.quantity - request.request_quantity_remaining }} / {{ request.quantity }} fulfilled
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: getProgressPercentage(request) + '%' }"
                ></div>
              </div>
              <div class="progress-percentage">{{ getProgressPercentage(request) }}%</div>
            </div>

            <!-- Action Buttons -->
            <div class="card-actions">
              <AppButton 
                @click="navigateToManualMatch(request.request_id)" 
                variant="primary"
                size="small">
                Manual Match
              </AppButton>
              <AppButton 
                @click="navigateToAutoMatch(request.request_id)" 
                variant="secondary"
                size="small">
                Auto Match
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

// Reactive data
const requests = ref([]);
const categories = ref([]);
const loading = ref(false);
const selectedCategory = ref('');
const sortBy = ref('newest');
const currentPage = ref(1);
const itemsPerPage = 10;

// Computed properties
const totalRequests = computed(() => requests.value.length);
const totalItemsNeeded = computed(() =>
  requests.value.reduce((sum, req) => sum + Number(req.request_quantity_remaining || 0), 0)
);
const urgentRequests = computed(() => 
  requests.value.filter(req => req.request_quantity_remaining === req.quantity).length
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
      return sorted; // Already sorted by newest, reverse for oldest
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
  router.push(`/create-match/${requestId}`);
};

const navigateToAutoMatch = (requestId) => {
  router.push(`/auto-match/${requestId}`);
};

const viewRequestDetails = (request) => {
  // Could open a modal or navigate to a details page
  alert(`Request Details:\n\nEvent: ${request.event_name}\nRequested by: ${request.requested_by}\nQuantity: ${request.quantity}\nDetails: ${request.details || 'No additional details'}`);
};

const fetchRequests = async () => {
  loading.value = true;
  try {
    console.log('Fetching requests...');
    const response = await api.get('/getRequestsForResponse');
    console.log('Requests response:', response.data);
    
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
            console.log('Fetching inventory for item:', request.item_name);
            const inventoryResponse = await api.get('/getItemAvailability');
            console.log('Inventory response received, items count:', inventoryResponse.data.length);
            
            const itemInventory = inventoryResponse.data.find(
              item => item.name === request.item_name
            );
            
            if (itemInventory) {
              request.available_inventory = itemInventory.available_combined || 0;
              request.inventory_breakdown = {
                admin: itemInventory.base_quantity || 0,
                pledges: itemInventory.available_pledged || 0
              };
              console.log('Found inventory for', request.item_name, ':', request.available_inventory);
            } else {
              console.log('No inventory found for item:', request.item_name);
            }
          } catch (error) {
            console.error('Error fetching inventory for item:', request.item_name, error);
            // Keep default values on error
          }
        }

        // Enhanced: Get user's pledges for this specific item
        if (authStore.userId && request.item_name) {
          try {
            console.log('Fetching pledges for user:', authStore.userId, 'item:', request.item_name);
            const pledgesResponse = await api.get(`/getPledges?user_id=${authStore.userId}`);
            console.log('Pledges response received, pledges count:', pledgesResponse.data.length);
            
            // Find pledges for this specific item
            const userPledgesForItem = pledgesResponse.data.filter(
              pledge => pledge.item_name === request.item_name
            );
            
            if (userPledgesForItem.length > 0) {
              console.log('Found user pledges for', request.item_name, ':', userPledgesForItem);
              
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
            // Keep default values on error
          }
        }
        
        return request;
      })
    );
    
    requests.value = requestsWithInventory;
    console.log('Final requests with inventory and pledges:', requests.value);
  } catch (error) {
    console.error('Error fetching requests:', error);
    
    // Check if it's a 404 error and provide more specific feedback
    if (error.response && error.response.status === 404) {
      console.error('404 Error - API endpoint not found:', error.config?.url || 'Unknown URL');
      alert(`API endpoint not found: ${error.config?.url || 'Unknown endpoint'}. Please check if the server is running.`);
    } else {
      alert('Failed to load requests. Please try again.');
    }
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
  currentPage.value = 1; // Reset to first page when filtering
};

const sortRequests = () => {
  currentPage.value = 1; // Reset to first page when sorting
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
  border-color: #ff6b6b;
  background: linear-gradient(135deg, #fff5f5, #ffebee);
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

.info-row .value.still-needed {
  color: #6c757d;
  font-weight: 500;
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
  color: #2e7d32;
  font-weight: 500;
}

.progress-section {
  margin-bottom: 20px;
}

.progress-text {
  font-size: 14px;
  color: #5c4033;
  margin-bottom: 8px;
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
  background: linear-gradient(90deg, #4caf50, #66bb6a);
  transition: width 0.3s ease;
}

.progress-percentage {
  font-size: 14px;
  font-weight: 600;
  color: #5c4033;
  text-align: right;
}

.card-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

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
}
</style>