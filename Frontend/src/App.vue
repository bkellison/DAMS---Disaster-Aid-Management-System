<script setup>
/* Importing RouterView from vue-router to display the matched component based on the current route */
import { RouterView, useRouter, useRoute } from 'vue-router';
import { useAuthStore } from "@/stores/auth";
import { computed, ref, watch } from 'vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

authStore.loadUserDataFromCookie();

// Make auth properties reactive
const isLoggedIn = computed(() => authStore.userId !== null);
const isAdmin = computed(() => authStore.role === 'Admin');
const isDonor = computed(() => authStore.role === 'Donor');
const isRecipient = computed(() => authStore.role === 'Recipient');

// Refs for showing/hiding contextual admin nav links
const showEventLinks = ref(false);
const showRequestLinks = ref(false);
const showItemLinks = ref(false);

// Watch for route changes to update nav link visibility
watch(() => route.path, (newPath) => {
  // For Events section
  if (newPath.includes('/admin/view-events') || newPath.includes('/admin/create-event')) {
    showEventLinks.value = true;
  } else {
    showEventLinks.value = false;
  }
  
  // For Requests section
  if (newPath.includes('/create-request') || newPath.includes('/respond-to-requests')) {
    showRequestLinks.value = true;
  } else {
    showRequestLinks.value = false;
  }
  
  // For Items section
  if (newPath.includes('/admin/manage-items')) {
    showItemLinks.value = true;
  } else {
    showItemLinks.value = false;
  }
}, { immediate: true });

const handleLogout = () => {
  authStore.logout();
  router.push({ path: `/`, replace: true });
}

// Function to toggle nav sections
const toggleEventLinks = () => {
  showEventLinks.value = !showEventLinks.value;
  if (showEventLinks.value) {
    router.push('/admin/view-events');
  }
}

const toggleRequestLinks = () => {
  showRequestLinks.value = !showRequestLinks.value;
  if (showRequestLinks.value) {
    router.push('/respond-to-requests');
  }
}

const toggleItemLinks = () => {
  showItemLinks.value = !showItemLinks.value;
  if (showItemLinks.value) {
    router.push('/admin/manage-items');
  }
}
</script>

<template>
  <header>
    <nav>
      <!-- Basic links for all users -->
      <template v-if="isLoggedIn">
        <router-link to="/" @click.prevent="handleLogout">Logout</router-link> |
        <router-link to="/reset-password" active-class="active-link">Reset Password</router-link> |
      </template>
      <template v-else>
        <router-link to="/" active-class="active-link">Login</router-link> |
        <router-link to="/register" active-class="active-link">Register</router-link> |
        <router-link to="/reset-password" active-class="active-link">Reset Password</router-link>
      </template>
      
      <!-- Admin has simplified main navigation -->
      <template v-if="isLoggedIn && isAdmin">
        <router-link to="/admin" active-class="active-link">Admin Dashboard</router-link>
      </template>
      
      <!-- Contextual admin navigation items -->
      <template v-if="isLoggedIn && isAdmin && showEventLinks">
        | <router-link to="/admin/create-event" active-class="active-link">Create Event</router-link>
        | <router-link to="/admin/view-events" active-class="active-link">View Events</router-link>
      </template>
      
      <template v-if="isLoggedIn && isAdmin && showRequestLinks">
        | <router-link to="/create-request" active-class="active-link">Create Request</router-link>
        | <router-link to="/respond-to-requests" active-class="active-link">Respond to Requests</router-link>
      </template>
      
      <template v-if="isLoggedIn && isAdmin && showItemLinks">
        | <router-link to="/admin/manage-items" active-class="active-link">Manage Items</router-link>
      </template>
      
      <!-- Donor navigation -->
      <template v-if="isLoggedIn && isDonor">
        | <router-link to="/donor" active-class="active-link">Donor Dashboard</router-link>
      </template>
      
      <!-- Recipient navigation -->
      <template v-if="isLoggedIn && isRecipient">
        | <router-link to="/recipient" active-class="active-link">Recipient Dashboard</router-link>
      </template>
    </nav>
  </header>
  
  <router-view></router-view>
</template>

<style>
/* Styling for the navigation bar */
nav {
  background: #8B5E3C;
  padding: 10px;
}

/* Styling for navigation links */
nav a {
  padding: 5px 10px;
  text-decoration: none;
  color: #f5e1c5;
}

/* Styling for the currently active navigation link */
nav a.router-link-exact-active {
  font-weight: bold;
  color: #f5e1c5; 
}

/* Styling for the active link */
nav a.active-link {
  font-weight: bold;
  color: #f5e1c5; 
}

/* Styling for the navigation bar */
button {
  background: #8B5E3C;
  padding: 10px;
}

/* Styling for navigation links */
button a {
  padding: 5px 10px;
  text-decoration: none;
  color: #5c4033;
}

/* Styling for the currently active navigation link */
button a.router-link-exact-active {
  font-weight: bold;
  color: #f5e1c5; 
}

/* Styling for the active link */
button a.active-link {
  font-weight: bold;
  color: #f5e1c5; 
}

/* Global body styling */
body {
  background-image: url('src/assets/VueProjectBackground4.png'); /* Background image for the app */
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  margin: 0;
  font-family: 'Poppins', sans-serif; 
}
</style>