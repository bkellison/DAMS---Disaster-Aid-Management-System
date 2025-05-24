<template>
  <div class="manage-container">
    <div class="content-box">
      <h2 class="manage-header">Manage Donation Items</h2>
      <p class="description">
        Add or edit donation items and view available quantities for matching.
      </p>

      <!-- Admin Observer Warning -->
      <div v-if="isAdminObserver" class="observer-warning">
        <strong>Admin Observer Mode:</strong> You can view all donation items and availability data but cannot add, edit, or delete items. This is a read-only view of the item management system.
      </div>

      <div class="tabs">
        <button 
          :class="['tab-button', { active: activeTab === 'add' }]" 
          @click="activeTab = 'add'"
        >
          {{ isAdminObserver ? 'View Items' : 'Add/Edit Items' }}
        </button>
        <button 
          :class="['tab-button', { active: activeTab === 'view' }]" 
          @click="activeTab = 'view'"
        >
          View Available Items
        </button>
      </div>

      <!-- Add/Edit Items Tab -->
      <div v-if="activeTab === 'add'" class="tab-content">
        <div v-if="!isAdminObserver">
          <form @submit.prevent="addOrUpdateItem">
            <div class="form-group">
              <label for="category">Category:</label>
              <select id="category" v-model="newItem.category_id" required>
                <option disabled value="">Select Category</option>
                <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
                  {{ cat.category_name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="name">Item Name:</label>
              <input id="name" v-model="newItem.name" placeholder="Item Name" required />
            </div>
            
            <div class="form-group">
              <label for="description">Description (optional):</label>
              <textarea id="description" v-model="newItem.description" placeholder="Description"></textarea>
            </div>
            
            <div class="form-group">
              <label for="quantity">Default Quantity:</label>
              <input id="quantity" type="number" v-model.number="newItem.quantity" placeholder="Default Quantity" min="1" required />
              <div class="help-text">This is the default quantity for new pledges of this item type.</div>
            </div>
            
            <div class="button-row">
              <AppButton type="submit" :variant="isEditing ? 'save' : 'add'">
                {{ isEditing ? 'Update Item' : 'Add Item' }}
              </AppButton>
              <AppButton v-if="isEditing" type="button" variant="cancel" @click="cancelEdit">Cancel</AppButton>
            </div>
          </form>
          <hr class="divider" />
        </div>

        <!-- Observer mode: Show read-only view -->
        <div v-if="isAdminObserver" class="observer-mode-notice">
          <div class="explanation-box">
            <h4>Item Management Overview</h4>
            <p>As an Admin Observer, you can view all donation items that have been configured in the system. This includes their categories, descriptions, and default quantities.</p>
          </div>
        </div>
        
        <div v-if="loading" class="loading">
          <span class="spinner"></span> Loading items...
        </div>
        <div v-else-if="items.length === 0" class="no-items">No items defined yet.</div>
        <ul v-else class="item-list">
          <li v-for="item in items" :key="item.id" class="item-entry">
            <div class="item-details">
              <strong>{{ item.name }}</strong>
              <span class="category-badge">({{ getCategoryName(item.category_id) }})</span>
              <div v-if="item.description" class="item-description">{{ item.description }}</div>
              <div class="item-meta">
                <span class="quantity-info">Default Quantity: {{ item.quantity }}</span>
                <span class="created-info">Created: {{ formatDate(item.created_at) }}</span>
              </div>
            </div>
            <div class="item-buttons">
              <AppButton 
                :variant="isAdminObserver ? 'view' : 'edit'" 
                @click="startEditItem(item)"
                :disabled="false"
                :title="isAdminObserver ? 'View item details (read-only)' : 'Edit this item'"
              >
                {{ isAdminObserver ? 'View Details' : 'Edit' }}
              </AppButton>
              <AppButton 
                variant="danger" 
                @click="deleteItem(item.id)"
                :disabled="isAdminObserver"
                :class="{ 'disabled-button': isAdminObserver }"
                :title="isAdminObserver ? 'Admin Observers cannot delete items' : 'Delete this item'"
              >
                {{ isAdminObserver ? 'Cannot Delete' : 'Delete' }}
              </AppButton>
            </div>
          </li>
        </ul>

        <div v-if="isAdminObserver" class="observer-notice">
          <p>Admin Observers can view all item configurations but cannot modify or delete them.</p>
          <p>This ensures you can monitor the system without accidentally making changes to item data.</p>
        </div>
      </div>
      
      <!-- View Available Items Tab -->
      <div v-if="activeTab === 'view'" class="tab-content">
        <div class="explanation-box">
          <h4>Understanding Item Availability</h4>
          <p>This view shows all items that are currently available for matching with requests, including both base quantities (added by admin) and donor pledges.</p>
        </div>
        <div v-if="loadingAvailability" class="loading">
          <span class="spinner"></span> Loading availability data...
        </div>

        <div v-else-if="!availableItems || availableItems.length === 0" class="no-items">
          No items are currently available for matching.
        </div>
        
        <table v-else class="availability-table">
          <thead>
            <tr>
              <th>Item</th>
              <th>Category</th>
              <th>Admin Quantity</th>
              <th>Pledged Quantity</th>
              <th>Total Available</th>
              <th>Already Matched</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in availableItems" :key="item.id">
              <td>{{ item.name }}</td>
              <td>{{ item.category_name }}</td>
              <td>{{ item.base_quantity }}</td>
              <td>{{ item.available_pledged }}</td>
              <td class="highlight">{{ item.available_combined }}</td>
              <td>{{ item.total_pledged - item.available_pledged }}</td>
            </tr>
          </tbody>
        </table>

        <div class="totals-summary">
          <h4>Total Available Items: {{ totalCombinedQuantity }}</h4>
          <p>These items are ready to be matched with recipient requests.</p>
        </div>

        <div class="action-buttons">
          <AppButton @click="refreshAvailability">Refresh Data</AppButton>
          <AppButton 
            @click="goToMatchPage" 
            variant="primary"
            :disabled="isAdminObserver"
            :class="{ 'disabled-button': isAdminObserver }"
            :title="isAdminObserver ? 'Admin Observers cannot access matching functions' : 'Match items to requests'"
          >
            {{ isAdminObserver ? 'Matching Not Available' : 'Match Items to Requests' }}
          </AppButton>
        </div>

        <div v-if="isAdminObserver" class="observer-notice">
          <p>Admin Observers can view all availability data and totals.</p>
          <p>However, matching functions are disabled to prevent accidental changes to the matching system.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit/View Item Modal -->
  <div v-if="selectedItem" class="modal-overlay" @click.self="closeModal">
    <div class="modal">
      <h3>{{ isAdminObserver ? 'View Item Details' : 'Edit Item' }}</h3>
      
      <div v-if="isAdminObserver" class="modal-observer-warning">
        <strong>View Only Mode:</strong> You can see all item details but cannot make changes.
      </div>
      
      <form @submit.prevent="updateItem">
        <div class="form-group">
          <label for="modal-category">Category:</label>
          <select 
            id="modal-category" 
            v-model="selectedItem.category_id" 
            required
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          >
            <option disabled value="">Select Category</option>
            <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
              {{ cat.category_name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="modal-name">Item Name:</label>
          <input 
            id="modal-name" 
            v-model="selectedItem.name" 
            placeholder="Item Name" 
            required 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          />
        </div>
        
        <div class="form-group">
          <label for="modal-description">Description:</label>
          <textarea 
            id="modal-description" 
            v-model="selectedItem.description" 
            placeholder="Description"
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label for="modal-quantity">Default Quantity:</label>
          <input 
            id="modal-quantity" 
            type="number" 
            v-model.number="selectedItem.quantity" 
            placeholder="Default Quantity" 
            min="1" 
            required 
            :disabled="isAdminObserver"
            :class="{ 'disabled-field': isAdminObserver }"
          />
          <div class="help-text">
            {{ isAdminObserver ? 'Default quantity is view-only in Admin Observer mode' : 'This is the default quantity for new pledges of this item type.' }}
          </div>
        </div>

        <div class="modal-buttons">
          <AppButton 
            v-if="!isAdminObserver"
            type="submit" 
            variant="save"
          >
            Save Changes
          </AppButton>
          <AppButton 
            type="button" 
            variant="cancel" 
            @click="closeModal"
          >
            {{ isAdminObserver ? 'Close' : 'Cancel' }}
          </AppButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();
const activeTab = ref('add');

// Admin Observer permission checks
const isAdminObserver = computed(() => authStore.isAdminObserver)
const canManageItems = computed(() => authStore.canManageItems)

const newItem = ref({
  name: '',
  category_id: '',
  description: '',
  quantity: 1,
  created_by: 4
})

const items = ref([])
const categories = ref([])
const isEditing = ref(false)
const editingItemId = ref(null)
const loading = ref(false)
const error = ref(null)
const selectedItem = ref(null)

// For availability tab
const availableItems = ref([])
const totalCombinedQuantity = computed(() => {
  if (!availableItems.value || availableItems.value.length === 0) return 0;
  return availableItems.value.reduce((total, item) => {
    return total + Number(item.available_combined);
  }, 0);
});
const loadingAvailability = ref(false)

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
};

// Close modal
const closeModal = () => {
  selectedItem.value = null;
  isEditing.value = false;
  editingItemId.value = null;
}

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
  if (isAdminObserver.value) {
    alert('Admin Observers cannot access matching functions. This is a view-only mode.');
    return;
  }
  router.push('/respond-to-requests');
}

// Helper to get category name from ID
const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.category_id === categoryId)
  return category ? category.category_name : 'Unknown Category'
}

