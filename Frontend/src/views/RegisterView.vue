<template>
  <div class="register-container">
    <div class="content-box">
      <h1 class="register-header">Register</h1>
      <p>Create your account by filling in the details below.</p>
      <form @submit.prevent="register">
        <label>Email:</label>
        <input type="email" v-model="email" required />

        <label>Username:</label>
        <input type="text" v-model="username" required />

        <label>Password:</label>
        <input type="password" v-model="password" required />

        <label>Role:</label>
        <select v-model="role" required>
          <option value="Recipient">Recipient</option>
          <option value="Donor">Donor</option>
          <option value="Admin">Admin</option>
        </select>
        
        <label v-if="role == 'Recipient'">Address Line 1:</label>
        <input  v-if="role == 'Recipient'" type="text" v-model="addressline1"></input>
        <label v-if="role == 'Recipient'">Address Line 2:</label>
        <input  v-if="role == 'Recipient'" type="text" v-model="addressline2"></input>
        <label v-if="role == 'Recipient'">City:</label>
        <input  v-if="role == 'Recipient'" type="text" v-model="city"></input>
        <label v-if="role == 'Recipient'">State:</label>
        <select v-if="role == 'Recipient'" v-model="state">
          <option v-for="s in state_list" :key="s.abbreviation" :value="s.abbreviation">{{ s.abbreviation }}</option>
        </select>
        <label>Zipcode:</label>
        <input type="text" v-model="zipcode" required></input>
        <button type="submit">Request Account</button>
      </form>

      <p>Already have an account? <router-link to="/">Login</router-link></p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios  from 'axios';

