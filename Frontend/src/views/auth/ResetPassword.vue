<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-header">Reset Password</h1>
      <p class="auth-description">Please enter your username and new password below.</p>
      
      <form @submit.prevent="resetPassword">
        <!-- Username field -->
        <AppInput
          v-model="username"
          label="Username"
          placeholder="Enter your username"
          required
          :error="usernameError"
        />
        
        <!-- New Password field -->
        <AppInput
          v-model="newPassword"
          type="password"
          label="New Password"
          placeholder="Create a new password"
          required
          :error="passwordError"
        />
        
        <!-- Confirm Password field -->
        <AppInput
          v-model="confirmPassword"
          type="password"
          label="Confirm Password"
          placeholder="Confirm your new password"
          required
          :error="confirmPasswordError"
        />
        
        <!-- Action button -->
        <div class="auth-actions">
          <AppButton type="submit" :loading="isLoading">Reset Password</AppButton>
        </div>
        
        <!-- Alert for errors or success messages -->
        <AppAlert v-if="alert.show" :type="alert.type" :title="alert.title" @dismiss="closeAlert">
          {{ alert.message }}
        </AppAlert>
        
        <!-- Link to login page -->
        <div class="auth-links">
          <p>Remember your password? <RouterLink to="/">Login</RouterLink></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; // ADD THIS IMPORT
import AppInput from '@/components/common/AppInput.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppAlert from '@/components/common/AppAlert.vue';
import useAlert from '@/composables/useAlert';
import useLoading from '@/composables/useLoading';
import api from '@/services/api'; // ADD THIS IMPORT

const router = useRouter();
const authStore = useAuthStore(); // ADD THIS LINE
const { alert, showAlert, closeAlert } = useAlert();
const { isLoading, showLoading, hideLoading } = useLoading();

// Form fields
const username = ref('');
const newPassword = ref('');
const confirmPassword = ref('');

// Error states
const usernameError = ref('');
const passwordError = ref('');
const confirmPasswordError = ref('');

// Form validation
const validateForm = () => {
  let isValid = true;
  
  // Validate username
  if (!username.value.trim()) {
    usernameError.value = 'Username is required';
    isValid = false;
  } else {
    usernameError.value = '';
  }
  
  // Validate password
  if (!newPassword.value) {
    passwordError.value = 'New password is required';
    isValid = false;
  } else if (newPassword.value.length < 6) {
    passwordError.value = 'Password must be at least 6 characters';
    isValid = false;
  } else {
    passwordError.value = '';
  }
  
  // Validate password confirmation
  if (!confirmPassword.value) {
    confirmPasswordError.value = 'Please confirm your password';
    isValid = false;
  } else if (newPassword.value !== confirmPassword.value) {
    confirmPasswordError.value = 'Passwords do not match';
    isValid = false;
  } else {
    confirmPasswordError.value = '';
  }
  
  return isValid;
};

// Handle password reset submission
const resetPassword = async () => {
  if (!validateForm()) return;
  
  try {
    showLoading('Resetting password...');
    
    // Prepare the password reset data
    const resetData = {
      username: username.value,
      new_password: newPassword.value
    };
  
    // Call the API directly instead of using authStore method
    const response = await api.post('/resetForgottenPassword', resetData);
    
    if (response.status === 200) {
      showAlert({
        type: 'success',
        title: 'Success',
        message: 'Password reset successful! You can now log in with your new password.',
        duration: 3000
      });
      
      // Redirect to login after a short delay
      setTimeout(() => {
        router.push('/');
      }, 3000);
    } else {
      showAlert({
        type: 'error',
        title: 'Reset Failed',
        message: response.data.error || 'Failed to reset password. Please try again.',
        duration: 5000
      });
    }
  } catch (error) {
    console.error('Password reset failed:', error);
    
    showAlert({
      type: 'error',
      title: 'Reset Failed',
      message: error.response?.data?.error || 'An error occurred. Please try again later.',
      duration: 5000
    });
  } finally {
    hideLoading();
  }
};
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
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