# Intención de compra en e-commerce · ML + Streamlit + Docker + GCP

Solución completa de Machine Learning, del dataset al despliegue: un modelo que estima si una sesión de navegación en una tienda online terminará en compra, servido con Streamlit dentro de un contenedor Docker en una máquina virtual de Google Cloud.

**Ruta elegida: A — aprendizaje supervisado (clasificación binaria).**

---

## 1. Objetivo

Predecir, a partir del comportamiento de un visitante durante su sesión, la probabilidad de que la sesión termine en una compra. Un equipo de marketing puede usar esa probabilidad para decidir a qué sesiones mostrar un incentivo (cupón, chat de ayuda, recordatorio de carrito).

## 2. Dataset

| | |
|---|---|
| Nombre | Online Shoppers Purchasing Intention Dataset |
| Fuente | Sakar, C. O., Polat, S. O., Katircioglu, M., & Kastro, Y. (2019). *Neural Computing and Applications*, 31, 6893–6908. Repositorio UCI ML (id 468) |
| Archivo | `data/online_shoppers_intention.csv` (incluido en el repo, datos públicos y anónimos) |
| Tamaño | 12 330 filas × 18 columnas, sin valores faltantes |
| **Unidad de observación** | **Una fila = una sesión de navegación** de un usuario en la tienda, durante un año. Cada sesión pertenece a un usuario distinto. |
| Variable objetivo | `Revenue` — `True` si la sesión terminó en compra |
| Balance de clases | 15,5 % compra · 84,5 % no compra (desbalanceado) |

## 3. Variables utilizadas

**Numéricas (comportamiento de la sesión)**

| Variable | Significado |
|---|---|
| `Administrative`, `Informational`, `ProductRelated` | Número de páginas visitadas de cada tipo (cuenta, información, producto) |
| `*_Duration` | Segundos totales en cada tipo de página |
| `BounceRates` | Tasa de rebote promedio de las páginas visitadas |
| `ExitRates` | Tasa de salida promedio de las páginas visitadas |
| `PageValues` | Valor de página promedio según Google Analytics |
| `SpecialDay` | Cercanía a una fecha especial (0 = lejos, 1 = el día clave; p. ej. San Valentín) |

**Categóricas (contexto)**: `Month`, `VisitorType` (nuevo, recurrente, otro), `Weekend`.

**Excluidas**: `OperatingSystems`, `Browser`, `Region`, `TrafficType`. Son códigos enteros anónimos sin etiqueta; una persona no podría llenarlos con sentido en la app, y tratarlos como números sería incorrecto.

**Riesgo de fuga revisado — `PageValues`**: Google Analytics calcula el valor de una página con el historial de transacciones de todo el sitio, y lo asigna a las páginas que suelen preceder a una compra. Es información disponible durante la sesión, por eso se conserva. Como es la variable más fuerte, `train.py` reporta también el desempeño **sin** ella (ROC-AUC 0,76 frente a 0,93) para que se vea cuánto depende el modelo de esa variable.

## 4. Preparación de datos

Todo vive dentro de un único `Pipeline` de scikit-learn, de modo que la app aplica exactamente las mismas transformaciones que el entrenamiento:

- **Numéricas**: imputación por mediana → `log1p` (las duraciones y conteos son muy asimétricos) → `StandardScaler`.
- **Categóricas**: imputación por moda → `OneHotEncoder(handle_unknown="ignore")`.
- Partición 80 / 20 estratificada (`random_state=42`).

## 5. Modelo y justificación

Se comparan dos modelos con validación cruzada estratificada de 5 pliegues **solo sobre entrenamiento**, usando F1 de la clase "compra":

| Modelo | F1 (CV) |
|---|---|
| Regresión logística (`class_weight="balanced"`) | 0,665 |
| **Random forest** (300 árboles, `min_samples_leaf=5`, `class_weight="balanced"`) | **0,668** ← elegido |

Ambos usan `class_weight="balanced"` para que la clase minoritaria (compra) pese lo mismo que la mayoritaria. El random forest captura interacciones (p. ej. muchas páginas de producto **y** baja tasa de salida) sin tener que construirlas a mano.

## 6. Evaluación (conjunto de prueba, 2 466 sesiones nunca vistas)

| Métrica | Valor |
|---|---|
| ROC-AUC | **0,928** |
| PR-AUC | 0,728 (la línea base al azar sería 0,155) |
| Recall de compra | **77,5 %** |
| Precisión de compra | 53,9 % |
| F1 de compra | 0,636 |
| F1 ponderado | 0,872 |

Matriz de confusión (umbral 0,5):

| | Predicho: no compra | Predicho: compra |
|---|---|---|
| **Real: no compra** | 1 831 | 253 |
| **Real: compra** | 86 | 296 |

**Por qué estas métricas.** Con 84,5 % de sesiones sin compra, un modelo que diga siempre "no compra" tendría 84,5 % de accuracy y sería inútil. Por eso se priorizan el **recall** y el **F1 de la clase compra**, y el **ROC-AUC / PR-AUC** para medir la capacidad de ordenar sesiones por probabilidad. Para un incentivo de marketing es preferible detectar 3 de cada 4 compradores potenciales aunque algunos avisos lleguen a quien no compraría.

Las métricas completas quedan en `metrics.json` cada vez que se entrena.

