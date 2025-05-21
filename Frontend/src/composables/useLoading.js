import { ref, computed } from 'vue';

export default function useLoading() {
  const isLoading = ref(false);
  const loadingText = ref('Loading...');

  const showLoading = (text = 'Loading...') => {
    loadingText.value = text;
    isLoading.value = true;
  };

  const hideLoading = () => {
    isLoading.value = false;
  };

  const withLoading = async (asyncFunction, text = 'Loading...') => {
    showLoading(text);
    try {
      return await asyncFunction();
    } finally {
      hideLoading();
    }
  };

  return {
    isLoading,
    loadingText,
    showLoading,
    hideLoading,
    withLoading
  };
}