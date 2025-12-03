<template>
  <div :class="['main-wrapper', { 'dark-mode': isDarkMode }]">
    
    <button class="theme-toggle" @click="toggleTheme" title="Cambiar Tema">
      {{ isDarkMode ? '☀️ Modo Claro' : '🌙 Modo Oscuro' }}
    </button>

    <div class="container">
      <div class="card">
        <h1>MHealth Analyzer</h1>
        <p class="subtitle">Sistema de Reconocimiento de Actividad</p>

        <div class="upload-area" v-if="!loading && !result">
          <input type="file" @change="handleFileUpload" accept=".log,.txt" id="fileInput" />
          <label for="fileInput" class="upload-btn">
            📂 Seleccionar archivo .log
          </label>
          <p class="hint">Formatos aceptados: MHealth RAW Data</p>
        </div>

        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>Procesando sensores...</p>
        </div>

        <div v-if="result" class="result-box">
          
          <div class="winner-badge">
            <h3>Actividad Predominante</h3>
            <div class="big-text">{{ result.top_activity }}</div>
            <div class="confidence">Confianza: {{ result.confidence }}%</div>
          </div>

          <div class="stats-grid">
            <div class="stat-item">
              <span class="label">Muestras Totales</span>
              <span class="value">{{ result.total_samples }}</span>
            </div>
            <div class="stat-item">
              <span class="label">Duración Archivo</span>
              <span class="value">{{ result.total_duration }} seg</span>
            </div>
            <div class="stat-item">
              <span class="label">Ventana de Análisis</span>
              <span class="value">{{ result.window_duration }} seg</span>
            </div>
          </div>

          <div class="table-container">
            <h4>Detalle por Actividad</h4>
            <table>
              <thead>
                <tr>
                  <th>Actividad</th>
                  <th>Ventanas Detectadas</th>
                  <th>% Presencia</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in result.ranking" :key="index">
                  <td>{{ item.activity }}</td>
                  <td>{{ item.count }}</td>
                  <td>
                    <div class="progress-wrapper">
                      <span>{{ item.percentage }}%</span>
                      <div class="progress-bar">
                        <div class="fill" :style="{ width: item.percentage + '%' }"></div>
                      </div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <button @click="reset" class="retry-btn">Analizar otro archivo</button>
        </div>

        <div v-if="error" class="error">
          ⚠️ {{ error }}
          <br>
          <button @click="reset" class="retry-btn-small">Intentar de nuevo</button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      loading: false,
      result: null,
      error: null,
      file: null,
      isDarkMode: false
    };
  },
  methods: {
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode;
    },
    async handleFileUpload(event) {
      this.file = event.target.files[0];
      if (!this.file) return;

      this.loading = true;
      this.error = null;
      const formData = new FormData();
      formData.append('file', this.file);

      try {
        const response = await fetch('http://localhost:5000/detect', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Error del servidor');
        this.result = data;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
        // Limpiar input para permitir subir el mismo archivo de nuevo si se desea
        event.target.value = '';
      }
    },
    reset() {
      this.result = null;
      this.error = null;
      this.file = null;
    }
  }
};
</script>

<style>
/* --- RESET & BASE --- */
body, html { margin: 0; padding: 0; height: 100%; font-family: 'Segoe UI', sans-serif; }

/* Wrapper principal que controla el tema */
.main-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
  color: #333;
  transition: background 0.3s, color 0.3s;
}

/* --- MODO OSCURO --- */
.main-wrapper.dark-mode {
  background-color: #121212;
  color: #e0e0e0;
}
.main-wrapper.dark-mode .card {
  background-color: #1e1e1e;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}
.main-wrapper.dark-mode h1, 
.main-wrapper.dark-mode h3,
.main-wrapper.dark-mode h4 { color: #ffffff; }
.main-wrapper.dark-mode .subtitle,
.main-wrapper.dark-mode .label { color: #b0b0b0; }
.main-wrapper.dark-mode table th { background-color: #333; color: #fff; }
.main-wrapper.dark-mode table td { border-bottom: 1px solid #333; }
.main-wrapper.dark-mode .retry-btn { border-color: #555; color: #fff; }

/* --- UI COMPONENTS --- */
.theme-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: 2px solid currentColor;
  padding: 8px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: bold;
  color: inherit;
  opacity: 0.7;
}
.theme-toggle:hover { opacity: 1; }

.container { width: 100%; max-width: 600px; padding: 20px; }

.card {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  text-align: center;
  transition: background 0.3s;
}

h1 { margin: 0; color: #2c3e50; }
.subtitle { color: #7f8c8d; margin-bottom: 2rem; }
.hint { font-size: 0.8rem; color: #999; margin-top: 10px; }

.upload-btn {
  background: #3b82f6;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: inline-block;
  transition: transform 0.2s;
}
.upload-btn:hover { transform: translateY(-2px); background: #2563eb; }
input[type="file"] { display: none; }

/* --- RESULTADOS --- */
.winner-badge {
  background: rgba(59, 130, 246, 0.1);
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 20px;
  border: 1px solid rgba(59, 130, 246, 0.3);
}
.big-text { font-size: 1.8rem; font-weight: bold; color: #3b82f6; margin: 10px 0; }
.confidence { font-weight: bold; font-size: 0.9rem; opacity: 0.8; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 25px;
}
.stat-item {
  background: rgba(0,0,0,0.05);
  padding: 10px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}
.main-wrapper.dark-mode .stat-item { background: rgba(255,255,255,0.05); }

.stat-item .label { font-size: 0.75rem; margin-bottom: 4px; }
.stat-item .value { font-weight: bold; font-size: 1rem; }

/* --- TABLA --- */
.table-container { margin-bottom: 20px; text-align: left; }
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f8f9fa; font-weight: 600; color: #555; }

.progress-wrapper { display: flex; align-items: center; gap: 10px; }
.progress-bar { flex-grow: 1; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; }
.fill { height: 100%; background: #10b981; }

.retry-btn {
  background: transparent;
  border: 1px solid #ccc;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  color: inherit;
  font-weight: 600;
}
.retry-btn:hover { background: rgba(0,0,0,0.05); }

/* --- LOADING SPINNER --- */
.spinner {
  border: 4px solid rgba(0,0,0,0.1);
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 40px; height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.error { color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 8px; }
.retry-btn-small { margin-top: 5px; cursor: pointer; }
</style>