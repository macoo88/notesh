<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

// Pole, do ktorého uložíme triedy z databázy
const myClasses = ref([])
const loading = ref(true)
const router = useRouter()

const showProfileMenu = ref(false)
const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}
const fetchClasses = async () => {
  try {
    const token = localStorage.getItem('token'); // Získame tvoj uložený token
    
    const response = await axios.get('http://127.0.0.1:8000/users/me/classes', {
      headers: {
        Authorization: `Bearer ${token}` // Autorizácia pre get_current_user
      }
    });

    myClasses.value = response.data; // Uložíme výsledok (zoznam objektov ClassModel)
  } catch (error) {
    console.error("Chyba pri načítaní tried:", error);
  } finally {
    loading.value = false;
  }
}

const goToClass = (classId) => {
  router.push(`/class/${classId}`)
}

// Spustí sa automaticky pri otvorení okna
onMounted(() => {
  fetchClasses();
})
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user_id')
  router.push('/')
}
</script>
<template>
 <div class="myClassesPage">

  <header class="main-header">
    <div class="container">
      <button class="homeBtn" @click="router.push('/notes')">Home</button>
          <h1>Moje Triedy</h1>

          <div>
            <button class="profileImg" @click="toggleProfileMenu">
            <img src="@/assets/user.png" alt="Profile Image" />
            </button>

          <div v-if="showProfileMenu" class="profile-menu">
         <p>User Profile</p>
          <button @click="logout" class="btn btn-logout">Logout</button>
       </div>

      </div>
    </div>

  </header>
  
  <div class="main-content-wrapper">
    <!-- Indikátor načítavania -->
    <div v-if="loading">Načítavam triedy...</div>

    <!-- Zoznam tried -->
    <div v-else class="classes-grid">
      <div v-if="myClasses.length === 0" class="empty-state">
        Nie ste členom žiadnej triedy.
      </div>

      <div 
        v-for="cls in myClasses" 
        :key="cls.id" 
        class="class-card"
      >
        <div class="class-header">
          <h2>{{ cls.name }}</h2>
          <span class="invite-code">#{{ cls.invite_code }}</span>
        </div>
        <p class="class-desc">{{ cls.description }}</p>
        
        <button class="btn btn-enter" @click="goToClass(cls.id)">
          Vstúpiť do triedy
        </button>
      </div>
    </div>
  </div>
 </div>

</template>
<style src="@/assets/myClasses.css"></style>