<template>
  <div class="app-wrapper">
    <!-- Always show the header, regardless of route -->
    <AppHeader />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <div :key="$route.fullPath">
            <component :is="Component" />
          </div>
        </transition>
      </router-view>
    </main>
    <AppFooter v-if="showFooter" />
  </div>
</template>

<script>
import { computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppHeader from '@/components/layout/AppHeader.vue';
import AppFooter from '@/components/layout/AppFooter.vue';

export default {
  name: 'App',
  components: {
    AppHeader,
    AppFooter
  },
  setup() {
    const route = useRoute();
    const authStore = useAuthStore();

    // Only hide footer on login/register pages
    const showFooter = computed(() => {
      const authRoutes = ['login', 'register', 'reset-password'];
      // Show footer if user is authenticated OR if not on an auth route
      return authStore.isAuthenticated || !authRoutes.includes(route.name);
    });

    // Load user data from storage on mount
    onMounted(() => {
      authStore.loadUserDataFromCookie();
    });

    return {
      showFooter
    };
  }
}
</script>

<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Global reset */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Global styles */
body {
  font-family: 'Poppins', sans-serif;
  line-height: 1.6;
  background-image: url('@/assets/VueProjectBackground4.png');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  color: #5c4033;
  min-height: 100vh;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 20px 0;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  color: #5c4033;
  margin-bottom: 0.5em;
}

p {
  margin-bottom: 1em;
}

a {
  color: #8B5E3C;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Page transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>