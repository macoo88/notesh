<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router' // PRIDANÉ: useRoute

const router = useRouter()
const route = useRoute() // PRIDANÉ: aktivácia route (bez tohto riadku to padalo)

const classId = route.params.id

const showProfileMenu = ref(false)
const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user_id')
  router.push('/')
}   

const isModalOpen = ref(false)

const days = ['Pondelok', 'Utorok', 'Streda', 'Štvrtok', 'Piatok']
const hours = [1, 2, 3, 4, 5, 6]

const scheduleData = ref({
  Pondelok: { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '' },
  Utorok:   { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '' },
  Streda:   { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '' },
  Štvrtok:  { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '' },
  Piatok:   { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '' }
})

const tempScheduleData = ref({})

const openAddScheduleModal = () => {
  // Hlboká kópia dát do pomocného stavu pre formulár
  tempScheduleData.value = JSON.parse(JSON.stringify(scheduleData.value))
  isModalOpen.value = true
}

// PRIDANÁ FUNKCIA: Bez nej formulár v template spôsoboval crash celej stránky
const handleScheduleSubmit = () => {
  // Skopírujeme dáta z formulára do hlavného zobrazenia
  scheduleData.value = JSON.parse(JSON.stringify(tempScheduleData.value))
  
  // Zatiaľ ukladáme lokálne v prehliadači, neskôr sem napojíme axios
  console.log("Ukladám rozvrh pre triedu " + classId, scheduleData.value)
  
  isModalOpen.value = false
  alert("Rozvrh bol dočasne uložený!")
}
</script>

<template>
  <div class="schedulePage">
    <header class="main-header">
      <div class="container">
        <button class="homeBtn" @click="router.push(`/class/${classId}`)">Späť do triedy</button>
        <h1>Rozvrh</h1>
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

    <main class="schedule-main">
      <div class="container">
        
        <div class="schedule-actions">
          <button class="btn btn-add-schedule" @click="openAddScheduleModal">
            Pridať / Upraviť rozvrh
          </button>
        </div>

        <div class="schedule-table-wrapper">
          <table class="schedule-table">
            <thead>
              <tr>
                <th>Deň</th>
                <th v-for="hour in hours" :key="hour">{{ hour }}. hodina</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="day in days" :key="day">
                <td class="day-cell"><strong>{{ day }}</strong></td>
                <td v-for="hour in hours" :key="hour" class="subject-cell">
                  {{ scheduleData[day][hour] || '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </main>
    
    <footer class="main-footer">
      <div class="container footer-center">
        Noha
      </div>
    </footer>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
      <div class="modal-content schedule-modal">
        <h2>Upraviť rozvrh hodín</h2>
        
        <form @submit.prevent="handleScheduleSubmit">
          <div class="table-scroll-container">
            <table class="schedule-form-table">
              <thead>
                <tr>
                  <th>Deň</th>
                  <th v-for="hour in hours" :key="hour">{{ hour }}. hod</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="day in days" :key="day">
                  <td class="day-label"><strong>{{ day }}</strong></td>
                  <td v-for="hour in hours" :key="hour">
                    <input 
                      type="text" 
                      v-model="tempScheduleData[day][hour]" 
                      placeholder="Predmet"
                      class="schedule-input"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-cancel" @click="isModalOpen = false">Zrušiť</button>
            <button type="submit" class="btn btn-submit">Uložiť rozvrh</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style  src="@/assets/schedule.css"></style>