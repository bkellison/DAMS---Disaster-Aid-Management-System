<template>
  <div class="respond-container">
    <div class="content-box">
      <h2 class="respond-header">Respond to Requests</h2>
      <p class="description">Browse the list of disaster relief requests that need your help.</p>

      <!-- Loading indicator -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading requests...</p>
      </div>

      <!-- No requests message -->
      <div v-else-if="requests.length === 0" class="no-requests">
        <p>No requests available at the moment.</p>
        <AppButton variant="secondary" @click="loadRequests">Refresh</AppButton>
      </div>

      <!-- Requests list -->
      <div v-else>
        <!-- Summary stats -->
        <div class="summary-stats">
          <div class="stat-card">
            <h3>Total Requests</h3>
            <p class="stat-number">{{ requests.length }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Items Needed</h3>
            <p class="stat-number">{{ totalItemsNeeded }}</p>
          </div>
          <div class="stat-card">
            <h3>Urgent Requests</h3>
            <p class="stat-number urgent">{{ urgentRequests }}</p>
          </div>
        </div>

        <!-- Filter and sort options -->
        <div class="controls">
          <div class="filter-group">
            <label for="categoryFilter">Filter by Category:</label>
            <select id="categoryFilter" v-model="selectedCategory" @change="applyFilters">
              <option value="">All Categories</option>
              <option v-for="category in uniqueCategories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="sortBy">Sort by:</label>
            <select id="sortBy" v-model="sortBy" @change="applySorting">
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="quantity_desc">Highest Quantity</option>
              <option value="quantity_asc">Lowest Quantity</option>
              <option value="remaining_desc">Most Remaining</option>
              <option value="remaining_asc">Least Remaining</option>
            </select>
          </div>

          <AppButton variant="secondary" @click="loadRequests" class="refresh-btn">
            Refresh
          </AppButton>
        </div>

        <!-- Request cards -->
        <ul class="request-list">
          <li v-for="request in filteredAndSortedRequests" :key="request.request_id" class="request-card">
            <div class="card-header">
              <h3 class="request-title">{{ request.event_name }} - {{ request.category }}</h3>
              <div class="request-status" :class="getStatusClass(request)">
                {{ getStatusText(request) }}
              </div>
            </div>

            <div class="request-location">
              <strong>Location:</strong> {{ request.event_location || 'Location not specified' }}
            </div>
            
            <div class="request-details">
              <div class="detail-row">
                <span class="detail-label">Requested by:</span>
                <span class="detail-value">{{ request.requested_by }}</span>
              </div>
              
              <div v-if="request.item_name" class="detail-row">
                <span class="detail-label">Specific Item:</span>
                <span class="detail-value">{{ request.item_name }}</span>
              </div>
              
              <div class="detail-row">
                <span class="detail-label">Total Requested:</span>
                <span class="detail-value">{{ request.quantity }}</span>
              </div>
              
              <div class="detail-row">
                <span class="detail-label">Still Needed:</span>
                <span class="detail-value remaining" :class="{ 'urgent': request.request_quantity_remaining > request.quantity * 0.8 }">
                  {{ request.request_quantity_remaining }}
                </span>
              </div>

              <div v-if="request.preferred_match_type_name" class="detail-row">
                <span class="detail-label">Preferred Matching:</span>
                <span class="detail-value">{{ request.preferred_match_type_name }}</span>
              </div>
              
              <div v-if="request.details && request.details.trim() !== ''" class="request-description">
                <strong>Details:</strong> {{ request.details }}
              </div>
            </div>

            <!-- Progress bar -->
            <div class="progress-section">
              <div class="progress-label">
                Progress: {{ request.quantity - request.request_quantity_remaining }} / {{ request.quantity }} fulfilled
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: getProgressPercentage(request) + '%' }"
                  :class="{ 'completed': getProgressPercentage(request) === 100 }">
                </div>
              </div>
              <div class="progress-percentage">{{ getProgressPercentage(request) }}%</div>
            </div>

            <div class="button-group">
              <AppButton 
                v-if="authStore.role === 'Donor'" 
                variant="primary" 
                @click="respondToRequest(request.request_id)"
                :disabled="request.request_quantity_remaining <= 0">
                {{ request.request_quantity_remaining <= 0 ? 'Fully Pledged' : 'Create Pledge' }}
              </AppButton>
              
              <AppButton 
                v-if="authStore.role === 'Admin'" 
                variant="primary" 
                @click="goToMatchForm(request.request_id)"
                :disabled="request.request_quantity_remaining <= 0">
                Manual Match
              </AppButton>
              
              <AppButton 
                v-if="authStore.role === 'Admin'" 
                variant="secondary" 
                @click="goToAutoMatch(request.request_id)"
                :disabled="request.request_quantity_remaining <= 0">
                Auto Match
              </AppButton>

              <AppButton 
                v-if="authStore.role === 'Admin' || authStore.role === 'Admin Observer'" 
                variant="info" 
                @click="viewRequestDetails(request.request_id)">
                View Details
              </AppButton>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, onBeforeRouteUpdate } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();
