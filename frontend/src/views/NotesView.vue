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
        <button class="myClasses_btn"@click="router.push('/my-classes')"> >
          My Classes
        </button>
        <button class="createClasses_btn" @click="toggleCreateClass">
          Create Class
        </button>
        <button class="joinClasses_btn" @click="toggleJoinClass">
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
          <input v-model="classData.name" type="text" placeholder="Class Name" class="class-name-input" />
          <input v-model="classData.description" type="text" placeholder="Class Description" class="class-description-input" />
        </div>
        
        <button class="btn btn-create" @click="handleCreateClass">Create</button>
        <button class="btn btn-cancel" @click="toggleCreateClass">Cancel</button>
      </div>
      <div v-if="joinClass" class="create-class-modal">
        <h1>Join a Class</h1>
        <div class="classInfo">
          <input v-model="classData.name" type="text" placeholder="Invite Code" class="class-name-input" />
        </div>
        
        <button class="btn btn-create" @click="handleJoinClass">Join </button>
        <button class="btn btn-cancel" @click="toggleJoinClass">Cancel</button>
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
const joinClass  = ref(false)

const toggleCreateClass = () => {
  createClass.value = !createClass.value
}
const toggleJoinClass = () => {
  joinClass.value = !joinClass.value
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
    const name = classData.value.name;
    const desc = classData.value.description;

    // Posielame request na backend
    const response = await axios.post(
     `http://127.0.0.1:8000/classes/create?name=${encodeURIComponent(name)}&description=${encodeURIComponent(desc)}`,
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

const handleJoinClass = async () => {
  try {
    const token = localStorage.getItem('token');
    const inviteCode = classData.value.name; // Kód, ktorý používateľ napísal

    // URL musí končiť priamo tým kódom, napr. /join/ABCDEF12
    const response = await axios.post(
      `http://127.0.0.1:8000/classes/join/${inviteCode}`, 
      {}, // 1. Prázdne body (dáta)
      {
        headers: {
          Authorization: `Bearer ${token}` // 2. Konfigurácia s tokenom
        }
      }
    );

    alert(response.data.message || "Pridaný do triedy!");
    
    // Reset a zatvorenie
    classData.value.name = '';
    toggleJoinClass();

  } catch (error) {
    console.error(error);
    alert(error.response?.data?.detail || "Neplatný kód alebo iná chyba.");
  }
}
</script>

<style src="@/assets/loginPage.css"></style>