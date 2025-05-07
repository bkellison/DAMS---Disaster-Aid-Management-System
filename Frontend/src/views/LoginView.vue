<template>
  <div class="login-container">
    <h1 class="login-header">Login</h1>
    <p>Welcome back! Please enter your credentials.</p>
    
    <form @submit.prevent="handleLogin">
      <!-- <input type="email" placeholder="Email" v-model="email" required />
      <p v-if="emailError" class="error">{{ emailError }}</p> -->
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
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios  from 'axios';
import { useAuthStore } from "@/stores/auth";
import Cookies from 'js-cookie';

export default {
  setup() {
    // Form input fields
    const username = ref('');
    const password = ref('');
    const router = useRouter();

    async function handleLogin() {
      // if (this.validateEmail(this.email) === false) {
      //   this.emailError = 'Invalid email format.';
      // } else {
      //   this.emailError = '';
      // }

      if (this.password.length < 6) {
        this.passwordError = 'Password must be at least 6 characters.';
      } else {
        this.passwordError = '';
      }

      if (this.emailError || this.passwordError) {
        return;
      }

      let loginObject = 
      {
        "username": this.username,
        "password": this.password
      }
      const response = await checkLogin(loginObject)
    
      console.log(response)
      if(response.status == 200 && response.data != null)
      {
        const authStore = useAuthStore();
        authStore.setUserId(response.data);

        console.log('REDIRECT')
        if(response.data.role == 'Donor')
        {
          router.push({ path: `/donor`, replace: true }); // Redirect to donor page
        } else if (response.data.role == 'Admin')
        {
          router.push({ path: `/admin`, replace: true }); // Redirect to admin page
        }
        //add once there is a recipiant page
        // else if (response.data.role == 'Recipient')
        // {
        //   //need recipiant page
        // }
        else
        {
          router.push({ path: `/request-view`, replace: true }); // Redirect to home page
        }
        
      }
    } 

    return { username, password, handleLogin };

  },

  // data() {
  //   return {
  //     email: '',
  //     password: '',
  //     emailError: '',
  //     passwordError: '',
  //     username: ''
  //   };
  // },
  // methods: {
  //   // Will update when backend is ready
  //   async handleLogin() {
  //     const router = useRouter();
  //     // if (this.validateEmail(this.email) === false) {
  //     //   this.emailError = 'Invalid email format.';
  //     // } else {
  //     //   this.emailError = '';
  //     // }

  //     if (this.password.length < 6) {
  //       this.passwordError = 'Password must be at least 6 characters.';
  //     } else {
  //       this.passwordError = '';
  //     }

  //     if (this.emailError || this.passwordError) {
  //       return;
  //     }

  //     console.log('Logging in with', this.username, this.password);
  //     let loginObject = 
  //     {
  //       "username": this.username,
  //       "password": this.password
  //     }
  //     const response = await checkLogin(loginObject)
  //     if(response.status == 200)
  //     {
  //       console.log('success')
  //       router.push({ path: `/home`, replace: true }); // Redirect to home page
  //     }
  //   } 
  // }
};

async function checkLogin(loginObject){
      try {
        const response = await axios.post('http://127.0.0.1:5000/login', loginObject); 
        
        return response;
        //this.data = response.data;
      } catch (error) {
        console.error('Error fetching data:', error);
        return false;
      }
    }
</script>

<style scoped>
/* Font for text */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

/* Login page container styling */
.login-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C; 
  max-width: 400px;
  margin: auto;
  padding: 50px 20px; 
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
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 18px;
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
</style>