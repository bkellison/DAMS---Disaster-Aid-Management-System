<template>
  <div class="app-pagination">
    <button 
      class="app-pagination__button" 
      :disabled="currentPage === 1"
      @click="$emit('update:currentPage', currentPage - 1)"
    >
      Previous
    </button>
    
    <div class="app-pagination__pages">
      <button 
        v-for="page in visiblePages" 
        :key="page"
        class="app-pagination__page-button" 
        :class="{ 'app-pagination__page-button--active': page === currentPage }"
        @click="$emit('update:currentPage', page)"
      >
        {{ page }}
      </button>
    </div>
    
    <button 
      class="app-pagination__button" 
      :disabled="currentPage === totalPages"
      @click="$emit('update:currentPage', currentPage + 1)"
    >
      Next
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalItems: {
    type: Number,
    required: true
  },
  itemsPerPage: {
    type: Number,
    default: 10
  },
  maxVisiblePages: {
    type: Number,
    default: 5
  }
});

const emit = defineEmits(['update:currentPage']);

// Calculate total pages
const totalPages = computed(() => {
  return Math.ceil(props.totalItems / props.itemsPerPage) || 1;
});

// Calculate which page buttons to show
const visiblePages = computed(() => {
  const { currentPage, maxVisiblePages } = props;
  const total = totalPages.value;
  
  // If we have fewer pages than max visible, show all
  if (total <= maxVisiblePages) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  
  // Calculate middle point and offset
  const half = Math.floor(maxVisiblePages / 2);
  let start = currentPage - half;
  let end = currentPage + half;
  
  // Adjust for boundaries
  if (start < 1) {
    end = Math.min(total, end + (1 - start));
    start = 1;
  }
  
  if (end > total) {
    start = Math.max(1, start - (end - total));
    end = total;
  }
  
  return Array.from({ length: end - start + 1 }, (_, i) => start + i);
});
</script>

<style scoped>
.app-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0;
}

.app-pagination__button {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.app-pagination__button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.app-pagination__pages {
  display: flex;
  margin: 0 10px;
}

.app-pagination__page-button {
  width: 36px;
  height: 36px;
  margin: 0 5px;
  border-radius: 4px;
  border: 1px solid #d3c0a3;
  background-color: white;
  color: #5c4033;
  cursor: pointer;
  transition: all 0.2s ease;
}

.app-pagination__page-button--active {
  background-color: #8B5E3C;
  color: white;
  border-color: #8B5E3C;
}

.app-pagination__page-button:hover:not(.app-pagination__page-button--active) {
  background-color: #f5e1c5;
}
</style>