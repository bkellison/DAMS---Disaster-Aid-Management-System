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

// Refs for showing/hiding contextual donor nav links
const showPledgeLinks = ref(false);
const showDonorRequestLinks = ref(false);
const showDonorMatchLinks = ref(false);

// Refs for showing/hiding contextual recipient nav links
const showCreateRequestLinks = ref(false);
const showRecipientRequestLinks = ref(false);
const showRecipientMatchLinks = ref(false);

// Watch for route changes to update nav link visibility
watch(() => route.path, (newPath) => {
  // For Admin - Events section
  if (newPath.includes('/admin/view-events') || newPath.includes('/admin/create-event')) {
    showEventLinks.value = true;
  } else {
    showEventLinks.value = false;
  }
  
  // For Admin - Requests section
  if (newPath.includes('/create-request') || newPath.includes('/respond-to-requests')) {
    showRequestLinks.value = true;
  } else {
    showRequestLinks.value = false;
  }
  
  // For Admin - Items section
  if (newPath.includes('/admin/manage-items')) {
    showItemLinks.value = true;
  } else {
    showItemLinks.value = false;
  }
  
  // For Donor - Pledges section
  if (newPath.includes('/pledge-view') || newPath.includes('/create-pledge')) {
    showPledgeLinks.value = true;
  } else {
    showPledgeLinks.value = false;
  }
  
  // For Donor - Requests section
  if (isDonor.value && (newPath.includes('/respond-to-requests') || newPath.includes('/respond/'))) {
    showDonorRequestLinks.value = true;
  } else {
    showDonorRequestLinks.value = false;
  }
  
  // For Donor - Matches section
  if (isDonor.value && newPath.includes('/match-view')) {
    showDonorMatchLinks.value = true;
  } else {
    showDonorMatchLinks.value = false;
  }
  
  // For Recipient - Create Request section
  if (isRecipient.value && newPath.includes('/create-request')) {
    showCreateRequestLinks.value = true;
  } else {
    showCreateRequestLinks.value = false;
  }
  
  // For Recipient - View Requests section
  if (isRecipient.value && newPath.includes('/request-view')) {
    showRecipientRequestLinks.value = true;
  } else {
    showRecipientRequestLinks.value = false;
  }
  
  // For Recipient - Matches section
  if (isRecipient.value && newPath.includes('/match-view')) {
    showRecipientMatchLinks.value = true;
  } else {
    showRecipientMatchLinks.value = false;
  }
}, { immediate: true });

const handleLogout = () => {
  authStore.logout();
  router.push({ path: `/`, replace: true });
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
      
      <!-- Main Dashboard Links by Role -->
      <template v-if="isLoggedIn && isAdmin">
        <router-link to="/admin" active-class="active-link">Admin Dashboard</router-link>
      </template>
      
      <template v-if="isLoggedIn && isDonor">
        <router-link to="/donor" active-class="active-link">Donor Dashboard</router-link>
      </template>
      
      <template v-if="isLoggedIn && isRecipient">
        <router-link to="/recipient" active-class="active-link">Recipient Dashboard</router-link>
      </template>
      
      <!-- Admin Contextual Navigation -->
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
      
      <!-- Donor Contextual Navigation -->
      <template v-if="isLoggedIn && isDonor && showPledgeLinks">
        | <router-link to="/create-pledge" active-class="active-link">Create Pledge</router-link>
        | <router-link to="/pledge-view" active-class="active-link">View Pledges</router-link>
      </template>
      
      <template v-if="isLoggedIn && isDonor && showDonorRequestLinks">
        | <router-link to="/respond-to-requests" active-class="active-link">View All Requests</router-link>
      </template>
      
      <template v-if="isLoggedIn && isDonor && showDonorMatchLinks">
        | <router-link to="/match-view" active-class="active-link">View Matches</router-link>
      </template>
      
      <!-- Recipient Contextual Navigation -->
      <template v-if="isLoggedIn && isRecipient && showCreateRequestLinks">
        | <router-link to="/create-request" active-class="active-link">Create Request</router-link>
      </template>
      
      <template v-if="isLoggedIn && isRecipient && showRecipientRequestLinks">
        | <router-link to="/request-view" active-class="active-link">View Requests</router-link>
      </template>
      
      <template v-if="isLoggedIn && isRecipient && showRecipientMatchLinks">
        | <router-link to="/match-view" active-class="active-link">View Matches</router-link>
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