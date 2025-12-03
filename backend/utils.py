import numpy as np
import pandas as pd
from scipy import stats

# Configuración de ventanas (2.56 segundos aprox a 50Hz)
WINDOW_SIZE = 128 
STEP_SIZE = 64  # 50% overlap

def create_windows(X, y, time_steps=1, step=1):
    Xs, ys = [], []
    for i in range(0, len(X) - time_steps, step):
        v = X.iloc[i:(i + time_steps)].values
        # Aquí extraemos características estadísticas para hacer el modelo robusto y ligero
        # Media y Desviación estándar de cada sensor en la ventana
        features = np.concatenate([np.mean(v, axis=0), np.std(v, axis=0)])
        Xs.append(features)
        # Tomamos la etiqueta más frecuente en esta ventana (Moda)
        ys.append(stats.mode(y.iloc[i:(i + time_steps)])[0])
    return np.array(Xs), np.array(ys).reshape(-1)

def preprocess_input(df):
    # Asumimos que el archivo viene sin headers (formato MHealth)
    # Las columnas 23 es la etiqueta. Las anteriores son sensores.
    # Filtramos la actividad 0 (Null/Nada)
    df = df[df.iloc[:, -1] != 0]
    return df