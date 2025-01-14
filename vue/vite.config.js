import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'


// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})

//modules.export = {
//    pages: {
//        'index': {
//            entry: './src/home/main.js',
//            template: './index.html',
//            title: 'Home',
//            chunks: []
//        },
//        'add_player': {
//            entry: './src/add_player/main.js',
//            template: './add_player.html',
//            'title': 'Add Players',
//            chunks: []
//        }
//    }

//}
