<script setup>
/* Importing RouterView from vue-router to display the matched component based on the current route */
import { RouterView, useRouter } from 'vue-router';
import { useAuthStore } from "@/stores/auth";
import { computed } from 'vue';

const router = useRouter();
const authStore = useAuthStore();

authStore.loadUserDataFromCookie();

// Make auth properties reactive
const isLoggedIn = computed(() => authStore.userId !== null);
const isAdmin = computed(() => authStore.role === 'Admin');
const isDonor = computed(() => authStore.role === 'Donor');
const isRecipient = computed(() => authStore.role === 'Recipient');


const handleLogout = () => {
  authStore.logout();
  router.push({ path: `/`, replace: true });
}
</script>

<template>
  <header>
    <nav>
      <template v-if="isLoggedIn">
        <router-link to="/" @click.prevent="handleLogout">Logout</router-link> |
      </template>
      <template v-else>
        <router-link to="/" active-class="active-link">Login</router-link> |
      </template>
      <router-link to="/register" active-class="active-link">Register</router-link> |
      <router-link to="/reset-password" active-class="active-link">Reset Password</router-link>
      
      <template v-if="isLoggedIn">
        <template v-if="isAdmin">
          | <router-link to="/admin" active-class="active-link">Admin</router-link>
          | <router-link to="/admin/create-event" active-class="active-link">Create Event</router-link>
          | <router-link to="/admin/manage-items" active-class="active-link">Manage Items</router-link>
          | <router-link to="/admin/view-events" active-class="active-link">View Events</router-link>
        </template>
        <template v-if="isDonor">
          | <router-link to="/donor" active-class="active-link">Donor</router-link>
        </template>
        <template v-if="isRecipient || isAdmin">
          | <router-link to="/create-request" active-class="active-link">Create Request</router-link>
        </template>
        <template v-if="isRecipient">
          | <router-link to="/match-view" active-class="active-link">Your Matches</router-link>
        </template>
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
  color: #5c4033;
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