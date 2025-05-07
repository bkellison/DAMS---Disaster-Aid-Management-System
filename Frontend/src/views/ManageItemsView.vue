<template>
  <div class="manage-container">
    <h2 class="manage-header">Manage Donation Items</h2>
    <p>Add new items or remove existing ones from the list.</p>

    <form @submit.prevent="addOrUpdateItem">
      <select v-model="newItem.category_id" required>
        <option disabled value="">Select Category</option>
        <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
          {{ cat.category_name }}
        </option>
      </select>

      <input v-model="newItem.name" placeholder="Item Name" required />
      <textarea v-model="newItem.description" placeholder="Description"></textarea>
      
      <div class="button-row">
        <button type="submit">{{ isEditing ? 'Update Item' : 'Add Item' }}</button>
        <button v-if="isEditing" type="button" class="cancel-btn" @click="cancelEdit">Cancel</button>
      </div>
    </form>

    <hr class="divider" />

    <div v-if="items.length === 0">No items yet.</div>
    <ul class="item-list">
      <li v-for="item in items" :key="item.item_id" class="item-entry">
        <div>
          <strong>{{ item.name }}</strong>
          ({{ categories.find(c => c.category_id === item.category_id)?.category_name || 'Unknown' }})
          - {{ item.quantity }}
        </div>
        <div>
          <button @click="startEditItem(item)" class="edit-btn">Edit</button>
          <button @click="deleteItem(item.id)" class="delete-btn">Delete</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const newItem = ref({
  name: '',
  category_id: null,
  description: '',
  quantity: 1,
  created_by: 4
})

const items = ref([])
const categories = ref([])

const fetchItems = async () => {
  const res = await axios.get('http://127.0.0.1:5000/api/admin/items')
  items.value = res.data
}

const fetchCategories = async () => {
  const res = await axios.get('http://127.0.0.1:5000/getCategories')
  categories.value = res.data
}

const addOrUpdateItem = async () => {
  if (isEditing.value) {
    // Update existing item
    await axios.put(`http://127.0.0.1:5000/api/admin/items/${editingItemId.value}`, newItem.value)
    isEditing.value = false
    editingItemId.value = null
  } else {
    // Create new item
    await axios.post('http://127.0.0.1:5000/api/admin/items', newItem.value)
  }
  await fetchItems()
  Object.assign(newItem.value, { name: '', description: '', category_id: '' })
}

const cancelEdit = () => {
  isEditing.value = false
  editingItemId.value = null
  Object.assign(newItem.value, { name: '', description: '', category_id: '', quantity: 1 })
}

const deleteItem = async (id) => {
  if (confirm('Are you sure?')) {
    await axios.delete(`http://127.0.0.1:5000/api/admin/items/${id}`)
    await fetchItems()
  }
}

const isEditing = ref(false)
const editingItemId = ref(null)

const startEditItem = (item) => {
  isEditing.value = true
  editingItemId.value = item.id
  newItem.value = {
    name: item.name,
    description: item.description,
    category_id: item.category_id,
    quantity: item.quantity,
    created_by: item.created_by
  }
}


onMounted(() => {
  fetchItems()
  fetchCategories()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

.manage-container {
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #8B5E3C;
  max-width: 600px;
  margin: auto;
  padding: 50px 20px;
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
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

input,
select,
textarea {
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 16px;
  width: 100%;
  box-sizing: border-box;
}

button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 18px;
  transition: transform 0.2s ease-in-out, background-color 0.3s;
}

button:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}

.divider {
  margin: 30px 0;
  border: none;
  height: 1px;
  background-color: #ccc;
}

.item-list {
  list-style: none;
  padding: 0;
  text-align: left;
}

.item-entry {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ddd;
}

.delete-btn {
  color: #e63946;
  background: none;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

.delete-btn:hover {
  text-decoration: underline;
}

.edit-btn {
  color: #007bff;
  background: none;
  border: none;
  font-weight: bold;
  cursor: pointer;
  margin-right: 10px;
}

.edit-btn:hover {
  text-decoration: underline;
}

.button-row {
  display: flex;
  gap: 10px;
  justify-content: flex-start;
  margin-top: 10px;
}

.cancel-btn {
  background-color: #ccc;
  color: #333;
  padding: 12px;
  border-radius: 8px;
  font-size: 16px;
  border: none;
  transition: background-color 0.2s ease;
}

.cancel-btn:hover {
  background-color: #bbb;
}

</style>
