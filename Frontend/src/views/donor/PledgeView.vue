<template>
    <div class="pledge-container">
      <div class="pledge-wrapper">
        <h1 class="pledge-header">Pledges View</h1>
        
        <div v-if="!isAdmin && !isAdminObserver" class="action-button-container">
          <AppButton variant="add" @click="goToPledgeForm">+ Create New Pledge</AppButton>
        </div>

        <!-- Loading indicator -->
        <div v-if="loading" class="loading">
          <span class="spinner"></span> Loading pledges...
        </div>

        <!-- No pledges message -->
        <div v-else-if="pledges.length === 0" class="no-pledges">
          No pledges found.
        </div>

        <!-- Pledges table -->
        <table v-else class="pledge-table">
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Item</th>
                    <th>Total Pledged</th>
                    <th>Allocated</th>
                    <th>Fulfilled</th>
                    <th>Available</th>
                    <th>Status</th>
                    <th v-if="isAdmin || isAdminObserver">Donor ID</th>
                    <th v-if="isAdmin || isAdminObserver">Zipcode</th>
                    <th v-if="isAdmin || isDonor || isAdminObserver">Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(pledge, index) in pledges" :key="index" :class="{ 'editing-row': rowToEditId === pledge.pledge_id }">
                    <td>{{ pledge.category_name }}</td>
                    <td>{{ pledge.item_name }}</td>
                    
                    <!-- Total Pledged Quantity (editable) -->
                    <td v-if="rowToEditId === pledge.pledge_id && canUpdatePledges">
                       <input 
                         type="number" 
                         v-model.number="pledge.item_quantity" 
                         class="qty-input" 
                         :min="pledge.allocated_quantity + pledge.fulfilled_quantity"
                         @keyup.enter="allowEdit(pledge)"
                         @keyup.escape="cancelEdit(pledge)"
                       />
                       <div class="input-help">Min: {{ pledge.allocated_quantity + pledge.fulfilled_quantity }}</div>
                    </td>
                    <td v-else>
                        {{ pledge.item_quantity }}
                    </td>
                    
                    <!-- Allocated Quantity (matched but not shipped) -->
                    <td class="quantity-cell allocated">
                        {{ pledge.allocated_quantity || 0 }}
                        <span v-if="pledge.allocated_quantity > 0" class="status-badge allocated-badge">Matched</span>
                    </td>
                    
                    <!-- Fulfilled Quantity (shipped/delivered) -->
                    <td class="quantity-cell fulfilled">
                        {{ pledge.fulfilled_quantity || 0 }}
                        <span v-if="pledge.fulfilled_quantity > 0" class="status-badge fulfilled-badge">Shipped</span>
                    </td>
                    
                    <!-- Available Quantity (can still be matched) -->
                    <td class="quantity-cell available">
                        {{ pledge.items_left }}
                        <span v-if="pledge.items_left > 0" class="status-badge available-badge">Available</span>
                        <span v-else-if="pledge.items_left === 0 && pledge.item_quantity > 0" class="status-badge depleted-badge">Depleted</span>
                    </td>
                    
                    <!-- Overall Status -->
                    <td class="status-cell">
                        <span :class="getStatusClass(pledge)">{{ getStatusText(pledge) }}</span>
                    </td>
                    
                    <td v-if="isAdmin || isAdminObserver">{{ pledge.donor_id }}</td>
                    <td v-if="isAdmin || isAdminObserver">{{ pledge.zip_code }}</td>
                    <td v-if="isAdmin || isDonor || isAdminObserver" class="action-buttons">
                        <AppButton 
                          v-if="rowToEditId === pledge.pledge_id"
                          variant="save" 
                          @click="allowEdit(pledge)" 
                          :disabled="isAdminObserver || !canUpdatePledges"
                          title="Save changes">
                          Save
                        </AppButton>
                        <AppButton 
                          v-if="rowToEditId === pledge.pledge_id"
                          variant="cancel" 
                          @click="cancelEdit(pledge)" 
                          title="Cancel editing">
                          Cancel
                        </AppButton>
                        <AppButton 
                          v-else
                          variant="edit" 
                          @click="allowEdit(pledge)" 
                          :disabled="isAdminObserver || !canUpdatePledges || pledge.fulfilled_quantity > 0"
                          :class="{ 'disabled-button': isAdminObserver }"
                          title="Update Pledged Quantity">
                          Edit
                        </AppButton>
                        <AppButton 
                          variant="danger" 
                          @click="cancelPledge(pledge.pledge_id)" 
                          :disabled="isAdminObserver || !canUpdatePledges || (pledge.allocated_quantity + pledge.fulfilled_quantity) > 0"
                          :class="{ 'disabled-button': isAdminObserver }"
                          title="Cancel remaining pledged items">
                          {{ (pledge.allocated_quantity + pledge.fulfilled_quantity) > 0 ? 'Cannot Delete' : 'Delete' }}
                        </AppButton>
                    </td>
                </tr>
            </tbody>
        </table>

        <!-- Summary statistics -->
        <div v-if="pledges.length > 0" class="summary-stats">
          <div class="stat-card">
            <h3>Total Pledges</h3>
            <p class="stat-number">{{ pledges.length }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Items Pledged</h3>
            <p class="stat-number">{{ totalItemsPledged }}</p>
          </div>
          <div class="stat-card">
            <h3>Available Items</h3>
            <p class="stat-number available">{{ totalAvailableItems }}</p>
          </div>
          <div class="stat-card">
            <h3>Items in Transit</h3>
            <p class="stat-number allocated">{{ totalAllocatedItems }}</p>
          </div>
          <div class="stat-card">
            <h3>Items Delivered</h3>
            <p class="stat-number fulfilled">{{ totalFulfilledItems }}</p>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import AppButton from '@/components/common/AppButton.vue';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.isAdmin);
