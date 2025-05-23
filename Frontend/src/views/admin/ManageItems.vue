<template>
  <div class="manage-items">
    <div class="tabs">
      <button :class="{ active: activeTab === 'add' }" @click="activeTab = 'add'">Add/Edit Items</button>
      <button :class="{ active: activeTab === 'view' }" @click="activeTab = 'view'">View Availability</button>
    </div>

    <!-- Add/Edit Items Tab -->
    <div v-if="activeTab === 'add'" class="form-section">
      <h2>{{ isEditing ? 'Edit Item' : 'Add New Item' }}</h2>
      <form @submit.prevent="addOrUpdateItem">
        <div>
          <label for="name">Item Name</label>
          <input type="text" v-model="newItem.name" :disabled="isAdminObserver" required />
        </div>
        <div>
          <label for="category">Category</label>
          <select v-model="newItem.category_id" :disabled="isAdminObserver" required>
            <option disabled value="">Select a Category</option>
            <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
              {{ category.category_name }}
            </option>
          </select>
        </div>
        <div>
          <label for="description">Description</label>
          <textarea v-model="newItem.description" :disabled="isAdminObserver"></textarea>
        </div>
        <div>
          <label for="quantity">Quantity</label>
          <input type="number" v-model="newItem.quantity" min="1" :disabled="isAdminObserver" required />
        </div>

        <AppButton 
          type="submit" 
          variant="primary" 
          :disabled="isAdminObserver"
        >
          {{ isEditing ? 'Update Item' : 'Add Item' }}
        </AppButton>
        <AppButton 
          type="button" 
          variant="secondary" 
          @click="cancelEdit" 
          :disabled="isAdminObserver || !isEditing"
        >
          Cancel
        </AppButton>
      </form>

      <hr />

      <h3>Existing Items</h3>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Description</th>
            <th>Quantity</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ getCategoryName(item.category_id) }}</td>
            <td>{{ item.description }}</td>
            <td>{{ item.quantity }}</td>
            <td>
              <AppButton 
                variant="edit" 
                @click="startEditItem(item)" 
                :disabled="isAdminObserver"
              >
                Edit
              </AppButton>
              <AppButton 
                variant="danger" 
                @click="deleteItem(item.id)" 
                :disabled="isAdminObserver"
              >
                Delete
              </AppButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- View Availability Tab -->
    <div v-else class="availability-section">
      <h2>Item Availability</h2>
      <AppButton variant="secondary" @click="refreshAvailability">Refresh</AppButton>
      <p v-if="loadingAvailability">Loading availability...</p>
      <table v-else>
        <thead>
          <tr>
            <th>Item</th>
            <th>Category</th>
            <th>Base Quantity</th>
            <th>Pledged</th>
            <th>Combined Available</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in availableItems" :key="item.item_id">
            <td>{{ item.item_name }}</td>
            <td>{{ getCategoryName(item.category_id) }}</td>
            <td>{{ item.base_quantity }}</td>
            <td>{{ item.available_pledged }}</td>
            <td>{{ item.available_combined }}</td>
          </tr>
        </tbody>
      </table>
      <p>Total Combined Quantity: {{ totalCombinedQuantity }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const activeTab = ref('add');  // Default to add/edit tab
const authStore = useAuthStore(); 
const isAdminObserver = computed(() => authStore.isAdminObserver);

const newItem = ref({
  name: '',
  category_id: '',
  description: '',
  quantity: 1,
  created_by: 4  // Default created_by - consider getting this from auth store
})

const items = ref([])
const categories = ref([])
const isEditing = ref(false)
const editingItemId = ref(null)
const loading = ref(false)
const error = ref(null)

// For availability tab
const availableItems = ref([])
const totalCombinedQuantity = computed(() => {
  if (!availableItems.value || availableItems.value.length === 0) return 0;
  return availableItems.value.reduce((total, item) => {
    return total + Number(item.available_combined);
  }, 0);
});
const loadingAvailability = ref(false)

// Fetch all items from the API
const fetchItems = async () => {
  loading.value = true
  error.value = null
  
  try {
    const res = await api.get('/api/admin/items')
    items.value = res.data
    console.log('Fetched items:', items.value)
  } catch (err) {
    console.error('Error fetching items:', err)
    error.value = 'Failed to load items. Please try again.'
  } finally {
    loading.value = false
  }
}

// Fetch all categories from the API
const fetchCategories = async () => {
  try {
    const res = await api.get('/getCategories')
    categories.value = res.data
  } catch (err) {
    console.error('Error fetching categories:', err)
    error.value = 'Failed to load categories. Please try again.'
  }
}

// Fetch item availability data
const fetchItemAvailability = async () => {
  loadingAvailability.value = true;
  
  try {
    const res = await api.get('/getItemAvailability')
    availableItems.value = res.data.filter(
      item => item.base_quantity > 0 || item.available_pledged > 0
    );
    console.log('Fetched availability:', availableItems.value)
  } catch (err) {
    console.error('Error fetching item availability:', err)
    alert('Failed to load item availability data. Please try again.')
  } finally {
    loadingAvailability.value = false
  }
}

// Refresh availability data
const refreshAvailability = () => {
  fetchItemAvailability();
}

// Navigate to match page
const goToMatchPage = () => {
  router.push('/respond-to-requests');
}

// Helper to get category name from ID
const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.category_id === categoryId)
  return category ? category.category_name : 'Unknown Category'
}

