<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// Získanie ID triedy z URL
const classId = route.params.id 

// Reaktívne premenné
const className = ref("Načítavam triedu...")
const subjects = ref([])
const notes = ref([])
const activeNote = ref(null)
const selectedSubject = ref("")
const loading = ref(true)

// Spoločné nastavenie pre Axios
const token = localStorage.getItem('token')
const axiosConfig = { headers: { Authorization: `Bearer ${token}` } }

const loadPageData = async () => {
  try {
    const classRes = await axios.get(`http://127.0.0.1:8000/classes/${classId}`, axiosConfig)
    className.value = classRes.data.name
    await refreshSubjects() // Načíta predmety
  } catch (error) {
    console.error("Chyba pri načítavaní dát triedy:", error)
  } finally {
    loading.value = false;
  }
}

const refreshSubjects = async () => {
  const subjectsRes = await axios.get(`http://127.0.0.1:8000/classes/${classId}/subjects`, axiosConfig)
  subjects.value = subjectsRes.data
}

const openAddNoteModal = () => {
  newNoteData.value = {
    subject: selectedSubject.value || '',
    title: '',
    content: ''
  }
  isModalOpen.value = true
}

// Kliknutie na konkrétny predmet
const selectSubject = async (subjName) => {
  selectedSubject.value = subjName
  activeNote.value = null // Reset zobrazenia detailu poznámky
  try {
    const notesRes = await axios.get(`http://127.0.0.1:8000/classes/${classId}/notes/${subjName}`, axiosConfig)
    notes.value = notesRes.data
  } catch (error) {
    console.error("Chyba pri načítaní poznámok:", error)
  }
}

async function handleAddNoteSubmit(){
  if (!newNoteData.value.subject.trim() || !newNoteData.value.title.trim()) {
    alert("Predmet a Titulok musia byť vyplnené.")
    return
  }
  try {
    await axios.post(
      `http://127.0.0.1:8000/classes/${classId}/notes`, 
      {
        title: newNoteData.value.title,
        content: newNoteData.value.content,
        subject: newNoteData.value.subject.trim(),
      }, 
      axiosConfig
    );
    isModalOpen.value = false
    await refreshSubjects()
    await selectSubject(newNoteData.value.subject.trim())
  } catch (error) {
    console.error("Chyba pri pridávaní poznámky:", error)
  }
}

// Výber aktívnej poznámky na zobrazenie detailu
const setActiveNote = (note) => {
  activeNote.value = note
}

onMounted(() => {
  loadPageData()
})

const showProfileMenu = ref(false)
const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user_id')
  router.push('/')
}

// Stav pre modálne okno
const isModalOpen = ref(false)
const newNoteData = ref({
  subject: '',
  title: '',
  content: ''
})

</script>

<template>
  <div class="class-view">
  <header class="main-header">
    <div class="header-container">
        <button class="btn btn-back" @click="router.push('/my-classes')">Späť na prehľad</button>
        <h1>Trieda #{{ className }}</h1>
    </div>
              <div>
            <button class="profileImg" @click="toggleProfileMenu">
            <img src="@/assets/user.png" alt="Profile Image" />
            </button>

          <div v-if="showProfileMenu" class="profile-menu">
         <p>User Profile</p>
          <button @click="logout" class="btn btn-logout">Logout</button>
       </div>

      </div>
  </header>
  
  <div v-if="loading" class="loading-state">Načítavam...</div>

  <div v-else class="class-view-layout">
    
    <aside class="sidebar">
        <div class="subjects-section">
            <h3 class="sidebar-title">Predmety</h3>
            <div v-if="subjects.length === 0" class="empty-text">Zatiaľ žiadne predmety.</div>

            <ul class="subjects-list">
              <li 
                v-for="subj in subjects" 
                :key="subj"
                @click="selectSubject(subj)"
                :class="['subject-item', { 'active-subject': selectedSubject === subj }]"
              >
                {{ subj }}
              </li>
            </ul>
        </div>
        <div class="sidebar-footer">
            <button class="btn btn-add" @click="openAddNoteModal">Add note</button>
        </div>
    </aside>

    <main class="main-content">
      
      <div v-if="selectedSubject" class="notes-section">
        <h3 class="section-title">Poznámky pre: {{ selectedSubject }}</h3>
        <div v-if="notes.length === 0" class="empty-text">V tomto predmete nie sú žiadne poznámky.</div>
        
        <div class="notes-grid">
          <div 
            v-for="note in notes" 
            :key="note.id"
            @click="setActiveNote(note)"
            class="note-card"
          >
            <h4 class="note-card-title">{{ note.title }}</h4>
            <p class="note-card-preview">
              {{ note.content.substring(0, 50) }}{{ note.content.length > 50 ? '...' : '' }}
            </p>
          </div>
        </div>
      </div>
      
      <div v-else class="no-selection-state">
        Vyber si predmet z ľavého menu pre zobrazenie poznámok.
      </div>

      <div v-if="activeNote" class="note-detail-box">
        <h2 class="note-detail-title">{{ activeNote.title }}</h2>
        <hr class="note-detail-divider" />
        <p class="note-detail-content">{{ activeNote.content }}</p>
      </div>

    </main>

  </div>
</div>

<div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
    <div class="modal-content">
      <h2>Pridať novú poznámku</h2>
      <form @submit.prevent="handleAddNoteSubmit">
        <div class="form-group">
          <label>Predmet</label>
          <input type="text" v-model="newNoteData.subject"  required />
        </div>
        <div class="form-group">
          <label>Titulok poznámky</label>
          <input type="text" v-model="newNoteData.title"  required />
        </div>
        <div class="form-group">
          <label>Obsah</label>
          <textarea v-model="newNoteData.content"  rows="6"></textarea>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-cancel" @click="isModalOpen = false">Zrušiť</button>
          <button type="submit" class="btn btn-submit">Vytvoriť</button>
        </div>
      </form>
    </div>
  </div>
</template>
<style src="@/assets/classView.css"></style>