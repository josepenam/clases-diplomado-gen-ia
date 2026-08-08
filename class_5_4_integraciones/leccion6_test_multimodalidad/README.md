# leccion6_test_multimodalidad

**Dibujar a ciegas: el test del unicornio, tres años después.** El experimento de *Sparks of AGI* (Bubeck et al., 2023) repetido con modelos actuales: se les pide dibujar en **TikZ** — texto puro, sin ver jamás el resultado — se compila con LaTeX, se rasteriza con PyMuPDF, y un modelo *con visión* (`gpt-5-mini`) juzga cada imagen contra lo pedido. Texto → código → imagen → juicio visual: la integración multimodal completa, ida y vuelta, con dos llamadas de API y un compilador de los años 80.

Sexta y última lección de la Clase 5.4 — Integraciones.

## Qué hace

| Paso | Detalle |
|---|---|
| El pipeline | `pedir_tikz` (el modelo emite solo el bloque tikzpicture) → `limpiar_codigo` (fences, `\usetikzlibrary` al preámbulo) → `compilar_y_rasterizar` (LaTeX + PyMuPDF). Un TikZ inválido es un ❌ en la grilla, no una excepción: la coherencia sintáctica es parte del dato. |
| El torneo | 3 modelos con gradiente de capacidad (`gpt-5.5` / `gpt-5.4-mini` / `gpt-5-nano`) × 4 dibujos: unicornio, **bicicleta** (el test duro de coherencia estructural), pingüino esquiando, red neuronal (diagrama técnico). 12 llamadas. |
| La grilla | matplotlib, modelo × dibujo, con los fracasos de compilación visibles. |
| El juez visual | `gpt-5-mini` mira cada PNG y puntúa 1–5 con comentario; ranking por promedio. |

## Requisitos

- Python 3.12 y [uv](https://github.com/astral-sh/uv), o Google Colab.
- **Un motor LaTeX** (el notebook detecta cualquiera de los dos):
  - macOS: `brew install tectonic` (standalone, ~100 MB) o MacTeX si ya lo tienes.
  - Colab / Linux: `apt-get install texlive-latex-extra` (la celda inicial trae la línea lista para descomentar).
  - Sin LaTeX el notebook degrada: muestra el código TikZ generado, sin render.
- `OPENAI_API_KEY` — ~24 llamadas (12 de dibujo + 12 de juicio), mayormente a modelos mini/nano; costo bajo.
- El rasterizado usa **PyMuPDF** (pip puro): no hace falta poppler ni ninguna dependencia de sistema aparte del motor LaTeX.

## Configuración

```bash
# 1. Copia la plantilla de secretos y completa tu llave
cp .env.example .env          # edita OPENAI_API_KEY

# 2. Sincroniza el entorno (crea .venv con las dependencias fijadas)
UV_CACHE_DIR=.uv-cache uv sync --python 3.12
```

## Ejecución local

```bash
# Registra el kernel de Jupyter para este entorno
uv run python -m ipykernel install --user \
  --name clase-5-4-l6 --display-name "Python (clase 5.4 · L6)"

# Abre el notebook
uv run --with jupyterlab jupyter lab test_de_multimodalidad.ipynb
```

Los `.tex`, PDFs y PNGs quedan en `outputs/tikz/` y la grilla en `outputs/grilla_multimodalidad.png` (todo git-ignorado).

## Nota sobre el material original

El notebook de origen (`visual_understanding_test.ipynb`) era un benchmark sin prosa con `pdflatex` + `pdftocairo` (poppler) y una función de evaluación truncada. Esta versión agrega la narrativa completa, reconstruye la evaluación, reemplaza poppler por PyMuPDF (una dependencia de sistema menos), actualiza el lineup (`gpt-5.2/gpt-5/gpt-4o/gpt-4o-mini` → modelos vigentes), reduce las corridas de 20 a 12 y agrega el juez visual que cierra el círculo multimodal.

## Referencias

- https://arxiv.org/abs/2303.12712 (Sparks of AGI — sección 2.2, el unicornio)
- https://tikz.dev
