<template>
  <div class="notesView">

    <header class="main-header">
      <div class="container">
        <div class="logo-area">
          <img src="@/assets/icon.webp" alt="Notes logo" class="notes-logo" />
          <h1 class="notes-title">Notes</h1>
      </div>
      
      <div class="nav-buttons">
        
        
        <button class="profileImg" @click="toggleProfileMenu">
          <img src="@/assets/user.png" alt="Profile Image" />
        </button>
      </div>

    </div>
   </header>

    <main class="notes-main">
      <div class="Class_btns">
        <button class="myClasses_btn">
          My Classes
        </button>
        <button class="createClasses_btn">
          Create Class
        </button>
        <button class="joinClasses_btn">
          Join Class
        </button>
      </div>
      <div>
        <img src="@/assets/notes.png" alt="">
      </div>
    </main>

    <footer class="main-footer">
       <div class="container footer-center">
        Noha
      </div>
    </footer>

    <div>
      <div v-if="showProfileMenu" class="profile-menu">
        <p>User Profile</p>
        <button @click="logout" class="btn btn-logout">Logout</button>
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const showProfileMenu = ref(false)

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user_id')
  router.push('/')
}
</script>

<style src="@/assets/loginPage.css"></style>