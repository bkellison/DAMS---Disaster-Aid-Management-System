<script setup>
import { ref, onMounted, computed  } from 'vue'
import { useAuthStore } from '@/stores/auth';
import { RouterView, useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.role === 'Admin');
const isDonor = computed(() => authStore.role === 'Donor');

const pledges = ref([])

async function getPledges() {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/getPledges?user_id=${authStore.userId}`)
        pledges.value = response.data;
    } catch (error) {
        console.error('Error getting pledges:', error);
        throw error;
    }
}

onMounted(() => {
    getPledges();
})

const goToPledgeForm = () => {
  router.push({ path: '/create-pledge' })
}

async function cancelPledge(pledge_id) {
    try {
        await axios.post(`http://127.0.0.1:5000/cancelPledge/${pledge_id}`)
        getPledges()
    } catch (error) {
        console.error('Error cancelling pledge:', error);
        throw error;
    }
}

const rowToEditId = ref(null)
const allowEdit = (pledge) => {
    if(rowToEditId.value == pledge.pledge_id) {
        if (pledge.item_quantity < pledge.items_locked) {
            alert('You cannot update pledge to equal less then locked items')
        }
        updatePledge(pledge, pledge.item_quantity)
        rowToEditId.value = null
    }
    else {
        rowToEditId.value = pledge.pledge_id
    }
}

async function updatePledge(pledge, qty) {
    // Prepare the payload
    const updatePledgeObject = {
        pledge_id: pledge.pledge_id,
        item_quantity: qty,
        user_id: authStore.userId
    };

    try {
        const response = await axios.post('http://127.0.0.1:5000/updatePledge', updatePledgeObject);
        router.push({ path: `/pledge-view`, replace: true });
    } catch (error) {
        console.error('Error creating pledge:', error);
        throw error;
    }
}
</script>

<template>
    <div class="pledge-container">
      <div class="pledge-wrapper">
        <h1 class="pledge-header">Pledges View</h1>
        
        <div v-if="!isAdmin" class="action-button-container">
          <button @click="goToPledgeForm" class="create-btn">+ Create New Pledge</button>
        </div>

        <table class="pledge-table">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Item</th>
                    <th>Pledged Qty</th>
                    <th>Qty (Locked / Left)</th>
                    <th v-if="isAdmin">Donor</th>
                    <th v-if="isAdmin">Zipcode</th>
                    <th v-if="isAdmin || isDonor">Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(pledge, index) in pledges" :key="index">
                    <td>{{ pledge.category_name }}</td>
                    <td>{{ pledge.item_name }}</td>
                    <td v-if="rowToEditId == pledge.pledge_id">
                       <input type="number" v-model="pledge.item_quantity" class="qty-input" />
                    </td>
                    <td v-else>
                        {{ pledge.item_quantity }}
                    </td>
                    <td>{{ pledge.items_locked }} / {{ pledge.items_left }}</td>
                    <td v-if="isAdmin">{{ pledge.donor_id }}</td>
                    <td v-if="isAdmin">{{ pledge.zip_code }}</td>
                    <td v-if="isAdmin || isDonor" class="action-buttons">
                        <button @click="allowEdit(pledge)" title="Update Pledged Qty" class="update-btn">
                          {{ rowToEditId == pledge.pledge_id ? 'Save' : 'Update' }}
                        </button>
                        <button @click="cancelPledge(pledge.pledge_id)" title="Cancel Remaining Pledged Items" class="delete-btn">
                          Cancel
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
  
.pledge-container {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    color: #f5e1c5; 
    max-width: 1000px;
    margin: auto;
    padding: 50px 20px; 
}
  
.pledge-wrapper {
    background-color: #5c4033; 
    padding: 50px; 
    border-radius: 12px;
    margin-top: 40px; 
    border: 10px solid #c9b28e;

}
  
.pledge-header {
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

.action-button-container {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 20px;
}

.create-btn {
    background: #2e8b57;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.create-btn:hover {
    background: #236b43;
}

.pledge-table {
    width: 100%;
    margin-top: 30px;
    border-collapse: collapse;
    border: 5px solid #c9b28e;

}

.pledge-table th,
.pledge-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #ddd;
    font-size: 16px;
}

.pledge-table th {
    background-color: #f5e1c5;
    color: #5c4033;
    text-align: left;
}

.pledge-table td {
    background-color: #fdf6ee;
    color: #5c4033;
    text-align: left;
}

.action-buttons {
    display: flex;
    gap: 8px;
}

.update-btn {
    background-color: #0077cc;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.update-btn:hover {
    background-color: #005fa3;
    transform: scale(1.05);
}

.delete-btn {
    background-color: #e63946;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.delete-btn:hover {
    background-color: #c82333;
    transform: scale(1.05);
}

.qty-input {
    width: 80px;
    padding: 6px;
    border: 1px solid #ccc;
    border-radius: 4px;
}
</style>