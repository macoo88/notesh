import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// Importujeme novú stranu (musíš si ju vytvoriť vo views/NotesView.vue)
// Namiesto '../views/NotesView.vue' skús toto:
import NotesView from '@/views/NotesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/notes',
      name: 'notes',
      component: NotesView,
      // Táto meta informácia nám pomôže strážiť stránku
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

// --- TOTO JE OCHRANA (Navigation Guard) ---
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token') // Skontroluje, či máme token

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Ak stránka vyžaduje prihlásenie a my nie sme prihlásení, hodí nás to na Home
    next('/')
  } else {
    next() // Inak nás pustí ďalej
  }
})

export default router