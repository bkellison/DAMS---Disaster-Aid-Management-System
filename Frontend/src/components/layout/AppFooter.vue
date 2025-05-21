<template>
  <footer class="app-footer">
    <div class="app-footer__content">
      <p>© {{ currentYear }} Disaster Relief Portal. All rights reserved.</p>
      <div class="app-footer__links">
        <a href="#" @click.prevent="showPrivacyPolicy">Privacy Policy</a>
        <a href="#" @click.prevent="showTerms">Terms of Service</a>
        <a href="#" @click.prevent="showContactInfo">Contact Us</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());

// These functions would typically open modals or navigate to appropriate pages
const showPrivacyPolicy = () => {
  console.log('Show privacy policy');
};

const showTerms = () => {
  console.log('Show terms of service');
};

const showContactInfo = () => {
  console.log('Show contact information');
};
</script>

<style scoped>
.app-footer {
  background-color: #5c4033;
  color: #f5e1c5;
  padding: 20px;
  margin-top: auto; /* Push to bottom if main content doesn't fill the page */
}

.app-footer__content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.app-footer p {
  margin: 0;
}

.app-footer__links {
  display: flex;
  gap: 20px;
}

.app-footer__links a {
  color: #f5e1c5;
  text-decoration: none;
  transition: opacity 0.2s;
}

.app-footer__links a:hover {
  opacity: 0.8;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .app-footer__content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
