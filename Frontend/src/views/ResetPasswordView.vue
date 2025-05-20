<template>
  <div class="reset-password-container">
    <div class="content-box">
      <h1 class="reset-password-header">Reset Password</h1>
      <p>Please enter your email and new password below.</p>
      <form @submit.prevent="resetPassword">
        <label>Username:</label>
        <input type="text" v-model="username" required />

        <label>New Password:</label>
        <input type="password" v-model="newPassword" required />

        <label>Confirm Password:</label>
        <input type="password" v-model="confirmPassword" required />
        <button type="submit">Reset Password</button>
      </form>
      <p>Remember your password? <router-link to="/">Login</router-link></p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios  from 'axios';

export default {
  setup() {
    /* Reactive variables for form fields */
    const email = ref('');
    const newPassword = ref('');
    const confirmPassword = ref('');
    const username = ref('');
    const router = useRouter(); /* Vue Router instance for navigation */

    /* Function to handle password reset logic */
    async function resetPassword() {
      /* Ensure all fields are filled out */
      if (!newPassword.value || !confirmPassword.value || !username.value) {
        alert('Please fill out all fields.');
        return;
      }
      
      /* Check if the new password and confirmation match */
      if (newPassword.value !== confirmPassword.value) {
        alert('Passwords do not match.');
        return;
      }

      /* Simulated password reset process (will be changed with backend API call) */
      let updatedPasswrodObj = {
        "username": username.value,
        "new_password": newPassword.value
      }
      
      try {
        const response = await resetForgottenPassword(updatedPasswrodObj)
        
        if (response.status == 200) {
          router.push({ path: `/`, replace: true }); // Redirect to login
        } else {
          alert(`Error: ${response.data.message}`);
        }
      } catch (error) {
        alert(`Error: ${error.message || 'An error occurred'}`);
      }    
    }
    async function resetForgottenPassword(updatedPasswrodObj){
      try {
        
        const response = await axios.post('http://127.0.0.1:5000/resetForgottenPassword', updatedPasswrodObj); 
        return response;

      } catch (error) {
        console.error('Error fetching data:', error);
        return false;
      }
    }

    /* Return variables and functions to the template */
    return { email, newPassword, confirmPassword, username, resetPassword };
  }
};
</script>

<style scoped>
/* Font for text */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

/* Container for the reset password form */
.reset-password-container {
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

/* Header styling */
.reset-password-header {
  background: #f5e1c5; 
  padding: 15px 30px; 
  border-radius: 20px;
  display: inline-block;
  font-size: 32px; 
  font-weight: 600;
  color: #5c4033; 
  margin-bottom: 20px;
  white-space: nowrap;
}

/* Form styling */
form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Label Styling */
label {
  font-size: 16px;
  font-weight: 500;
  color: #5c4033;
  text-align: left;
}

/* Input fields */
input {
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 18px;
  background-color: white;
}

/* Submit button */
button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 18px;
}
/* Button Hover Effect */
button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}

/* Text styling */
p {
  margin-top: 20px;
}

/* Styling for login link */
a {
  color: #8B5E3C;
  text-decoration: none;
  font-weight: 600;
}

a:hover {
  text-decoration: underline;
}
</style>