// Add or update an item
const addOrUpdateItem = async () => {
  if (isAdminObserver.value) {
    alert('Admin Observers cannot modify items. This is a view-only mode.');
    return;
  }

  if (!canManageItems.value) {
    alert('You do not have permission to manage items.');
    return;
  }

  try {
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
    if (err.response && err.response.status === 403) {
      alert('You do not have permission to manage items.');
    } else {
      alert('Failed to save item. Please try again.');
    }
  }
}

// Update item from modal
const updateItem = async () => {
  if (isAdminObserver.value) {
    alert('Admin Observers cannot update items. This is a view-only mode.');
    return;
  }

  if (!canManageItems.value) {
    alert('You do not have permission to update items.');
    return;
  }

  try {
    const res = await api.put(`/api/admin/items/${selectedItem.value.id}`, selectedItem.value)
    console.log('Item updated:', res.data)
    
    // Update local list
    const index = items.value.findIndex(item => item.id === selectedItem.value.id)
    if (index !== -1) {
      items.value[index] = { ...items.value[index], ...selectedItem.value }
    }
    
    // Refresh availability data if we're looking at that tab
    if (activeTab.value === 'view') {
      fetchItemAvailability();
    }
    
    closeModal()
    alert('Item updated successfully!')
  } catch (err) {
    console.error('Error updating item:', err)
    if (err.response && err.response.status === 403) {
      alert('You do not have permission to update items.');
    } else {
      alert('Failed to update item. Please try again.');
    }
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
    alert('Admin Observers cannot delete items. This is a view-only mode.');
    return;
  }

  if (!canManageItems.value) {
    alert('You do not have permission to delete items.');
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
      if (err.response && err.response.status === 403) {
        alert('You do not have permission to delete items.');
      } else {
        alert("Failed to delete item: " + (err.response?.data?.error || err.message));
      }
    }
  }
};

