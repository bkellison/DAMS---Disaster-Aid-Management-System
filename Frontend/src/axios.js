import axios from 'axios';

const instance = axios.create({
  baseURL: 'http://127.0.0.1:5000',  // Base url - currently set up localhost of py project
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

//if we use local storage - this is an option
// axios.interceptors.request.use((config) => {
//   const token = localStorage.getItem("jwt"); 
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

export default instance;