const isDonor = computed(() => authStore.isDonor);
const isAdminObserver = computed(() => authStore.isAdminObserver);
const canEdit = computed(() => authStore.canEdit);
const canUpdatePledges = computed(() => authStore.canUpdatePledges);

const pledges = ref([])
const loading = ref(false)
const rowToEditId = ref(null)
const originalPledgeData = ref({}) // Store original data for cancel functionality

// Computed summary statistics
const totalItemsPledged = computed(() => {
    return pledges.value.reduce((sum, pledge) => sum + (pledge.item_quantity || 0), 0)
})

const totalAvailableItems = computed(() => {
    return pledges.value.reduce((sum, pledge) => sum + (pledge.items_left || 0), 0)
})

const totalAllocatedItems = computed(() => {
    return pledges.value.reduce((sum, pledge) => sum + (pledge.allocated_quantity || 0), 0)
})

const totalFulfilledItems = computed(() => {
    return pledges.value.reduce((sum, pledge) => sum + (pledge.fulfilled_quantity || 0), 0)
})

async function getPledges() {
    loading.value = true
    try {
        const response = await api.get(`/getPledges?user_id=${authStore.userId}`)
        pledges.value = response.data || []
        console.log('Fetched pledges:', pledges.value)
    } catch (error) {
        console.error('Error getting pledges:', error)
        alert('Error loading pledges. Please try again.')
    } finally {
        loading.value = false
    }
}

async function cancelPledge(pledge_id) {
    if (isAdminObserver.value) {
        alert('Admin Observers cannot delete pledges.');
        return;
    }
    
    const pledge = pledges.value.find(p => p.pledge_id === pledge_id)
    if (pledge && (pledge.allocated_quantity + pledge.fulfilled_quantity) > 0) {
        alert('Cannot delete pledge with allocated or fulfilled items. Please wait for all matches to be completed or cancelled.')
        return
    }
    
    if (!confirm('Are you sure you want to cancel this pledge? This will remove all remaining available quantity.')) {
        return
    }
    
    try {
        await api.post(`/cancelPledge/${pledge_id}`)
        await getPledges() // Refresh the data to show updated quantities
    } catch (error) {
        console.error('Error cancelling pledge:', error)
        alert('Error cancelling pledge. Please try again.')
    }
}

const allowEdit = (pledge) => {
    if (isAdminObserver.value) {
        alert('Admin Observers cannot update pledges.');
        return;
    }
    
    if (pledge.fulfilled_quantity > 0) {
        alert('Cannot edit pledges that have fulfilled items.');
        return;
    }
    
    if(rowToEditId.value === pledge.pledge_id) {
        // Save the changes
        const minQuantity = pledge.allocated_quantity + pledge.fulfilled_quantity
        if (pledge.item_quantity < minQuantity) {
            alert(`You cannot update pledge quantity to less than ${minQuantity} (allocated + fulfilled items)`)
            return
        }
        updatePledge(pledge, pledge.item_quantity)
    } else {
        // Start editing
        rowToEditId.value = pledge.pledge_id
        // Store original data for cancel functionality
        originalPledgeData.value[pledge.pledge_id] = { ...pledge }
    }
}

const cancelEdit = (pledge) => {
    // Restore original data
    if (originalPledgeData.value[pledge.pledge_id]) {
        Object.assign(pledge, originalPledgeData.value[pledge.pledge_id])
        delete originalPledgeData.value[pledge.pledge_id]
    }
    rowToEditId.value = null
}

async function updatePledge(pledge, qty) {
    if (isAdminObserver.value) {
        alert('Admin Observers cannot update pledges.');
        return;
    }
    
    // Prepare the payload
    const updatePledgeObject = {
        pledge_id: pledge.pledge_id,
        item_quantity: qty,
        user_id: authStore.userId
    };

    try {
        await api.post('/updatePledge', updatePledgeObject);
        rowToEditId.value = null
        delete originalPledgeData.value[pledge.pledge_id]
        await getPledges() // Refresh data to show updated quantities
    } catch (error) {
        console.error('Error updating pledge:', error);
        alert('Error updating pledge. Please try again.')
    }
}

