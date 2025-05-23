<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-header">Login</h1>
      <p class="auth-description">Welcome back! Please enter your credentials.</p>
      
      <form @submit.prevent="handleSubmit">
        <!-- Username field -->
        <AppInput
          v-model="formValues.username"
          label="Username"
          placeholder="Enter your username"
          required
          :error="errors.username"
          @update:modelValue="value => handleChange('username', value)"
        />
        
        <!-- Password field -->
        <AppInput
          v-model="formValues.password"
          type="password"
          label="Password"
          placeholder="Enter your password"
          required
          :error="errors.password"
          @update:modelValue="value => handleChange('password', value)"
        />
        
        <!-- Remember me checkbox -->
        <div class="form-check">
          <input
            id="remember-me"
            type="checkbox"
            v-model="formValues.rememberMe"
            @change="value => handleChange('rememberMe', value.target.checked)"
          />
          <label for="remember-me">Remember me</label>
        </div>
        
        <!-- Action buttons -->
        <div class="auth-actions">
          <AppButton type="submit" :loading="isLoading">Login</AppButton>
        </div>
        
        <!-- Alert for errors -->
        <AppAlert v-if="alert.show" :type="alert.type" :title="alert.title" @dismiss="closeAlert">
          {{ alert.message }}
        </AppAlert>
        
        <!-- Links -->
        <div class="auth-links">
          <p>Don't have an account? <RouterLink to="/register">Register</RouterLink></p>
          <p>Forgot your password? <RouterLink to="/reset-password">Reset Password</RouterLink></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppInput from '@/components/common/AppInput.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppAlert from '@/components/common/AppAlert.vue';
import useFormValidation from '@/composables/useFormValidation';
import useAlert from '@/composables/useAlert';
import useLoading from '@/composables/useLoading';
import api from '@/services/api';

// Initialize router and auth store
const router = useRouter();
const authStore = useAuthStore();

// Initialize composables
const { alert, showAlert, closeAlert } = useAlert();
const { isLoading, showLoading, hideLoading } = useLoading();

// Form validation rules
const validationRules = {
  username: [
    value => !!value || 'Username is required'
  ],
  password: [
    value => !!value || 'Password is required',
    value => value?.length >= 6 || 'Password must be at least 6 characters'
  ]
};

// Try to load saved username from localStorage if remember me was checked previously
const savedUsername = localStorage.getItem('rememberedUsername') || '';

// Initialize form with validation
const {
  formValues,
  errors,
  handleChange,
  validate
} = useFormValidation({
  username: savedUsername,
  password: '',
  rememberMe: !!savedUsername // Check rememberMe if we found a saved username
}, validationRules);

// Handle form submission
const handleSubmit = async () => {
  if (!validate()) return;

  try {
    showLoading('Logging in...');

    // Axios call
    const response = await api.post('/login', {
      username: formValues.username,
      password: formValues.password
    });

    // ✅ Axios automatically parses JSON
    const data = response.data;

    // Handle "Remember me" preference
    if (formValues.rememberMe) {
      localStorage.setItem('rememberedUsername', formValues.username);
    } else {
      localStorage.removeItem('rememberedUsername');
    }

    // Set user data in auth store
    authStore.setUserData(data);

    // Redirect based on user role
    if (authStore.isAdmin) {
      router.push('/admin');
    } else if (authStore.isDonor) {
      router.push('/donor');
    } else if (authStore.isRecipient) {
      router.push('/recipient');
    } else {
      router.push('/');
    }
  } catch (error) {
    console.error('Login failed:', error);

    let errorMessage = 'Connection error. Please try again later.';
    if (error.response) {
      // Server responded with an error
      errorMessage = error.response.data?.error || 'Invalid credentials. Please try again.';
    }

    showAlert({
      type: 'error',
      title: 'Login Failed',
      message: errorMessage,
      duration: 5000
    });
  } finally {
    hideLoading();
  }
};


// Redirect if already logged in
onMounted(() => {
  if (authStore.isAuthenticated) {
    if (authStore.isAdmin) {
      router.push('/admin');
    } else if (authStore.isDonor) {
      router.push('/donor');
    } else if (authStore.isRecipient) {
      router.push('/recipient');
    }
  }
});
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Changed from center to flex-start */
  min-height: calc(100vh - 60px); /* Adjust for header height */
  padding: 20px;
  padding-top: 80px; /* Add top padding to position content higher */
}

.auth-card {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 40px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
  margin-bottom: 40px; /* Added for spacing */
}

.auth-header {
  background: #f5e1c5;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 32px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
}

.auth-description {
  margin-bottom: 30px;
  color: #6c757d;
}

.auth-actions {
  margin-top: 30px;
  margin-bottom: 20px;
}

.form-check {
  display: flex;
  align-items: center;
  margin-top: 15px;
}

.form-check input {
  margin-right: 10px;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.form-check label {
  color: #5c4033;
  cursor: pointer;
}

.auth-links {
  text-align: center;
  margin-top: 30px;
}

.auth-links p {
  margin-bottom: 10px;
  color: #5c4033;
}

.auth-links a {
  color: #8B5E3C;
  font-weight: 600;
}
</style>