from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import numpy as np
from collections import Counter
from utils import create_windows, preprocess_input, WINDOW_SIZE, STEP_SIZE

app = Flask(__name__)
CORS(app)

# Frecuencia de muestreo del MHealth Dataset (50Hz = 50 muestras por segundo)
SAMPLING_RATE = 50 

try:
    model = joblib.load('model/classifier.pkl')
    print("Modelo cargado exitosamente.")
except:
    print("ADVERTENCIA: No se encontró el modelo.")
    model = None

ACTIVITIES = {
    0: "Null/Nada",
    1: "De pie (Standing)", 2: "Sentado (Sitting)", 3: "Acostado (Lying)",
    4: "Caminando (Walking)", 5: "Subiendo escaleras", 6: "Doblando cintura",
    7: "Elevación brazos frontal", 8: "Flexión rodillas", 9: "Ciclismo",
    10: "Trotar (Jogging)", 11: "Corriendo (Running)", 12: "Saltando"
}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/detect', methods=['POST'])
def detect_activity():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # 1. Leer archivo
        df = pd.read_csv(file, sep='\t', header=None)
        
        # Validación de columnas (Fix anterior)
        if df.shape[1] >= 23:
            X_raw = df.iloc[:, :23] 
        else:
            return jsonify({"error": f"El archivo tiene solo {df.shape[1]} columnas. Se requieren 23."}), 400

        # --- CÁLCULOS DE TIEMPO ---
        total_samples = len(X_raw)
        total_duration_sec = total_samples / SAMPLING_RATE
        # --------------------------

        # 2. Ventaneo
        dummy_y = pd.Series(np.zeros(len(X_raw))) 
        X_win, _ = create_windows(X_raw, dummy_y, WINDOW_SIZE, WINDOW_SIZE) 

        if len(X_win) == 0:
             return jsonify({"error": "Archivo muy corto (menos de 2.56 seg)"}), 400

        # 3. Predicción
        predictions = model.predict(X_win)
        
        # 4. Generar Ranking (Tabla de resultados)
        counts = Counter(predictions)
        total_preds = sum(counts.values())
        
        ranking = []
        for act_code, count in counts.items():
            percentage = round((count / total_preds) * 100, 1)
            ranking.append({
                "activity": ACTIVITIES.get(int(act_code), "Desconocido"),
                "count": count, # Cuantas ventanas se clasificaron así
                "percentage": percentage
            })
        
        # Ordenar de Mayor a Menor porcentaje
        ranking.sort(key=lambda x: x['percentage'], reverse=True)

        # La actividad ganadora es la primera del ranking
        top_activity = ranking[0]

        return jsonify({
            "top_activity": top_activity['activity'],
            "confidence": top_activity['percentage'],
            "total_samples": total_samples,
            "total_duration": round(total_duration_sec, 2),
            "window_duration": round(WINDOW_SIZE / SAMPLING_RATE, 2), # Cuantos segs dura cada ventana de análisis
            "ranking": ranking
        })

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)