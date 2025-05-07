<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth'

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const selectedCategory = ref('');
const selectedItem = ref(null);
const itemQty = ref('');

const selectedRequest = ref({})
const pledges = ref([])

const selectedPledge = ref(null)
const selectedPledgeMatchCount = ref(0)

async function selectPledge(pledge)
{
    selectedPledge.value = pledge;
    selectedPledgeMatchCount.value = pledge.count
}

async function getPledges() {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/getPledges?user_id=${authStore.userId}`)
        pledges.value = response.data.filter(i => i.items_left > 0);
    } catch (error) {
        console.error('Error getting pledges:', error);
        throw error;
    }
}

async function getRequestId(requestId) {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/getRequests?user_id=${authStore.userId}&request_id=${requestId}`)
        if(response.data != [])
        {
            selectedRequest.value = response.data[0]
        }
    } catch (error) {
        console.error('Error getting request id:', error);
        throw error;
    }
}

//Hardcoded / Mock Data temporarily
onMounted(() => {
    const requestId = route.params.id;
    getRequestId(requestId);
    getPledges();
})

async function createManualMatch(selectedRequest) 
{
    try
    {
        let matchRequest = {
            requestId: selectedRequest.request_id,
            pledgeId: selectedPledge.value.pledge_id,
            matchQuantity: selectedPledgeMatchCount.value
        }
        await axios.post('http://127.0.0.1:5000/createMatch', matchRequest)
        router.push({ path: `/match-view`, replace: true });
    }
    catch (error)
    {
        console.log('Match Creation Failed', error)
    }

}

watch(selectedPledgeMatchCount, (value) => {
    const num = parseInt(value);

    //add validation for match count
    if(!value || isNaN(num))
    {
        
    }
});

</script>

<template>
    <div class="register-container">
    <h1 class="register-header">Create Manual Match</h1>
    <div v-if="selectedRequest.request_quantity_remaining < 1" class="auto-match-info">
       Request has enough pledges and matches to fulfill
    </div>
    <div v-else>
      <div class="request-info">
        <h2>Matching for Request: {{ selectedRequest.event_name }}</h2>
        <p v-if="selectedRequest.requester_zipcode != null">Recipient Zipcode: {{ selectedRequest.requester_zipcode }}</p>
        <div>Item Reqested: {{ selectedRequest.item_name }} / Request Count: {{ selectedRequest.request_quantity_remaining }}</div>
        <!-- <ul> -->
            <!-- <div v-for="(item, index) in selectedRequest.requestIdItem" :key="index">
                {{ item.itemName }} ({{ item.count }})
            </div> -->
        <!-- </ul> -->
      </div>
      <div v-if="pledges.filter(i => i.item_id == selectedRequest.item_id)" class="pledge-list">
          <h3>Select a Pledge to Match</h3>
          <!-- <ul> -->
              <div v-for="pledge in pledges" :key="pledge.pledge_id">
                  <button v-if="pledge.item_id == selectedRequest.item_id" style="margin-bottom: 10px;" @click="selectPledge(pledge)">
                      {{ pledge.item_name }} (Available: {{ pledge.items_left }})
                  </button>
              </div>
          <!-- </ul> -->
      </div>
      <div v-else>No pledges match requested items</div>
      <div v-if="selectedPledge" class="update-match">
          <h3>Selected: {{ selectedPledge.item_name }}</h3>
          <label style="margin-right: 5px; color: white;">Match Quantity</label>
          <input type="number" v-model="selectedPledgeMatchCount" min="1" :max="selectedPledge.request_quantity" style="margin-right: 5px;" />
          <button @click="createManualMatch(selectedRequest)">Create Match</button>
      </div>      
    </div>
    
    <!-- <form @submit.prevent="createManualMatch">
        <label>Category:</label>
        <select v-model="selectedCategory" required>
            <option v-for="category in categories" :key="category.categoryId" :value="category.categoryId">
                {{ category.categoryName }}
            </option>
        </select>

      <label>Item:</label>
      <select v-model="selectedItem" required :disabled="selectedCategory == ''">
        <option v-for="item in filteredItems" :key="item.itemId" :value="item.itemId">
            {{ item.itemName }}
        </option>
      </select>

      <label>Item Qty:</label>
      <input type="number" v-model="itemQty" required :disabled="selectedItem == null"/>

      <button type="submit">Make Pledge</button>
    </form> -->
  </div>
</template>

<style scoped>

/* Registration Page Container Styling */
.register-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C; 
  max-width: 600px;
  margin: auto;
  padding: 50px 20px;
}

/* Registration Header Styling */
.register-header {
  background: #f5e1c5; 
  padding: 15px 65px; 
  border-radius: 20px;
  display: inline-block;
  font-size: 32px; 
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px; 
}

/* Form Styling */
form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Label Styling */
label {
  font-size: 16px;
  font-weight: 500;
  color: #5c4033;
  text-align: left;
}

/* Input and Select Styling */
input, select {
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 18px;
}

/* Button Styling */
button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 18px;
}

/* Button Hover Effect */
button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}

/* Text and Link Styling */
p {
  margin-top: 20px;
}

a {
  color: #8B5E3C;
  text-decoration: none;
  font-weight: 600;
}

a:hover {
  text-decoration: underline;
}

.request-info,
.pledge-list,
.update-match {
  margin-bottom: 20px;
}

.match-form {
  font-family: 'Poppins', sans-serif;
  padding: 20px;
}
</style>