## 7. Interpretación de la salida

La app muestra:

- **Clase predicha**: "Compra" si la probabilidad ≥ 0,5; si no, "No compra".
- **Probabilidad de compra**: promedio de las probabilidades que asignan los 300 árboles (entrenados con pesos balanceados). Sirve para ordenar sesiones: una de 0,90 merece más atención que una de 0,55.

Las sesiones con `PageValues` alto, muchas páginas de producto y tasas de salida bajas reciben probabilidades altas; las sesiones de rebote rápido, probabilidades cercanas a cero.

## 8. Estructura del proyecto

```
intencion-compra-streamlit/
├── app.py                  # Interfaz Streamlit (carga model.joblib, no reentrena)
├── train.py                # Entrenamiento reproducible → model.joblib + metrics.json
├── model.joblib            # Pipeline entrenado + metadatos para la interfaz
├── metrics.json            # Métricas de la última ejecución de train.py
├── requirements.txt        # Dependencias con versiones fijas (las usa Docker)
├── requirements-dev.txt    # requirements + pytest
├── Dockerfile
├── .dockerignore
├── data/
│   └── online_shoppers_intention.csv
├── notebooks/
│   └── 01_desarrollo_colab.ipynb   # Exploración, entrenamiento y prueba de la app en Colab
├── tests/
│   └── test_app.py         # Pruebas del artefacto y de la app con 3 casos
└── docs/
    ├── GUIA_PASO_A_PASO.md        # Todo el reto, de Colab a GCP
    ├── prueba_cruzada.md          # Formato para registrar la prueba con otra pareja
    └── preguntas_discusion.md     # Respuestas preparadas para la discusión final
```

## 9. Cómo ejecutar `train.py`

```bash
pip install -r requirements.txt
python train.py
```

Salida esperada: el F1 de validación cruzada de cada modelo, el reporte de clasificación y la línea `Modelo guardado en model.joblib`. Tarda menos de un minuto.

## 10. Cómo ejecutar Streamlit (sin Docker)

```bash
streamlit run app.py
```

Abrir `http://localhost:8501`.

**En Google Colab**: abrir `notebooks/01_desarrollo_colab.ipynb` (botón "Open in Colab" o `Archivo → Abrir cuaderno → GitHub`) y ejecutar las celdas en orden; la sección 5 levanta la app y crea un túnel temporal.

## 11. Cómo construir la imagen Docker

Dentro de la carpeta del repositorio (en la VM de GCP):

```bash
docker build -t intencion-compra-app .
docker images            # debe aparecer intencion-compra-app
```

## 12. Cómo ejecutar el contenedor

```bash
# Prueba interactiva (Ctrl+C para detener)
docker run --rm -p 8501:8501 intencion-compra-app

# En segundo plano, se reinicia solo si la VM se reinicia
docker run -d --name intencion-compra --restart unless-stopped -p 8501:8501 intencion-compra-app

docker ps
docker logs intencion-compra
```

Abrir `http://IP_EXTERNA_DE_LA_VM:8501` (requiere la regla de firewall del puerto 8501; ver `docs/GUIA_PASO_A_PASO.md`, fase 4).

**Actualizar tras cambios en GitHub:**

```bash
git pull
docker stop intencion-compra && docker rm intencion-compra
docker build -t intencion-compra-app .
docker run -d --name intencion-compra --restart unless-stopped -p 8501:8501 intencion-compra-app
```

## 13. Ejemplo de entrada y salida

En la app, el selector **"Cargar un caso de ejemplo"** llena estos valores:

| Variable | Sesión con alta intención | Sesión de rebote rápido |
|---|---|---|
| Administrative / Duration | 3 / 80 s | 0 / 0 s |
| Informational / Duration | 1 / 30 s | 0 / 0 s |
| ProductRelated / Duration | 35 / 1 400 s | 2 / 15 s |
| BounceRates | 0,000 | 0,200 |
| ExitRates | 0,012 | 0,200 |
| PageValues | 40,0 | 0,0 |
| SpecialDay | 0,0 | 0,0 |
| Month | Nov | May |
| VisitorType | New_Visitor | Returning_Visitor |
| Weekend | False | False |
| **Salida esperada** | **Compra — 94,5 %** | **No compra — 0,1 %** |

El caso "Valores típicos (mediana)" da **No compra — 3,2 %**.

## 14. Pruebas

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Verifican que `model.joblib` tiene los metadatos que usa la app y que la app responde sin errores a los tres casos de ejemplo.

## 15. Notas de reproducibilidad

- `requirements.txt` fija versiones: un `model.joblib` solo carga de forma confiable con la **misma versión de scikit-learn** con que se entrenó. Si cambia alguna versión, ejecute de nuevo `python train.py`.
- La imagen usa `python:3.12-slim`; el proyecto se probó con Python 3.12 y 3.13.
- `.dockerignore` deja fuera `data/`, `notebooks/`, `docs/` y `tests/`: el contenedor solo necesita `app.py`, `model.joblib` y las dependencias.
- **Costos en GCP**: al terminar, detenga o elimine la VM (`Compute Engine → Instancias de VM → Detener/Borrar`).

## 16. Autores

- Allison Loango — allison.loango@est.uexternado.edu.co
- *[Nombre de la pareja]*

Universidad Externado de Colombia · Ciencia de Datos
