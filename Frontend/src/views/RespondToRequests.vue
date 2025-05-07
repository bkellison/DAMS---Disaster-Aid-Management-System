<template>
  <div class="response-container">
    <h1 class="response-header">Respond to Requests</h1>
    <p>Select a request to respond to:</p>

    <div v-if="requests.length === 0">
      <p>No requests available to respond to at the moment.</p>
    </div>

    <div v-else>
      <div v-for="request in requests" :key="request.request_id" class="request-box">
        <h3>{{ request.event_name }} - {{ request.category_name }}</h3>
        <p v-if="request.item_name">Specific Item: {{ request.item_name }}</p>
        <p>Requested Quantity: {{ request.quantity }}</p>
        <p v-if="request.details != '' && request.details != null">Details: {{ request.details }}</p>
        <button v-if="authStore.role == 'Donor'" @click="respondToRequest(request.request_id)">Respond</button>
        <!-- <button v-if="authStore.role == 'Recipient'" @click="respondToRequest(request.request_id)">View Request</button> -->
        <button v-if="authStore.role == 'Admin'" @click="goToMatchForm(request.request_id)">Manual Match</button>
        <button v-if="authStore.role == 'Admin'" @click="goToAutoMatch(request.request_id)">Auto Match</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();
authStore.loadUserDataFromCookie();
const requests = ref([]);

onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/getRequestsForResponse');
    requests.value = response.data.filter(i => i.request_quantity_remaining > 0) || [];
  } catch (error) {
    console.error('Error fetching requests:', error);
  }
});

// Navigate to the "Pledge" or "Response" page
const respondToRequest = (requestId) => {
  router.push({ path: `/respond/${requestId}` });
};

const goToMatchForm = (requestId) => {
  router.push({ path: `/create-match/${requestId}`})
}

const goToAutoMatch = (requestId) => {
  router.push({ path: `/auto-match/${requestId}`})
}
</script>

<style scoped>
.response-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C;
  max-width: 800px;
  margin: auto;
  padding: 50px 20px;
}

.response-header {
  background: #f5e1c5;
  padding: 15px 65px;
  border-radius: 20px;
  display: inline-block;
  font-size: 32px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
}

.request-box {
  background: #f5e1c5;
  padding: 20px;
  border-radius: 12px;
  margin: 20px 0;
}

.request-box h3 {
  font-size: 24px;
  font-weight: 600;
  color: #5c4033;
}

.request-box p {
  font-size: 16px;
  font-weight: 400;
  color: #5c4033;
  margin-bottom: 10px;
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
  margin-right: 10px;
}

.request-box button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}
</style>