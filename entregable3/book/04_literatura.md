---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Revisión de literatura y novedad

```{code-cell} ipython3
:tags: [remove-cell]
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path.cwd().parent))
import pandas as pd
from src.libro import configurar, mostrar
configurar()
RL = pathlib.Path.cwd().parent / "experiments" / "revision_literatura"
busqueda = json.loads((RL / "busqueda_2026-10-26.json").read_text(encoding="utf-8"))
citas = json.loads((RL / "citas_2026-10-26.json").read_text(encoding="utf-8"))
repos = json.loads(sorted(RL.glob("repositorios_*.json"))[-1].read_text(encoding="utf-8"))
```

La novedad del modelo original no se declara: se busca evidencia de que no existe. Este capítulo documenta cómo se buscó, qué se encontró y en qué se diferencia la propuesta de los trabajos más cercanos.

## Protocolo de búsqueda

La búsqueda se hizo el **26 de octubre de 2026** y se repitió el **15 de noviembre de 2026**, antes de la entrega final ({ref}`sec-repeticion`), con los scripts `experiments/revision_literatura/buscar.py` (bases bibliográficas), `citas.py` (búsqueda por citación) y `repositorios.py` (GitHub). Los resultados crudos quedaron guardados con la fecha en el nombre del archivo.

**Bases consultadas.** OpenAlex (más de 250 millones de trabajos; integra el antiguo Microsoft Academic Graph y la mayoría de las revistas indexadas en Scopus y Web of Science), Semantic Scholar (centrada en computación e inteligencia artificial), arXiv (preprints de aprendizaje automático y estadística) y Crossref (registro de DOI de casi todas las editoriales). Scopus y Web of Science no tienen una API abierta sin suscripción institucional, por lo que se reemplazaron por OpenAlex y Crossref, que cubren sus mismas revistas.

**Cadenas.** Ocho cadenas combinan (i) la familia del modelo (bosque aleatorio, árboles extremadamente aleatorizados, bosque ordinal, criterio de partición ponderado), (ii) el problema (calidad del vino, evento binario obtenido al cortar una respuesta ordinal) y (iii) sinónimos en inglés y en español. Cada base recibió la sintaxis booleana que admite.

**Criterio de relevancia.** Un trabajo es relevante si (a) aplica árboles o ensambles a la calidad del vino, (b) propone árboles o bosques que usan la estructura ordinal o acumulada de la respuesta, (c) usa reglas de puntuación ponderadas por umbral para entrenar o partir, o (d) usa etiquetas ordinales para mejorar un clasificador binario. Se leyeron los títulos de los 50 primeros resultados por relevancia de cada base (25 en Crossref, cuyo buscador no es booleano y por eso reporta millones de coincidencias parciales) y el resumen de los potencialmente relevantes.

```{code-cell} ipython3
:tags: [hide-input]
cadenas = (pd.DataFrame([{"Cadena": c["cadena"], "Base": c["base"], "Consulta": c["consulta"]} for c in busqueda["consultas"]])
           .drop_duplicates("Cadena")[["Cadena"]].assign(
    **{"Descripción": [next(c["descripcion"] for c in busqueda["consultas"] if c["cadena"] == k) for k in
                       pd.DataFrame(busqueda["consultas"]).drop_duplicates("cadena")["cadena"]]}))
mostrar(cadenas)
```

## Matriz de novedad

```{code-cell} ipython3
:tags: [hide-input]
matriz = pd.read_csv(RL / "matriz_novedad.csv")
m = matriz.rename(columns={"cadena": "Cadena", "base": "Base", "resultados": "Resultados", "revisados": "Revisados",
                           "relevantes": "Relevantes", "observacion": "Observación"}).drop(columns="consulta")
mostrar(m[m["Revisados"] > 0])
```

```{code-cell} ipython3
:tags: [hide-input]
from myst_nb import glue
glue("n_revisados", int(matriz["revisados"].sum()), display=False)
glue("n_relevantes", int(matriz["relevantes"].sum()), display=False)
glue("n_citas", len({p.get("title") for s in citas["semillas"].values() for t in ("citas", "referencias") for p in s[t] if p.get("title")}), display=False)
```

En total se revisaron {glue:text}`n_revisados` títulos y se marcaron {glue:text}`n_relevantes` coincidencias relevantes (varias repetidas entre bases). Las combinaciones sin fila tuvieron cero resultados.

