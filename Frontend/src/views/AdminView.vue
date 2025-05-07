<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const handleManualMatch = () => {
  router.push({ path: `/respond-to-requests`, replace: true });
};
const handleCreateEvent = () => {
  router.push({ path: `/admin/create-event`, replace: true });
};
const handleManageItems = () => {
  router.push({ path: `/admin/manage-items`, replace: true });
};
</script>

<template>
  <div class="admin-container">
    <div class="admin-wrapper">
      <h1 class="admin-header">Admin Dashboard</h1>
      <p>Manage users and system settings from here.</p>

      <div class="admin-boxes">
        <div class="admin-box">
          <h3>Match Requests and Pledges</h3>
          <p>View requests and manually match with pledges.</p>
          <button @click="handleManualMatch">View Requests + Match</button>
        </div>

        <div class="admin-box">
          <h3>Create Event</h3>
          <p>Create new events.</p>
          <button @click="handleCreateEvent">Create Event</button>
        </div>

        <div class="admin-box">
          <h3>Manage Items</h3>
          <p>Add and modify new items</p>
          <button @click="handleManageItems">Manage Items</button>
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
/* Font for text*/
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

/* Admin page container styling */
.admin-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #f5e1c5; 
  max-width: 1000px;
  margin: auto;
  padding: 50px 20px; 
}

/* Wrapper for admin content */
.admin-wrapper {
  background-color: #5c4033; 
  padding: 50px; 
  border-radius: 12px;
  margin-top: 40px; 
}

/* Admin header styling */
.admin-header {
  background: #f5e1c5; 
  padding: 15px 65px; 
  border-radius: 20px;
  display: inline-block;
  font-size: 32px; 
  font-weight: 600;
  color: #5c4033; 
  margin-bottom: 25px; 
}

/* Box container styling */
.admin-boxes {
  display: flex;
  justify-content: space-between; /* Content is spaced out evenly */
  gap: 25px;
  flex-wrap: nowrap; /* Prevent wrapping and ensure all boxes stay in a single row */
  margin-top: 40px; 
}

/* Individual box styling */
.admin-box {
  background: #f5e1c5;
  padding: 20px;
  width: 32%;
  border-radius: 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* Content is spaced out evenly */
  min-height: 250px;
}

/* Ensures all the boxes are the same height */
.admin-box h3 {
  font-size: 24px;
  font-weight: 600;
  color: #5c4033; 
  margin-bottom: 10px;
}

.admin-box p {
  font-size: 16px;
  font-weight: 400;
  color: #5c4033;
  margin-bottom: 30px;
  flex-grow: 1; /* Allows the paragraph to grow and fill space */
}

/* Button styling */
.admin-box button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  color: white;;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 18px;
  margin-top: 20px; 
}

.admin-box button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C)
}
</style>
