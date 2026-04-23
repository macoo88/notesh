<template>
  <div class="notesView">

    <header class="main-header">
      <div class="container">
        <div class="logo-area">
          <img src="@/assets/icon.webp" alt="Notes logo" class="notes-logo" />
          <h1 class="notes-title">Notes</h1>
      </div>
      
      <div class="nav-buttons">
        <button class="btn btn-login" @click="logout" >Logout</button>
        
        <button class="profileImg">
          <img src="@/assets/user.png" alt="Profile Image" />
        </button>
      </div>

    </div>
   </header>
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

<style src="@/assets/loginPage.css"></style>