<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const isAdmin = computed(() => authStore.role === 'Admin')
const isDonor = computed(() => authStore.role === 'Donor')
const isRecipient = computed(() => authStore.role === 'Recipient')

const matches = ref([])

async function getMatches() {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/getMatches?user_id=${authStore.userId}`)
        matches.value = response.data;
        console.log('Matches retrieved:', matches.value);
    } catch (error) {
        console.error('Error getting matches:', error);
        console.error('Error response:', error.response?.data);
    }
}

onMounted(() => {
    getMatches();
})

const viewShippingDetails = (match) => {
    router.push({ path: `/shipping/${match.match_id}` })
}

const getStatusClass = (status) => {
    switch(status) {
        case 'shipped':
            return 'status-shipped'
        case 'delivered':
            return 'status-delivered'
        default:
            return 'status-pending'
    }
}
</script>

<template>
    <div class="match-container">
      <div class="match-wrapper">
        <h1 class="match-header">Matches View</h1>
        <p class="description">Track matched donations, shipping information and delivery status.</p>

        <div class="table-container">
          <table class="match-table">
              <thead>
                  <tr>
                      <th>Event</th>
                      <th>Category</th>
                      <th>Item</th>
                      <th>Count</th>
                      <th>Match Status</th>
                      <th>Shipping Status</th>
                      <th>Actions</th>
                  </tr>
              </thead>
              <tbody>
                  <tr v-for="(match, index) in matches" :key="index">
                      <td>{{ match.event_name }}</td>
                      <td>{{ match.category_name }}</td>
                      <td>{{ match.item_name }}</td>
                      <td>{{ match.match_quantity }}</td>
                      <td>{{ match.match_status }}</td>
                      <td>
                        <span :class="getStatusClass(match.shipping_status)">
                          {{ match.shipping_status || 'pending' }}
                        </span>
                      </td>
                      <td>
                        <AppButton 
                          variant="primary" 
                          @click="viewShippingDetails(match)">
                          {{ match.shipping_status === 'pending' ? 'Update Shipping' : 'View Shipping' }}
                        </AppButton>
                      </td>
                  </tr>
              </tbody>
          </table>
        </div>
      </div>
    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
  
.match-container {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    color: #f5e1c5; 
    max-width: 1400px; /* Increased from 1000px */
    margin: auto;
    padding: 50px 20px; 
}
  
.match-wrapper {
    background-color: #5c4033; 
    padding: 50px; 
    border-radius: 12px;
    margin-top: 40px; 
    border: 10px solid #c9b28e;
    min-width: 1200px; /* Added minimum width */
    width: 100%; /* Ensure it takes full available width */
}
  
.match-header {
    background: #f5e1c5; 
    padding: 15px 65px; 
    border-radius: 20px;
    display: inline-block;
    font-size: 32px; 
    font-weight: 600;
    color: #5c4033; 
    margin-bottom: 15px; 
    border: 5px solid #c9b28e;
}

.description {
    color: #f5e1c5;
    font-size: 16px;
    margin-bottom: 30px;
}

.table-container {
    display: flex;
    justify-content: center;
    width: 100%;
}

.match-table {
    width: 100%;
    margin-top: 30px;
    border-collapse: collapse;
    border: 5px solid #c9b28e;
    min-width: 1000px; /* Added minimum width for table */
    table-layout: auto; /* Allow table to expand as needed */
}

.match-table th,
.match-table td {
    padding: 15px 20px; /* Increased padding from 12px 16px */
    border-bottom: 1px solid #ddd;
    font-size: 16px;
    white-space: nowrap; /* Prevent text wrapping */
    text-align: center;
}

.match-table th {
    background-color: #f5e1c5;
    color: #5c4033;
    font-weight: 600; /* Made headers more prominent */
}

.match-table td {
    background-color: #fdf6ee;
    color: #5c4033;
}

/* Make action column slightly wider for buttons */
.match-table th:last-child,
.match-table td:last-child {
    min-width: 180px;
    white-space: normal; /* Allow button text to wrap if needed */
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

/* Add responsive design for smaller screens */
@media (max-width: 1440px) {
  .match-container {
    max-width: 95%;
    padding: 30px 15px;
  }
  
  .match-wrapper {
    min-width: auto;
    padding: 30px;
  }
  
  .match-table {
    min-width: auto;
    font-size: 14px;
  }
  
  .match-table th,
  .match-table td {
    padding: 10px 12px;
  }
}

@media (max-width: 768px) {
  .match-container {
    padding: 20px 10px;
  }
  
  .match-wrapper {
    padding: 20px;
    border: 5px solid #c9b28e;
  }
  
  .match-header {
    font-size: 24px;
    padding: 12px 30px;
  }
  
  .match-table {
    font-size: 12px;
  }
  
  .match-table th,
  .match-table td {
    padding: 8px 6px;
  }
  
  .match-table th:last-child,
  .match-table td:last-child {
    min-width: 120px;
  }
}
</style>