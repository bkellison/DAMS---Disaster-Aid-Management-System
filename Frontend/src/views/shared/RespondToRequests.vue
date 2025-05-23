<template>
  <div class="respond-container">
    <div class="content-box">
      <h2 class="respond-header">Respond to Requests</h2>
      <p class="description">Browse the list of disaster relief requests that need your help.</p>

      <div v-if="requests.length === 0" class="no-requests">No requests available at the moment.</div>

      <ul class="request-list">
        <li v-for="request in requests" :key="request.request_id" class="request-card">
          <h3 class="request-title">{{ request.event_name }} - {{ request.category }}</h3>
          <div class="request-location">
            <strong>Location:</strong> {{ request.event_location || 'Location not specified' }}
          </div>
          <p v-if="request.item_name"><strong>Specific Item:</strong> {{ request.item_name }}</p>
          <p><strong>Requested Quantity:</strong> {{ request.quantity }}</p>
          <p v-if="request.details && request.details.trim() !== ''"><strong>Details:</strong> {{ request.details }}</p>
          <p><strong>Remaining Needed:</strong> {{ request.request_quantity_remaining }}</p>

          <div class="button-group">
            <AppButton v-if="authStore.role == 'Donor'" variant="primary" @click="respondToRequest(request.request_id)">Respond</AppButton>
            <AppButton v-if="authStore.role == 'Admin'" variant="primary" @click="goToMatchForm(request.request_id)">Manual Match</AppButton>
            <AppButton v-if="authStore.role == 'Admin'" variant="primary" @click="goToAutoMatch(request.request_id)">Auto Match</AppButton>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, onBeforeRouteUpdate } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();
authStore.loadUserDataFromCookie();
const requests = ref([]);

const loadRequests = async () => {
  try {
    const response = await api.get('/getRequestsForResponse');
    // Only filter out requests where remaining quantity is 0 or less (completely fulfilled)
    // Keep requests that still have remaining quantity > 0 (partially fulfilled or unfulfilled)
    requests.value = response.data.filter(request => 
      request.request_quantity_remaining > 0
    ) || [];
  } catch (error) {
    console.error('Error fetching requests:', error);
  }
};

onMounted(loadRequests);

// Refresh list if navigating back from a response
onBeforeRouteUpdate((to, from, next) => {
  loadRequests();
  next();
});

const respondToRequest = (requestId) => {
  router.push({ path: `/respond/${requestId}` }).then(() => {
    // Optional: set a localStorage flag to reload when coming back
    localStorage.setItem('reloadRequests', 'true');
  });
};

const goToMatchForm = (requestId) => {
  router.push({ path: `/create-match/${requestId}`});
};

const goToAutoMatch = (requestId) => {
  router.push({ path: `/auto-match/${requestId}`});
};

if (localStorage.getItem('reloadRequests')) {
  loadRequests();
  localStorage.removeItem('reloadRequests');
}
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
  color: #6c757d; /* Gray color matching login page */
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

.request-location {
  background-color: #e8f5e8;
  padding: 10px 15px;
  border-radius: 8px;
  margin: 10px 0 15px 0;
  border-left: 4px solid #2e8b57;
  font-size: 16px;
  color: #2e8b57;
}

.button-group {
  margin-top: 20px;
  display: flex;
  gap: 15px; /* Increased gap between buttons */
}

.request-card p {
  margin: 10px 0;
  line-height: 1.5;
}
</style>