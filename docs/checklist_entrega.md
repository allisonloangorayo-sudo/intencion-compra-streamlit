# Checklist de entrega

Estado de cada punto de la guía. ✅ hecho · ⏳ pendiente (lo hacen las autoras) · ⚠️ alternativa acordada.

## Entregables (sección 32)

| Entregable | Estado | Dónde |
|---|---|---|
| Repositorio GitHub | ✅ | https://github.com/allisonloangorayo-sudo/intencion-compra-streamlit |
| Dataset o instrucciones para obtenerlo | ✅ | `data/online_shoppers_intention.csv` y README §2 |
| `train.py` reproducible | ✅ | `train.py` (semilla fija; reentrenar da las mismas métricas) |
| `model.joblib` | ✅ | raíz del repo |
| `app.py` funcional | ✅ | `app.py` + `ui/` |
| `requirements.txt` | ✅ | versiones fijas |
| `Dockerfile` y `.dockerignore` | ✅ | raíz del repo |
| README completo | ✅ | `README.md` (los 14 puntos de la sección 20, más despliegue, pruebas y uso de IA) |
| Aplicación desplegada | ⚠️ | https://intencion-compra.streamlit.app (Streamlit Community Cloud). La VM de Compute Engine requiere activar facturación; pasos completos en `docs/GUIA_PASO_A_PASO.md` |
| Docker ejecutado en Linux de Google | ⏳ | GitHub Codespaces: README §12. Capturas en `docs/evidencias/` |
| Evidencia de la prueba cruzada | ⏳ | `docs/prueba_cruzada.md` |
| Interpretación de resultados | ✅ | README §6 y §7, pestaña "El modelo" de la app |

## Checklist final de la pareja (sección 34)

| Punto | Estado | Evidencia |
|---|---|---|
| Entendemos qué representa una fila | ✅ | README §2: una fila = una sesión de navegación |
| Ruta definida (supervisada / no supervisada) | ✅ | Ruta A, clasificación binaria |
| Variables justificadas | ✅ | README §3 (incluye las 4 descartadas y el análisis de fuga de `PageValues`) |
| Preprocesamiento dentro del pipeline | ✅ | `train.py`: `ColumnTransformer` + modelo en un `Pipeline` |
| `train.py` corre de principio a fin | ✅ | celda `!python train.py` del cuaderno de Colab |
| `model.joblib` se genera | ✅ | ídem |
| `app.py` no vuelve a entrenar | ✅ | solo hace `joblib.load` |
| Probamos Streamlit en Colab | ✅ | túnel de Cloudflare; captura del caso extremo (valor de página 300 → compra 89,5 %) |
| `requirements.txt`, `Dockerfile`, `.dockerignore` | ✅ | raíz del repo |
| El repositorio tiene todos los archivos | ✅ | ver README §8 |
| VM creada y acceso por SSH | ⚠️ | sin facturación en Google Cloud; se usa GitHub Codespaces (Linux en la nube con terminal en el navegador) |
| Docker instalado | ✅ | el Codespace estándar de GitHub ya lo trae (`docker --version`) |
| `docker build` termina bien | ⏳ | captura `02_docker_build.png` |
| `docker run` deja el contenedor activo | ⏳ | captura `03_docker_ps.png` |
| `docker logs` sin errores críticos | ⏳ | captura `04_docker_logs.png` |
| Regla de firewall | ⚠️ | no aplica en Codespaces (el reenvío de puertos expone el 8501); pasos para la VM en la guía, fase 4.4 |
| La app abre desde fuera | ✅ | https://intencion-compra.streamlit.app; en Codespaces, captura `05_docker_app.png` |
| Otra pareja reprodujo el proyecto | ⏳ | `docs/prueba_cruzada.md` |
| Sabemos detener / eliminar recursos | ✅ | guía, fase 6 |

## Preguntas de discusión (sección 35)

✅ Respuestas preparadas en `docs/preguntas_discusion.md`.
