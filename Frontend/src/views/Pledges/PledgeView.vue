<script setup>
import { ref, onMounted, computed  } from 'vue'
import { useAuthStore } from '@/stores/auth'
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
async function cancelPledge (pledge_id)
{
    try {
        await axios.post(`http://127.0.0.1:5000/cancelPledge/${pledge_id}`)
        getPledges()
    } catch (error) {
        console.error('Error getting pledges:', error);
        throw error;
    }
}

const rowToEditId = ref(null)
const allowEdit = (pledge) => {
    if(rowToEditId.value == pledge.pledge_id)
    {
        if (pledge.item_quantity < pledge.items_locked)
        {
            alert('You cannot update pledge to equal less then locked items')
        }
        updatePledge(pledge, pledge.item_quantity)
        rowToEditId.value = null
    }
    else 
    {
        rowToEditId.value = pledge.pledge_id
    }
}
async function updatePledge (pledge, qty) {
    
    // Prepare the payload
    const updatePledgeObject = {
        pledge_id: pledge.pledge_id,
        item_quantity: qty,
        user_id: authStore.userId //logged in users id
    };

    try {
        const response = await axios.post('http://127.0.0.1:5000/updatePledge', updatePledgeObject);
        router.push({ path: `/pledge-view`, replace: true });
    } catch (error) {
        console.error('Error creating pledge:', error);
        throw error; // Throw error
    }

}

</script>

<template>
    <div class="pledges-container">
      <div class="pledges-wrapper">
        <h1 class="pledges-header">Pledges View</h1>

        <table class="pledge-table">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Item</th>
                    <th>Pledged Qty</th>
                    <th>Qty (Locked / Left)</th>
                    <th v-if="isAdmin">Donor</th>
                    <th v-if="isAdmin">Zipcode</th>
                    <th v-if="isAdmin || isDonor">Modify</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(pledge, index) in pledges" :key="index">
                    <td>{{ pledge.category_name }}</td>
                    <td>{{ pledge.item_name }}</td>
                    <td v-if="rowToEditId == pledge.pledge_id">
                       <input type="number" v-model="pledge.item_quantity" />
                    </td>
                    <td v-else>
                        {{ pledge.item_quantity }}
                    </td>
                    <td>{{ pledge.items_locked }} / {{ pledge.items_left }}</td>
                    <td v-if="isAdmin">Donor: {{ pledge.donor_id }}</td>
                    <td v-if="isAdmin">{{ pledge.zip_code }}</td>
                    <td v-if="isAdmin || isDonor">
                        <button @click="allowEdit(pledge)" title="Update Pledged Qty">{{ rowToEditId == pledge.pledge_id ? 'Save' : 'Update' }}</button>
                        <button @click="cancelPledge(pledge.pledge_id)" title="Cancel Remaining Pledged Items">Cancel</button>
                    </td>
                </tr>
                <tr v-if="!isAdmin" class="form-btn" @click="goToPledgeForm">
                    <td>+ Create Pledge</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
            </tbody>
        </table>
      </div>
    </div>
</template>

<style scoped>
/* Font for text*/
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
  
/* Admin page container styling */
.pledges-container {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    color: #f5e1c5; 
    max-width: 1000px;
    margin: auto;
    padding: 50px 20px; 
}
  
/* Wrapper for admin content */
.pledges-wrapper {
    background-color: #5c4033; 
    padding: 50px; 
    border-radius: 12px;
    margin-top: 40px; 
}
  
/* Admin header styling */
.pledges-header {
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
.pledge-table {
    width: 100%;
    margin-top: 30px;
    border-collapse: collapse;
}

.pledge-table th,
.pledge-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #ddd;
    font-size: 18px;
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

/* Button styling */
.pledge-table button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  color: white;;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 18px;
  margin-top: 20px; 
  margin-right: 10px;
}

.pledge-table button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C)
}
</style>