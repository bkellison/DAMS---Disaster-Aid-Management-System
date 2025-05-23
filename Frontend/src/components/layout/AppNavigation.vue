<template>
  <nav class="app-nav">
    <div class="app-nav__links">
      <!-- Always visible links -->
      <template v-if="!authStore.isAuthenticated">
        <RouterLink to="/" active-class="active-link">Login</RouterLink>
        <RouterLink to="/register" active-class="active-link">Register</RouterLink>
        <RouterLink to="/reset-password" active-class="active-link">Reset Password</RouterLink>
      </template>
      
      <!-- Links for authenticated users -->
      <template v-else>
        <!-- Admin links -->
        <template v-if="authStore.isAdmin || authStore.role === 'Admin Observer'">
          <RouterLink to="/admin" active-class="active-link">Admin Dashboard</RouterLink>
          
          <div class="app-nav__dropdown">
            <a href="#" @click.prevent="toggleEvents" class="app-nav__link">
              Events <span class="dropdown-arrow">{{ showEvents ? '▲' : '▼' }}</span>
            </a>
            <div v-if="showEvents" class="app-nav__dropdown-menu">
              <RouterLink to="/admin/view-events" active-class="active-link">View Events</RouterLink>
              <RouterLink to="/admin/create-event" active-class="active-link">Create Event</RouterLink>
            </div>
          </div>
          
          <div class="app-nav__dropdown">
            <a href="#" @click.prevent="toggleRequests" class="app-nav__link">
              Requests <span class="dropdown-arrow">{{ showRequests ? '▲' : '▼' }}</span>
            </a>
            <div v-if="showRequests" class="app-nav__dropdown-menu">
              <RouterLink to="/respond-to-requests" active-class="active-link">Manage Requests</RouterLink>
              <RouterLink to="/create-request" active-class="active-link">Create Request</RouterLink>
            </div>
          </div>
          
          <div class="app-nav__dropdown">
            <a href="#" @click.prevent="toggleItems" class="app-nav__link">
              Items & Matches <span class="dropdown-arrow">{{ showItems ? '▲' : '▼' }}</span>
            </a>
            <div v-if="showItems" class="app-nav__dropdown-menu">
              <RouterLink to="/admin/manage-items" active-class="active-link">Manage Donation Items</RouterLink>
              <RouterLink to="/match-view" active-class="active-link">View Matches</RouterLink>
            </div>
          </div>
        </template>
        
        <!-- Donor links -->
        <template v-else-if="authStore.isDonor">
          <RouterLink to="/donor" active-class="active-link">Donor Dashboard</RouterLink>
          <RouterLink to="/pledge-view" active-class="active-link">My Pledges</RouterLink>
          <RouterLink to="/create-pledge" active-class="active-link">Create Pledge</RouterLink>
          <RouterLink to="/respond-to-requests" active-class="active-link">Respond to Requests</RouterLink>
          <RouterLink to="/match-view" active-class="active-link">My Matches</RouterLink>
        </template>
        
        <!-- Recipient links -->
        <template v-else-if="authStore.isRecipient">
          <RouterLink to="/recipient" active-class="active-link">Recipient Dashboard</RouterLink>
          <RouterLink to="/request-view" active-class="active-link">My Requests</RouterLink>
          <RouterLink to="/create-request" active-class="active-link">Create Request</RouterLink>
          <RouterLink to="/match-view" active-class="active-link">My Matches</RouterLink>
        </template>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { RouterLink, useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

// Track dropdown states with simple refs for more reliable reactivity
const showEvents = ref(false);
const showRequests = ref(false);
const showItems = ref(false);

// Toggle functions for each dropdown
const toggleEvents = () => {
  showEvents.value = !showEvents.value;
  if (showEvents.value) {
    showRequests.value = false;
    showItems.value = false;
  }
};

const toggleRequests = () => {
  showRequests.value = !showRequests.value;
  if (showRequests.value) {
    showEvents.value = false;
    showItems.value = false;
  }
};

const toggleItems = () => {
  showItems.value = !showItems.value;
  if (showItems.value) {
    showEvents.value = false;
    showRequests.value = false;
  }
};

// Close dropdowns when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.app-nav__dropdown')) {
    showEvents.value = false;
    showRequests.value = false;
    showItems.value = false;
  }
};

// Watch for route changes to close dropdowns when navigating
watch(() => router.currentRoute.value.path, () => {
  showEvents.value = false;
  showRequests.value = false;
  showItems.value = false;
});

// Add and remove event listeners properly
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.app-nav {
  flex: 1;
  padding: 0 20px;
}

.app-nav__links {
  display: flex;
  gap: 20px;
  justify-content: center;
  align-items: center;
}

.app-nav a, .app-nav__link {
  color: #f5e1c5;
  text-decoration: none;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
  font-size: 16px;
  text-align: center;
  display: inline-block;
  cursor: pointer;
}

.app-nav a:hover, .app-nav a.active-link, .app-nav__link:hover {
  background-color: rgba(245, 225, 197, 0.2);
}

.app-nav a.active-link {
  font-weight: 600;
}

.app-nav__dropdown {
  position: relative;
}

.dropdown-arrow {
  font-size: 10px;
  margin-left: 5px;
}

.app-nav__dropdown-menu {
  position: absolute;
  background-color: #8B5E3C;
  min-width: 180px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  padding: 8px 0;
  z-index: 10;
  margin-top: 5px;
  left: 50%;
  transform: translateX(-50%);
}

.app-nav__dropdown-menu a {
  display: block;
  width: 100%;
  text-align: center;
  padding: 10px 15px;
  color: #f5e1c5;
}

.app-nav__dropdown-menu a:hover {
  background-color: rgba(245, 225, 197, 0.2);
}
</style>