<script setup>
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
          <button class="btn btn-login" >Lagin</button>
          <button class="btn btn-register">Register</button>
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

    <div class="register">
      <div class="register_form">
        <h1>Register</h1>
      <p>Already have an account ?</p>
       <p>  Login here</p>
      </div>
      
      <div class="Username">Username</div>
      <div class="E-mail">E-mail</div>
      <div class="Password">Password</div>
      <div class="ConfirmPassword">Confirm password</div>

      <Button>Register</Button>
    </div>
  </div>
</template>

<style scoped>
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background-color: #1e1e1e; /* Nastav rovnakú farbu ako má tvoj LandingView */
}

#app {
  margin: 0;
  padding: 0;
  max-width: none; /* Zruší obmedzenie šírky, ak tam nejaké ostalo */
}

.landing-page {
  font-family: 'Inter', Arial, sans-serif; /* Ak máš Inter font, inak Arial */
  min-height: 100vh;
  background-color: #1e1e1e;
  color: white;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
}

.container {
width: 100%; max-width: 1920px;  margin: 0 auto;
  padding: 0 60px; /* Okraje po bokoch, aby to nebolo nalepené na hrane */
  box-sizing: border-box;
  display: flex;
  justify-content: space-between;
  align-items: center;
}


.main-header {
  height: 80px;
  display: flex;
  align-items: center;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notes-logo {
  height: 35px;
  width: auto;
}

.notes-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.nav-buttons {
  display: flex;
  gap: 20px;
}

.btn {
  padding: 10px 24px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
  font-size: 15px;
}

.btn-login {
  background: transparent;
  color: white;
  border: 1px solid #444;
}

.btn-login:hover {
  background: rgba(255, 255, 255, 0.05);
}

.btn-register {
  background-color: #5d5dff; /* Fialová farba z tvojho dizajnu */
  color: white;
  border: none;
}

.btn-register:hover {
  background-color: #4b4bcf;
}

/* HERO SECTION */
.hero {
  flex: 1;
  display: flex;
  align-items: center;
}

.hero-content {
  margin-left: 100px;
  margin-right: 100px;
  display: flex;
  align-items: center;
  gap: 40px;
}

.hero-title {
  font-size: 48px;
  line-height: 1.2;
  margin-bottom: 24px;
  max-width: 500px;
}

.hero-description {
  font-size: 18px;
  color: #b0b0b0;
  line-height: 1.6;
  max-width: 450px;
}

.hero-image-area {
  display: flex;
  justify-content: flex-end;
}

.sticky-notes-img {
  max-width: 100%;
  height: auto;
}


.main-footer {
  padding: 40px 0;
}

.footer-center {
  justify-content: center;
  color: #666;
  font-size: 14px;
}
.register_form{
  display: flex;
  gap: 30px;
}
.register{
  display: flex;
  flex-direction: column;
  align-items: center;
}
.Username{
  border: 1px solid black;
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 15px;
}
.E-mail{
  border: 1px solid black;
  padding: 10px;
  border-radius: 15px;
  margin-bottom: 10px ;
}
.Password{
  border: 1px solid black;
  padding: 10px;
  border-radius: 15px;
  margin-bottom: 10px ;
}
.ConfirmPassword{
  border: 1px solid black;
  padding: 10px;
  border-radius: 15px;
  margin-bottom: 30px ;
}
</style>