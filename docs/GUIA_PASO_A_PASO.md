# Guía paso a paso del reto

Del dataset al despliegue en Google Cloud. Cada fase corresponde a una parte de la rúbrica.

Repositorio: `https://github.com/allisonloangorayo-sudo/intencion-compra-streamlit`

| Fase | Qué se hace | Dónde | Rúbrica |
|---|---|---|---|
| 1 | Explorar datos, entrenar, probar la app | Google Colab | Problema y datos 10 % · Modelamiento 20 % · Streamlit 15 % |
| 2 | Revisar que el repo esté completo | GitHub | README 15 % |
| 3 | Crear la VM e instalar Docker | Google Cloud | GCP 15 % |
| 4 | Construir imagen, correr contenedor, abrir firewall | VM (SSH) | Docker 25 % · GCP |
| 5 | Prueba cruzada con otra pareja | Otra pareja | README y prueba cruzada |
| 6 | Apagar recursos | Google Cloud | — |

---

## Fase 1 — Desarrollo en Google Colab

1. Abrir Colab → `Archivo → Abrir cuaderno → GitHub` → pegar la URL del repositorio → elegir `notebooks/01_desarrollo_colab.ipynb`.
2. Ejecutar las celdas en orden. El cuaderno:
   - clona el repo e instala `requirements.txt`;
   - responde las preguntas de la sección 6 de la guía (qué es una fila, objetivo, faltantes, tipos de variables);
   - ejecuta `python train.py` y muestra `metrics.json`;
   - levanta Streamlit en segundo plano y abre un túnel con `localtunnel`;
   - corre las pruebas (`pytest`).
3. **Túnel de localtunnel**: la página que abre pide una contraseña. Es la IP pública del Colab; la imprime la celda `!curl -s ipv4.icanhazip.com`.
4. Probar los tres casos del selector "Cargar un caso de ejemplo" y al menos un caso propio con valores extremos.

> Si la red de la universidad bloquea el túnel, basta con que el log diga `You can now view your Streamlit app` y continuar con GCP (lo permite la guía).

**Checklist de la fase**: `train.py` corre de principio a fin · se genera `model.joblib` · la app carga sin reentrenar · probaron 3+ casos.

---

## Fase 2 — GitHub

El repositorio ya tiene todos los entregables. Antes de la demostración, revisar:

- [x] README → sección **Autoras**: Allison Loango y Angie Loango.
- [ ] Si reentrenan con otra versión de librerías, subir el nuevo `model.joblib` y `metrics.json`.
- [ ] No hay tokens, contraseñas ni archivos `.env`.

Para editar desde el navegador: abrir el archivo en GitHub → ícono de lápiz → *Commit changes*.

---

## Ruta usada en esta entrega: Streamlit Cloud + Cloud Shell

Crear la VM exige activar la facturación de Google Cloud, que pide una autorización temporal en una tarjeta. Mientras eso no sea posible, la entrega usa dos servicios gratuitos que cubren lo mismo:

**A. App pública en Streamlit Community Cloud**

1. Entrar a <https://share.streamlit.io> → **Continue with GitHub** → autorizar con permiso de solo lectura.
2. **Create app** → *Deploy a public app from GitHub*.
3. Repository `allisonloangorayo-sudo/intencion-compra-streamlit`, branch `main`, main file `app.py`, App URL `intencion-compra`.
4. **Advanced settings** → Python **3.12** → **Save** → **Deploy**.
5. Resultado: <https://intencion-compra.streamlit.app>. Cada cambio que se sube a `main` actualiza la app sola.

**B. Docker en Google Cloud Shell**

1. En la consola de Google Cloud, clic en el ícono `>_` (Activar Cloud Shell). No requiere facturación.
2. Ejecutar:

```bash
git clone https://github.com/allisonloangorayo-sudo/intencion-compra-streamlit.git
cd intencion-compra-streamlit
docker build -t intencion-compra-app .
docker run -d --name intencion-compra -p 8501:8501 intencion-compra-app
docker ps
docker logs intencion-compra
```

3. Arriba de la terminal: **Vista previa en la Web → Cambiar puerto → 8501 → Cambiar y obtener vista previa**.
4. Tomar captura de cada comando y de la app abierta.

Las fases 3 y 4 siguientes describen la VM, para cuando haya facturación o créditos del curso.

---

## Fase 3 — Máquina virtual en Google Cloud

### 3.1 Crear la VM

1. Entrar a <https://console.cloud.google.com> y elegir (o crear) el proyecto del laboratorio.
2. Menú → **Compute Engine → Instancias de VM**. Si lo pide, **Habilitar** la Compute Engine API (tarda 1–2 min).
3. **Crear instancia**:
   - **Nombre**: `vm-intencion-compra`
   - **Región**: `us-central1` (o la que indique el profesor)
   - **Tipo de máquina**: `e2-small` (2 GB de RAM; `e2-micro` se queda corta para instalar scikit-learn y Streamlit). Revisar el costo estimado que muestra la consola a la derecha.
   - **Disco de arranque → Cambiar**: *Ubuntu*, versión **Ubuntu 24.04 LTS** (x86/64), 10–20 GB.
   - **Redes → Etiquetas de red**: escribir `streamlit-server` (la regla de firewall de la fase 4 se aplica a esta etiqueta).
   - Confirmar que la interfaz de red tenga **IP externa: efímera**.
4. **Crear**. Cuando aparezca el check verde, anotar la **IP externa**.

### 3.2 Entrar por SSH

