<script setup>
import { ref, onMounted, computed  } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { RouterView, useRoute, useRouter } from 'vue-router';
import axios from 'axios';

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

//Hardcoded / Mock Data temporarily
onMounted(() => {
    getRequests();
})

const createNewRequest = () => {
  router.push({ path: `/create-request` });
}
</script>

<template>
    <div class="requests-container">
      <div class="content-box">
        <h1 class="requests-header">Your Requests</h1>
        
        <div class="action-section">
          <button class="create-btn" @click="createNewRequest">Create New Request</button>
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
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(request, index) in requests" :key="index">
                        <td>{{ request.event_name }}</td>
                        <td>{{ request.location }}</td>
                        <td>{{ request.category_name }}</td>
                        <td>{{ request.item_name }}</td>
                        <td>{{ request.request_quantity_remaining }}</td>
                        <td>{{ request.request_status }}</td>
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
    max-width: 1000px;
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

/* Create button styling */
.create-btn {
  background: #2e8b57;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.create-btn:hover {
  background: #236b43;
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
    text-align: left;
}

.requests-table td {
    background-color: #f9f3e8;
    color: #5c4033;
    text-align: left;
}
</style>