import os
import requests
import zipfile
import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from utils import create_windows, preprocess_input, WINDOW_SIZE, STEP_SIZE

# Configuración
DATA_URL = 'https://archive.ics.uci.edu/static/public/319/mhealth+dataset.zip'
DATA_DIR = 'data'
MODEL_PATH = 'model/classifier.pkl'

def download_and_extract():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    zip_path = os.path.join(DATA_DIR, 'dataset.zip')
    
    # Solo descargar si no existe el zip
    if not os.path.exists(zip_path):
        print(f"Descargando dataset desde {DATA_URL}...")
        try:
            r = requests.get(DATA_URL)
            with open(zip_path, 'wb') as f:
                f.write(r.content)
            print("Descarga completada.")
        except Exception as e:
            raise Exception(f"Error descargando: {e}")

    # Intentar descomprimir
    print("Descomprimiendo...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
    except zipfile.BadZipFile:
        raise Exception("El archivo descargado no es un ZIP válido.")

    # --- DIAGNÓSTICO: IMPRIMIR ESTRUCTURA DE ARCHIVOS ---
    print("\n--- DIAGNÓSTICO DE CARPETAS ---")
    log_files_found = []
    for root, dirs, files in os.walk(DATA_DIR):
        print(f"Carpeta: {root}")
        for f in files:
            # Imprimimos los primeros 5 archivos de cada carpeta para no saturar
            if len(files) < 5 or f in files[:5]:
                print(f"  - {f}")
            
            # Búsqueda agresiva: Cualquier archivo .log
            if f.endswith('.log'):
                log_files_found.append(os.path.join(root, f))
    print("-------------------------------\n")

    if not log_files_found:
        raise Exception("ERROR CRÍTICO: No se encontraron archivos .log en ninguna subcarpeta de 'data'.")

    # Tomamos la carpeta del primer archivo log encontrado
    target_dir = os.path.dirname(log_files_found[0])
    print(f"Target detectado: {target_dir}")
    return target_dir

def train():
    try:
        data_path = download_and_extract()
        
        # Listar archivos en la carpeta detectada
        files = [f for f in os.listdir(data_path) if f.endswith('.log')]
        files.sort()
        
        print(f"Archivos .log disponibles: {len(files)}")
        
        all_X = []
        all_y = []

        # Usamos los primeros 3 archivos para verificar que funciona
        # IMPORTANTE: Si esto funciona, para el modelo final cambia [:3] por [:]
        files_to_process = files[:3] 

        for file in files_to_process: 
            print(f"Procesando {file}...")
            full_path = os.path.join(data_path, file)
            
            try:
                df = pd.read_csv(full_path, sep='\t', header=None)
                
                # Validación simple de contenido
                if df.shape[1] < 23:
                    print(f"  -> Saltando {file} (Formato incorrecto, columnas: {df.shape[1]})")
                    continue

                df = preprocess_input(df)
                
                if df.empty: 
                    continue

                X_raw = df.iloc[:, :-1]
                y_raw = df.iloc[:, -1]

                X_win, y_win = create_windows(X_raw, y_raw, WINDOW_SIZE, STEP_SIZE)
                
                if len(X_win) > 0:
                    all_X.append(X_win)
                    all_y.append(y_win)
            except Exception as e:
                print(f"  -> Error en {file}: {e}")

        if not all_X:
            raise Exception("No hay datos suficientes para entrenar.")

        X_final = np.concatenate(all_X)
        y_final = np.concatenate(all_y)

        print(f"Entrenando modelo con {X_final.shape[0]} ventanas...")
        X_train, X_test, y_train, y_test = train_test_split(X_final, y_final, test_size=0.2, random_state=42)

        clf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
        clf.fit(X_train, y_train)

        print("\n--- REPORTE ---")
        print(classification_report(y_test, clf.predict(X_test)))

        if not os.path.exists('model'):
            os.makedirs('model')
        joblib.dump(clf, MODEL_PATH)
        print(f"MODELO GUARDADO EXITOSAMENTE EN: {MODEL_PATH}")

    except Exception as e:
        print(f"\n❌ ERROR FINAL: {e}")

if __name__ == "__main__":
    train()