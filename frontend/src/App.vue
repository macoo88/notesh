<script setup>
//toogle register
import { ref } from 'vue'

const showRegister = ref(false)

const toggleRegister = () => {
  showRegister.value = !showRegister.value
}
//

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
          <button class="btn btn-login" >Login</button>
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

    <div v-if="showRegister " class="modal-overlay" @click.self ="toggleRegister">
      <div class="modal-content">
        <div class="register">
          <div class="register_form">
            <h1>Register</h1>
            <div class="register_form_login">
              <p>Already have an account ?</p>
              <div class="register_form_login_button">
                <p> Login</p>
                <button>here</button>
              </div>
          
            </div>
          </div>
      
          <input type="text" placeholder="Username" class="Username">
          <input type="email" placeholder="E-mail" class="E-mail">
          <input type="password" placeholder="Password" class="Password">
          <input type="password" placeholder="Confirm password" class="ConfirmPassword">

          <button class="btn btn-register" @click="toggleRegister" >Register</button>

          <button class="close-btn" @click="toggleRegister">✕</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style src="@/assets/base.css"></style>