# Módulo 5 · Clase 5 — Estrategia y cierre

Diplomado de Extensión en IA Generativa para Organizaciones.

Las cuatro clases anteriores del módulo fueron capacidades: modelos abiertos, imágenes,
voz, integraciones. Esta es la que las convierte en decisiones. **No tiene código**: son
43 diapositivas, dos instrumentos interactivos que se abren con doble clic, y la evidencia
cuantitativa de ocho fuentes públicas sobre dónde está realmente la adopción de IA en la
empresa —con sus límites metodológicos dichos en voz alta, porque la mitad de esos
informes los publica quien vende la infraestructura.

El recorrido va de un marco de cinco preguntas sobre el valor de un LLM, a la evidencia de
industria, al método para priorizar qué automatizar, al contexto como recurso escaso, y
cierra con los temas de frontera y las reflexiones de tres años haciendo esto en
producción.

**El hilo conductor: la unidad de análisis es la tarea, no el cargo — y el activo
defendible es el contexto, no el modelo.** Un cargo es un paquete heterogéneo del que solo
algunas piezas se automatizan; una tarea sí se puede medir, priorizar y delegar. Y todos
tienen acceso al mismo modelo: nadie tiene acceso a tus datos.

---

## Objetivos de aprendizaje

Al terminar la clase, un estudiante puede:

1. Responder las **cinco preguntas estratégicas** sobre un LLM —cuál es su valor, dónde es
   suplementario, dónde complementario, qué necesita y dónde se usa— y explicar por qué
   ninguna se contesta con un benchmark.
2. Formular el valor de un LLM como **reducción de costo de una operación específica**
   (entender y generar texto lógico en base a un contexto), y usar esa formulación para
   descartar casos de uso que no lo son.
3. Aplicar el **ratio de delegación** (potencia del modelo / complejidad de la tarea) y
   explicar por qué casi siempre es más barato bajar el denominador que subir el numerador.
4. Leer una encuesta de industria con criterio: distinguir **año de publicación de ventana
   de campo**, reconocer una muestra autoseleccionada, y detectar cuándo un informe no
   desagrega el segmento que a uno le importa.
5. Explicar la **contradicción del ROI** —80–89 % que reporta retorno frente a 39 % que lo
   atribuye a EBIT y 95 % de pilotos sin impacto en P&L— como un problema de nivel de
   medición, no de veracidad.
6. Identificar **dónde se movió el cuello de botella**: el volumen de datos se resolvió
   (49 % → 16 % en tres años) y lo reemplazaron el gobierno de datos y el talento.
7. Priorizar automatización **por tarea y no por cargo**, estimando FTE liberado y
   puntuando complejidad con una rúbrica de seis preguntas.
8. Distinguir los **tres niveles de automatización** (productividad personal · scripts ·
   productos de IA) y argumentar por qué el RPA clásico envejece mal frente a código
   versionable.
9. Interpretar la **exposición observada** del Anthropic Economic Index sobre la taxonomía
   O*NET, y explorar las 17.992 tareas en el instrumento de la clase.
10. Sostener que el buen contexto es **relevante, preciso, seguro, actual y gobernado**, y
    que las cinco son propiedades de la arquitectura de datos, no del modelo.
11. Gobernar agentes con **presupuestos en cuatro dimensiones** (cuánto, qué tan rápido,
    qué es reversible, quién mira) y aplicar el *test del undo*.
12. Diagnosticar un sistema por su **tasa de error** —qué arreglar cambia según si estás
    sobre 50 %, sobre 30 %, entre 10 y 30, o bajo 10.

## Prerrequisitos

Ninguno técnico. **No hay entornos, no hay llaves y no hay nada que instalar** — es la
única clase del módulo sin código.

- Un navegador para los dos instrumentos HTML de `deck/`. Los dos son autocontenidos y
  funcionan **sin conexión**: se abren con doble clic.
- Haber pasado por las clases 5.1 a 5.4 ayuda pero no es requisito: la línea de tiempo del
  *context engineering* (acto 5) es exactamente el recorrido de esas cuatro clases, y el
  acto 6 vuelve sobre MCP, skills y capas semánticas.

> **Sobre las lecturas.** Los tres informes de NVIDIA en `deck/lecturas/` son la fuente de
> casi todas las cifras de los actos 3 y 4. No hace falta leerlos para seguir la clase,
> pero están ahí para que cualquier número del deck se pueda rastrear hasta su página.

---

## Estructura del proyecto

```
class_5_5_estrategia/
├── README.md                              ← este archivo
├── deck/
│   ├── deck_5_5_estrategia.pptx            43 diapositivas · 6 actos · 17 gráficos
│   ├── analisis_automatizacion.html        Instrumento: 17.992 tareas O*NET por
│   │                                       penetración observada de IA — búsqueda,
│   │                                       familias semánticas, nube t-SNE, export CSV.
│   │                                       Autocontenido, offline
│   ├── estado_de_la_ia_2026.html           Instrumento: comparador de las tres industrias
│   │                                       (finanzas · salud · retail), etapa de agentes,
│   │                                       la contradicción del ROI, barreras por ola y la
│   │                                       ficha metodológica de las ocho fuentes.
│   │                                       Autocontenido, offline
│   └── lecturas/                           Los tres informes de NVIDIA que sostienen los
│       ├── nvidia-state-of-ai-             actos 3 y 4 (campo ago–sep 2025, publicados
│       │   financial-services-2026.pdf     como «2026 Trends»)
│       ├── nvidia-state-of-ai-healthcare-2026.pdf
│       └── nvidia-state-of-ai-retail-cpg-2026.pdf
├── data/                                  Insumos locales (vacío por convención)
└── outputs/                               Artefactos generados (git-ignorado salvo .gitkeep)
```

