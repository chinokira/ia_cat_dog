<template>
  <div class="image-uploader card">
    <h2 class="mb-3">Upload une image</h2>

    <!-- Zone de drop -->
    <div
      class="drop-zone"
      :class="{ 'drop-zone-active': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="$refs.fileInput.click()"
    >
      <div v-if="!previewUrl" class="drop-zone-content">
        <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="drop-zone-text">Clique ou glisse une image ici</p>
        <p class="drop-zone-subtext">JPG, PNG, GIF jusqu'à 10MB</p>
      </div>

      <!-- Prévisualisation de l'image -->
      <div v-else class="preview-container">
        <img :src="previewUrl" alt="Preview" class="preview-image" />
        <button @click.stop="clearImage" class="clear-btn">✕</button>
      </div>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      @change="handleFileSelect"
      style="display: none"
    />

    <!-- Bouton de prédiction -->
    <button
      v-if="selectedFile"
      @click="predictImage"
      :disabled="loading"
      class="btn btn-primary mt-3"
      style="width: 100%"
    >
      <span v-if="!loading">🔮 Prédire</span>
      <span v-else>⏳ Analyse en cours...</span>
    </button>

    <!-- Messages d'erreur -->
    <div v-if="error" class="error-message mt-2">
      ⚠️ {{ error }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default {
  name: 'ImageUploader',
  data() {
    return {
      selectedFile: null,
      previewUrl: null,
      isDragging: false,
      loading: false,
      error: null
    }
  },
  methods: {
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.processFile(file)
      }
    },
    handleDrop(event) {
      this.isDragging = false
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        this.processFile(file)
      } else {
        this.error = 'Le fichier doit être une image'
      }
    },
    processFile(file) {
      // Vérifier la taille (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        this.error = 'L\'image est trop grande (max 10MB)'
        return
      }

      this.selectedFile = file
      this.error = null

      // Créer la prévisualisation
      const reader = new FileReader()
      reader.onload = (e) => {
        this.previewUrl = e.target.result
      }
      reader.readAsDataURL(file)
    },
    clearImage() {
      this.selectedFile = null
      this.previewUrl = null
      this.error = null
      this.$refs.fileInput.value = ''
    },
    async predictImage() {
      if (!this.selectedFile) return

      this.loading = true
      this.error = null

      try {
        const formData = new FormData()
        formData.append('file', this.selectedFile)

        const response = await axios.post(`${API_URL}/predict`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data.success) {
          this.$emit('prediction', response.data.prediction)
        } else {
          this.error = 'Erreur lors de la prédiction'
        }
      } catch (err) {
        console.error('Erreur:', err)
        this.error = err.response?.data?.detail || 'Impossible de se connecter au serveur'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.image-uploader h2 {
  font-size: 1.5rem;
  color: var(--text-color);
}

.drop-zone {
  border: 3px dashed var(--border-color);
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fafafa;
  position: relative;
}

.drop-zone:hover {
  border-color: var(--primary-color);
  background-color: #f0f0f0;
}

.drop-zone-active {
  border-color: var(--primary-color);
  background-color: #eef2ff;
}

.drop-zone-content {
  pointer-events: none;
}

.upload-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
  color: var(--text-secondary);
}

.drop-zone-text {
  font-size: 1.1rem;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.drop-zone-subtext {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.preview-container {
  position: relative;
  max-width: 100%;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  object-fit: contain;
}

.clear-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.clear-btn:hover {
  background: rgba(0, 0, 0, 0.9);
}

.error-message {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}
</style>
