# Evidencias

Evidencias de la entrega.

- `docker_codespaces_log.txt`: salida completa de `bash scripts/docker_demo.sh` en GitHub Codespaces (build, images, run, ps y logs).

Capturas de pantalla: Súbelas aquí con estos nombres (GitHub: **Add file → Upload files**, dentro de esta carpeta).

| Archivo | Qué debe verse |
|---|---|
| `01_colab_app.png` | La app abierta desde Colab con un resultado (por ejemplo, valor de página 300 → compra 89,5 %) |
| `02_docker_build.png` | Final de `docker build -t intencion-compra-app .` en Codespaces, sin errores |
| `03_docker_ps.png` | `docker ps` con el contenedor `intencion-compra` en estado *Up* |
| `04_docker_logs.png` | `docker logs intencion-compra` con la línea *You can now view your Streamlit app* |
| `05_docker_app.png` | La app servida por el contenedor (puerto 8501 del Codespace) con un resultado |
| `06_streamlit_cloud.png` | La app en https://intencion-compra.streamlit.app, con la URL visible |
| `07_prueba_cruzada.png` | La app funcionando en el entorno de la otra pareja |
