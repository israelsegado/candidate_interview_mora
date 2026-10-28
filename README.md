# Prueba técnica: motor de reglas de marca Smiley

Bacci Sourcing & Consulting · Proyecto Mora AI

Puedes usar modelos preentrenados, OCR y asistentes de IA, y subirles este material, solo para esta prueba. Si tienes dudas, escríbenos a [yagotobiosouto@gmail.com](mailto:yagotobiosouto@gmail.com).

## Qué recibes

- `faces/` y `wordmarks/`, cada una con `Approved/` y `Rejected/`. El motivo de cada rechazo está en `Rejected/rejection_reasons.txt`.
- `test_set/`: más imágenes, sin respuestas. Pásalas por tu programa y revisa tú el resultado.
- `review.py`: el punto de entrada, por implementar.
- `tests/`: tests que comparan tu salida con las respuestas de `tests/expected.csv`.

## Qué tienes que construir

**1. Proceso por lotes.** Lo ejecutaremos tal cual sobre imágenes que no has visto:

```bash
python review.py faces/ wordmarks/ -o results.csv
```

Recorre las carpetas de forma recursiva y escribe una fila por imagen en `results.csv` y en `results.xlsx` (mismo nombre, junto al CSV). El Excel es lo que abre el equipo de negocio. `review.py` es solo la puerta de entrada: por dentro puede llamar a lo que quieras.

**2. Aplicación para alguien no técnico.** Tiene que poder arrastrar o elegir imágenes, ver para cada una el tipo, el programa, el resultado de cada regla y el motivo, y descargar el Excel. Usa la tecnología que quieras, no tiene que ser Python, siempre que esté al servicio de quien la usa. Debe usar el mismo motor de reglas que `review.py` y arrancar con un comando que documentes. Suma que enseñe por qué decide, por ejemplo marcando sobre la imagen los ojos y los hoyuelos que detecta.

**3. Vídeo.** Qué has hecho y por qué, una demo de la app, dónde falla y qué harías después.

## Formato de salida

| columna   | valores                       | qué es                                         |
|-----------|-------------------------------|------------------------------------------------|
| `file`    | nombre o ruta                 | se compara por nombre de archivo               |
| `type`    | `face` / `text` / `face+text` | cara, texto, o las dos cosas                   |
| `program` | `smiley` / `smileyworld`      | regla 1                                        |
| `verdict` | `PASS` / `FAIL`               | `FAIL` si alguna regla da `FAIL`               |
| `mouth`   | `PASS` / `FAIL` / `N/A`       | regla 2; `N/A` si `type` es `text`             |
| `eyes`    | `PASS` / `FAIL` / `N/A`       | regla 3; `N/A` si `type` es `text`             |
| `text`    | `PASS` / `FAIL` / `N/A`       | reglas 4 y 5; `N/A` si `type` es `face`        |
| `reason`  | texto libre                   | una frase que explica el veredicto             |

```csv
file,type,program,verdict,mouth,eyes,text,reason
f17_EXAMPLE_expressionfail.png,face,smiley,FAIL,PASS,FAIL,N/A,Tiene 3 ojos; una cara válida tiene 2
w11_EXAMPLE_FAIL_nodots.png,text,smiley,FAIL,N/A,N/A,FAIL,"Leído ""SW SMILEY"": faltan los puntos tras la S y la W"
```

Escribe el CSV con el módulo `csv` o equivalente, porque el motivo puede llevar comas o comillas.

## Las reglas

Hay dos programas, Smiley y SmileyWorld, y se distinguen por el texto. La cara se valida aparte: `faces/Approved/` y `faces/Rejected/` muestran qué caras valen.

1. **Programa.** `smileyworld` si la imagen lleva el texto SmileyWorld. Si no (texto S.W. Smiley o solo una cara), `smiley`.
2. **Boca.** Sonrisa grande con un hoyuelo en cada extremo: la boca acaba en un pequeño remate que se curva o cruza hacia fuera. Falla si la sonrisa es corta, si falta algún hoyuelo o si los remates no tienen forma de hoyuelo (por ejemplo, planos y solo hacia dentro).
3. **Ojos.** Exactamente dos, de cualquier estilo: óvalos, guiño, aspas, cerrados, zigzag, `> <`, pestañas, tristes. Un tercer ojo falla. El contorno puede tener cualquier forma (círculo, corazón, cuadrado). Si la cara va con el texto SmileyWorld, los ojos tienen que hacer algo, y dos óvalos estándar fallan. Sin ese texto, los óvalos estándar valen.
4. **Texto SmileyWorld.** Junto (`SMILEYWORLD`, `SmileyWorld`), apilado en dos líneas o con el mismo espacio entre todas las letras. Falla con un espacio en medio (`SMILEY WORLD`) o con un hueco doble entre letras espaciadas.
5. **Texto S.W. Smiley.** Punto tras la S y tras la W, en mayúsculas o minúsculas. Falla si falta alguno.
6. **Cara y texto juntos (`face+text`).** Se aplican todas: boca y ojos a la cara, y la regla de texto del programa al texto.

## Cómo validar

```bash
pip install -r requirements.txt
pytest                          # ejecuta review.py sobre faces/ y wordmarks/
pytest -k f17                   # una sola imagen
pytest --results=results.csv    # valida un CSV ya generado
```

Los tests comprueban el formato, que el Excel coincide con el CSV y el veredicto de cada imagen, y al final muestran un resumen de aciertos. Escribe las opciones con `=`; con un espacio, pytest puede tomar la ruta por un archivo de tests.

No hace falta que pase todo. La evaluación final usa otras imágenes, así que ajustar umbrales a estas no ayuda. Preferimos un sistema que generalice, con sus límites bien explicados.

## IA y APIs

Puedes usar Claude Code u otros asistentes con tu propia suscripción. Si tu solución llama a APIs de modelos al ejecutarse, lee las claves de un `.env` (git ya lo ignora), pon los nombres de las variables en `.env.example` y mándanos tu `.env` por correo al entregar.

La decisión tiene que salir de código que mide (geometría, texto leído) y no solo del prompt de un modelo, para que se pueda seguir por qué se tomó.

## Entrega

1. Haz un fork privado de este repositorio.
2. Sube el código, `results.csv`, `results.xlsx`, el enlace al vídeo e instrucciones para ejecutar el proceso y la app.
3. Envía el enlace del fork a [yagotobiosouto@gmail.com](mailto:yagotobiosouto@gmail.com) y comprueba que tenemos acceso.

Nos importa más que cuentes con honestidad dónde falla que un resultado inflado. Puedes dejar partes sin terminar si lo explicas.

## Cómo evaluamos

1. La solución técnica: resultados sobre imágenes nuevas y si las reglas miden lo que deben.
2. El enfoque y el diseño: cómo planteas el problema, cómo organizas el sistema y lo fácil que es la app para alguien no técnico.
3. La claridad del vídeo.
4. Lo fácil que sería seguir con el proyecto: código legible, reglas fáciles de cambiar, dependencias claras, tests.
