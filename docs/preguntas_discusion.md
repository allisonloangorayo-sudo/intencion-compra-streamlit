# Preguntas para la discusión final — respuestas preparadas

Respuestas cortas, aplicadas a este proyecto.

**1. ¿Qué diferencia hay entre el notebook de experimentación y `train.py`?**
El notebook sirve para explorar: las celdas se pueden correr en cualquier orden y el estado queda en memoria. `train.py` es el procedimiento final, de principio a fin, en un solo comando (`python train.py`). Cualquiera lo puede ejecutar y obtiene el mismo `model.joblib` (semilla fija, mismos datos, mismas versiones).

**2. ¿Por qué guardar preprocesamiento y modelo en el mismo Pipeline?**
Porque así la imputación, el `log1p`, el escalado y el one-hot quedan "congelados" con los parámetros aprendidos en entrenamiento (medianas, medias, categorías). La app recibe datos crudos y el pipeline los transforma igual. Además evita fuga de información en la validación cruzada: el escalador se ajusta solo con los pliegues de entrenamiento.

**3. ¿Qué pasa si Streamlit transforma los datos distinto al entrenamiento?**
El modelo recibe números en otra escala o categorías que nunca vio, y las predicciones son incorrectas sin dar error (*training-serving skew*). Ejemplo aquí: si la app escalara las duraciones sin `log1p`, una sesión normal parecería extrema.

**4. ¿Qué diferencia hay entre `model.joblib` y la imagen Docker?**
`model.joblib` es solo el objeto entrenado (pipeline + metadatos). La imagen contiene todo lo necesario para usarlo: sistema base, Python 3.12, librerías con versiones fijas, `app.py` y el propio `model.joblib`.

**5. ¿Qué contiene realmente una imagen Docker?**
Un conjunto de capas de sistema de archivos de solo lectura (una por instrucción del Dockerfile) más metadatos: puerto expuesto, directorio de trabajo y comando de inicio (`CMD`).

**6. ¿Imagen vs. contenedor?**
La imagen es la plantilla inmutable; el contenedor es un proceso en ejecución creado a partir de ella, con una capa propia de escritura. De una imagen se pueden crear muchos contenedores.

**7. ¿Por qué escribimos el Dockerfile en Colab pero lo construimos en la VM?**
Colab no permite ejecutar el demonio de Docker. El Dockerfile es un archivo de texto y se puede escribir en cualquier parte; para construir y ejecutar se necesita un Linux con Docker, que es la VM.

**8. ¿Por qué mapear puertos?**
El contenedor tiene su propia red aislada. `-p 8501:8501` reenvía el puerto 8501 de la VM al 8501 del contenedor; sin eso, Streamlit escucha dentro del contenedor y nadie de afuera lo alcanza.

**9. ¿Por qué además una regla de firewall en GCP?**
Son dos barreras distintas. El mapeo de puertos conecta VM ↔ contenedor; el firewall de la VPC decide qué tráfico de Internet llega a la VM. Por defecto GCP bloquea todo excepto SSH (22) y, si se marcan, HTTP/HTTPS (80/443).

**10. ¿Qué cambia entre clasificación y clustering?**
El problema estadístico: la definición de variables (hay o no `y`), el modelo, la evaluación (F1/ROC-AUC frente a silhouette e inercia) y la salida de la app (clase y probabilidad frente a cluster y perfil). El flujo de ingeniería (`train.py` → `model.joblib` → `app.py` → Docker → VM) es el mismo.

**11. ¿Qué sería idéntico si el modelo fuera una red neuronal?**
Casi todo lo de ingeniería: la app, el Dockerfile, la VM, el firewall y el flujo de actualización. Cambiarían el formato del artefacto (p. ej. `.keras` o `.pt`), las dependencias (TensorFlow/PyTorch, imagen más pesada) y tal vez la máquina (más RAM o GPU).

**12. ¿Qué mejoraríamos para producción?**
HTTPS y dominio (Nginx o un balanceador), autenticación, separar API (FastAPI) y frontend, publicar la imagen en Artifact Registry, CI con GitHub Actions que corra `pytest` y construya la imagen, registrar versiones de modelo y métricas (MLflow), monitorear deriva de datos, y evaluar Cloud Run para no pagar una VM encendida todo el tiempo.
