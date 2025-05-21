import { ref } from 'vue';

export default function useConfirm() {
  const confirm = ref({
    show: false,
    title: '',
    message: '',
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    confirmCallback: null,
    cancelCallback: null
  });

  const showConfirm = (options) => {
    confirm.value = {
      show: true,
      title: options.title || 'Confirm',
      message: options.message || 'Are you sure?',
      confirmText: options.confirmText || 'Confirm',
      cancelText: options.cancelText || 'Cancel',
      confirmCallback: options.onConfirm || null,
      cancelCallback: options.onCancel || null
    };
  };

  const handleConfirm = () => {
    if (confirm.value.confirmCallback) {
      confirm.value.confirmCallback();
    }
    closeConfirm();
  };

  const handleCancel = () => {
    if (confirm.value.cancelCallback) {
      confirm.value.cancelCallback();
    }
    closeConfirm();
  };

  const closeConfirm = () => {
    confirm.value.show = false;
  };

  return {
    confirm,
    showConfirm,
    handleConfirm,
    handleCancel,
    closeConfirm
  };
}