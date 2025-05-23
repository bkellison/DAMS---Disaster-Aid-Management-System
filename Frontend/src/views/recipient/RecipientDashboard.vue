<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth';
import { RouterView, useRoute, useRouter } from 'vue-router';
import AppButton from '@/components/common/AppButton.vue';

const router = useRouter();
const authStore = useAuthStore();

const handleCreateRequest = () => {
  router.push({ path: `/create-request`, replace: true });
}

const handleViewRequests = () => {
  router.push({ path: `/request-view`, replace: true });
}

const handleViewMatches = () => {
  router.push({ path: `/match-view`, replace: true });
}
</script>

<template>
  <div class="recipient-container">
    <div class="content-box">
      <h1 class="recipient-header">Recipient Dashboard</h1>
      <p>Manage your requests and track donations from donors.</p>
      
      <div class="recipient-boxes">
        <div class="recipient-box">
          <h3>Create Request</h3>
          <p>Create a new request for disaster relief supplies you need</p>
          <AppButton variant="primary" @click="handleCreateRequest">Create Request</AppButton>
        </div>

        <div class="recipient-box">
          <h3>View Requests</h3>
          <p>Track your existing requests and their fulfillment status</p>
          <AppButton variant="primary" @click="handleViewRequests">View Requests</AppButton>
        </div>

        <div class="recipient-box">
          <h3>View Matches</h3>
          <p>See donor matches, shipping information and track deliveries</p>
          <AppButton variant="primary" @click="handleViewMatches">View Matches</AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Font for text*/
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

/* Recipient page container styling */
.recipient-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #5c4033;
  max-width: 1000px;
  margin: auto;
  padding: 50px 20px;
}

/* Content box styling */
.content-box {
  background-color: #5c4033;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 10px solid #c9b28e;
}

/* Recipient header styling */
.recipient-header {
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

/* Box container styling */
.recipient-boxes {
  display: flex;
  justify-content: space-between;
  gap: 25px;
  flex-wrap: nowrap;
  margin-top: 40px;
}

/* Individual box styling */
.recipient-box {
  background: #f5e1c5;
  padding: 20px;
  width: 32%;
  border-radius: 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 250px;
  border: 5px solid #c9b28e;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

/* Ensures all the boxes are the same height */
.recipient-box h3 {
  font-size: 24px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 10px;
}

.recipient-box p {
  font-size: 16px;
  font-weight: 400;
  color: #5c4033;
  margin-bottom: 30px;
  flex-grow: 1;
}
</style>