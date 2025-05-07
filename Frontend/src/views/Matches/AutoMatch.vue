<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth'


const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();



const matchTypes = ref({})
const selectedRequest = ref({})

async function getMatchType() {
    try {
        const response = await axios.get(`http://127.0.0.1:5000/api/getAutoMatchType`)
        if(response.data != [])
        {
            console.log("types!")
            matchTypes.value = response.data
            console.log(response.data)
        }
    } catch (error) {
        console.error('Error getting match types:', error);
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

async function createAutoMatch(selectedRequest, matchType) 
{
    try
    {
        let matchRequest = {
            request_id: selectedRequest.request_id,
            match_type_name: matchType.name
        }
        const response = await axios.post('http://127.0.0.1:5000/api/autoMatch', matchRequest)
        .then((response) => {
            console.log(response)
            if(response.status == 200){
                alert(response.data.message),
                router.push({ path: `/match-view`, replace: true })
            }
            else
            {
                alert(response.error)
            };
            
        }).catch((response) =>{
            console.log(response)
            alert('No Pledges to Match')
            router.push({ path: `/respond-to-requests`, replace: true })
        })
    }
    catch (error)
    {
        console.log('Match Creation Failed', error)
    }

}
//Hardcoded / Mock Data temporarily
onMounted(() => {
    const requestId = route.params.id;
    getRequestId(requestId);
    getMatchType();
    
})
</script>

<template>
    <div class="auto-match-container">
    <h1 class="auto-match-header">Initiate Auto Match</h1>
    <div v-if="selectedRequest.request_quantity_remaining < 1" class="auto-match-info">
       Request has enough pledges and matches to fulfill
    </div> 
    <div v-else class="auto-match-info">
        <h2>Matching for Request: {{ selectedRequest.event_name }}</h2>
        <p v-if="selectedRequest.requester_zipcode != null">Recipient Zipcode: {{ selectedRequest.requester_zipcode }}</p>
        <div>Item Reqested: {{ selectedRequest.item_name }} / Request Count: {{ selectedRequest.request_quantity_remaining }}</div>
        <div>
            <button v-for="matchType in matchTypes" :key="matchType.match_type_id" :value="matchType.match_type_id" @click="createAutoMatch(selectedRequest, matchType)">
                {{ matchType.name }}
            </button>
        </div>
    </div>
    <div>
    </div>
  </div>
</template>

<style scoped>
/* Registration Page Container Styling */
.auto-match-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C; 
  max-width: 600px;
  margin: auto;
  padding: 50px 20px;
}

/* Registration Header Styling */
.auto-match-header {
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
  margin-right: 10px;
  margin-top: 20px;
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