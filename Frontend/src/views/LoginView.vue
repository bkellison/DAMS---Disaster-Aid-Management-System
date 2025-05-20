<template>
  <div class="login-container">
    <div class="content-box">
      <h1 class="login-header">Login</h1>
      <p>Welcome back! Please enter your credentials.</p>
      
      <form @submit.prevent="handleLogin">
        <input type="text" placeholder="Username" v-model="username" required />
        
        <input type="password" placeholder="Password" v-model="password" required />
        <p v-if="passwordError" class="error">{{ passwordError }}</p>

        <button type="submit">Login</button>

        <label>
          <input type="checkbox" v-model="rememberMe" />
          Remember Me
        </label>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios  from 'axios';
import { useAuthStore } from "@/stores/auth";
import Cookies from 'js-cookie';

export default {
  setup() {
    // Initialize router and auth store at the component root level
    const router = useRouter();
    const authStore = useAuthStore();
    
    // Form input fields
    const username = ref('');
    const password = ref('');
    const passwordError = ref('');
    const rememberMe = ref(false);

    async function handleLogin() {
      // Validation
      if (password.value.length < 6) {
        passwordError.value = 'Password must be at least 6 characters.';
        return;
      } else {
        passwordError.value = '';
      }

      try {
        // Prepare login object
        const loginObject = {
          "username": username.value,
          "password": password.value
        };
        
        // Send login request
        const response = await axios.post('http://127.0.0.1:5000/login', loginObject);
        
        // Handle successful response
        if (response.status == 200 && response.data) {
          // Set user data in auth store
          authStore.setUserId(response.data);

          // Redirect based on user role
          if (response.data.role === 'Donor') {
            router.push({ path: `/donor`, replace: true });
          } else if (response.data.role === 'Admin') {
            router.push({ path: `/admin`, replace: true });
          } else if (response.data.role === 'Recipient') {
            router.push({ path: `/recipient`, replace: true });
          } else {
            router.push({ path: `/`, replace: true });
          }
        }
      } catch (error) {
        console.error('Login failed:', error);
        passwordError.value = 'Login failed. Please check your credentials.';
      }
    }

    return { 
      username, 
      password, 
      passwordError,
      rememberMe, 
      handleLogin 
    };
  }
};
</script>

<style scoped>
/* Font for text */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

/* Login page container styling */
.login-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C; 
  max-width: 500px;
  margin: auto;
  padding: 50px 20px; 
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
}

/* Login header styling */
.login-header {
  background: #f5e1c5; /* Light tan rectangle */
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 32px; 
  font-weight: 600;
  color: #5c4033; 
  margin-bottom: 20px; 
}

/* Form styling */
form {
  display: flex;
  flex-direction: column;
  gap: 15px; /* Space between input fields */
}

/* Input field styling */
input {
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 18px;
  background-color: white;
}

/* Button styling */
button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 18px;
}

/* Button hover effect */
button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C)
}

.error {
  color: #e74c3c;
  font-size: 14px;
  margin-top: -5px;
}
</style>