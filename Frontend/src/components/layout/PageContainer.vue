<template>
  <div class="page-container">
    <h1 v-if="title" class="page-title">{{ title }}</h1>
    <p v-if="description" class="page-description">{{ description }}</p>
    <div class="page-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  background: #f5e1c5;
  padding: 15px 30px;
  border-radius: 20px;
  display: inline-block;
  font-size: 28px;
  font-weight: 600;
  color: #5c4033;
  margin-bottom: 20px;
}

.page-description {
  color: #5c4033;
  max-width: 800px;
  margin-bottom: 30px;
}

.page-content {
  background-color: #f9f3e8;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c3;
}

@media (max-width: 768px) {
  .page-container {
    padding: 15px;
  }
  
  .page-title {
    font-size: 24px;
    padding: 12px 20px;
  }
  
  .page-content {
    padding: 20px;
  }
}
</style>