import { defineStore } from "pinia";
import axios from "@/axios";
import Cookies from 'js-cookie';

export const useAuthStore = defineStore("auth", {
    //with token
    // state: () => ({
    //   user: null,
    //   authenticated: false,
    // }),
    // actions: {
    //   async checkAuth() {
    //     try {
    //       const response = await axios.get("http://127.0.0.1:5000/auth/status", {withCredentials: true});
    //       this.user = response.data.user;
    //       this.authenticated = true;
    //       console.log("Authenticated User:", response.data);
    //     } catch {
    //       this.user = null;
    //       this.authenticated = false;
    //       console.error("Auth check failed:", error.response ? error.response.data : error);
    //     }
    //   },
    // },
    state: () => ({
        userId: null,
        role: null
      }),
      actions: {
        setUserId(userData) {
          const userId = userData.user_id;
          const role = userData.role;

          Cookies.set('authUser', JSON.stringify({ userId, role }), {
            expires: 1 / 24,
            sameSite: 'Strict'
          })
        },
        logout() {
          this.userId = null;
          this.role = null;
          Cookies.remove('authUser');
        },
        loadUserDataFromCookie(){
          const cookie = Cookies.get('authUser');
          console.log('cookie')
          console.log(cookie)
          if(cookie)
          {
            try
            {
              const { userId, role } = JSON.parse(cookie);

              this.userId = userId;
              this.role = role;
            } 
            catch(err)
            {
              console.error('Invalid cookie');
              this.logout();
            }
          } 
          else {
            this.logout(); // cookie is expired or is missing
          }
          
        }

      }
  });