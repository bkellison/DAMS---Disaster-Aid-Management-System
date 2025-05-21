<template>
  <div class="respond-container">
    <div class="content-box">
      <h2 class="respond-header">Respond to Requests</h2>
      <p class="description">Browse the list of disaster relief requests that need your help.</p>

      <div v-if="requests.length === 0" class="no-requests">No requests available at the moment.</div>

      <ul class="request-list">
        <li v-for="request in requests" :key="request.request_id" class="request-card">
          <h3 class="request-title">{{ request.event_name }} - {{ request.category }}</h3>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
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

.respond-container {
  font-family: 'Poppins', sans-serif;
  max-width: 1000px;
  margin: auto;
  padding: 50px 20px;
  text-align: center;
}

.description {
  color: #6c757d; 
  font-size: 16px;
  margin-bottom: 20px;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
}

.respond-header {
  background: #f5e1c5;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 28px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
}

.no-requests {
  font-size: 18px;
  color: #777;
  margin-top: 20px;
  padding: 40px;
  background: #f5f5f5;
  border-radius: 8px;
}

.request-list {
  list-style: none;
  padding: 0;
  margin-top: 30px;
}

.request-card {
  background: #ffffff;
  border: 2px solid #d3c0a3;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 20px;
  text-align: left;
  transition: box-shadow 0.3s ease;
  color: #5c4033;
}

.request-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.request-title {
  font-size: 22px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 15px;
}

.button-group {
  margin-top: 20px;
}

.action-btn {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  margin-right: 10px;
}

.action-btn:hover {
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
  transform: scale(1.05);
}

.request-card p {
  margin: 10px 0;
  line-height: 1.5;
}
</style>