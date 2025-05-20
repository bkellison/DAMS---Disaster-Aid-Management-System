<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

// Functions to navigate and set appropriate nav context
const handleEvents = () => {
  router.push({ path: `/admin/view-events`, replace: true });
};

const handleRequests = () => {
  router.push({ path: `/respond-to-requests`, replace: true });
};

const handleManageItems = () => {
  router.push({ path: `/admin/manage-items`, replace: true });
};
</script>

<template>
  <div class="admin-container">
    <div class="content-box">
      <h1 class="admin-header">Admin Dashboard</h1>
      <p>Manage disaster relief operations from a central hub.</p>

      <div class="admin-boxes">
        <div class="admin-box">
          <h3>Event Management</h3>
          <p>Create, view, and manage disaster events. Set up categories and locations for relief efforts.</p>
          <button @click="handleEvents">Manage Events</button>
        </div>

        <div class="admin-box">
          <h3>Request Management</h3>
          <p>View recipient requests and manually match them with donor pledges. Create requests on behalf of recipients.</p>
          <button @click="handleRequests">Manage Requests</button>
        </div>

        <div class="admin-box">
          <h3>Item Management</h3>
          <p>Add, edit, and remove items that can be pledged and requested in the system.</p>
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
  border: 5px solid #c9b28e;
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
  border: 5px solid #c9b28e;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
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