// Start editing an item or view details for observer
const startEditItem = (item) => {
  if (isAdminObserver.value) {
    // For observers, show modal in view-only mode
    selectedItem.value = {
      ...item
    };
  } else {
    // For admins, allow editing in form
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
  }
};

// Initialize data on component mount
onMounted(() => {
  console.log('ManageItems component mounted');
  console.log('isAdminObserver:', isAdminObserver.value);
  console.log('canManageItems:', canManageItems.value);
  
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

/* Observer warning styling */
.observer-warning {
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  border: 2px solid #2196f3;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
  color: #1565c0;
  text-align: center;
  font-size: 16px;
  box-shadow: 0 4px 8px rgba(33, 150, 243, 0.1);
}

.observer-mode-notice {
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

input:disabled, select:disabled, textarea:disabled {
  background-color: #f0f0f0;
  cursor: not-allowed;
  color: #666;
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

.item-details {
  flex: 1;
}

.category-badge {
  background-color: #f5e1c5;
  color: #5c4033;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 10px;
}

.item-description {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.item-meta {
  margin-top: 8px;
  font-size: 13px;
  color: #8B5E3C;
}

.item-meta span {
  margin-right: 15px;
}

.quantity-info {
  font-weight: 500;
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

/* Disabled button styling */
.disabled-button {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
  background-color: #cccccc !important;
  color: #666666 !important;
}

.disabled-button:hover {
  transform: none !important;
  box-shadow: none !important;
  background-color: #cccccc !important;
}

.observer-notice {
  background: linear-gradient(135deg, #fff3e0, #fce4ec);
  border: 2px solid #ff9800;
  border-radius: 10px;
  padding: 20px;
  margin-top: 30px;
  text-align: center;
  color: #e65100;
}

.observer-notice p {
  margin: 8px 0;
  font-size: 14px;
  line-height: 1.5;
}

.observer-notice p:first-child {
  font-weight: 600;
  font-size: 15px;
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

/* Modal Styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal {
  background: #f9f3e8;
  padding: 30px;
  border-radius: 15px;
  max-width: 600px;
  width: 90%;
  font-family: 'Poppins', sans-serif;
  color: #5c4033;
  box-shadow: 0 6px 20px rgba(0,0,0,0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  font-size: 24px;
  text-align: center;
  margin-bottom: 20px;
  color: #5c4033;
}

.modal-observer-warning {
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  border: 2px solid #2196f3;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  color: #1565c0;
  text-align: center;
  font-size: 14px;
}

.modal .form-group {
  margin-bottom: 15px;
}

.modal .form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #5c4033;
}

.modal input,
.modal select,
.modal textarea {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #d3c0a3;
  font-size: 16px;
  font-family: 'Poppins', sans-serif;
  transition: all 0.3s ease;
}

.modal textarea {
  height: 80px;
  resize: vertical;
}

/* Disabled field styling */
.disabled-field,
.modal input:disabled,
.modal select:disabled,
.modal textarea:disabled {
  background-color: #f8f9fa !important;
  color: #6c757d !important;
  cursor: not-allowed !important;
  opacity: 0.8 !important;
  border-color: #dee2e6 !important;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 25px;
  gap: 15px;
}

/* Responsive design */
@media (max-width: 768px) {
  .item-entry {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .item-buttons {
    width: 100%;
    justify-content: flex-start;
  }
  
  .modal {
    max-width: 95%;
    padding: 20px;
  }

  .observer-warning,
  .observer-notice {
    font-size: 14px;
    padding: 15px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 15px;
  }

  .item-meta {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .item-meta span {
    margin-right: 0;
  }
}
</style>