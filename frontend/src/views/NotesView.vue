<template>
  <div class="notes-page">
    <h1>Moje Poznámky</h1>
    <p>Ak toto vidíš, presmerovanie funguje!</p>
    <button @click="logout">Odhlásiť sa</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user_id')
  router.push('/')
}
</script>

<style scoped>
.notes-page {
  padding: 20px;
  text-align: center;
}
</style>