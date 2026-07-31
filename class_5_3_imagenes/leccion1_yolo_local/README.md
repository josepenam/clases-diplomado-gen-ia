# leccion1_yolo_local

**Detección y tracking de objetos, 100% local**: corre [YOLO](https://docs.ultralytics.com)
(ultralytics) sobre tu webcam, con cajas de detección e IDs de track persistentes (ByteTrack).
Sin API keys y sin nube — la visión "clásica" (convoluciones) que precede a los modelos
multimodales de las lecciones siguientes.

Primera de las cuatro lecciones de la Clase 5.3 — cubre el tramo del deck
*Reconocimiento de imágenes* (convolución → CNNs → YOLO).

## Qué hace

`yolo_tracking.py` abre la fuente de video (webcam por defecto), corre el modelo cuadro a
cuadro en streaming y dibuja las detecciones en una ventana en vivo:

| Flag | Default | Para qué |
|---|---|---|
| `--model` | `yolov8n.pt` | Peso a usar (prueba también `yolo11n.pt`) |
| `--source` | `0` | `0` = webcam; también acepta ruta a un video o imagen |
| `--tracker` | `bytetrack.yaml` | Config del tracker (IDs persistentes) |
| `--conf` / `--iou` | `0.25` / `0.45` | Umbrales de confianza y de NMS |
| `--imgsz` | `640` | Tamaño de inferencia |
| `--device` | auto | `cpu`, `0` (GPU), `mps` (Apple Silicon) |

El peso (~6 MB para el modelo *nano*) se descarga automáticamente la primera vez y está
git-ignorado.

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv).
- Una webcam — macOS pedirá permiso de cámara la primera vez.
- Esta lección es **local por diseño** (ventana en vivo); no corre en Colab.

## Ejecución

```bash
# Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12

# Tracking en vivo sobre la webcam (cierra con q o Ctrl-C)
uv run python yolo_tracking.py
```

¿Sin webcam a mano? Prueba la detección sobre la imagen de ejemplo:

```bash
uv run yolo predict model=yolov8n.pt source=Cachureos2020.jpg
```

La imagen anotada queda en `runs/detect/predict/` (git-ignorado). Cuenta cuántas "person"
encuentra entre los disfraces — buen pie para discutir qué *no* entiende un detector de
clases fijas, y por qué la lección 2 cambia a un modelo multimodal.

## Referencias

- https://docs.ultralytics.com/modes/track/
- https://docs.ultralytics.com/models/