authStore.loadUserDataFromCookie();

const requests = ref([]);
const loading = ref(false);
const selectedCategory = ref('');
const sortBy = ref('newest');

// Computed properties for stats and filtering
const totalItemsNeeded = computed(() => {
  return requests.value.reduce((sum, request) => sum + request.request_quantity_remaining, 0);
});

const urgentRequests = computed(() => {
  return requests.value.filter(request => 
    request.request_quantity_remaining > request.quantity * 0.8
  ).length;
});

const uniqueCategories = computed(() => {
  const categories = [...new Set(requests.value.map(request => request.category))];
  return categories.sort();
});

const filteredAndSortedRequests = computed(() => {
  let filtered = requests.value;

  // Apply category filter
  if (selectedCategory.value) {
    filtered = filtered.filter(request => request.category === selectedCategory.value);
  }

  // Apply sorting
  const sorted = [...filtered];
  switch (sortBy.value) {
    case 'newest':
      // Assuming request_id correlates with creation time
      sorted.sort((a, b) => b.request_id - a.request_id);
      break;
    case 'oldest':
      sorted.sort((a, b) => a.request_id - b.request_id);
      break;
    case 'quantity_desc':
      sorted.sort((a, b) => b.quantity - a.quantity);
      break;
    case 'quantity_asc':
      sorted.sort((a, b) => a.quantity - b.quantity);
      break;
    case 'remaining_desc':
      sorted.sort((a, b) => b.request_quantity_remaining - a.request_quantity_remaining);
      break;
    case 'remaining_asc':
      sorted.sort((a, b) => a.request_quantity_remaining - b.request_quantity_remaining);
      break;
  }

  return sorted;
});

// Load requests data
const loadRequests = async () => {
  loading.value = true;
  try {
    const response = await api.get('/getRequestsForResponse');
    // Keep all requests but show their current remaining status
    requests.value = response.data || [];
    console.log('Loaded requests:', requests.value);
  } catch (error) {
    console.error('Error fetching requests:', error);
    alert('Error loading requests. Please try again.');
  } finally {
    loading.value = false;
  }
};

// Helper functions
const getProgressPercentage = (request) => {
  if (request.quantity === 0) return 0;
  const fulfilled = request.quantity - request.request_quantity_remaining;
  return Math.round((fulfilled / request.quantity) * 100);
};

const getStatusText = (request) => {
  if (request.request_quantity_remaining <= 0) {
    return 'Fully Pledged';
  } else if (request.request_quantity_remaining < request.quantity) {
    return 'Partially Pledged';
  } else {
    return 'Needs Pledges';
  }
};

const getStatusClass = (request) => {
  if (request.request_quantity_remaining <= 0) {
    return 'status-complete';
  } else if (request.request_quantity_remaining < request.quantity) {
    return 'status-partial';
  } else {
    return 'status-pending';
  }
};

// Filter and sort functions
const applyFilters = () => {
  // Computed property will automatically update
};

const applySorting = () => {
  // Computed property will automatically update
};

