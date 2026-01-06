<template>
  <div class="prediction-result card mt-4">
    <h2 class="mb-3">Résultat</h2>

    <div class="result-content">
      <!-- Icône et classe prédite -->
      <div class="prediction-main">
        <div class="icon-container">
          <span class="prediction-icon">{{ getIcon(prediction.predicted_class) }}</span>
        </div>
        <h3 class="prediction-class">{{ getLabel(prediction.predicted_class) }}</h3>
        <div class="confidence-badge" :class="getConfidenceClass(prediction.confidence)">
          {{ formatPercentage(prediction.confidence) }} de confiance
        </div>
      </div>

      <!-- Scores détaillés -->
      <div class="scores-section mt-4">
        <h4 class="mb-2">Scores détaillés</h4>
        <div class="scores-list">
          <div
            v-for="(score, className) in prediction.all_scores"
            :key="className"
            class="score-item"
          >
            <div class="score-header">
              <span class="score-label">
                {{ getIcon(className) }} {{ getLabel(className) }}
              </span>
              <span class="score-value">{{ formatPercentage(score) }}</span>
            </div>
            <div class="score-bar-container">
              <div
                class="score-bar"
                :style="{ width: `${score * 100}%` }"
                :class="{ 'score-bar-active': className === prediction.predicted_class }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PredictionResult',
  props: {
    prediction: {
      type: Object,
      required: true
    }
  },
  methods: {
    getIcon(className) {
      const icons = {
        'cat': '🐱',
        'dog': '🐶'
      }
      return icons[className] || '❓'
    },
    getLabel(className) {
      const labels = {
        'cat': 'Chat',
        'dog': 'Chien'
      }
      return labels[className] || className
    },
    formatPercentage(value) {
      return `${(value * 100).toFixed(1)}%`
    },
    getConfidenceClass(confidence) {
      if (confidence >= 0.9) return 'confidence-high'
      if (confidence >= 0.7) return 'confidence-medium'
      return 'confidence-low'
    }
  }
}
</script>

<style scoped>
.prediction-result h2 {
  font-size: 1.5rem;
  color: var(--text-color);
}

.result-content {
  text-align: center;
}

.prediction-main {
  padding: 2rem 0;
}

.icon-container {
  margin-bottom: 1rem;
}

.prediction-icon {
  font-size: 5rem;
  display: inline-block;
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.prediction-class {
  font-size: 2rem;
  color: var(--text-color);
  margin-bottom: 1rem;
  font-weight: 700;
}

.confidence-badge {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 1rem;
}

.confidence-high {
  background-color: #d1fae5;
  color: #065f46;
}

.confidence-medium {
  background-color: #fef3c7;
  color: #92400e;
}

.confidence-low {
  background-color: #fee2e2;
  color: #991b1b;
}

.scores-section {
  background-color: #f9fafb;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: left;
}

.scores-section h4 {
  font-size: 1.1rem;
  color: var(--text-color);
  font-weight: 600;
}

.scores-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.score-item {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.score-label {
  font-size: 1rem;
  color: var(--text-color);
  font-weight: 500;
}

.score-value {
  font-size: 1rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.score-bar-container {
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.score-bar {
  height: 100%;
  background: linear-gradient(90deg, #93c5fd, #3b82f6);
  transition: width 0.6s ease-out;
  border-radius: 4px;
}

.score-bar-active {
  background: linear-gradient(90deg, #86efac, #10b981);
}
</style>
