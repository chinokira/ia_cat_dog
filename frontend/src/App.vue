<template>
  <div id="app">
    <header class="header">
      <div class="container">
        <h1>🐱🐶 Cat & Dog Classifier</h1>
        <p>Upload une image pour découvrir si c'est un chat ou un chien!</p>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <ImageUploader @prediction="handlePrediction" />
        <PredictionResult v-if="prediction" :prediction="prediction" />
      </div>
    </main>

    <footer class="footer">
      <div class="container text-center">
        <p>Powered by TensorFlow & MobileNetV2</p>
      </div>
    </footer>
  </div>
</template>

<script>
import ImageUploader from './components/ImageUploader.vue'
import PredictionResult from './components/PredictionResult.vue'

export default {
  name: 'App',
  components: {
    ImageUploader,
    PredictionResult
  },
  data() {
    return {
      prediction: null
    }
  },
  methods: {
    handlePrediction(result) {
      this.prediction = result
    }
  }
}
</script>

<style scoped>
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem 0;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.main {
  flex: 1;
  padding: 3rem 0;
}

.footer {
  background-color: #f3f4f6;
  padding: 2rem 0;
  margin-top: 4rem;
  border-top: 1px solid var(--border-color);
}

.footer p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}
</style>
