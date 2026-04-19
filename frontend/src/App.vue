<script setup>
//toogle register
import { ref, reactive } from 'vue'
import axios from 'axios'

const showRegister = ref(false)
const showLogin = ref(false)

const switchToRegister = () => {
  showLogin.value = false;    
  showRegister.value = true;  
}
const switchToLogin = () => {
  showRegister.value = false;    
  showLogin.value = true;  
}
const toggleRegister = () => {
  showRegister.value = !showRegister.value
}
const toggleLogin = () => {
  showLogin.value = !showLogin.value
}

const registerData = reactive({
  username: '',
  email: '',
  password: '',
  again_password: ''
})

const handleRegister = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/register', {
      username: registerData.username,
      email: registerData.email,
      password: registerData.password,
      again_password: registerData.again_password
    })
    
    alert(response.data.message) 
    toggleRegister() 
    
    
    registerData.username = ''
    registerData.email = ''
    registerData.password = ''
    registerData.again_password = ''
    
  } catch (error) {
    
    alert(error.response?.data?.detail || "Niečo sa pokazilo")
  }
}

const loginData = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/login', {
      username: loginData.username,
      password: loginData.password
    })

    localStorage.setItem('token', response.data.access_token)
    localStorage.setItem('user_id', response.data.user_id)

    alert("Prihlásenie úspešné!")
    
    toggleLogin() 
    
    

  } catch (error) {
    alert(error.response?.data?.detail || "Nesprávne meno alebo heslo")
  }
}
</script>

<template>
  <div class="landing-page">
    
    <header class="main-header">
      <div class="container">
        <div class="logo-area">
          <img src="@/assets/icon.webp" alt="Notes logo" class="notes-logo" />
          <h1 class="notes-title">Notes</h1>
        </div>
        
        <div class="nav-buttons">
          <button class="btn btn-login" @click="toggleLogin" >Login</button>
          <button class="btn btn-register" @click="toggleRegister" >Register</button>
        </div>
      </div>
    </header>

    <main class="hero">
      <div class="container hero-content">
        <div class="hero-text-area">
          <h2 class="hero-title">Všetko pre tvoju triedu na jednom mieste.</h2>
          <p class="hero-description">
            Organizuj si rozvrh, zdieľaj poznámky a spolupracuj so spolužiakmi jednoducho a rýchlo.
          </p>
        </div>
        
        <div class="hero-image-area">
          <img src="@/assets/notes.png" alt="Sticky notes" class="sticky-notes-img" />
        </div>
      </div>
    </main>
    
    <footer class="main-footer">
       <div class="container footer-center">
        Noha
      </div>
    </footer>
    <!-- --- REGISTER  --- -->
    <div v-if="showRegister " class="modal-overlay" @click.self ="toggleRegister">
      <div class="modal-content">
        <div class="register">
          <div class="register_form">
            <h1>Register</h1>
            <div class="register_form_login">
              <p>Already have an account ?</p>
              <div class="register_form_login_button">
                <p> Login</p>
                <button  @click= "switchToLogin ">here</button>
              </div>
          
            </div>
          </div>
      
          <input v-model="registerData.username" type="text" placeholder="Username" class="Username">
          <input v-model="registerData.email" type="email" placeholder="E-mail" class="E-mail">
          <input v-model="registerData.password" type="password" placeholder="Password" class="Password">
          <input v-model="registerData.again_password" type="password" placeholder="Confirm password" class="ConfirmPassword">

          <button class="btn btn-register" @click="handleRegister" >Register</button>

          <button class="close-btn" @click="toggleRegister">✕</button>
        </div>
      </div>
    </div>
    <!-- end of register -->

    <!-- --- LOGIN  --- -->
     <div v-if="showLogin" class="modal-overlay" @click.self="toggleLogin">
      <div class="modal-content">
        <div class="login">
          <div class="login_form">
            <h1>Login</h1>
              <div class="register_form_login">
                <p>Don't have an account ?</p>
                <div class="register_form_login_button">
                  <p> Register</p>
                  <button  @click= "switchToRegister ">here</button>
                </div>
            </div>
          </div>

          <input v-model="loginData.username" type="text" placeholder="Username" class="Username_Login">
          <input v-model="loginData.password" type="password" placeholder="Password" class="Password_Login">
  
          <button class="btn btn-login" @click="handleLogin">Login</button>
          
           <button class="close-btn" @click="toggleLogin">✕</button>

        </div>
      </div>
    </div>

  </div>
</template>

<style src="@/assets/base.css"></style>