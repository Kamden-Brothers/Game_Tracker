import { createWebHistory, createRouter } from 'vue-router'

import HomeView from './components/home.vue'
import add_player from './components/add_player.vue'
import add_team from './components/add_team.vue'
import create_game from './components/create_game.vue'


const routes = [
    { path: '/', component: HomeView },
    { path: '/add_player', component: add_player },
    { path: '/add_team', component: add_team },
    { path: '/create_game', component: create_game },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router