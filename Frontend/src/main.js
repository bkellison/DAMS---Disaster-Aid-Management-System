// src/main.js
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import axios from 'axios';

// Create the app instance
const app = createApp(App);

// Set up axios defaults
axios.defaults.baseURL = 'http://localhost:5000';
axios.defaults.withCredentials = true; // Enable cookies for cross-origin requests

// Use Pinia for state management
const pinia = createPinia();
app.use(pinia);

// Use the router
app.use(router);

// Mount the app
app.mount('#app');