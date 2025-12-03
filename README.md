# Proyecto Final --- Sistema de Reconocimiento de Actividad Humana (MHealth)

Este proyecto corresponde a una aplicación **Full-Stack** para desplegar
un modelo de *Machine Learning* capaz de reconocer actividades humanas
(caminar, trotar, sentarse, etc.) usando datos biométricos del dataset
**MHealth**.

El objetivo es demostrar el ciclo completo de Ingeniería de ML:
preprocesamiento de series de tiempo, entrenamiento de modelos y
despliegue en un entorno contenerizado con Docker.

------------------------------------------------------------------------

## 🚀 Arquitectura del Sistema

El sistema utiliza una arquitectura de microservicios basada en Docker:

### **1. Frontend (Vue.js 3)**

-   Interfaz limpia y responsiva (Dark Mode).
-   Permite subir archivos `.log`.

### **2. Backend (Flask, Python)**

-   Procesa el archivo.
-   Ejecuta el modelo.
-   Devuelve probabilidades y actividad predominante.

### **3. Modelo Predictivo**

-   Clasificador **Random Forest**.
-   Entrenado a partir de estadísticas temporales (media y desviación
    estándar).

------------------------------------------------------------------------

## 📦 Instalación y Despliegue

Requisitos: **Docker + Docker Compose**.

### **1. Clonar el repositorio**

``` bash
git clone https://github.com/VCornejo10/Py-Final---Taller-Integrado-de-Ciencias-de-Datos---Victor-Cornejo
cd "Py-Final---Taller-Integrado-de-Ciencias-de-Datos---Victor-Cornejo"
```

### **2. Entrenar el Modelo (Opcional)**

El dataset y el modelo se pudieron subir a github, pero en el caso que se quiera generar un nuevo modelo desde 0, estos son los pasos a seguir.

1.  Levantar el backend:

``` bash
docker-compose up -d backend
```

2.  Ejecutar el entrenamiento:

``` bash
docker-compose exec backend python model_train.py
```

Cuando aparezca el mensaje:

    ¡ÉXITO! Modelo guardado en model/classifier.pkl

el modelo estará listo.

### **3. Ejecutar todo el sistema**

``` bash
docker-compose down
docker-compose up --build
```

### **4. Acceder**

-   **Frontend:** http://localhost:8080\
-   **Backend (Health Check):** http://localhost:5000/health

------------------------------------------------------------------------

## 📁 Estructura del Proyecto

    .
    |-- backend/
    |   |-- data/
    |   |-- model/
    |   |-- app.py
    |   |-- model_train.py
    |   |-- utils.py
    |   |-- Dockerfile
    |-- frontend/
    |   |-- src/
    |   |-- Dockerfile
    |   |-- package.json
    |-- prompts/
    |-- docker-compose.yml
    |-- README.md

------------------------------------------------------------------------

## 🧪 Cómo Probar el Sistema

1.  Abrir la aplicación web.\
2.  Subir un archivo `.log` del dataset MHealth.\
3.  Recibirás:
    -   Actividad predominante.
    -   Ranking de probabilidades.
    -   Estadísticas temporales.

> Acepta archivos con **23 columnas** (solo sensores) o **24 columnas**
> (sensores + etiqueta).

------------------------------------------------------------------------

## 🤖 Uso de IA Generativa

La carpeta `prompts/` registra el uso de herramientas de IA en la
generación de código y documentación, siguiendo los requisitos del
curso.

------------------------------------------------------------------------

**Desarrollado por Victor Cornejo --- Taller Integrador de Ciencia de
Datos (2025)**