// Navigation functions
const respondToRequest = (requestId) => {
  router.push({ path: `/respond/${requestId}` });
};

const goToMatchForm = (requestId) => {
  router.push({ path: `/create-match/${requestId}` });
};

const goToAutoMatch = (requestId) => {
  router.push({ path: `/auto-match/${requestId}` });
};

const viewRequestDetails = (requestId) => {
  router.push({ path: `/request-details/${requestId}` });
};

// Auto-refresh when returning from other pages
onMounted(() => {
  loadRequests();
});

// Refresh when navigating back from a response/match page
onBeforeRouteUpdate((to, from, next) => {
  loadRequests();
  next();
});

// Check for reload flag from localStorage (set when returning from pledge creation)
if (localStorage.getItem('reloadRequests')) {
  loadRequests();
  localStorage.removeItem('reloadRequests');
}

// Watch for route changes to refresh data
watch(() => router.currentRoute.value.fullPath, () => {
  if (router.currentRoute.value.name === 'respond-to-requests') {
    loadRequests();
  }
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.respond-container {
  font-family: 'Poppins', sans-serif;
  max-width: 1200px;
  margin: auto;
  padding: 50px 20px;
  text-align: center;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
}

.respond-header {
  background: #f5e1c5;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 28px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
}

.description {
  color: #6c757d;
  font-size: 16px;
  margin-bottom: 30px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: #8B5E3C;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(139, 94, 60, 0.3);
  border-radius: 50%;
  border-top-color: #8B5E3C;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-requests {
  font-size: 18px;
  color: #777;
  padding: 40px;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.summary-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30px;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-card {
  background: #ffffff;
  border: 2px solid #d3c0a3;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  min-width: 120px;
  flex: 1;
}

.stat-card h3 {
  color: #5c4033;
  font-size: 14px;
  margin-bottom: 10px;
  font-weight: 500;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #5c4033;
  margin: 0;
}

.stat-number.urgent {
  color: #dc3545;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
  flex-wrap: wrap;
  background: #ffffff;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #d3c0a3;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  text-align: left;
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
  font-size: 14px;
  background-color: #fcfcfc;
  min-width: 150px;
}

.refresh-btn {
  margin-left: auto;
}

.request-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.request-card {
  background: #ffffff;
  border: 2px solid #d3c0a3;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 20px;
  text-align: left;
  transition: all 0.3s ease;
  color: #5c4033;
}

.request-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.request-title {
  font-size: 20px;
  font-weight: 600;
  color: #5c4033;
  margin: 0;
  flex: 1;
}

.request-status {
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  margin-left: 15px;
}

.status-complete {
  background-color: #d4edda;
  color: #155724;
}

.status-partial {
  background-color: #fff3cd;
  color: #856404;
}

.status-pending {
  background-color: #f8d7da;
  color: #721c24;
}

.request-location {
  background-color: #e8f5e8;
  padding: 12px 15px;
  border-radius: 8px;
  margin: 15px 0;
  border-left: 4px solid #2e8b57;
  font-size: 16px;
  color: #2e8b57;
}

.request-details {
  margin: 20px 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: #666;
  min-width: 120px;
}

.detail-value {
  color: #5c4033;
  font-weight: 500;
}

.detail-value.remaining {
  font-size: 18px;
  font-weight: 600;
  color: #007bff;
}

.detail-value.remaining.urgent {
  color: #dc3545;
}

.request-description {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-top: 15px;
  border-left: 4px solid #8B5E3C;
  color: #5c4033;
  line-height: 1.5;
}

.progress-section {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.progress-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background-color: #e9ecef;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 5px;
}

.progress-fill {
  height: 100%;
  background-color: #007bff;
  transition: width 0.3s ease;
}

.progress-fill.completed {
  background-color: #28a745;
}

.progress-percentage {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-align: right;
}

.button-group {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

/* Responsive design */
@media (max-width: 768px) {
  .summary-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-group select {
    min-width: 100%;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .request-status {
    margin-left: 0;
    align-self: flex-start;
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .button-group {
    flex-direction: column;
  }
}
</style>