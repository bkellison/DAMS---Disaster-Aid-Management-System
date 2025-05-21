<template>
  <transition name="alert">
    <div v-if="show" class="app-alert" :class="[`app-alert--${type}`]">
      <div class="app-alert__icon">
        <span class="icon" :class="iconClass"></span>
      </div>
      <div class="app-alert__content">
        <strong v-if="title" class="app-alert__title">{{ title }}</strong>
        <div class="app-alert__message">
          <slot></slot>
        </div>
      </div>
      <button v-if="dismissible" class="app-alert__close" @click="dismiss">
        &times;
      </button>
    </div>
  </transition>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['info', 'success', 'warning', 'error'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  dismissible: {
    type: Boolean,
    default: false
  },
  autoDismiss: {
    type: Number,
    default: 0 // milliseconds, 0 = never auto dismiss
  }
});

const emit = defineEmits(['dismiss']);

const show = ref(true);

const dismiss = () => {
  show.value = false;
  emit('dismiss');
};

const iconClass = computed(() => {
  switch (props.type) {
    case 'success': return 'icon-check';
    case 'warning': return 'icon-warning';
    case 'error': return 'icon-error';
    case 'info': 
    default: return 'icon-info';
  }
});

// Auto-dismiss logic
if (props.autoDismiss > 0) {
  setTimeout(() => {
    dismiss();
  }, props.autoDismiss);
}
</script>

<style scoped>
.app-alert {
  display: flex;
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 8px;
  border-left: 4px solid;
  background-color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.app-alert--info {
  border-left-color: #0077cc;
  background-color: #f0f7ff;
}

.app-alert--success {
  border-left-color: #2e8b57;
  background-color: #f0fff5;
}

.app-alert--warning {
  border-left-color: #e6a23c;
  background-color: #fffbf0;
}

.app-alert--error {
  border-left-color: #e63946;
  background-color: #fff0f0;
}

.app-alert__icon {
  margin-right: 12px;
  display: flex;
  align-items: center;
}

.app-alert__content {
  flex: 1;
}

.app-alert__title {
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
  font-size: 16px;
}

.app-alert__close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  align-self: flex-start;
  margin: -8px;
  padding: 8px;
}

.app-alert__close:hover {
  color: #333;
}

/* Icons */
.icon {
  display: inline-block;
  width: 24px;
  height: 24px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.icon-info {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%230077cc'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 15c-.55 0-1-.45-1-1v-4c0-.55.45-1 1-1s1 .45 1 1v4c0 .55-.45 1-1 1zm1-8h-2V7h2v2z'/%3E%3C/svg%3E");
}

.icon-check {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%232e8b57'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E");
}

.icon-warning {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23e6a23c'%3E%3Cpath d='M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z'/%3E%3C/svg%3E");
}

.icon-error {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23e63946'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z'/%3E%3C/svg%3E");
}

/* Transition animation */
.alert-enter-active, .alert-leave-active {
  transition: all 0.3s ease-out;
}

.alert-enter-from, .alert-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