**Búsqueda por citación.** Desde los seis trabajos más cercanos (Janitza et al., 2016; Hornung, 2020; Tutz, 2022; Lechner y Okasa, 2024; Buczak, 2024; Rotenberg et al., 2026) se recorrieron sus referencias (hacia atrás) y los trabajos que los citan (hacia adelante) con Semantic Scholar: {glue:text}`n_citas` títulos únicos. Aparecieron cinco trabajos relevantes más: los criterios de partición para árboles ordinales {cite:p}`splitting2025`, fabOF {cite:p}`buczak2024fabof`, una aplicación del Ordered Forest al fútbol, un ensamble apilado para la preferencia de vino y los efectos de escala en árboles ordinales. Ninguno combina umbrales vecinos para un evento binario.

**Repositorios de código.** En GitHub se buscaron siete cadenas (bosque ordinal, Ordered Forest, probabilidades acumuladas, vino ordinal, Extra-Trees ordinal, RPS ponderado). Aparecen implementaciones de Ordinal Forest (paquete `ordinalForest` de R y versiones en Python), del Ordered Forest de Lechner y Okasa (`okasag/OrderedForest`) y varios proyectos que tratan la calidad del vino como regresión ordinal (logística ordinal, regresión ordinal bayesiana) o comparan regresión y clasificación. Ninguno implementa un criterio de partición ponderado por umbral ni la combinación de umbrales vecinos para un evento binario.

```{code-cell} ipython3
:tags: [hide-input]
mostrar(pd.DataFrame([{"Consulta en GitHub": c["consulta"], "Repositorios": c["total"],
                       "Ejemplos": "; ".join(i["repo"] for i in c["items"][:3])} for c in repos["consultas"]]))
```

(sec-repeticion)=
## Repetición de la búsqueda

El 15 de noviembre de 2026 se ejecutaron de nuevo las mismas ocho cadenas en las cuatro bases, la búsqueda por citación desde los seis trabajos más cercanos y las siete consultas en GitHub. La tabla compara el número de resultados de ambas fechas y cuenta, entre los títulos que se revisan en cada base (los 50 primeros, o 25 en Crossref), los que no habían aparecido en la primera búsqueda.

```{code-cell} ipython3
:tags: [hide-input]
import re
busqueda2 = json.loads((RL / "busqueda_2026-11-15.json").read_text(encoding="utf-8"))
citas2 = json.loads((RL / "citas_2026-11-15.json").read_text(encoding="utf-8"))
repos1 = json.loads((RL / "repositorios_2026-10-26.json").read_text(encoding="utf-8"))
repos2 = json.loads((RL / "repositorios_2026-11-15.json").read_text(encoding="utf-8"))


def clave(t):
    return re.sub(r"\W+", "", (t or "").lower())


vistos = {clave(i.get("titulo")) for c in busqueda["consultas"] for i in c["items"]}
antes = {(c["cadena"], c["base"]): c["total"] for c in busqueda["consultas"]}
filas, nuevos = [], set()
for c in busqueda2["consultas"]:
    revisados = c["items"][:25 if c["base"] == "Crossref" else 50]
    n = {clave(i.get("titulo")) for i in revisados} - vistos
    nuevos |= n
    if c["total"]:
        filas.append({"Cadena": c["cadena"], "Base": c["base"], "Resultados 26/10": antes.get((c["cadena"], c["base"])),
                      "Resultados 15/11": c["total"], "Títulos nuevos revisados": len(n)})
mostrar(pd.DataFrame(filas))

vistas = {clave(p.get("title")) for s in citas["semillas"].values() for t in ("citas", "referencias") for p in s[t]}
citas_nuevas = {clave(p.get("title")) for s in citas2["semillas"].values() for t in ("citas", "referencias") for p in s[t]} - vistas
repos_vistos = {i["repo"] for c in repos1["consultas"] for i in c["items"]}
glue("n_nuevos", len(nuevos), display=False)
glue("n_citas_nuevas", len(citas_nuevas), display=False)
glue("n_repos_nuevos", len({i["repo"] for c in repos2["consultas"] for i in c["items"]} - repos_vistos), display=False)
```

Aparecieron {glue:text}`n_nuevos` títulos que no estaban en la primera búsqueda. Casi todos son aplicaciones de bosques aleatorios o de reglas de puntuación a otros problemas (incendios, salud, energía, educación) que comparten palabras con las cadenas. Cuatro son relevantes según el criterio anterior y ninguno cambia la declaración de novedad:

