<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
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

// Modálne okno a konštanty rozvrhu
const isModalOpen = ref(false)
const days = ['Pondelok', 'Utorok', 'Streda', 'Štvrtok', 'Piatok']
const hours = [1, 2, 3, 4, 5, 6, 7, 8]

// Funkcia na vygenerovanie prázdnej 2D štruktúry rozvrhu
const generateEmptySchedule = () => ({
  Pondelok: { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '' },
  Utorok:   { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '' },
  Streda:   { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '' },
  Štvrtok:  { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '' },
  Piatok:   { 1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '' }
})

const scheduleData = ref(generateEmptySchedule())
const tempScheduleData = ref({})

// Nastavenie autorizácie pre Axios (Bearer token)
const token = localStorage.getItem('token')
const axiosConfig = { headers: { Authorization: `Bearer ${token}` } }

// --- 1. NAČÍTANIE ROZVRHU Z BACKENDU ---
const fetchSchedule = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/classes/${classId}/schedule`, axiosConfig)
    
    const freshSchedule = generateEmptySchedule()
    
    // Transformácia plochého poľa z backendu do našej priradenej 2D štruktúry
    response.data.forEach(cell => {
      if (freshSchedule[cell.day] && freshSchedule[cell.day].hasOwnProperty(cell.period)) {
        freshSchedule[cell.day][cell.period] = cell.subject_name || ''
      }
    })
    
    scheduleData.value = freshSchedule
  } catch (error) {
    console.error("Chyba pri načítavaní rozvrhu z backendu:", error)
  }
}

// Načítame dáta hneď pri namontovaní komponentu
onMounted(() => {
  fetchSchedule()
})

const openAddScheduleModal = () => {
  // Vytvoríme hlbokú kópiu dát, aby sme nemenili pôvodný rozvrh pred stlačením "Uložiť"
  tempScheduleData.value = JSON.parse(JSON.stringify(scheduleData.value))
  isModalOpen.value = true
}

// --- 2. UKLADANIE ROZVRHU NA BACKEND ---
const handleScheduleSubmit = async () => {
  try {
    const payload = []
    
    // Sploštenie 2D objektu na pole objektov pre backend (List[schemas.ScheduleCellUpdate])
    days.forEach(day => {
      hours.forEach(hour => {
        const value = tempScheduleData.value[day][hour]
        payload.push({
          day: day,
          period: Number(hour),
          subject_name: value && value.trim() !== '' ? value.trim() : null
        })
      })
    })

    // Odoslanie dát na FastAPI backend
    await axios.post(`http://127.0.0.1:8000/classes/${classId}/schedule`, payload, axiosConfig)
    
    // Ak zápis prebehol v poriadku, prepíšeme ostré dáta a zatvoríme modál
    scheduleData.value = JSON.parse(JSON.stringify(tempScheduleData.value))
    isModalOpen.value = false
    alert("Rozvrh bol úspešne uložený na server!")
    
  } catch (error) {
    console.error("Chyba pri ukladaní rozvrhu na backend:", error)
    // Ak nie si owner triedy, backend vráti 403 detail správu, ktorú tu korektne vypíšeme
    alert(error.response?.data?.detail || "Nepodarilo sa uložiť rozvrh na server.");
  }
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
      <div class="container footer-center"></div>
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

<style src="@/assets/schedule.css"></style>