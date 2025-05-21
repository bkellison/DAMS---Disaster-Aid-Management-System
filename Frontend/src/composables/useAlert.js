import { ref, computed } from 'vue';

export default function useAlert() {
  const alert = ref({
    show: false,
    type: 'info',
    title: '',
    message: '',
    timeout: null
  });

  const showAlert = (options) => {
    // Clear any existing timeout
    if (alert.value.timeout) {
      clearTimeout(alert.value.timeout);
    }

    // Set alert properties
    alert.value = {
      show: true,
      type: options.type || 'info',
      title: options.title || '',
      message: options.message || '',
      timeout: null
    };

    // Auto-dismiss if duration is provided
    if (options.duration) {
      alert.value.timeout = setTimeout(() => {
        closeAlert();
      }, options.duration);
    }
  };

  const closeAlert = () => {
    alert.value.show = false;
    if (alert.value.timeout) {
      clearTimeout(alert.value.timeout);
      alert.value.timeout = null;
    }
  };

  const isVisible = computed(() => alert.value.show);

  return {
    alert,
    showAlert,
    closeAlert,
    isVisible
  };
}