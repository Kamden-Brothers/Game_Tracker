//import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.css'
import * as bootstrap from 'bootstrap/dist/js/bootstrap.bundle';


import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

createApp(App)
    .provide('bootstrap', bootstrap)
    .use(router)
    .mount('#app')