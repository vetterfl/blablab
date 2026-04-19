import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../App.vue'),
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
