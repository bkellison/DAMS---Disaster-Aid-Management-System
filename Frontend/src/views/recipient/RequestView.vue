<script setup>
import { ref, onMounted, computed  } from 'vue'
import { useAuthStore } from '@/stores/auth';
import { RouterView, useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import AppButton from '@/components/common/AppButton.vue';

const router = useRouter();
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.role === 'Admin');

const requests = ref([])

async function getRequests() {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/getRequests?user_id=${authStore.userId}`)
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
            <table class="requests-table">
                <thead>
                    <tr>
                        <th>Event</th>
                        <th>Event Location</th>
                        <th>Category</th>
                        <th>Item</th>
                        <th>Qty Remaining</th>
                        <th>Status</th>
                        <th>Preferred Match</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(request, index) in requests" :key="index">
                        <td>{{ request.event_name }}</td>
                        <td>{{ request.location }}</td>
                        <td>{{ request.category_name }}</td>
                        <td>{{ request.item_name || 'Any item in category' }}</td>
                        <td>{{ request.request_quantity_remaining }}</td>
                        <td>
                            <span 
                                :class="[
                                'status-label',
                                getStatusClass(request.request_status)
                                ]"
                            >
                                {{ request.request_status?.toLowerCase() || 'pending' }}
                            </span>
                        </td>
                        <td>
                            <span 
                                :class="[
                                'match-type-badge',
                                getMatchTypeBadgeClass(request.preferred_match_type_name)
                                ]"
                                :title="request.preferred_match_type_name ? `You requested ${request.preferred_match_type_name} matching` : 'No preference specified'"
                            >
                                {{ request.preferred_match_type_name || 'Not specified' }}
                            </span>
                        </td>
                    </tr>
                </tbody>
            </table>
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

/* Table styling */
.requests-table {
    width: 100%;
    margin-top: 30px;
    border-collapse: collapse;
    border: 5px solid #c9b28e;
}

.requests-table th,
.requests-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #d3c0a3;
    font-size: 16px;
}

.requests-table th {
    background-color: #f5e1c5;
    color: #5c4033;
    text-align: center;
    font-weight: 600;
}

.requests-table td {
    background-color: #f9f3e8;
    color: #5c4033;
    text-align: center;
}

.status-label {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 14px;
    color: white;
    text-transform: capitalize;
    min-width: 80px;
    text-align: center;
}

.status-pending {
    color: #b8860b;
    font-weight: bold;
}

.status-shipped {
    color: #0066cc;
    font-weight: bold;
}

.status-delivered {
    color: #2e8b57;
    font-weight: bold;
}

/* Match type badge styling */
.match-type-badge {
    display: inline-block;
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
    
    .requests-table {
        font-size: 14px;
    }
    
    .requests-table th,
    .requests-table td {
        padding: 8px 4px;
    }
    
    .match-type-badge,
    .status-label {
        font-size: 12px;
        padding: 4px 8px;
        min-width: 60px;
    }
}

/* Table overflow for mobile */
@media (max-width: 600px) {
    .requests-table {
        display: block;
        overflow-x: auto;
        white-space: nowrap;
    }
}
</style>