export default {

  setup() {
    // Form input fields
    const username = ref('');
    const email = ref('');
    const role = ref('');
    const password = ref('');
    const zipcode = ref('');
    const addressline1 = ref('');
    const addressline2 = ref('');
    const city = ref('');
    const state = ref('');
    const router = useRouter();

    const state_list = [
      {
          "name": "Alabama",
          "abbreviation": "AL"
      },
      {
          "name": "Alaska",
          "abbreviation": "AK"
      },
      {
          "name": "American Samoa",
          "abbreviation": "AS"
      },
      {
          "name": "Arizona",
          "abbreviation": "AZ"
      },
      {
          "name": "Arkansas",
          "abbreviation": "AR"
      },
      {
          "name": "California",
          "abbreviation": "CA"
      },
      {
          "name": "Colorado",
          "abbreviation": "CO"
      },
      {
          "name": "Connecticut",
          "abbreviation": "CT"
      },
      {
          "name": "Delaware",
          "abbreviation": "DE"
      },
      {
          "name": "District Of Columbia",
          "abbreviation": "DC"
      },
      {
          "name": "Federated States Of Micronesia",
          "abbreviation": "FM"
      },
      {
          "name": "Florida",
          "abbreviation": "FL"
      },
      {
          "name": "Georgia",
          "abbreviation": "GA"
      },
      {
          "name": "Guam",
          "abbreviation": "GU"
      },
      {
          "name": "Hawaii",
          "abbreviation": "HI"
      },
      {
          "name": "Idaho",
          "abbreviation": "ID"
      },
      {
          "name": "Illinois",
          "abbreviation": "IL"
      },
      {
          "name": "Indiana",
          "abbreviation": "IN"
      },
      {
          "name": "Iowa",
          "abbreviation": "IA"
      },
      {
          "name": "Kansas",
          "abbreviation": "KS"
      },
      {
          "name": "Kentucky",
          "abbreviation": "KY"
      },
      {
          "name": "Louisiana",
          "abbreviation": "LA"
      },
      {
          "name": "Maine",
          "abbreviation": "ME"
      },
      {
          "name": "Marshall Islands",
          "abbreviation": "MH"
      },
      {
          "name": "Maryland",
          "abbreviation": "MD"
      },
      {
          "name": "Massachusetts",
          "abbreviation": "MA"
      },
      {
          "name": "Michigan",
          "abbreviation": "MI"
      },
      {
          "name": "Minnesota",
          "abbreviation": "MN"
      },
      {
          "name": "Mississippi",
          "abbreviation": "MS"
      },
      {
          "name": "Missouri",
          "abbreviation": "MO"
      },
      {
          "name": "Montana",
          "abbreviation": "MT"
      },
      {
          "name": "Nebraska",
          "abbreviation": "NE"
      },
      {
          "name": "Nevada",
          "abbreviation": "NV"
      },
      {
          "name": "New Hampshire",
          "abbreviation": "NH"
      },
      {
          "name": "New Jersey",
          "abbreviation": "NJ"
      },
      {
          "name": "New Mexico",
          "abbreviation": "NM"
      },
      {
          "name": "New York",
          "abbreviation": "NY"
      },
      {
          "name": "North Carolina",
          "abbreviation": "NC"
      },
      {
          "name": "North Dakota",
          "abbreviation": "ND"
      },
      {
          "name": "Northern Mariana Islands",
          "abbreviation": "MP"
      },
      {
          "name": "Ohio",
          "abbreviation": "OH"
      },
      {
          "name": "Oklahoma",
          "abbreviation": "OK"
      },
      {
          "name": "Oregon",
          "abbreviation": "OR"
      },
      {
          "name": "Palau",
          "abbreviation": "PW"
      },
      {
          "name": "Pennsylvania",
          "abbreviation": "PA"
      },
      {
          "name": "Puerto Rico",
          "abbreviation": "PR"
      },
      {
          "name": "Rhode Island",
          "abbreviation": "RI"
      },
      {
          "name": "South Carolina",
          "abbreviation": "SC"
      },
      {
          "name": "South Dakota",
          "abbreviation": "SD"
      },
      {
          "name": "Tennessee",
          "abbreviation": "TN"
      },
      {
          "name": "Texas",
          "abbreviation": "TX"
      },
      {
          "name": "Utah",
          "abbreviation": "UT"
      },
      {
          "name": "Vermont",
          "abbreviation": "VT"
      },
      {
          "name": "Virgin Islands",
          "abbreviation": "VI"
      },
      {
          "name": "Virginia",
          "abbreviation": "VA"
      },
      {
          "name": "Washington",
          "abbreviation": "WA"
      },
      {
          "name": "West Virginia",
          "abbreviation": "WV"
      },
      {
          "name": "Wisconsin",
          "abbreviation": "WI"
      },
      {
          "name": "Wyoming",
          "abbreviation": "WY"
      }
    ]
    
    // Handle user registration
    async function register() {
      console.log("register!");
      if (!username.value || !email.value || !password.value || !zipcode.value || !role.value) {
        alert("Please fill out all fields.");
        return;
      }
      if(role.value == 'Recipient' && (!addressline1.value || !state.value || !city.value)){

      }
      console.log(`Registering: ${username.value}, ${email.value}, ${role.value}`);

      // Prepare the request payload
      const requestedAccountObject = {
        username: username.value,
        password: password.value,
        role: role.value,
        email: email.value,
        zipcode: zipcode.value,
        addressline1: addressline1.value,
        addressline2: addressline2.value,
        state: state.value,
        city: city.value
      };

      try {
        const response = await callRegisterAccount(requestedAccountObject);
        if (response.status == 201) {
          router.push({ path: `/`, replace: true }); // Redirect to login
        } else {
          alert(`Error: ${response.data.message}`);
        }
      } catch (error) {
        alert(`Error: ${error.message || 'An error occurred'}`);
      }
    }

    // Make API request to register account
    async function callRegisterAccount(requestedAccountObject) {
      console.log('made it');
      try {
        const response = await axios.post('http://127.0.0.1:5000/requestNewAccount', requestedAccountObject);
        return response;
      } catch (error) {
        console.error('Error fetching data:', error);
        throw error; // Throw error
      }
    }

    return { username, email, role, password, zipcode, register, state, city, addressline1, addressline2, state_list };
  }
};

</script>

<style scoped>
/* Font for text */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

/* Registration Page Container Styling */
.register-container {
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

/* Registration Header Styling */
.register-header {
  background: #f5e1c5; 
  padding: 15px 65px; 
  border-radius: 20px;
  display: inline-block;
  font-size: 32px; 
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px; 
}

/* Form Styling */
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

/* Input and Select Styling */
input, select {
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 18px;
  background-color: white;
}

/* Button Styling */
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

/* Text and Link Styling */
p {
  margin-top: 20px;
}

a {
  color: #8B5E3C;
  text-decoration: none;
  font-weight: 600;
}

a:hover {
  text-decoration: underline;
}
</style>