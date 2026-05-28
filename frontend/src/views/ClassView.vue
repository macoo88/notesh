<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// Získanie ID triedy z URL
const classId = route.params.id 

// --- REAKTÍVNE PREMENNÉ (Formulár musí byť definovaný hneď navrchu) ---
const className = ref("")
const subjects = ref([])
const notes = ref([])
const activeNote = ref(null)
const selectedSubject = ref("")
const loading = ref(true)

const isModalOpen = ref(false)
const isEditing = ref(false)
const editingNoteId = ref(null)

// Objekt pre dáta novej/editovanej poznámky
const newNoteData = ref({
  subject: '',
  title: '',
  content: ''
})

// Premenné pre nahrávanie súborov (Obrázkov)
const fileInputRef = ref(null)
const selectedFile = ref(null)
const selectedFilePreview = ref("")

// Spoločné nastavenie pre Axios
const token = localStorage.getItem('token')
const axiosConfig = { headers: { Authorization: `Bearer ${token}` } }

const loadPageData = async () => {
  try {
    const classRes = await axios.get(`http://127.0.0.1:8000/classes/${classId}`, axiosConfig)
    className.value = classRes.data.name 
    await refreshSubjects() 
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
  isEditing.value = false
  editingNoteId.value = null
  selectedFile.value = null
  selectedFilePreview.value = ""
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
  activeNote.value = null 
  try {
    const notesRes = await axios.get(`http://127.0.0.1:8000/classes/${classId}/notes/${subjName}`, axiosConfig)
    notes.value = notesRes.data
  } catch (error) {
    console.error("Chyba pri načítaní poznámok:", error)
  }
}

// Vyvolanie kliknutia na skrytý file input (Otvorí File Explorer)
const triggerFileSelect = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

// Spracovanie vybraného súboru z File Explorera
const onFileSelected = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    selectedFilePreview.value = file.name
  }
}

async function handleAddNoteSubmit(){
  if (!newNoteData.value.subject || !newNoteData.value.subject.trim() || 
      !newNoteData.value.title || !newNoteData.value.title.trim()) {
    alert("Predmet a Titulok musia byť vyplnené.")
    return
  }
  
  try {
    if (isEditing.value) {
      // REŽIM ÚPRAVY -> PUT request
      await axios.put(
        `http://127.0.0.1:8000/classes/${classId}/notes/${editingNoteId.value}`,
        {
          title: newNoteData.value.title,
          content: newNoteData.value.content || '',
          subject: newNoteData.value.subject.trim(),
        },
        axiosConfig
      );
    } else {
      // REŽIM VYTVORENIA
      if (selectedFile.value) {
        // Ak používateľ vybral súbor, posielame FormData
        const formData = new FormData()
        formData.append("title", newNoteData.value.title)
        formData.append("content", newNoteData.value.content || '')
        formData.append("subject", newNoteData.value.subject.trim())
        formData.append("image", selectedFile.value)

        const multipartConfig = {
          headers: {
            ...axiosConfig.headers,
            "Content-Type": "multipart/form-data"
          }
        }

        await axios.post(
          `http://127.0.0.1:8000/classes/${classId}/notes-with-image`, 
          formData, 
          multipartConfig
        );
      } else {
        // Klasický POST bez obrázka (čistý JSON)
        await axios.post(
          `http://127.0.0.1:8000/classes/${classId}/notes`, 
          {
            title: newNoteData.value.title,
            content: newNoteData.value.content || '',
            subject: newNoteData.value.subject.trim(),
          }, 
          axiosConfig
        );
      }
    }

    isModalOpen.value = false
    await refreshSubjects()
    await selectSubject(newNoteData.value.subject.trim())
    
    // Reset hodnôt súboru
    selectedFile.value = null
    selectedFilePreview.value = ""

  } catch (error) {
    console.error("Chyba pri ukladaní poznámky:", error)
    // Ak backend vráti detailnú správu o chybe, zobrazíme ju, inak všeobecnú hlášku
    alert(error.response?.data?.detail || "Nepodarilo sa uložiť zmeny. Skontroluj konzolu servera.");
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

const openEditNoteModal = (note) => {
  isEditing.value = true
  editingNoteId.value = note.id
  selectedFile.value = null
  selectedFilePreview.value = ""
  
  newNoteData.value = {
    subject: note.subject,
    title: note.title,
    content: note.content
  }
  isModalOpen.value = true
}
</script>

<template>
  <div class="class-view">
    <header class="main-header">
      <div class="header-container">
        <button class="btn btn-back" @click="router.push('/my-classes')">Späť na prehľad</button>
        <h1>Trieda: {{ className }}</h1>    
      </div>
              
      <div>
        <button class="btn btn-schedule" @click="router.push(`/class/${classId}/schedule`)">
          Rozvrh
        </button>
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
                {{ note.content ? note.content.substring(0, 50) : '' }}{{ note.content && note.content.length > 50 ? '...' : '' }}
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
          <div class="note-detail-content-wrapper">
            <p class="note-detail-content">{{ activeNote.content }}</p>
            
            <div v-if="activeNote.image_path" class="note-image-preview-container" style="margin: 15px 0; text-align: left;">
              <img 
                :src="`http://127.0.0.1:8000/${activeNote.image_path}`" 
                alt="Príloha poznámky" 
                style="max-width: 100%; max-height: 350px; border-radius: 6px; border: 1px solid #333;"
              />
            </div>

            <button class="btn btn-edit" @click="openEditNoteModal(activeNote)">Upraviť</button>
          </div>
        </div>
      </main>
    </div>
  </div>

  <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
    <div class="modal-content">
      <h2>{{ isEditing ? 'Upraviť poznámku' : 'Pridať novú poznámku' }}</h2>
      <form @submit.prevent="handleAddNoteSubmit">
        <div class="form-group">
          <label>Predmet</label>
          <input type="text" v-model="newNoteData.subject" required />
        </div>
        <div class="form-group">
          <label>Titulok poznámky</label>
          <input type="text" v-model="newNoteData.title" required />
        </div>
        <div class="form-group">
          <label>Obsah</label>
          <textarea v-model="newNoteData.content" rows="6"></textarea>
        </div>
        
        <div class="modal-actions">
          <div>
            <input 
              type="file" 
              ref="fileInputRef" 
              style="display: none;" 
              accept="image/*" 
              @change="onFileSelected"
            />
            
            <button 
              v-if="!isEditing"
              type="button" 
              title="Pridať prílohu (obrázok)" 
              @click="triggerFileSelect"
              style="background-color: transparent; border: none; cursor: pointer; padding: 5px;"
            >
              <span class="material-icons" style="font-size: 24px; color: #b3b3b3;">attach_file</span>
            </button>
          </div>
          
          <button type="button" class="btn btn-cancel" @click="isModalOpen = false">Zrušiť</button>
          <button type="submit" class="btn btn-submit">{{ isEditing ? 'Uložiť zmeny' : 'Vytvoriť' }}</button>        
        </div>

        <div v-if="selectedFilePreview" style="font-size: 13px; color: #5d5dff; margin-top: 10px; text-align: left;">
          📎 Vybraný súbor: <strong>{{ selectedFilePreview }}</strong>
        </div>
      </form>
    </div>
  </div>
</template>

<style src="@/assets/classView.css"></style>