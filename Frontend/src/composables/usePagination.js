import { ref, computed, watch } from 'vue';

export default function usePagination(options = {}) {
  const currentPage = ref(options.initialPage || 1);
  const itemsPerPage = ref(options.itemsPerPage || 10);
  const totalItems = ref(options.totalItems || 0);
  
  // Calculate total pages
  const totalPages = computed(() => {
    return Math.ceil(totalItems.value / itemsPerPage.value) || 1;
  });
  
  // Ensure current page is within bounds
  watch([totalPages, currentPage], ([newTotalPages, newCurrentPage]) => {
    if (newCurrentPage > newTotalPages) {
      currentPage.value = newTotalPages;
    } else if (newCurrentPage < 1) {
      currentPage.value = 1;
    }
  });
  
  // Calculate offset for API requests
  const offset = computed(() => {
    return (currentPage.value - 1) * itemsPerPage.value;
  });
  
  // Get displayed page numbers (for pagination UI)
  const pageNumbers = computed(() => {
    const maxVisible = options.maxVisiblePages || 5;
    const totalPagesValue = totalPages.value;
    
    if (totalPagesValue <= maxVisible) {
      return Array.from({ length: totalPagesValue }, (_, i) => i + 1);
    }
    
    // Always show first and last page
    const pages = [1];
    
    let startPage = Math.max(2, currentPage.value - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPagesValue - 1, startPage + maxVisible - 3);
    
    // Adjust if we're at the end
    if (endPage === totalPagesValue - 1) {
      startPage = Math.max(2, endPage - (maxVisible - 3));
    }
    
    // Add ellipsis if needed
    if (startPage > 2) {
      pages.push('...');
    }
    
    // Add middle pages
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    // Add ellipsis if needed
    if (endPage < totalPagesValue - 1) {
      pages.push('...');
    }
    
    // Add last page
    if (totalPagesValue > 1) {
      pages.push(totalPagesValue);
    }
    
    return pages;
  });
  
  // Methods to change page
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page;
    }
  };
  
  const goToNextPage = () => {
    if (currentPage.value < totalPages.value) {
      currentPage.value++;
    }
  };
  
  const goToPrevPage = () => {
    if (currentPage.value > 1) {
      currentPage.value--;
    }
  };
  
  const goToFirstPage = () => {
    currentPage.value = 1;
  };
  
  const goToLastPage = () => {
    currentPage.value = totalPages.value;
  };
  
  // Pagination metadata
  const paginationInfo = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value + 1;
    const end = Math.min(start + itemsPerPage.value - 1, totalItems.value);
    
    return {
      start,
      end,
      total: totalItems.value,
      isFirstPage: currentPage.value === 1,
      isLastPage: currentPage.value === totalPages.value
    };
  });
  
  return {
    currentPage,
    itemsPerPage,
    totalItems,
    totalPages,
    offset,
    pageNumbers,
    paginationInfo,
    goToPage,
    goToNextPage,
    goToPrevPage,
    goToFirstPage,
    goToLastPage
  };
}