En la fila de la VM, clic en **SSH**. Se abre una terminal Linux en el navegador.

### 3.3 Instalar Docker y Git

```bash
sudo apt update
sudo apt install -y docker.io git
sudo systemctl enable --now docker
docker --version
git --version
```

Para usar Docker sin `sudo`:

```bash
sudo usermod -aG docker $USER
exit
```

Cerrar la ventana SSH, volver a abrirla y comprobar con `docker ps` (no debe pedir sudo ni dar *permission denied*).

---

## Fase 4 — Docker en la VM

### 4.1 Clonar

```bash
git clone https://github.com/allisonloangorayo-sudo/intencion-compra-streamlit.git
cd intencion-compra-streamlit
ls -la
```

Deben aparecer `Dockerfile`, `app.py`, `model.joblib` y `requirements.txt`.

### 4.2 Construir la imagen

```bash
docker build -t intencion-compra-app .
docker images
```

El punto final es el **contexto de construcción** (la carpeta actual). La primera vez tarda 2–4 minutos: descarga `python:3.12-slim` e instala las librerías.

```
Dockerfile --docker build--> Imagen --docker run--> Contenedor
(receta)                     (plantilla inmutable)  (proceso en ejecución)
```

### 4.3 Ejecutar el contenedor

Primero interactivo, para ver errores en pantalla:

```bash
docker run --rm -p 8501:8501 intencion-compra-app
```

Si aparece `You can now view your Streamlit app`, detener con `Ctrl+C` y dejarlo en segundo plano:

```bash
docker run -d --name intencion-compra --restart unless-stopped -p 8501:8501 intencion-compra-app
docker ps
docker logs intencion-compra
curl -s localhost:8501/_stcore/health     # debe responder: ok
```

`-p 8501:8501` conecta el puerto 8501 de la VM con el 8501 del contenedor.

### 4.4 Abrir el puerto 8501 (firewall)

El contenedor ya responde dentro de la VM, pero GCP bloquea el tráfico de Internet hasta que exista una regla.

**Opción A — consola web**: Menú → **Red de VPC → Firewall → Crear regla de firewall**

| Campo | Valor |
|---|---|
| Nombre | `allow-streamlit-8501` |
| Dirección | Entrada (ingress) |
| Acción | Permitir |
| Destinos | Etiquetas de destino especificadas → `streamlit-server` |
| Rangos IPv4 de origen | `0.0.0.0/0` (solo para el laboratorio) |
| Protocolos y puertos | TCP → `8501` |

**Opción B — Cloud Shell** (ícono `>_` arriba a la derecha de la consola):

```bash
gcloud compute firewall-rules create allow-streamlit-8501 \
  --allow=tcp:8501 --direction=INGRESS \
  --source-ranges=0.0.0.0/0 --target-tags=streamlit-server
```

Si la VM se creó sin la etiqueta: `Instancias de VM → vm-intencion-compra → Editar → Etiquetas de red → streamlit-server → Guardar`.

### 4.5 Probar

Abrir en el navegador (con **http**, no https):

```
http://IP_EXTERNA_DE_LA_VM:8501
```

Cargar "Sesión con alta intención" → **Ejecutar modelo** → debe salir *Compra · 94,5 %*.

### 4.6 Diagnóstico rápido

| Síntoma | Revisión |
|---|---|
| `docker build` falla en `pip install` | Leer el error completo; revisar `requirements.txt` |
| El contenedor se detiene | `docker ps -a` y `docker logs intencion-compra` |
| `curl localhost:8501` no responde | Confirmar `-p 8501:8501` y que el CMD use `--server.address=0.0.0.0` |
| Responde en la VM pero no desde el navegador | Regla de firewall, etiqueta `streamlit-server` en la VM, IP externa, usar `http://` |
| `permission denied` con docker | Cerrar y abrir SSH tras `usermod`, o anteponer `sudo` |
| Cambios de GitHub no aparecen | `git pull` → `docker stop/rm` → `docker build` → `docker run` |

---

## Fase 5 — Prueba cruzada

1. Enviar a la otra pareja **solo** la URL del repositorio.
2. Ellos clonan, leen el README sin ayuda verbal, construyen la imagen, corren el contenedor y prueban un caso.
3. Llenar `docs/prueba_cruzada.md` con lo que reporten (errores, instrucciones faltantes, tiempos) y una captura de su app funcionando.
4. Si encontraron un vacío en el README, corregirlo y anotarlo en la misma ficha.

Recíprocamente, ustedes reproducen el proyecto de ellos y les entregan su ficha.

---

## Fase 6 — Cerrar y controlar costos

Al terminar la demostración:

```bash
docker stop intencion-compra
```

En la consola: **Compute Engine → Instancias de VM → ⋮ → Detener** (deja de cobrar CPU; el disco sigue cobrando poco) o **Borrar** (elimina todo). Borrar también la regla `allow-streamlit-8501` si ya no se usa.

---

## Entregables (sección 32 de la guía)

| Entregable | Dónde está |
|---|---|
| Repositorio GitHub | URL de arriba |
| Dataset | `data/online_shoppers_intention.csv` |
| `train.py` reproducible | raíz |
| `model.joblib` | raíz |
| `app.py` funcional | raíz |
| `requirements.txt`, `Dockerfile`, `.dockerignore` | raíz |
| README completo | `README.md` |
| App desplegada en la VM | Fase 4 |
| Evidencia de prueba cruzada | `docs/prueba_cruzada.md` |
| Interpretación de resultados | README §6–7 |
