<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-header">Register</h1>
      <p class="auth-description">Create your account by filling in the details below.</p>
      
      <form @submit.prevent="handleSubmit">
        <!-- Email field -->
        <AppInput
          v-model="formValues.email"
          label="Email"
          type="email"
          placeholder="Enter your email"
          required
          :error="errors.email"
          @update:modelValue="value => handleChange('email', value)"
        />
        
        <!-- Username field -->
        <AppInput
          v-model="formValues.username"
          label="Username"
          placeholder="Choose a username"
          required
          :error="errors.username"
          @update:modelValue="value => handleChange('username', value)"
        />
        
        <!-- Password field -->
        <AppInput
          v-model="formValues.password"
          type="password"
          label="Password"
          placeholder="Create a password"
          required
          :error="errors.password"
          @update:modelValue="value => handleChange('password', value)"
        />
        
        <!-- Role selection -->
        <AppSelect
          v-model="formValues.role"
          label="Role"
          :options="roleOptions"
          required
          :error="errors.role"
          @update:modelValue="value => handleChange('role', value)"
        />
        
        <!-- Conditional address fields for Recipients -->
        <template v-if="formValues.role === 'Recipient'">
          <AppInput
            v-model="formValues.addressline1"
            label="Address Line 1"
            placeholder="Enter your street address"
            required
            :error="errors.addressline1"
            @update:modelValue="value => handleChange('addressline1', value)"
          />
          
          <AppInput
            v-model="formValues.addressline2"
            label="Address Line 2 (Optional)"
            placeholder="Apartment, suite, etc."
            @update:modelValue="value => handleChange('addressline2', value)"
          />
          
          <AppInput
            v-model="formValues.city"
            label="City"
            placeholder="Enter city"
            required
            :error="errors.city"
            @update:modelValue="value => handleChange('city', value)"
          />
          
          <AppSelect
            v-model="formValues.state"
            label="State"
            :options="stateOptions"
            required
            :error="errors.state"
            @update:modelValue="value => handleChange('state', value)"
          />
        </template>
        
        <!-- Zipcode field for all roles -->
        <AppInput
          v-model="formValues.zipcode"
          label="Zipcode"
          placeholder="Enter zipcode"
          required
          :error="errors.zipcode"
          @update:modelValue="value => handleChange('zipcode', value)"
        />
        
        <!-- Action buttons -->
        <div class="auth-actions">
          <AppButton type="submit" :loading="isLoading">Request Account</AppButton>
        </div>
        
        <!-- Alert for messages -->
        <AppAlert v-if="alert.show" :type="alert.type" :title="alert.title" @dismiss="closeAlert">
          {{ alert.message }}
        </AppAlert>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppInput from '@/components/common/AppInput.vue';
import AppSelect from '@/components/common/AppSelect.vue';
import AppButton from '@/components/common/AppButton.vue';
import AppAlert from '@/components/common/AppAlert.vue';
import useFormValidation from '@/composables/useFormValidation';
import useAlert from '@/composables/useAlert';
import useLoading from '@/composables/useLoading';
import api from '@/services/api'; // ADD THIS IMPORT

// Initialize router
const router = useRouter();
const authStore = useAuthStore();

// Initialize composables
const { alert, showAlert, closeAlert } = useAlert();
const { isLoading, showLoading, hideLoading } = useLoading();

// Role options for select
const roleOptions = [
  { value: 'Recipient', label: 'Recipient' },
  { value: 'Donor', label: 'Donor' },
  // { value: 'Admin', label: 'Admin' }, // Commented out - Admin accounts must be created by existing admins
  { value: 'Admin Observer', label: 'Admin Observer' }
];

