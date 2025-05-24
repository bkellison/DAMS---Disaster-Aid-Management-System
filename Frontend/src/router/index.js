import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// Auth routes
import Login from '@/views/auth/Login.vue';
import Register from '@/views/auth/Register.vue';
import ResetPassword from '@/views/auth/ResetPassword.vue';
// Admin routes
import AdminDashboard from '@/views/admin/AdminDashboard.vue';
import CreateEvent from '@/views/admin/CreateEvent.vue';
import ManageItems from '@/views/admin/ManageItems.vue';
import ViewEvents from '@/views/admin/ViewEvents.vue';

// Donor routes
import DonorDashboard from '@/views/donor/DonorDashboard.vue';
import PledgeView from '@/views/donor/PledgeView.vue';
import CreatePledgeForm from '@/views/donor/CreatePledgeForm.vue';

// Recipient routes
import RecipientDashboard from '@/views/recipient/RecipientDashboard.vue';
import RequestView from '@/views/recipient/RequestView.vue';

// Shared routes
import CreateRequest from '@/views/shared/CreateRequest.vue';
import RespondToRequests from '@/views/shared/RespondToRequests.vue';
import RespondPage from '@/views/shared/RespondPage.vue';
import MatchView from '@/views/shared/MatchView.vue';
import ShippingInfo from '@/views/shared/ShippingInfo.vue';
import AutoMatch from '@/views/shared/AutoMatch.vue';
import ManualMatchForm from '@/views/shared/ManualMatchForm.vue';

// Define routes
const routes = [
  // Auth routes (public)
  {
    path: '/',
    name: 'login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: ResetPassword,
    meta: { requiresAuth: false }
  },
  
  // Admin routes - UPDATED to include Admin Observer for view-only access
  {
    path: '/admin',
    name: 'admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ['Admin', 'Admin Observer'] } // Allow both Admin and Admin Observer
  },
  {
    path: '/admin/create-event',
    name: 'create-event',
    component: CreateEvent,
    meta: { requiresAuth: true, roles: ['Admin'] } // Only full Admin can create
  },
  {
    path: '/admin/manage-items',
    name: 'manage-items',
    component: ManageItems,
    meta: { requiresAuth: true, roles: ['Admin'] } // Only full Admin can manage
  },
  {
    path: '/admin/view-events',
    name: 'view-events',
    component: ViewEvents,
    meta: { requiresAuth: true, roles: ['Admin', 'Admin Observer'] } // Both can view
  },
  
  // Donor routes
  {
    path: '/donor',
    name: 'donor',
    component: DonorDashboard,
    meta: { requiresAuth: true, roles: ['Donor'] }
  },
  {
    path: '/pledge-view',
    name: 'pledges',
    component: PledgeView,
    meta: { requiresAuth: true, roles: ['Donor', 'Admin', 'Admin Observer'] } // Admin Observer can view
  },
  {
    path: '/create-pledge',
    name: 'create-pledge',
    component: CreatePledgeForm,
    meta: { requiresAuth: true, roles: ['Donor'] } // Admin Observer cannot create
  },
  
  // Recipient routes
  {
    path: '/recipient',
    name: 'recipient',
    component: RecipientDashboard,
    meta: { requiresAuth: true, roles: ['Recipient'] }
  },
  {
    path: '/request-view',
    name: 'requests',
    component: RequestView,
    meta: { requiresAuth: true, roles: ['Recipient', 'Admin', 'Admin Observer'] } // Admin Observer can view
  },
  
  // Shared routes - UPDATED for Admin Observer permissions
  {
    path: '/create-request',
    name: 'create-request',
    component: CreateRequest,
    meta: { requiresAuth: true, roles: ['Recipient', 'Donor', 'Admin'] } // Admin Observer cannot create
  },
  {
    path: '/respond-to-requests',
    name: 'respond-to-requests',
    component: RespondToRequests,
    meta: { requiresAuth: true, roles: ['Donor', 'Admin', 'Admin Observer'] } // Admin Observer can view requests
  },
  {
    path: '/respond/:id',
    name: 'respond-page',
    component: RespondPage,
    meta: { requiresAuth: true, roles: ['Donor', 'Admin'] } // Admin Observer cannot respond
  },
  {
    path: '/match-view',
    name: 'matches',
    component: MatchView,
    meta: { requiresAuth: true, roles: ['Donor', 'Recipient', 'Admin', 'Admin Observer'] } // Admin Observer can view
  },
  {
    path: '/shipping/:id',
    name: 'shipping',
    component: ShippingInfo,
    meta: { requiresAuth: true, roles: ['Donor', 'Recipient', 'Admin', 'Admin Observer'] } // Admin Observer can view
  },
  {
    path: '/create-match/:id',
    name: 'create-match',
    component: ManualMatchForm,
    meta: { requiresAuth: true, roles: ['Admin'] } // Only full Admin can create matches
  },
  {
    path: '/auto-match/:id',
    name: 'auto-match',
    component: AutoMatch,
    meta: { requiresAuth: true, roles: ['Admin'] } // Only full Admin can auto-match
  },
  
  // Catch-all route (404)
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Scroll to top on navigation
    return savedPosition || { top: 0 };
  }
});

// Navigation guard - UPDATED to handle Admin Observer routing
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  authStore.loadUserDataFromCookie();
  
  // Check if the route requires authentication
  if (to.meta.requiresAuth) {
    // If not authenticated, redirect to login
    if (!authStore.isAuthenticated) {
      next({ name: 'login' });
      return;
    }
    
    // Check if user has required role for the route
    if (to.meta.roles && !to.meta.roles.includes(authStore.role)) {
      // Redirect to appropriate dashboard if user doesn't have required role
      if (authStore.isAdmin || authStore.isAdminObserver) {
        next({ name: 'admin' }); // Both Admin and Admin Observer go to admin dashboard
      } else if (authStore.isDonor) {
        next({ name: 'donor' });
      } else if (authStore.isRecipient) {
        next({ name: 'recipient' });
      } else {
        next({ name: 'login' });
      }
      return;
    }
  } else if (authStore.isAuthenticated) {
    // Redirect to appropriate dashboard if already logged in and trying to access auth pages
    if (to.name === 'login' || to.name === 'register' || to.name === 'reset-password') {
      if (authStore.isAdmin || authStore.isAdminObserver) {
        next({ name: 'admin' }); // Both go to admin dashboard
      } else if (authStore.isDonor) {
        next({ name: 'donor' });
      } else if (authStore.isRecipient) {
        next({ name: 'recipient' });
      } else {
        next();
      }
      return;
    }
  }
  
  // All good, proceed to the route
  next();
});

export default router;