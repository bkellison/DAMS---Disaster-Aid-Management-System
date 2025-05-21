<template>
  <div class="app-card" :class="[`app-card--${variant}`]">
    <div v-if="title" class="app-card__header">
      <h3 class="app-card__title">{{ title }}</h3>
    </div>
    <div class="app-card__body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="app-card__footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'secondary'].includes(value)
  }
});
</script>

<style scoped>
.app-card {
  background-color: #f9f3e8;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
  margin-bottom: 20px;
}

.app-card--primary {
  border: 2px solid #8B5E3C;
}

.app-card--secondary {
  background-color: white;
}

.app-card__header {
  padding: 15px 20px;
  border-bottom: 1px solid #e0d4c3;
  background-color: #f5e1c5;
}

.app-card__title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #5c4033;
}

.app-card__body {
  padding: 20px;
}

.app-card__footer {
  padding: 15px 20px;
  border-top: 1px solid #e0d4c3;
  background-color: #f5e1c5;
}
</style>