A diferencia del resto del módulo, **no hay carpetas de lección**: la clase es el deck y
sus dos instrumentos. Lo que en las otras clases son lecciones, aquí son **actos**.

## El deck, acto por acto

### Acto 1 — “GenAI, consideraciones estratégicas” *(slides 2–10)*

El marco propio de la clase: un mapa de cinco preguntas que se recorre nodo por nodo, con
el mapa reapareciendo entre respuestas para señalar en qué rama estamos. El valor de un
LLM formulado como reducción de costo; suplementario frente a complementario y por qué
`+potencia ⇒ +suplementariedad`; el **ratio de delegación** y el techo real de la
capacidad («¿cuánto es el potencial?» — 97 % del uso observado cae en tareas
teóricamente factibles, pero en cómputo y matemáticas la capacidad teórica es 94 % contra
33 % de cobertura observada); y cierra con qué necesita el modelo y dónde se usa.

### Acto 2 — “¿Dónde está la industria?” *(slides 11–20)*

La evidencia, empezando por **las fuentes y sus límites** — porque el rigor es parte de la
clase, no una nota al pie. Después: la era piloto terminó (adopción activa 45 → 65 % en
servicios financieros mientras el «evaluando» cae de 50 % a 24 %); en qué se está usando;
agentes con uso incipiente pero acelerado y para qué sirven hoy; **¿hay valor en la IA?**
en dos dimensiones —la percepción de retorno frente a la atribución contable—; el cuello
de botella que se movió de los datos a las personas; dónde se ejecutan las cargas (el
híbrido superó a la nube pura por primera vez); y si llegamos al techo de capex.

### Acto 3 — “IA y automatización” *(slides 21–28)*

El método. **Automatizar tareas, no cargos**: levantar tareas, estimar FTE, clasificar por
automatizabilidad e impacto, y reempaquetar los cargos con lo que queda. Los tres niveles
de automatización y la advertencia sobre el RPA clásico. La matriz impacto × complejidad
con su rúbrica de seis preguntas. Y la contraparte medida: la **exposición observada** del
Anthropic Economic Index (1.348 de 17.992 tareas O*NET, base 7,49 %), dónde está
concentrada la penetración, el instrumento para explorarla, y lo que la evidencia dice del
empleo —sin aumento sistemático del desempleo, pero con la puerta de entrada de los
jóvenes de 22 a 25 años angostándose un 14 %.

### Acto 4 — “IA sin contexto = ChatGPT Wrapper” *(slides 29–31)*

*All you need is ~~love~~ context.* La línea de tiempo del context engineering —2024
tools y ReAct, 2025 MCP y multiagentes, 2026 filesystem, CLI y skills, ¿2027?— que es
literalmente el recorrido de las clases 5.1 a 5.4. Y la conclusión que sobrevive al cambio
de mecanismo: el buen contexto es **relevante, preciso, seguro, actual y gobernado**, y
las cinco son propiedades de tu arquitectura de datos.

### Acto 5 — “Temas clave” y gobernanza *(slides 32–38)*

Lo que se está discutiendo en la frontera, del **AI Engineer World's Fair 2026** (San
Francisco, 500+ sesiones): **tokenomics** —ruteo de modelos, caching, y medir ROI en vez
de gasto bruto—; **tu modelo de datos es tu principal diferenciador**, con la capa
semántica y la ontología como activo que ningún modelo nuevo te quita («el agente propone,
la ontología permite»); la rúbrica para elegir entre MCPs, CLIs y skills; evaluar y
observar, con el *tracing primero*; **la brecha de gobernanza** (72 % corre agentes en
producción, 20 % tiene gobernanza madura); y quién es dueño de esto.

### Acto 6 — “Tercer año del GenAI, algunas reflexiones” *(slides 39–43)*

Las opiniones ganadas en producción: los frameworks todavía cambian, así que programa
sabiendo que vas a refactorizar; los copilots hacen más polivalente a un experto, no más
experto; **a mayor potencia de modelo, mayor simpleza de arquitectura**; y la **escalera de
la tasa de error**, que es el diagnóstico más útil del deck — sobre 50 % espera el próximo
modelo o cambia de problema, sobre 30 % es mala arquitectura, entre 10 y 30 falta mejora
continua, bajo 10 falta dataset.

---

## Recursos del deck

Las dos páginas HTML son **autocontenidas**: cero CDN, cero librerías, cero peticiones de
red. Se abren con doble clic y funcionan sin conexión. Las dos respetan el tema claro u
oscuro del sistema y traen su propio interruptor.