// State options for select
const stateOptions = [
  { value: 'AL', label: 'Alabama' },
  { value: 'AK', label: 'Alaska' },
  { value: 'AZ', label: 'Arizona' },
  { value: 'AR', label: 'Arkansas' },
  { value: 'CA', label: 'California' },
  { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' },
  { value: 'DE', label: 'Delaware' },
  { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' },
  { value: 'HI', label: 'Hawaii' },
  { value: 'ID', label: 'Idaho' },
  { value: 'IL', label: 'Illinois' },
  { value: 'IN', label: 'Indiana' },
  { value: 'IA', label: 'Iowa' },
  { value: 'KS', label: 'Kansas' },
  { value: 'KY', label: 'Kentucky' },
  { value: 'LA', label: 'Louisiana' },
  { value: 'ME', label: 'Maine' },
  { value: 'MD', label: 'Maryland' },
  { value: 'MA', label: 'Massachusetts' },
  { value: 'MI', label: 'Michigan' },
  { value: 'MN', label: 'Minnesota' },
  { value: 'MS', label: 'Mississippi' },
  { value: 'MO', label: 'Missouri' },
  { value: 'MT', label: 'Montana' },
  { value: 'NE', label: 'Nebraska' },
  { value: 'NV', label: 'Nevada' },
  { value: 'NH', label: 'New Hampshire' },
  { value: 'NJ', label: 'New Jersey' },
  { value: 'NM', label: 'New Mexico' },
  { value: 'NY', label: 'New York' },
  { value: 'NC', label: 'North Carolina' },
  { value: 'ND', label: 'North Dakota' },
  { value: 'OH', label: 'Ohio' },
  { value: 'OK', label: 'Oklahoma' },
  { value: 'OR', label: 'Oregon' },
  { value: 'PA', label: 'Pennsylvania' },
  { value: 'RI', label: 'Rhode Island' },
  { value: 'SC', label: 'South Carolina' },
  { value: 'SD', label: 'South Dakota' },
  { value: 'TN', label: 'Tennessee' },
  { value: 'TX', label: 'Texas' },
  { value: 'UT', label: 'Utah' },
  { value: 'VT', label: 'Vermont' },
  { value: 'VA', label: 'Virginia' },
  { value: 'WA', label: 'Washington' },
  { value: 'WV', label: 'West Virginia' },
  { value: 'WI', label: 'Wisconsin' },
  { value: 'WY', label: 'Wyoming' }
];

// Form validation rules
const validationRules = {
  username: [
    value => !!value || 'Username is required',
    value => value?.length >= 3 || 'Username must be at least 3 characters'
  ],
  email: [
    value => !!value || 'Email is required',
    value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Email must be valid'
  ],
  password: [
    value => !!value || 'Password is required',
    value => value?.length >= 6 || 'Password must be at least 6 characters'
  ],
  role: [
    value => !!value || 'Role is required'
  ],
  zipcode: [
    value => !!value || 'Zipcode is required',
    value => /^\d{5}(-\d{4})?$/.test(value) || 'Zipcode must be valid (XXXXX or XXXXX-XXXX)'
  ]
};

// Conditional validation based on role
const conditionalValidation = computed(() => {
  const rules = { ...validationRules };
  
  if (formValues.role === 'Recipient') {
    rules.addressline1 = [value => !!value || 'Address Line 1 is required'];
    rules.city = [value => !!value || 'City is required'];
    rules.state = [value => !!value || 'State is required'];
  }
  
  return rules;
});

// Initialize form with validation
const {
  formValues,
  errors,
  handleChange,
  validate
} = useFormValidation({
  username: '',
  email: '',
  password: '',
  role: 'Recipient',
  addressline1: '',
  addressline2: '',
  city: '',
  state: '',
  zipcode: ''
}, validationRules);

// Handle form submission
const handleSubmit = async () => {
  // Apply conditional validation for recipient fields
  if (formValues.role === 'Recipient') {
    const recipientRules = {
      addressline1: [value => !!value || 'Address Line 1 is required'],
      city: [value => !!value || 'City is required'],
      state: [value => !!value || 'State is required']
    };
    
    // Validate recipient fields
    for (const [field, rules] of Object.entries(recipientRules)) {
      for (const rule of rules) {
        const result = rule(formValues[field]);
        if (result !== true) {
          errors[field] = result;
          return;
        }
      }
    }
  }
  
  if (!validate()) return;
  
  try {
    showLoading('Creating account...');
    
    // Create account request data
    const requestData = {
      username: formValues.username,
      password: formValues.password,
      role: formValues.role,
      email: formValues.email,
      zipcode: formValues.zipcode
    };
    
    // Add recipient-specific fields if applicable
    if (formValues.role === 'Recipient') {
      requestData.addressline1 = formValues.addressline1;
      requestData.addressline2 = formValues.addressline2;
      requestData.city = formValues.city;
      requestData.state = formValues.state;
    }
    
    // FIXED: Call API directly instead of using authStore method
    const response = await api.post('/requestNewAccount', requestData);
    
    if (response.status === 201) {
      showAlert({
        type: 'success',
        title: 'Registration Successful',
        message: 'Your account request has been submitted. Please wait for approval before logging in.',
        duration: 5000
      });
      
      // Redirect to login after a short delay
      setTimeout(() => {
        router.push('/');
      }, 3000);
    } else {
      showAlert({
        type: 'error',
        title: 'Registration Failed',
        message: response.data?.error || 'An error occurred during registration. Please try again.',
        duration: 5000
      });
    }
  } catch (error) {
    console.error('Registration failed:', error);
    
    let errorMessage = 'Connection error. Please try again later.';
    if (error.response) {
      errorMessage = error.response.data?.error || 'An error occurred during registration. Please try again.';
    }
    
    // Show error message
    showAlert({
      type: 'error',
      title: 'Registration Failed',
      message: errorMessage,
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
  align-items: flex-start; /* Changed from center to flex-start */
  min-height: calc(100vh - 60px); /* Adjust for header height */
  padding: 20px;
  padding-top: 50px; /* Added padding at the top to raise the form higher */
}

.auth-card {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 40px;
  width: 100%;
  max-width: 750px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
  margin-bottom: 40px;
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
</style>