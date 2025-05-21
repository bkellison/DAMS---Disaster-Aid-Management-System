<template>
  <div class="app-table-wrapper">
    <table class="app-table">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key" :class="{ 'sortable': column.sortable }">
            <div class="column-header" @click="column.sortable ? sortByColumn(column.key) : null">
              {{ column.label }}
              <span v-if="column.sortable" class="sort-icon">
                <span v-if="sortKey === column.key && sortDirection === 'asc'">▲</span>
                <span v-else-if="sortKey === column.key && sortDirection === 'desc'">▼</span>
                <span v-else>⇅</span>
              </span>
            </div>
          </th>
          <th v-if="$slots.actions">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in sortedItems" :key="getItemKey(item, index)">
          <td v-for="column in columns" :key="column.key">
            <slot :name="`column-${column.key}`" :item="item" :value="getValue(item, column.key)">
              {{ getValue(item, column.key) }}
            </slot>
          </td>
          <td v-if="$slots.actions" class="actions-column">
            <slot name="actions" :item="item" :index="index"></slot>
          </td>
        </tr>
        <tr v-if="items.length === 0">
          <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="empty-message">
            <slot name="empty">No data available</slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    required: true,
    validator: (value) => {
      // Each column must have key and label properties
      return value.every(column => column.key && column.label);
    }
  },
  itemKey: {
    type: String,
    default: ''
  }
});

const sortKey = ref('');
const sortDirection = ref('asc');

// Function to sort the table by a column
const sortByColumn = (key) => {
  if (sortKey.value === key) {
    // Toggle direction if already sorting by this column
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    // Set new sort key and default to ascending
    sortKey.value = key;
    sortDirection.value = 'asc';
  }
};

// Get a value from an object using dot notation (e.g., 'user.name')
const getValue = (item, key) => {
  return key.split('.').reduce((o, i) => (o ? o[i] : undefined), item);
};

// Sort items by the current sort key and direction
const sortedItems = computed(() => {
  if (!sortKey.value) return props.items;
  
  const direction = sortDirection.value === 'asc' ? 1 : -1;
  
  return [...props.items].sort((a, b) => {
    const aValue = getValue(a, sortKey.value);
    const bValue = getValue(b, sortKey.value);
    
    if (aValue === bValue) return 0;
    if (aValue === undefined) return 1;
    if (bValue === undefined) return -1;
    
    return aValue > bValue ? direction : -direction;
  });
});

// Get a unique key for each item in the list
const getItemKey = (item, index) => {
  if (props.itemKey) {
    return getValue(item, props.itemKey);
  }
  return index;
};
</script>

<style scoped>
.app-table-wrapper {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 20px;
}

.app-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.app-table th, .app-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #d3c0a3;
}

.app-table th {
  background-color: #f5e1c5;
  color: #5c4033;
  font-weight: 600;
}

.app-table tbody tr {
  background-color: #f9f3e8;
  transition: background-color 0.2s ease;
}

.app-table tbody tr:hover {
  background-color: #f1e5d3;
}

.app-table th.sortable {
  cursor: pointer;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sort-icon {
  margin-left: 8px;
}

.actions-column {
  text-align: right;
  white-space: nowrap;
}

.empty-message {
  text-align: center;
  padding: 32px;
  color: #6c757d;
}
</style>