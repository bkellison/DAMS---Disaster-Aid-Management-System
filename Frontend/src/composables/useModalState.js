import { ref } from 'vue';

export default function useModalState() {
  const isModalOpen = ref(false);
  const modalData = ref(null);

  const openModal = (data = null) => {
    modalData.value = data;
    isModalOpen.value = true;
  };

  const closeModal = () => {
    isModalOpen.value = false;
    // Clear data after a short delay to prevent visual glitches
    setTimeout(() => {
      modalData.value = null;
    }, 300);
  };

  return {
    isModalOpen,
    modalData,
    openModal,
    closeModal
  };
}