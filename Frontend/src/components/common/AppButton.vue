<template>
  <button 
    :class="[
      'app-button', 
      `app-button--${variant}`,
      { 'app-button--loading': loading }
    ]" 
    :disabled="loading || disabled"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="spinner"></span>
    <slot></slot>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger', 'success'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

defineEmits(['click']);
</script>

<style scoped>
.app-button {
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s ease-in-out, background-color 0.3s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
}

.app-button:hover:not(:disabled) {
  transform: scale(1.05);
}

.app-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.app-button--primary {
  background: linear-gradient(135deg, #8B5E3C, #6A3E2B);
  color: white;
}

.app-button--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #6A3E2B, #8B5E3C);
}

.app-button--secondary {
  background-color: #f5e1c5;
  color: #5c4033;
  border: 1px solid #d3c0a3;
}

.app-button--secondary:hover:not(:disabled) {
  background-color: #e0d4c3;
}

.app-button--danger {
  background-color: #e63946;
  color: white;
}

.app-button--danger:hover:not(:disabled) {
  background-color: #c82333;
}

.app-button--success {
  background-color: #2e8b57;
  color: white;
}

.app-button--success:hover:not(:disabled) {
  background-color: #227548;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
