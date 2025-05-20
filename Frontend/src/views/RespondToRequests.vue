<template>
  <div class="event-view-container">
    <h2 class="event-header">Respond to Requests</h2>
    <p>Browse the list of disaster relief requests that need your help.</p>

    <div v-if="requests.length === 0" class="no-events">No requests available at the moment.</div>

    <ul class="event-list">
      <li v-for="request in requests" :key="request.request_id" class="event-card">
        <h3 class="event-title">{{ request.event_name }} - {{ request.category }}</h3>
        <p v-if="request.item_name"><strong>Specific Item:</strong> {{ request.item_name }}</p>
        <p><strong>Requested Quantity:</strong> {{ request.quantity }}</p>
        <p v-if="request.details && request.details.trim() !== ''"><strong>Details:</strong> {{ request.details }}</p>
        <p><strong>Remaining Needed:</strong> {{ request.request_quantity_remaining }}</p>

        <div class="button-group">
          <button v-if="authStore.role == 'Donor'" class="action-btn" @click="respondToRequest(request.request_id)">Respond</button>
          <button v-if="authStore.role == 'Admin'" class="action-btn" @click="goToMatchForm(request.request_id)">Manual Match</button>
          <button v-if="authStore.role == 'Admin'" class="action-btn" @click="goToAutoMatch(request.request_id)">Auto Match</button>
        </div>
      </li>
    </ul>
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
  router.push({ path: `/create-match/${requestId}`});
};

const goToAutoMatch = (requestId) => {
  router.push({ path: `/auto-match/${requestId}`});
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.event-view-container {
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C;
  max-width: 800px;
  margin: auto;
  padding: 50px 20px;
  text-align: center;
}

.event-header {
  background: #f5e1c5;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 28px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
}

.no-events {
  font-size: 18px;
  color: #777;
  margin-top: 20px;
}

.event-list {
  list-style: none;
  padding: 0;
  margin-top: 30px;
}

.event-card {
  background: #f9f9f9;
  border: 1px solid #d3c0a3;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  text-align: left;
  transition: box-shadow 0.3s ease;
}

.event-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.event-title {
  font-size: 22px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 10px;
}

.button-group {
  margin-top: 15px;
}

.action-btn {
  font-size: 14px;
  padding: 8px 14px;
  margin-right: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.3s ease;
  background-color: #8B5E3C;
  color: white;
}

.action-btn:hover {
  background-color: #6A3E2B;
  transform: scale(1.05);
}
</style>