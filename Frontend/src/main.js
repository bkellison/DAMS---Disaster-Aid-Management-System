import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';
import { useAuthStore } from "@/stores/auth";
import axios from 'axios'

const app = createApp(App);
app.use(createPinia());
app.use(router);
axios.defaults.baseURL = 'http://localhost:5000'


// const authStore = useAuthStore();
// authStore.checkAuth();  // Check authentication on startup
app.mount('#app');
