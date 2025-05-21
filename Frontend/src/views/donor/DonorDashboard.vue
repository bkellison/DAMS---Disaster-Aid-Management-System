<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppButton from '@/components/common/AppButton.vue';

const router = useRouter();
const authStore = useAuthStore();

const handlePledge = () => {
  router.push('/pledge-view');
};

const handleRespond = () => {
  router.push('/respond-to-requests');
};

const handleMatches = () => {
  router.push('/match-view');
};
</script>

<template>
  <div class="donor-container">
    <div class="content-box">
      <h1 class="donor-header">Donor Dashboard</h1>
      <p>Manage your donations and fulfill requests from recipients.</p>

      <div class="donor-boxes">
        <div class="donor-box">
          <h3>Pledges</h3>
          <p>Create and manage your donation pledges to help those in need</p>
          <AppButton variant="primary" @click="handlePledge">Manage Pledges</AppButton>
        </div>

        <div class="donor-box">
          <h3>Requests</h3>
          <p>View and respond to requests for help from recipients</p>
          <AppButton variant="primary" @click="handleRespond">View Requests</AppButton>
        </div>

        <div class="donor-box">
          <h3>Matches</h3>
          <p>Track matched donations, shipping information and delivery status</p>
          <AppButton variant="primary" @click="handleMatches">View Matches</AppButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.donor-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #5c4033;
  max-width: 1000px;
  margin: auto;
  padding: 50px 20px;
}

.content-box {
  background-color: #5c4033;
  border-radius: 15px;
  padding: 40px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 10px solid #c9b28e;
}

.donor-header {
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

.donor-boxes {
  display: flex;
  justify-content: space-between;
  gap: 25px;
  flex-wrap: nowrap;
  margin-top: 40px;
}

.donor-box {
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

.donor-box h3 {
  font-size: 24px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 10px;
}

.donor-box p {
  font-size: 16px;
  font-weight: 400;
  color: #5c4033;
  margin-bottom: 30px;
  flex-grow: 1;
}
</style>