// Helper functions for status display
const getStatusText = (pledge) => {
    if (pledge.fulfilled_flag) {
        return 'Completed'
    } else if (pledge.canceled_flag) {
        return 'Cancelled'
    } else if (pledge.items_left === 0 && pledge.item_quantity > 0) {
        return 'Fully Allocated'
    } else if (pledge.allocated_quantity > 0) {
        return 'Partially Allocated'
    } else {
        return 'Available'
    }
}

const getStatusClass = (pledge) => {
    if (pledge.fulfilled_flag) {
        return 'status-completed'
    } else if (pledge.canceled_flag) {
        return 'status-cancelled'
    } else if (pledge.items_left === 0 && pledge.item_quantity > 0) {
        return 'status-allocated'
    } else if (pledge.allocated_quantity > 0) {
        return 'status-partial'
    } else {
        return 'status-available'
    }
}

onMounted(() => {
    getPledges();
})

const goToPledgeForm = () => {
  router.push({ path: '/create-pledge' })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
  
.pledge-container {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    color: #f5e1c5; 
    max-width: 1200px;
    margin: auto;
    padding: 50px 20px; 
}
  
.pledge-wrapper {
    background-color: #5c4033; 
    padding: 50px; 
    border-radius: 12px;
    margin-top: 40px; 
    border: 10px solid #c9b28e;
}
  
.pledge-header {
    background: #f5e1c5; 
    padding: 15px 65px; 
    border-radius: 20px;
    display: inline-block;
    font-size: 32px; 
    font-weight: 600;
    color: #5c4033; 
    margin-bottom: 25px; 
    border: 5px solid #c9b28e;
}

.action-button-container {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 20px;
}

.loading {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px;
    color: #f5e1c5;
}

.spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(245, 225, 197, 0.3);
    border-radius: 50%;
    border-top-color: #f5e1c5;
    animation: spin 1s ease-in-out infinite;
    margin-right: 10px;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.no-pledges {
    padding: 40px;
    color: #f5e1c5;
    font-style: italic;
    font-size: 18px;
}

.pledge-table {
    width: 100%;
    margin-top: 30px;
    border-collapse: collapse;
    border: 5px solid #c9b28e;
}

.pledge-table th,
.pledge-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #ddd;
    font-size: 14px;
    vertical-align: top;
}

.pledge-table th {
    background-color: #f5e1c5;
    color: #5c4033;
    text-align: left;
    font-weight: 600;
}

.pledge-table td {
    background-color: #fdf6ee;
    color: #5c4033;
    text-align: left;
}

.editing-row td {
    background-color: #fff3e0 !important;
}

.quantity-cell {
    text-align: center;
    font-weight: 500;
}

.status-cell {
    text-align: center;
}

.action-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.qty-input {
    width: 80px;
    padding: 6px;
    border: 1px solid #ccc;
    border-radius: 4px;
    text-align: center;
}

.input-help {
    font-size: 11px;
    color: #666;
    margin-top: 2px;
}

.disabled-button {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    background-color: #ccc !important;
}

.disabled-button:hover {
    transform: none !important;
    box-shadow: none !important;
}

/* Status badges */
.status-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: 500;
    margin-left: 5px;
}

.allocated-badge {
    background-color: #fff3cd;
    color: #856404;
}

.fulfilled-badge {
    background-color: #d4edda;
    color: #155724;
}

.available-badge {
    background-color: #cce7ff;
    color: #004085;
}

.depleted-badge {
    background-color: #f8d7da;
    color: #721c24;
}

/* Status text classes */
.status-completed {
    color: #28a745;
    font-weight: 600;
}

.status-cancelled {
    color: #dc3545;
    font-weight: 600;
}

.status-allocated {
    color: #ffc107;
    font-weight: 600;
}

.status-partial {
    color: #17a2b8;
    font-weight: 600;
}

.status-available {
    color: #007bff;
    font-weight: 600;
}

/* Summary statistics */
.summary-stats {
    display: flex;
    justify-content: space-around;
    margin-top: 30px;
    gap: 20px;
    flex-wrap: wrap;
}

.stat-card {
    background-color: #f5e1c5;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    min-width: 120px;
    border: 2px solid #c9b28e;
}

.stat-card h3 {
    color: #5c4033;
    font-size: 14px;
    margin-bottom: 10px;
    font-weight: 500;
}

.stat-number {
    font-size: 24px;
    font-weight: 600;
    color: #5c4033;
    margin: 0;
}

.stat-number.available {
    color: #007bff;
}

.stat-number.allocated {
    color: #ffc107;
}

.stat-number.fulfilled {
    color: #28a745;
}

/* Responsive design */
@media (max-width: 768px) {
    .pledge-table {
        font-size: 12px;
    }
    
    .pledge-table th,
    .pledge-table td {
        padding: 8px 4px;
    }
    
    .action-buttons {
        flex-direction: column;
        gap: 4px;
    }
    
    .summary-stats {
        flex-direction: column;
        gap: 10px;
    }
}
</style>