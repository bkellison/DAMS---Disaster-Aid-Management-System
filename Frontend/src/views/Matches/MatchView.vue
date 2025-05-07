<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

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
                      <button @click="viewShippingDetails(match)" class="action-btn">
                        {{ match.shipping_status === 'pending' ? 'Update Shipping' : 'View Shipping' }}
                      </button>
                    </td>
                </tr>
            </tbody>
        </table>
      </div>
    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
  
.match-container {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    color: #f5e1c5; 
    max-width: 1000px;
    margin: auto;
    padding: 50px 20px; 
}
  
.match-wrapper {
    background-color: #5c4033; 
    padding: 50px; 
    border-radius: 12px;
    margin-top: 40px; 
}
  
.match-header {
    background: #f5e1c5; 
    padding: 15px 65px; 
    border-radius: 20px;
    display: inline-block;
    font-size: 32px; 
    font-weight: 600;
    color: #5c4033; 
    margin-bottom: 25px; 
}

.match-table {
    width: 100%;
    margin-top: 30px;
    border-collapse: collapse;
}

.match-table th,
.match-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #ddd;
    font-size: 18px;
}

.match-table th {
    background-color: #f5e1c5;
    color: #5c4033;
    text-align: left;
}

.match-table td {
    background-color: #fdf6ee;
    color: #5c4033;
    text-align: left;
}

.action-btn {
    background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    transition: transform 0.2s ease-in-out, background-color 0.3s;
}

.action-btn:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
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
</style>