- dos aplicaciones de árboles y bosques a la calidad del vino publicadas en 2026 (una con árbol de decisión y bosque aleatorio sobre el vino tinto, otra con selección de variables y clasificadores estándar), que tratan la nota como clase o la binarizan sin usar los niveles;
- el artículo del paquete OGBoost, el *boosting* ordinal con variable latente que ya figuraba en la primera búsqueda como preprint, y que predice la clase ordinal;
- una revisión de 2025 sobre reglas de puntuación propias para estimar y evaluar pronósticos, que no las usa como criterio de partición de árboles.

La búsqueda por citación sumó {glue:text}`n_citas_nuevas` títulos nuevos (trabajos que citan a los seis más cercanos, sobre todo aplicaciones a otros dominios), ninguno relevante. En GitHub aparecieron {glue:text}`n_repos_nuevos` repositorios nuevos; el único cercano compara la nota del vino tinto tratada como ordinal o como categórica, sin bosques ponderados por umbral ni combinación de umbrales.

## Trabajos más cercanos y diferencias

```{code-cell} ipython3
:tags: [hide-input]
rel = pd.read_csv(pathlib.Path.cwd().parent / "data" / "app" / "trabajos_relacionados.csv")
mostrar(rel.rename(columns={"metodo": "Método", "familia": "Familia", "objetivo": "Qué predice",
                            "informacion_ordinal": "Usa la respuesta ordinal", "agrega_umbrales": "Combina umbrales vecinos",
                            "diferencia": "Qué es nuevo en el BOF"}).drop(columns=["referencia"]))
```

Lo que el Bosque Ordinal Focalizado **conserva** de estos métodos son los árboles extremadamente aleatorizados {cite:p}`geurts2006`, el bagging {cite:p}`breiman2001` y la idea de modelar las probabilidades acumuladas de una respuesta ordinal {cite:p}`frank2001,mccullagh1980,lechner2024`. Lo **nuevo** son tres piezas que responden a un problema distinto, predecir un evento binario definido por un corte de la respuesta ordinal:

1. Un criterio de partición que pondera las impurezas de los indicadores acumulados con un núcleo centrado en el umbral del evento. Con ancho cero es el criterio de Gini del evento binario; con ancho infinito es el Gini ordinal de {cite:t}`piccarreta2008`. Es el puntaje de Brier ponderado por umbral, la versión discreta del CRPS ponderado de {cite:t}`gneiting2011`, que hasta ahora se usaba para evaluar pronósticos y no para construir árboles.
2. Un puntaje que combina las probabilidades acumuladas de los umbrales vecinos del evento con un segundo núcleo, en lugar de quedarse con la probabilidad de un solo umbral (Ordered Forest, Frank y Hall) o con la media de unos puntajes de clase (Ordinal Forest, fabOF).
3. La calibración del puntaje combinado con los casos fuera de bolsa, que devuelve una probabilidad del evento sin datos adicionales.

Los métodos existentes no resuelven la limitación identificada (la pérdida de información al binarizar la nota) porque su objetivo es la clase ordinal: optimizan la exactitud ordinal o el error de clasificación ponderado, y para obtener P(nota ≥ 7) usan un único umbral, con la varianza que eso implica, o una transformación de puntajes que no está centrada en el evento.

## Declaración de novedad

> Según la búsqueda descrita (cuatro bases bibliográficas, ocho cadenas, búsqueda por citación desde seis trabajos y revisión de repositorios, realizada el 26 de octubre de 2026 y repetida el 15 de noviembre de 2026), no se encontraron estudios que apliquen a la clasificación de vinos buenos del conjunto Wine Quality un bosque que (i) elija las particiones con una impureza acumulada ponderada por un núcleo centrado en el umbral del evento, (ii) combine las probabilidades acumuladas de los umbrales vecinos para puntuar el evento y (iii) calibre ese puntaje fuera de bolsa. Los trabajos más cercanos son el Ordered Forest {cite:p}`lechner2024`, que estima cada probabilidad acumulada con un bosque separado y no combina umbrales; los árboles ordinales sin puntajes {cite:p}`tutz2022`, que combinan modelos binarios para predecir la clase ordinal; Ordinal Forest y fabOF {cite:p}`hornung2020,buczak2024fabof`, que usan puntajes de clase optimizados; y la descomposición de {cite:t}`frank2001`, que entrena un clasificador por umbral. En el conjunto Wine Quality, la literatura encontrada usa bosques y Extra-Trees como clasificadores estándar o la regresión ordinal clásica, pero no este mecanismo.

La declaración tiene el alcance de la búsqueda: no se revisaron bases de pago (Scopus, Web of Science) ni literatura gris fuera de los repositorios consultados, y el texto completo solo se leyó cuando el resumen no permitía decidir.
