import { createRouter, createWebHistory } from 'vue-router';
import Cookies from 'js-cookie';
import axios from "@/axios"; 
import { useAuthStore } from '@/stores/auth';
import LoginView from '@/views/LoginView.vue';
import RegisterView from '@/views/RegisterView.vue';
import AdminView from '@/views/AdminView.vue';
import ResetPasswordView from '@/views/ResetPasswordView.vue';
import HomePage from '@/views/HomePage.vue';
import DonorPage from '@/views/DonorLandingPage.vue';
import PledgePage from '@/views/Pledges/PledgeView.vue';
import CreatePledge from '@/views/Pledges/CreatePledgeForm.vue';
import CreateMatch from '@/views/Matches/ManualMatchForm.vue';
import AutoMatch from '@/views/Matches/AutoMatch.vue';
import RespondToRequests from '@/views/RespondToRequests.vue';
import RespondPage from '@/views/RespondPage.vue';
import CreateRequestView from '@/views/CreateRequestView.vue';
import MatchesPage from '@/views/Matches/MatchView.vue';
import RequestPage from '@/views/Requests/RequestsView.vue';
import CreateEventView from '@/views/CreateEventView.vue';
import ManageItemsView from '@/views/ManageItemsView.vue';
import ViewEvents from '@/views/ViewEvents.vue';
import ShippingView from '@/views/ShippingView.vue';

const routes = [
  { path: '/', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/reset-password', name: 'ResetPassword', component: ResetPasswordView },
  { path: '/admin', name: 'Admin', component: AdminView, meta: { requiresAuth: true } },
  { path: '/admin/create-event', name: 'CreateEvent', component: CreateEventView, meta: { requiresAuth: true } },
  { path: '/admin/manage-items', name: 'ManageItems', component: ManageItemsView, meta: { requiresAuth: true } },
  { path: '/admin/view-events', name: 'ViewEvents', component: ViewEvents, meta: { requiresAuth: true } },
  { path: '/donor', name: 'Donor', component: DonorPage, meta: { requiresAuth: true } },
  { path: '/pledge-view', name: 'Pledges', component: PledgePage, meta: { requiresAuth: true } },
  { path: '/create-pledge', name: 'CreatePledge', component: CreatePledge, meta: { requiresAuth: true } },
  { path: '/respond-to-requests', name: 'RespondToRequests', component: RespondToRequests, meta: { requiresAuth: true } },
  { path: '/respond/:id', name: 'RespondPage', component: RespondPage, meta: { requiresAuth: true } },
  { path: '/create-request', name: 'CreateRequest', component: CreateRequestView, meta: { requiresAuth: true } },
  { path: '/create-match/:id', name: 'CreateMatch', component: CreateMatch, meta: { requiresAuth: true } },
  { path: '/auto-match/:id', name: 'AutoMatch', component: AutoMatch, meta: { requiresAuth: true } },
  { path: '/match-view', name: 'MatchesPage', component: MatchesPage, meta: { requiresAuth: true } },
  { path: '/request-view', name: 'RequestPage', component: RequestPage, meta: { requiresAuth: true } },
  { path: '/shipping/:id', name: 'ShippingView', component: ShippingView, meta: { requiresAuth: true } },

];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

/* Will uncomment once auhtoization features work */

// Add route guard to check authentication for protected routes (like Admin)
router.beforeEach(async (to, from, next) => {
  const isAuthenticated = false; // Replace with actual auth check
  if (to.meta.requiresAuth) {
    try {
      console.log("to")
      console.log(to)
      console.log(from)
      //const response = await axios.get("http://127.0.0.1:5000/auth/status");
      // console.log(response)      
      const authStore = useAuthStore();
      authStore.loadUserDataFromCookie();
      console.log(authStore.userId); 
      console.log(authStore.role)
      if (authStore.userId != null) {
        if(to.name == 'Admin' && authStore.role == "Admin")
        {
          next();
        }
        if(to.name == 'Donor' && authStore.role == "Donor")
        {
          next();
        }
        if(to.name == 'CreatePledge' && authStore.role == "Donor")
        {
          next();
        }
        if(to.name == 'Pledges' && (authStore.role == "Donor" || authStore.role == "Admin"))
        {
          next();
        }
        if (to.name == 'CreateRequest' && (authStore.role == "Recipient" || authStore.role == "Donor" || authStore.role == "Admin")) 
        {
          next();
        }
        if (to.name == 'RespondToRequests' && (authStore.role == "Donor" || authStore.role == "Admin")) 
        {
          next();
        }
        if (to.name == 'RespondPage' && (authStore.role == "Donor" || authStore.role == "Admin")) 
        {
          next();
        }
        if(to.name == 'RequestPage')
        {
          next();
        }
        if(to.name == 'Home')
        {
          next();
        }
        if(to.name == 'CreateMatch' && authStore.role == 'Admin') 
        {
          next();
        }
        if(to.name == 'AutoMatch' && authStore.role == 'Admin') 
        {
          next();
        }
        if(to.name == 'MatchesPage') 
        {
          next();
        }
        if(to.name == 'CreateEvent' && authStore.role == 'Admin')
        {
          next();
        }
        if(to.name == 'ViewEvents' && authStore.role == 'Admin')
        {
          next();
        }
        if(to.name == 'ManageItems' && authStore.role == 'Admin')
        {
          next();
        }
        if (to.name == 'ShippingView') {
          next();
        }
        
      } else {
        next("/");
      }
    } catch {
      next("/");
    }
  } else {
    next();
  }
});

export default router;