| Recurso | Para qué | Cuándo usarlo |
|---|---|---|
| [`analisis_automatizacion.html`](deck/analisis_automatizacion.html) | Las **17.992 tareas** de la taxonomía O*NET puntuadas por penetración observada de IA (1.348 con penetración, base 7,49 %). Búsqueda por palabra o concepto, filtro por familia semántica, nube de embeddings t-SNE y export a CSV. | Acto 3, después de «dónde está la penetración». El ejercicio dura dos minutos: buscar los verbos del propio trabajo y mirar el puntaje. Lo revelador no es el número, es cuántas tareas propias no aparecen en la taxonomía. |
| [`estado_de_la_ia_2026.html`](deck/estado_de_la_ia_2026.html) | Comparador de las tres industrias con selector de sector: KPIs, etapa de despliegue de agentes, la contradicción del ROI, barreras con toggle antes/ahora, tabla ordenable de ~18 métricas y export a CSV. Incluye la ficha metodológica de las ocho fuentes, abierta por defecto. | Acto 2, como respaldo cuando alguien pregunte por su industria o por la cifra exacta. También sirve para responder «¿de dónde salió ese número?» sin salir de la clase. |
| [`deck/lecturas/`](deck/lecturas/) | Los tres informes de NVIDIA en PDF: servicios financieros (6.ª edición, n = 839), salud y ciencias de la vida (n > 600) y retail y consumo masivo (N no revelado). | Para rastrear cualquier cifra de los actos 2 y 3 hasta su página. |

## Fuentes, y por qué importa leerlas con criterio

El acto 2 abre con este cuadro a propósito. Ninguna de estas cifras es un censo.

| Fuente | N | Campo | Qué hay que saber |
|---|---|---|---|
| NVIDIA · *State of AI in Financial Services: 2026 Trends* (6.ª ed.) | 839 | ago–sep 2025 | 50/50 gerencia y practicantes. Un tercio con ingresos > US$ 250 M. **Seguros está en la muestra pero nunca se desagrega**, y no existe corte de fondos de pensiones. |
| NVIDIA · *Healthcare and Life Sciences: 2026 Trends* | > 600 | ago–sep 2025 | 60/40 gerencia y practicantes. Global, listas de distribución de NVIDIA. |
| NVIDIA · *Retail and CPG: 2026 Trends* (3.ª ed.) | no revelado | ago–sep 2025 | **No publica el N**, así que ninguna de sus cifras admite lectura de precisión. |
| [Anthropic + Material · *The 2026 State of AI Agents Report*](https://resources.anthropic.com/hubfs/The%202026%20State%20of%20AI%20Agents%20Report.pdf) | > 500 | fines 2025 | Líderes técnicos, **solo Estados Unidos**. Encuesta de proveedor. |
| [Anthropic Economic Index · *Economic primitives*](https://www.anthropic.com/research/anthropic-economic-index-january-2026-report) | 1 M + 1 M | 13–20 nov 2025 | Un millón de conversaciones de Claude.ai y un millón de la API, con métodos que preservan privacidad. Mide el uso de **un** modelo: es un piso, no un total. |
| [Anthropic · *Labor market impacts of AI*](https://www.anthropic.com/research/labor-market-impacts) | — | 2025 | Define la **exposición observada**: capacidad teórica × uso real, con la aumentación ponderada al 50 %. Datos abiertos en [HuggingFace](https://huggingface.co/datasets/Anthropic/EconomicIndex). |
| [McKinsey · *State of AI trust in 2026*](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/tech-forward/state-of-ai-trust-in-2026-shifting-to-the-agentic-era) | no revelado | 2026 | Consultora con incentivo comercial. Es el contrapunto útil porque mide **atribución a EBIT**, no percepción. |
| MIT NANDA · *The GenAI Divide* | 52 + 153 + 300 | 2025–26 | 52 entrevistas, 153 encuestas y 300 despliegues públicos. Base cualitativa chica para un titular tan citado como el «95 % de los pilotos». |
| AI Engineer World's Fair 2026 | 500+ sesiones | 29 jun – 2 jul 2026 | Conferencia en San Francisco. Las cifras **las autoinforma cada expositor** (Microsoft, McKinsey, Anthropic, Gates Foundation, Neo4j, Berkeley, Salesforce): son orden de magnitud, no medición. |

Tres advertencias transversales, que en el deck se dicen en voz alta:

1. El **«2026» del título de los informes de NVIDIA es el año de publicación**. El trabajo
   de campo es de agosto–septiembre de 2025, y todo «subió desde X» compara contra la ola
   anterior de la encuesta, no contra el año calendario.
2. Las muestras son **autoseleccionadas** de las listas del propio proveedor. No son
   probabilísticas: no hay margen de error que citar.
3. La **contradicción del ROI no es que alguien mienta**. Un dueño de caso de uso que ve su
   proceso mejorar reporta retorno con razón; un CFO que busca la mejora en el EBIT
   consolidado no la encuentra, también con razón — porque está diluida entre doce
   iniciativas de las cuales ninguna mueve la aguja sola.
