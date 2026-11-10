# Evidencias

Evidencias de la entrega.

- `docker_codespaces_log.txt`: salida completa de `bash scripts/docker_demo.sh` en GitHub Codespaces (build, images, run, ps y logs).

Capturas de pantalla: Súbelas aquí con estos nombres (GitHub: **Add file → Upload files**, dentro de esta carpeta).

| Archivo | Qué debe verse |
|---|---|
| `01_colab_app.png` | La app abierta desde Colab con un resultado (por ejemplo, valor de página 300 → compra 89,5 %) |
| `docker_codespaces_log.txt` ✅ | Salida completa del build, `docker images`, `docker run`, `docker ps` y `docker logs` |
| `03_docker_ps.png` ✅ | Contenedor recreado con `docker run` y `docker ps` en estado *Up*, puerto 8501 |
| `04_puerto_8501.png` ✅ | Pestaña *Puertos* del Codespace: el 8501 reenviado y el proceso de Streamlit (Python 3.12) en ejecución |
| `05_docker_app.png` ✅ | La app servida por el contenedor en `...-8501.app.github.dev`, con el ticket calculado por el modelo (94,5 %) |
| `06_streamlit_cloud.png` | La app en https://intencion-compra.streamlit.app, con la URL visible |
| `07_prueba_cruzada.png` | La app funcionando en el entorno de la otra pareja |
