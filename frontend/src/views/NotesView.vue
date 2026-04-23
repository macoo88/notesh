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
        <button class="myClasses_btn" >
          My Classes
        </button>
        <button class="createClasses_btn" @click="toggleCreateClass">
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

    <div>
      <div v-if="createClass" class="create-class-modal">
        <h1>Create a New Class</h1>
        <div class="classInfo">
          <input type="text" placeholder="Class Name" class="class-name-input" />
          <input type="text" placeholder="Class Description" class="class-description-input" />
        </div>
        
        <button class="btn btn-create" @click="handleCreateClass">Create</button>
        <button class="btn btn-cancel" @click="toggleCreateClass">Cancel</button>
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const showProfileMenu = ref(false)
const createClass  = ref(false)

const toggleCreateClass = () => {
  createClass.value = !createClass.value
}

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user_id')
  router.push('/')
}

//nova trieda
const classData = ref({
  name: '',
  description: ''
})

const handleCreateClass = async () => {
  try {
    const token = localStorage.getItem('token'); // Tu je ten tvoj uložený kód!

    // Posielame request na backend
    const response = await axios.post(
      `http://127.0.0.1:8000/classes/create?name=${encodeURIComponent(classData.name)}&description=${encodeURIComponent(classData.description)}`,
      {}, // Telo je prázdne, lebo backend čaká Query parametre (pozri nižšie)
      {
        headers: {
          Authorization: `Bearer ${token}` 
        }
      }
    );

    alert(`Trieda vytvorená! Pozývací kód: ${response.data.invite_code}`);
    
    // Reset a zatvorenie
    classData.name = '';
    classData.description = '';
    toggleCreateClass();

  } catch (error) {
    console.error(error);
    alert(error.response?.data?.detail || "Nepodarilo sa vytvoriť triedu. Skontroluj, či si prihlásený.");
  }
}
</script>

<style src="@/assets/loginPage.css"></style>