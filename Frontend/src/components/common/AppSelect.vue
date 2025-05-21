<template>
  <div class="app-select">
    <label v-if="label" :for="id" class="app-select__label">
      {{ label }}
      <span v-if="required" class="app-select__required">*</span>
    </label>
    <div class="app-select__wrapper">
      <select
        :id="id"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        class="app-select__field"
        @change="$emit('update:modelValue', $event.target.value)"
      >
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <option 
          v-for="option in options" 
          :key="option.value" 
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>
    </div>
    <p v-if="error" class="app-select__error">{{ error }}</p>
    <p v-if="hint" class="app-select__hint">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  options: {
    type: Array,
    default: () => [],
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Select an option'
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  id: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['update:modelValue']);

const uniqueId = computed(() => props.id || `select-${Math.random().toString(36).substring(2, 9)}`);
</script>

<style scoped>
.app-select {
  margin-bottom: 16px;
  width: 100%;
}

.app-select__label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #5c4033;
  text-align: left;
  font-size: 16px;
}

.app-select__required {
  color: #e63946;
  margin-left: 2px;
}

.app-select__wrapper {
  position: relative;
}

.app-select__field {
  width: 100%;
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  background-color: white;
  transition: border-color 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%235c4033' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 40px;
}

.app-select__field:focus {
  outline: none;
  border-color: #8B5E3C;
  box-shadow: 0 0 0 2px rgba(139, 94, 60, 0.2);
}

.app-select__field:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.app-select__error {
  color: #e63946;
  font-size: 14px;
  margin-top: 4px;
  text-align: left;
}

.app-select__hint {
  color: #6c757d;
  font-size: 14px;
  margin-top: 4px;
  text-align: left;
}
</style>