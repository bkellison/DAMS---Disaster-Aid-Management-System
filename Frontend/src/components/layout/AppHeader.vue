<template>
  <header class="app-header">
    <div class="app-header__logo">
      <h1>Disaster Relief Portal</h1>
    </div>
    <!-- Only show navigation when user is authenticated -->
    <AppNavigation v-if="authStore.isAuthenticated" />
    
    <!-- User info and logout button only shown when authenticated -->
    <div class="app-header__user" v-if="authStore.isAuthenticated">
      <span class="user-info">{{ authStore.username || 'User' }}</span>
      <span class="role-badge" :class="`role-badge--${authStore.role?.toLowerCase()}`">
        {{ authStore.role }}
      </span>
      <button class="logout-button" @click="handleLogout">Logout</button>
    </div>
    
    <!-- Authentication links shown only when NOT authenticated -->
    <div class="auth-links" v-else>
      <RouterLink to="/" class="auth-link" active-class="active-link">Login</RouterLink>
      <RouterLink to="/register" class="auth-link" active-class="active-link">Register</RouterLink>
      <RouterLink to="/reset-password" class="auth-link" active-class="active-link">Reset Password</RouterLink>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import AppNavigation from './AppNavigation.vue';

const authStore = useAuthStore();
const router = useRouter();

const handleLogout = () => {
  authStore.logout();
  router.push('/');
};
</script>

<style scoped>
.app-header {
  background-color: #8B5E3C;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  color: #f5e1c5;
}

.app-header__logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.app-header__user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  font-weight: 500;
}

.role-badge {
  background-color: #f5e1c5;
  color: #5c4033;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.role-badge--admin {
  background-color: #f8d7da;
  color: #721c24;
}

.role-badge--admin-observer {
  background-color: #fff3cd;
  color: #856404;
}

.role-badge--donor {
  background-color: #d4edda;
  color: #155724;
}

.role-badge--recipient {
  background-color: #cce5ff;
  color: #004085;
}

.logout-button {
  background-color: transparent;
  border: 1px solid #f5e1c5;
  color: #f5e1c5;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-button:hover {
  background-color: #f5e1c5;
  color: #8B5E3C;
}

/* Auth links styles */
.auth-links {
  display: flex;
  gap: 15px;
}

.auth-link {
  color: #f5e1c5;
  text-decoration: none;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.auth-link:hover, .auth-link.active-link {
  background-color: rgba(245, 225, 197, 0.2);
  text-decoration: none;
}

.auth-link.active-link {
  font-weight: 600;
}
</style>