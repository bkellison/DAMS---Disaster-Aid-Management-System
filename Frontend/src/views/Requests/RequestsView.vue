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
        console.error('Error getting pledges:', error);
        throw error;
    }
}

//Hardcoded / Mock Data temporarily
onMounted(() => {
    getRequests();
})

const goToMatchForm = (request) => {
  router.push({ path: `/create-match/${request.request_id}`})
}
</script>

<template>
    <div class="requests-container">
      <div class="requests-wrapper">
        <h1 class="requests-header">Requests View</h1>

        <div v-if="requests.length === 0">
            <p>No requests available to respond to at the moment.</p>
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
                        <!-- <th v-if="isAdmin">Action</th> -->
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
                        <!-- <td v-if="isAdmin">
                            <button class="action-btn" @click="goToMatchForm(request)">Find Match</button>
                        </td> -->
                    </tr>
                    <!-- <tr v-if="!isAdmin" class="form-btn" @click="goToMatchForm">
                        <td>+ Create Pledge</td>
                        <td></td>
                        <td></td>
                    </tr> -->
                </tbody>
            </table>
        </div>
        
      </div>
    </div>
</template>

<style scoped>
/* Font for text*/
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
  
/* Admin page container styling */
.requests-container {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    color: #f5e1c5; 
    max-width: 1000px;
    margin: auto;
    padding: 50px 20px; 
}
  
/* Wrapper for admin content */
.requests-wrapper {
    background-color: #5c4033; 
    padding: 50px; 
    border-radius: 12px;
    margin-top: 40px; 
}
  
/* Admin header styling */
.requests-header {
    background: #f5e1c5; 
    padding: 15px 65px; 
    border-radius: 20px;
    display: inline-block;
    font-size: 32px; 
    font-weight: 600;
    color: #5c4033; 
    margin-bottom: 25px; 
}

/* Table styling */
.requests-table {
    width: 100%;
    margin-top: 30px;
    border-collapse: collapse;
}

.requests-table th,
.requests-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #ddd;
    font-size: 18px;
}

.requests-table th {
    background-color: #f5e1c5;
    color: #5c4033;
    text-align: left;
}

.requests-table td {
    background-color: #fdf6ee;
    color: #5c4033;
    text-align: left;
}

/* Create Pledge Form */
.form-btn
{
    color: white;
    border: none;
    padding: 12px 20px;
    font-size: 18px;
    margin: 20px 0;
    cursor: pointer;
    transition: transform 0.2s ease-in-out, background-color 0.3s;
}

.form-btn:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #e89a79, #8B5E3C);
}

.action-btn {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

.action-btn:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}

.request-box button {
    background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
    transition: transform 0.2s ease-in-out, background-color 0.3s;
    color: white;
    border: none;
    padding: 12px;
    border-radius: 8px;
    font-size: 18px;
    margin-top: 20px;
  }
  
  .request-box button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
  }
</style>