// Add or update an item
const addOrUpdateItem = async () => {
  try {
    if (isAdminObserver.value) {
        alert('Admin Observers cannot add or update items.');
        return;
      }

    if (isEditing.value) {
      // Update existing item
      const res = await api.put(`/api/admin/items/${editingItemId.value}`, newItem.value)
      console.log('Item updated:', res.data)
      
      // Update local list without refreshing from server
      const index = items.value.findIndex(item => item.id === editingItemId.value)
      if (index !== -1) {
        items.value[index] = { ...items.value[index], ...newItem.value, id: editingItemId.value }
      }
      
      isEditing.value = false
      editingItemId.value = null
    } else {
      // Create new item
      const res = await api.post('/api/admin/items', newItem.value)
      console.log('Item created:', res.data)
      
      // If response includes the new item with ID, add it to our list
      if (res.data.item) {
        items.value.push({
          id: res.data.item.id,
          ...newItem.value
        })
      } else {
        // Otherwise refresh the full list
        await fetchItems()
      }
    }
    
    // Refresh availability data if we're looking at that tab
    if (activeTab.value === 'view') {
      fetchItemAvailability();
    }
    
    // Reset form
    resetForm()
  } catch (err) {
    console.error('Error saving item:', err)
    alert('Failed to save item. Please try again.')
  }
}

// Cancel editing
const cancelEdit = () => {
  isEditing.value = false
  editingItemId.value = null
  resetForm()
}

// Reset form to default values
const resetForm = () => {
  newItem.value = {
    name: '',
    description: '',
    category_id: '',
    quantity: 1,
    created_by: 4
  }
}



// Delete an item
const deleteItem = async (id) => {
  if (isAdminObserver.value) {
    alert('Admin Observers cannot delete items.');
    return;
  }
  
  if (confirm("Are you sure you want to delete this item?")) {
    try {
      await api.delete(`/api/admin/items/${id}`);
      
      // Remove from local list without refreshing
      items.value = items.value.filter(item => item.id !== id);
      
      // Refresh availability data if we're looking at that tab
      if (activeTab.value === 'view') {
        fetchItemAvailability();
      }
    } catch (err) {
      console.error('Failed to delete item:', err);
      alert("Failed to delete item: " + (err.response?.data?.error || err.message));
    }
  }
};

// Start editing an item
const startEditItem = (item) => {
  if (isAdminObserver.value) {
    alert('Admin Observers cannot edit items.');
    return;
  }
  
  isEditing.value = true;
  editingItemId.value = item.id;
  
  // Copy item data to form
  newItem.value = {
    name: item.name,
    description: item.description || '',
    category_id: item.category_id,
    quantity: item.quantity || 1,
    created_by: item.created_by
  };
  

  // Scroll to top of the form
  window.scrollTo({
    top: 0,
    behavior: 'smooth' 
  });
};

// Initialize data on component mount
onMounted(() => {
  fetchItems()
  fetchCategories()
  fetchItemAvailability()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.manage-container {
  display: flex;
  justify-content: center;
  min-height: 100vh;
  padding: 50px 20px;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C;
}

.content-box {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
  width: 90%;
  max-width: 1000px;
  text-align: center;
}

.manage-header {
  background: #f5e1c5;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 28px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
  text-align: center;
}

.description {
  color: #6c757d;
  font-size: 16px;
  margin-bottom: 20px;
}

/* Tabs styling */
.tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #d3c0a3;
}

.tab-button {
  padding: 12px 24px;
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 500;
  color: #8B5E3C;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.tab-button.active {
  color: #5c4033;
  font-weight: 600;
}

.tab-button.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: #8B5E3C;
}

.tab-button:hover {
  background-color: #f5e1c5;
}

.tab-content {
  padding: 20px 0;
}

.totals-summary {
  background-color: #e6f7ef;
  border: 1px solid #8fcea5;
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
  text-align: center;
  color: #666;
}

.totals-summary h4 {
  color: #2e8b57;
  margin-bottom: 5px;
  font-size: 18px;
}

/* Form styling */
form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.form-group {
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #5c4033;
}

.help-text {
  font-size: 13px;
  margin-top: 5px;
  color: #8B5E3C;
  font-style: italic;
}

input,
select,
textarea {
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  width: 100%;
  box-sizing: border-box;
  background-color: white;
}

input:disabled, select:disabled {
  background-color: #f0f0f0;
  cursor: not-allowed;
}

.divider {
  margin: 30px 0;
  border: none;
  height: 1px;
  background-color: #d3c0a3;
}

/* Item list styling */
.item-list {
  list-style: none;
  padding: 0;
  text-align: left;
}

.item-entry {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #d3c0a3;
  background-color: white;
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.item-description {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.button-row {
  display: flex;
  gap: 15px;
  justify-content: flex-start;
  margin-top: 10px;
}

.item-buttons {
  display: flex;
  gap: 15px;
}

.no-items {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  color: #8B5E3C;
  font-style: italic;
  border: 1px dashed #d3c0a3;
  margin-top: 20px;
}

/* Loading indicator */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 30px;
  font-style: italic;
  color: #8B5E3C;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(139, 94, 60, 0.3);
  border-radius: 50%;
  border-top-color: #8B5E3C;
  animation: spin 1s ease-in-out infinite;
  margin-right: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Availability table styling */
.availability-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.availability-table th, 
.availability-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #d3c0a3;
}

.availability-table th {
  background-color: #f5e1c5;
  color: #5c4033;
  font-weight: 600;
}

.availability-table tr:last-child td {
  border-bottom: none;
}

.availability-table tr:hover td {
  background-color: #fdf6ee;
}

.highlight {
  font-weight: 600;
  color: #2e8b57;
}

/* Explanation box */
.explanation-box {
  background-color: #f5e1c5;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  text-align: left;
}

.explanation-box h4 {
  color: #5c4033;
  margin-bottom: 10px;
}

.explanation-box p {
  color: #5c4033;
  margin: 0;
}

/* Action buttons */
.action-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}
</style>