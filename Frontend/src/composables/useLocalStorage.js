import { ref, watch } from 'vue';

export default function useLocalStorage(key, initialValue) {
  // Get from local storage then parse stored json or return initialValue
  const readValue = () => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  };

  // State
  const storedValue = ref(readValue());

  // Return a wrapped version of localStorage setter that saves the new value
  const setValue = (value) => {
    try {
      // Allow value to be a function for same API as useState
      const valueToStore = value instanceof Function ? value(storedValue.value) : value;
      
      // Save to state
      storedValue.value = valueToStore;
      
      // Save to localStorage
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };

  // Listen for changes to this localStorage value in other tabs/windows
  const handleStorageChange = (event) => {
    if (event.key === key && event.newValue) {
      storedValue.value = JSON.parse(event.newValue);
    }
  };

  // Add event listener for storage changes
  window.addEventListener('storage', handleStorageChange);

  // Remove event listener on unmount
  onUnmounted(() => {
    window.removeEventListener('storage', handleStorageChange);
  });

  return [storedValue, setValue];
}