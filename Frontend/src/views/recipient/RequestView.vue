<script setup>
import { ref, onMounted, computed  } from 'vue'
import { useAuthStore } from '@/stores/auth';
import { RouterView, useRoute, useRouter } from 'vue-router';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.role === 'Admin');

const requests = ref([])

async function getRequests() {
    try {
        const response = await api.get(`/getRequests?user_id=${authStore.userId}`)
        requests.value = response.data.filter(i => i.request_quantity_remaining > 0);
    } catch (error) {
        console.error('Error getting requests:', error);
        throw error;
    }
}

onMounted(() => {
    getRequests();
})

const createNewRequest = () => {
  router.push({ path: `/create-request` });
}

const getStatusClass = (status) => {
  const lowerStatus = (status || 'pending').toLowerCase();
  switch (lowerStatus) {
    case 'shipped':
      return 'status-shipped';
    case 'delivered':
      return 'status-delivered';
    default:
      return 'status-pending';
  }
}

const getMatchTypeBadgeClass = (matchTypeName) => {
  if (!matchTypeName) return 'match-type-none';
  const lowerName = matchTypeName.toLowerCase();
  switch (lowerName) {
    case 'nearest':
      return 'match-type-nearest';
    case 'quickest':
      return 'match-type-quickest';
    case 'fulfillment':
      return 'match-type-fulfillment';
    default:
      return 'match-type-default';
  }
}

</script>

<template>
    <div class="requests-container">
      <div class="content-box">
        <h1 class="requests-header">Your Requests</h1>
        
        <div class="action-section">
          <AppButton variant="add" @click="createNewRequest">Create New Request</AppButton>
        </div>

        <div v-if="requests.length === 0" class="no-requests-message">
            <p>You don't have any active requests. Click "Create New Request" to get started.</p>
        </div>

        <div v-else>
            <div class="requests-grid">
                <div v-for="(request, index) in requests" :key="index" class="request-card">
                    <div class="request-header">
                        <h3 class="request-title">{{ request.event_name }} - {{ request.category_name }}</h3>
                        <div class="request-location">
                            {{ request.location || 'Location not specified' }}
                        </div>
                    </div>
                    
                    <div class="request-details">
                        <div class="detail-row">
                            <strong>Specific Item:</strong> 
                            <span>{{ request.item_name || 'Any item in category' }}</span>
                        </div>
                        
                        <div class="detail-row">
                            <strong>Qty Remaining:</strong> 
                            <span class="quantity-badge">{{ request.request_quantity_remaining }}</span>
                        </div>
                        
                        <div class="detail-row">
                            <strong>Status:</strong> 
                            <span 
                                :class="[
                                'status-label',
                                getStatusClass(request.request_status)
                                ]"
                            >
                                {{ request.request_status?.toLowerCase() || 'pending' }}
                            </span>
                        </div>
                        
                        <div class="detail-row">
                            <strong>Preferred Match:</strong>
                            <span 
                                :class="[
                                'match-type-badge',
                                getMatchTypeBadgeClass(request.preferred_match_type_name)
                                ]"
                                :title="request.preferred_match_type_name ? `You requested ${request.preferred_match_type_name} matching` : 'No preference specified'"
                            >
                                {{ request.preferred_match_type_name || 'Not specified' }}
                            </span>
                        </div>
                        
                        <div v-if="request.request_details && request.request_details.trim() !== ''" class="detail-row">
                            <strong>Details:</strong> 
                            <span>{{ request.request_details }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
      </div>
    </div>
</template>

<style scoped>
/* Font for text*/
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
  
/* Container styling */
.requests-container {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    color: #5c4033; 
    max-width: 1200px;
    margin: auto;
    padding: 50px 20px; 
}
  
/* Content box styling */
.content-box {
    background-color: #5c4033;
    border-radius: 15px;
    padding: 40px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    border: 10px solid #c9b28e;
}
  
/* Header styling */
.requests-header {
    background: #f5e1c5; 
    padding: 15px 65px; 
    border-radius: 20px;
    display: inline-block;
    font-size: 32px; 
    font-weight: 600;
    color: #5c4033; 
    margin-bottom: 25px; 
    border: 5px solid #c9b28e;
}

/* Action section styling */
.action-section {
    margin-bottom: 30px;
    text-align: left;
}

/* No requests message styling */
.no-requests-message {
    background: #f9f3e8;
    border-radius: 10px;
    padding: 30px;
    margin: 20px 0;
    border: 1px solid #e0d4c3;
}

.no-requests-message p {
    font-size: 18px;
    color: #5c4033;
}

/* Grid layout for request cards */
.requests-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 20px;
    margin-top: 30px;
}

/* Request card styling */
.request-card {
    background: #f9f3e8;
    border: 2px solid #c9b28e;
    border-radius: 15px;
    padding: 25px;
    text-align: left;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.request-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.request-header {
    margin-bottom: 20px;
    border-bottom: 1px solid #d3c0a3;
    padding-bottom: 15px;
}

.request-title {
    font-size: 20px;
    font-weight: 600;
    color: #5c4033;
    margin-bottom: 10px;
}

.request-location {
    background-color: #e8f5e8;
    padding: 8px 12px;
    border-radius: 6px;
    border-left: 3px solid #2e8b57;
    font-size: 14px;
    color: #2e8b57;
}

.request-details {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}

.detail-row strong {
    color: #5c4033;
    font-weight: 600;
    min-width: 120px;
}

.quantity-badge {
    background: linear-gradient(135deg, #2e8b57, #227548);
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 14px;
}

.status-label {
    padding: 6px 12px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 14px;
    text-transform: capitalize;
    min-width: 80px;
    text-align: center;
}

.status-pending {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeeba;
}

.status-shipped {
    background-color: #cce5ff;
    color: #004085;
    border: 1px solid #99d3ff;
}

.status-delivered {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #8fcea5;
}

/* Match type badge styling */
.match-type-badge {
    padding: 6px 12px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 13px;
    color: white;
    text-transform: capitalize;
    min-width: 80px;
    text-align: center;
    cursor: help;
}

.match-type-nearest {
    background: linear-gradient(135deg, #0077cc, #005fa3);
}

.match-type-quickest {
    background: linear-gradient(135deg, #e6a23c, #cc8500);
}

.match-type-fulfillment {
    background: linear-gradient(135deg, #2e8b57, #227548);
}

.match-type-none, .match-type-default {
    background-color: #999;
    color: #fff;
}

/* Responsive design */
@media (max-width: 768px) {
    .requests-container {
        padding: 20px 10px;
    }
    
    .content-box {
        padding: 20px;
    }
    
    .requests-header {
        font-size: 24px;
        padding: 12px 30px;
    }
    
    .requests-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .request-card {
        padding: 20px;
    }
    
    .detail-row {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .detail-row strong {
        min-width: auto;
    }
}

/* Single column on very small screens */
@media (max-width: 480px) {
    .requests-grid {
        grid-template-columns: 1fr;
    }
    
    .request-title {
        font-size: 18px;
    }
}
</style>