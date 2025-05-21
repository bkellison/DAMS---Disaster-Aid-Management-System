<template>
  <div class="app-input">
    <label v-if="label" :for="id" class="app-input__label">
      {{ label }}
      <span v-if="required" class="app-input__required">*</span>
    </label>
    <div class="app-input__wrapper">
      <input
        :id="id"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        class="app-input__field"
        @input="$emit('update:modelValue', $event.target.value)"
      />
    </div>
    <p v-if="error" class="app-input__error">{{ error }}</p>
    <p v-if="hint" class="app-input__hint">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
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

const uniqueId = computed(() => props.id || `input-${Math.random().toString(36).substring(2, 9)}`);
</script>

<style scoped>
.app-input {
  margin-bottom: 16px;
  width: 100%;
}

.app-input__label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #5c4033;
  text-align: left;
  font-size: 16px;
}

.app-input__required {
  color: #e63946;
  margin-left: 2px;
}

.app-input__wrapper {
  position: relative;
}

.app-input__field {
  width: 100%;
  padding: 12px;
  border: 1px solid #d3c0a3;
  border-radius: 8px;
  font-size: 16px;
  background-color: white;
  transition: border-color 0.2s ease;
}

.app-input__field:focus {
  outline: none;
  border-color: #8B5E3C;
  box-shadow: 0 0 0 2px rgba(139, 94, 60, 0.2);
}

.app-input__field:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.app-input__error {
  color: #e63946;
  font-size: 14px;
  margin-top: 4px;
  text-align: left;
}

.app-input__hint {
  color: #6c757d;
  font-size: 14px;
  margin-top: 4px;
  text-align: left;
}
</style>