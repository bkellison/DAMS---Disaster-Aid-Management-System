<template>
  <div class="debug-container">
    <h2>Vue Router Debugger</h2>
    <p>Add this component temporarily to debug routing issues in your application.</p>
    
    <div class="debug-section">
      <h3>Current Route Info</h3>
      <div class="info-item">
        <strong>Path:</strong> {{ currentRoute.path }}
      </div>
      <div class="info-item">
        <strong>Name:</strong> {{ currentRoute.name }}
      </div>
      <div class="info-item">
        <strong>Params:</strong> {{ JSON.stringify(currentRoute.params) }}
      </div>
      <div class="info-item">
        <strong>Query:</strong> {{ JSON.stringify(currentRoute.query) }}
      </div>
      <div class="info-item">
        <strong>Hash:</strong> {{ currentRoute.hash }}
      </div>
      <div class="info-item">
        <strong>Full path:</strong> {{ currentRoute.fullPath }}
      </div>
      <div class="info-item">
        <strong>Matched Routes:</strong> {{ matchedRoutes.length }}
      </div>
    </div>
    
    <div class="debug-section">
      <h3>Route Matching</h3>
      <div v-for="(route, index) in matchedRoutes" :key="index" class="matched-route">
        <div><strong>Path:</strong> {{ route.path }}</div>
        <div><strong>Name:</strong> {{ route.name }}</div>
        <div><strong>Component:</strong> {{ getComponentName(route.components?.default) }}</div>
      </div>
      
      <div v-if="matchedRoutes.length === 0" class="no-matches">
        No routes matched! This indicates a routing problem.
      </div>
    </div>
    
    <div class="debug-section">
      <h3>Auth Status</h3>
      <div class="info-item">
        <strong>Authenticated:</strong> {{ authStore.isAuthenticated }}
      </div>
      <div class="info-item">
        <strong>User ID:</strong> {{ authStore.userId }}
      </div>
      <div class="info-item">
        <strong>Username:</strong> {{ authStore.username }}
      </div>
      <div class="info-item">
        <strong>Role:</strong> {{ authStore.role }}
      </div>
      <div class="info-item">
        <strong>isAdmin:</strong> {{ authStore.isAdmin }}
      </div>
      <div class="info-item">
        <strong>isDonor:</strong> {{ authStore.isDonor }}
      </div>
      <div class="info-item">
        <strong>isRecipient:</strong> {{ authStore.isRecipient }}
      </div>
    </div>
    
    <div class="debug-section">
      <h3>Navigate To</h3>
      <div class="nav-buttons">
        <button 
          v-for="route in commonRoutes" 
          :key="route.path"
          @click="navigateTo(route.path)"
          class="nav-button"
        >
          {{ route.name }}
        </button>
      </div>
    </div>
    
    <div class="debug-section">
      <h3>Console Output</h3>
      <div class="console">
        <div v-for="(log, index) in consoleLogs" :key="index" class="log-entry" :class="log.type">
          [{{ log.time }}] {{ log.message }}
        </div>
        <div v-if="consoleLogs.length === 0" class="no-logs">
          No logs captured yet.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Get current route information
const currentRoute = computed(() => route);
const matchedRoutes = computed(() => currentRoute.value.matched);

// Helper to get component name
const getComponentName = (component) => {
  if (!component) return 'Unknown';
  return component.name || component.__file?.split('/').pop() || 'Anonymous Component';
};

// Common routes for quick navigation
const commonRoutes = [
  { name: 'Home', path: '/' },
  { name: 'Admin Dashboard', path: '/admin' },
  { name: 'Donor Dashboard', path: '/donor' },
  { name: 'Recipient Dashboard', path: '/recipient' },
  { name: 'View Events', path: '/admin/view-events' },
  { name: 'Pledges', path: '/pledge-view' },
  { name: 'Requests', path: '/respond-to-requests' },
  { name: 'Matches', path: '/match-view' }
];

// Console log interceptor
const consoleLogs = ref([]);
const originalConsole = {
  log: console.log,
  error: console.error,
  warn: console.warn,
  info: console.info
};

// Navigate to a route
const navigateTo = (path) => {
  try {
    addLog(`Navigating to ${path}`, 'info');
    router.push(path);
  } catch (error) {
    addLog(`Navigation error: ${error.message}`, 'error');
  }
};

// Add log entry
const addLog = (message, type = 'log') => {
  const now = new Date();
  const time = `${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}.${now.getMilliseconds()}`;
  consoleLogs.value.push({ message, type, time });
  
  // Limit log size
  if (consoleLogs.value.length > 50) {
    consoleLogs.value.shift();
  }
};

// Override console methods to capture logs
onMounted(() => {
  console.log = (...args) => {
    const message = args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' ');
    addLog(message, 'log');
    originalConsole.log(...args);
  };
  
  console.error = (...args) => {
    const message = args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' ');
    addLog(message, 'error');
    originalConsole.error(...args);
  };
  
  console.warn = (...args) => {
    const message = args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' ');
    addLog(message, 'warn');
    originalConsole.warn(...args);
  };
  
  console.info = (...args) => {
    const message = args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' ');
    addLog(message, 'info');
    originalConsole.info(...args);
  };
  
  // Add initial log
  addLog('Router Debug Component Mounted', 'info');
  addLog(`Current Route: ${route.fullPath}`, 'info');
});

// Restore original console methods on unmount
onUnmounted(() => {
  console.log = originalConsole.log;
  console.error = originalConsole.error;
  console.warn = originalConsole.warn;
  console.info = originalConsole.info;
});
</script>

<style scoped>
.debug-container {
  font-family: 'Courier New', monospace;
  background-color: #1e1e1e;
  color: #f0f0f0;
  padding: 20px;
  border-radius: 8px;
  margin: 20px;
  max-width: 1000px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

h2 {
  color: #61dafb;
  margin-top: 0;
  font-size: 24px;
}

h3 {
  color: #61dafb;
  margin-top: 20px;
  margin-bottom: 10px;
  font-size: 18px;
  border-bottom: 1px solid #444;
  padding-bottom: 5px;
}

p {
  color: #ccc;
  margin-bottom: 20px;
}

.debug-section {
  margin-bottom: 25px;
  background-color: #252525;
  padding: 15px;
  border-radius: 5px;
}

.info-item {
  margin: 5px 0;
  padding: 5px 0;
  border-bottom: 1px dotted #444;
}

.matched-route {
  background-color: #2a2a2a;
  padding: 10px;
  margin: 10px 0;
  border-radius: 5px;
  border-left: 3px solid #61dafb;
}

.no-matches {
  color: #ff6b6b;
  font-weight: bold;
  padding: 10px;
  background-color: #3a2a2a;
  border-radius: 5px;
}

.nav-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.nav-button {
  background-color: #61dafb;
  color: #1e1e1e;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

.nav-button:hover {
  background-color: #4fa8d3;
}

.console {
  background-color: #000;
  padding: 10px;
  border-radius: 5px;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
}

.log-entry {
  margin: 5px 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-entry.log {
  color: #ffffff;
}

.log-entry.error {
  color: #ff6b6b;
}

.log-entry.warn {
  color: #ffd166;
}

.log-entry.info {
  color: #06d6a0;
}

.no-logs {
  color: #666;
  font-style: italic;
  text-align: center;
  padding: 20px;
}
</style>