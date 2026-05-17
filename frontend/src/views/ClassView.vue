<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// Get the class ID from the URL (e.g., if the URL is /classes/5)
const classId = route.params.id 

// State variables
const className = ref("Loading class...")
const subjects = ref([])
const notes = ref([])
const activeNote = ref(null)
const selectedSubject = ref("")
const loading = ref(true)

const token = localStorage.getItem('token')
const axiosConfig = { headers: { Authorization: `Bearer ${token}` } }

const loadPageData = async () => {
  try {
    // 1. Optional: Fetch class details to get the real name (if you have an endpoint for it)
    const classRes = await axios.get(`http://127.0.0.1:8000/classes/${classId}`, axiosConfig)
    className.value = classRes.data.name
    
    const subjectsRes = await axios.get(`http://127.0.0.1:8000/classes/${classId}/subjects`, axiosConfig)
    subjects.value = subjectsRes.data
  } catch (error) {
    console.error("Chyba:", error)
  } finally {
    loading.value = false;
  }
}

// Called when user clicks a subject
const selectSubject = async (subjName) => {
  selectedSubject.value = subjName
  activeNote.value = null // Reset active note view
  try {
    // Fetch notes filtered by this specific subject
    const notesRes = await axios.get(`http://127.0.0.1:8000/classes/${classId}/notes/${subjName}`, axiosConfig)
    notes.value = notesRes.data
  } catch (error) {
    console.error("Chyba pri načítaní poznámok:", error)
  }
}

async function addNote(){
    const token = localStorage.getItem('token'); // Tu je ten tvoj uložený kód!
    const response = await axios.post(
        `http://127.0.0.1:8000/classes/${classId}/notes`, 
        {
          title: "Yes",
          content: "maybe",
          subject: "Nonexd",
        }, // 1. Prázdne body (dáta)
        {
          headers: {
            Authorization: `Bearer ${token}` // 2. Konfigurácia s tokenom
          }
        });
    }

// Called when user clicks a specific note card
const setActiveNote = (note) => {
  activeNote.value = note
}

onMounted(() => {
  loadPageData()
})
</script>


<template>
  <header class="main-header">
    <div class="container">
        <button class="btn" @click="router.push('/my-classes')">Späť na prehľad</button>
        <h1>Trieda #{{ className }}</h1>
    </div>
  </header>
  
  <div v-if="loading" style="padding: 20px; text-align: center;">Načítavam...</div>

  <div v-else style="display: flex; height: calc(100vh - 70px); font-family: sans-serif;">
    
    <div style="width: 250px; border-right: 2px solid #ccc; background: #f9f9f9; padding: 15px; display: flex; flex-direction: column;">
        <div style="flex: 90%;">
            <h3 style="margin-top: 0; color: #333;">Predmety</h3>
            <div v-if="subjects.length === 0" style="color: #666; font-style: italic;">Zatiaľ žiadne predmety.</div>

            <ul style="list-style: none; padding: 0; margin: 0;">
              <li 
                v-for="subj in subjects" 
                :key="subj"
                @click="selectSubject(subj)"
                :style="{
                  padding: '10px',
                  marginBottom: '5px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  backgroundColor: selectedSubject === subj ? '#ddd' : 'transparent',
                  fontWeight: selectedSubject === subj ? 'bold' : 'normal'
                }"
              >
                {{ subj }}
              </li>
            </ul>
        </div>
        <div style="flex: 10%; align-content: center;">
            <button class="btn" @click="addNote()">Add note</button>
        </div>
      
      
    </div>

    <div style="flex: 1; display: flex; flex-direction: column; padding: 20px; overflow-y: auto;">
      
      <div v-if="selectedSubject" style="margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 20px;">
        <h3 style="margin-top: 0;">Poznámky pre: {{ selectedSubject }}</h3>
        <div v-if="notes.length === 0" style="color: #666;">V tomto predmete nie sú žiadne poznámky.</div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px;">
          <div 
            v-for="note in notes" 
            :key="note.id"
            @click="setActiveNote(note)"
            style="border: 1px solid #ccc; padding: 15px; border-radius: 6px; cursor: pointer; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"
          >
            <h4 style="margin: 0 0 10px 0; color: #007acc;">{{ note.title }}</h4>
            <p style="margin: 0; font-size: 0.9em; color: #555;">
              {{ note.content.substring(0, 50) }}{{ note.content.length > 50 ? '...' : '' }}
            </p>
          </div>
        </div>
      </div>
      
      <div v-else style="flex: 1; display: flex; align-items: center; justify-content: center; color: #999;">
        Vyber si predmet z ľavého menu pre zobrazenie poznámok.
      </div>

      <div v-if="activeNote" style="background: #fff8db; border-left: 4px solid #f1c40f; padding: 20px; border-radius: 4px;">
        <h2 style="margin-top: 0;">{{ activeNote.title }}</h2>
        <hr style="border: 0; border-top: 1px solid #e0d090; margin-bottom: 15px;" />
        <p style="white-space: pre-wrap; line-height: 1.6; color: #2c3e50;">{{ activeNote.content }}</p>
      </div>

    </div>

  </div>
</template>