<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from "@/stores/auth";
import { useRouter } from 'vue-router';

const router = useRouter();

const selectedCategory = ref('');
const selectedItem = ref(null);
const itemQty = ref('');
const daysToShip = ref('');

const categories = ref([])
//needs to be filtered by selected category
const items = ref([])


const filteredItems = computed(() =>    
    Array.isArray(items.value)
        ? items.value.filter(i => i.category_id == selectedCategory.value)
        : []
    //items.filter(i => i.category_id == selectedCategory.value)
)

async function getCategories() {
    try {
        const response = await axios.get('http://127.0.0.1:5000/getCategories')
        categories.value = response.data
    } catch (error) {
        console.log('/getCategories failed', error)
    }
}

async function getItems() {
    try {
        const response = await axios.get('http://127.0.0.1:5000/getItems')
        console.log('items')
        console.log(response)
        items.value = response.data
    } catch (error) {
        console.log('/getItems failed', error)
    }
}

onMounted(() => {
    getCategories()
    getItems()
})

async function createPledge() {
   

    const authStore = useAuthStore();
    authStore.loadUserDataFromCookie();
    console.log(authStore.userId)
    console.log("pledge!");
    if (!selectedCategory.value || !selectedItem.value || !itemQty.value || !daysToShip.value) {
        alert("Please fill out all fields.");
        return;
    }
    console.log(`Pledging: ${selectedCategory.value}, ${selectedItem.value}, ${itemQty.value}`);

    // Prepare the request payload
    const createPledgeObject = {
        selected_category_id: selectedCategory.value,
        selected_item_id: selectedItem.value,
        item_quantity: itemQty.value,
        days_to_ship: daysToShip.value,
        user_id: authStore.userId //logged in users id
    };

    console.log('made it');

    try {
        const response = await axios.post('http://127.0.0.1:5000/createPledge', createPledgeObject);
        router.push({ path: `/pledge-view`, replace: true });
    } catch (error) {
        console.error('Error creating pledge:', error);
        throw error; // Throw error
    }
    //call create pledge endpoint
    //confirmation popup and redirect to pledge page

}

</script>

<template>
    <div class="register-container">
    <h1 class="register-header">Pledge</h1>
    <p>Make a pledge by filling in the details below.</p>
    <form @submit.prevent="createPledge">
        <label>Category:</label>
        <select v-model="selectedCategory" required>
            <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
                {{ category.category_name }}
            </option>
        </select>

      <label>Item:</label>
      <select v-model="selectedItem" required :disabled="selectedCategory == ''">
        <option v-for="item in filteredItems" :key="item.item_id" :value="item.item_id">
            {{ item.name }}
        </option>
      </select>

      <label>Item Qty:</label>
      <input type="number" v-model="itemQty" required :disabled="selectedItem == null"/>

      <label>Days To Ship:</label>
      <input type="number" v-model="daysToShip" required :disabled="selectedItem == null"/>

      <button type="submit">Make Pledge</button>
    </form>
  </div>
</template>

<style scoped>

/* Registration Page Container Styling */
.register-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C; 
  max-width: 400px;
  margin: auto;
  padding: 50px 20px;
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
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 18px;
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

