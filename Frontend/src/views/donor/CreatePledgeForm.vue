<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const router = useRouter();

const selectedCategory = ref('');
const selectedItem = ref(null);
const itemQty = ref('');
const daysToShip = ref('');

const categories = ref([])
const items = ref([])

const filteredItems = computed(() =>    
    Array.isArray(items.value)
        ? items.value.filter(i => i.category_id == selectedCategory.value)
        : []
)

async function getCategories() {
    try {
        const response = await api.get('/getCategories')
        categories.value = response.data
    } catch (error) {
        console.log('/getCategories failed', error)
    }
}

async function getItems() {
    try {
        const response = await api.get('/getItems')
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
    
    if (!selectedCategory.value || !selectedItem.value || !itemQty.value || !daysToShip.value) {
        alert("Please fill out all fields.");
        return;
    }
    
    // Prepare the request payload
    const createPledgeObject = {
        selected_category_id: selectedCategory.value,
        selected_item_id: selectedItem.value,
        item_quantity: itemQty.value,
        days_to_ship: daysToShip.value,
        user_id: authStore.userId
    };

     try {
        const response = await api.post('/createPledge', createPledgeObject);
        router.push({ path: `/pledge-view`, replace: true });
    } catch (error) {
        console.error('Error creating pledge:', error);
        throw error;
    }
}
</script>

<template>
    <div class="pledge-form-container">
      <div class="content-box">
        <h1 class="pledge-form-header">Create Pledge</h1>
        <p class="description">Make a pledge by filling in the details below.</p>
        
        <form @submit.prevent="createPledge">
          <div class="form-group">
            <label>Category:</label>
            <select v-model="selectedCategory" required>
                <option value="" disabled selected>Select a category</option>
                <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
                    {{ category.category_name }}
                </option>
            </select>
          </div>

          <div class="form-group">
            <label>Item:</label>
            <select v-model="selectedItem" required :disabled="selectedCategory == ''">
              <option value="" disabled selected>Select an item</option>
              <option v-for="item in filteredItems" :key="item.item_id" :value="item.item_id">
                  {{ item.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Item Quantity:</label>
            <input type="number" v-model="itemQty" required :disabled="selectedItem == null" min="1"/>
          </div>

          <div class="form-group">
            <label>Days To Ship:</label>
            <input type="number" v-model="daysToShip" required :disabled="selectedItem == null" min="1"/>
          </div>

          <div class="auth-actions">
            <AppButton type="submit" variant="primary">Make Pledge</AppButton>
          </div>
        </form>
      </div>
    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.pledge-form-container {
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
  width: 500px;
}

.pledge-form-header {
  background: #f5e1c5; 
  padding: 15px 65px; 
  border-radius: 20px;
  display: inline-block;
  font-size: 32px; 
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px; 
}

.description {
  color: #6c757d;
  margin-bottom: 30px;
  text-align: left;
}

form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
}

label {
  font-size: 16px;
  font-weight: 500;
  color: #5c4033;
  text-align: left;
}

input, select {
  width: 100%;
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  background-color: white;
}

input:disabled, select:disabled {
  background-color: #f0f0f0;
  cursor: not-allowed;
}

.auth-actions {
  margin-top: 20px;
  text-align: left;
}
</style>