EDITOR DE SHORTS «MIAU CON CRITERIO» – INSTRUCCIONES DE MONTAJE

MATERIAL QUE TE PASO
- Vídeo base de Rinzurank (MP4).
- Voz del gato en MP3 (ElevenLabs).
- Guion con los puestos, las frases y los tiempos del original.
- Hoja de 20 poses de Don Miau (gato crema con gafas redondas), en 4 filas × 5 columnas.

REGLAS FIJAS
1. El ranking original NO se toca: ni se traduce, ni se tapa, ni se sustituye por otro.
2. El título de arriba solo se traduce al español, con el mismo estilo del original: barra negra, mismos colores (blanco + rosa en la línea 1, amarillo + blanco en la línea 2), tipografía gruesa (Poppins Bold) y misma posición.
3. Todo lo demás del vídeo original se queda igual, salvo lo que se indica abajo.
4. La voz tiene que sonar fluida: recorta los silencios.
5. Si el guion pide una pose que no está en la hoja, créala con el mismo gato y estilo y sigue sin preguntar.

PASO 1 – VOZ
- Detecta los tramos de voz (umbral −45 dB, ventanas de 20 ms; une huecos menores de 0,15 s).
- Deja 0,03 s de margen antes de cada tramo y 0,05 s después, con fundidos de 6 ms.
- Pausas finales: 0,03–0,05 s dentro de una frase, 0,07–0,08 s entre frases.
- Empareja cada tramo con su frase del guion. Si una frase viene en un solo bloque y conviene partirla (por ejemplo, en una coma), busca la pausa interna en la forma de onda y corta ahí.

PASO 2 – ANÁLISIS DEL VÍDEO
- Extrae todos los fotogramas y localiza los clips por los tramos negros entre ellos (brillo medio < 5 fuera del ranking).
- En cada clip, marca el momento clave: agarrón, caída, susto o grito.
- Mide la barra del título, la columna del ranking y la marca de agua.
- Mira el audio original: los gritos y golpes se conservan y la voz nunca va encima.

PASO 3 – LIMPIEZA
- Marca de agua RINZURANK: calcula su opacidad con la media de los fotogramas negros, réstala de cada fotograma y rellena el contorno restante (inpaint Telea, radio 3).
- Textos en inglés incrustados: crea una máscara con los píxeles que permanecen fijos mientras aparece el texto y cierra la máscara para cubrir toda la franja. Rellena esa zona y pega encima los píxeles del ranking tomados de un fotograma limpio. Después pon el texto en español en los mismos fotogramas, desplazado para no tapar el ranking.
- Clip muy oscuro: súbele el brillo (gamma 0,68 y +6 %).
- Quita los tramos negros entre clips.

PASO 4 – ORDEN
- Sigue el orden del guion, salvo que con ese orden el ranking original pierda filas de un clip al siguiente. En ese caso usa el orden del vídeo original, para que se llene del 5 al 1. Cada frase va siempre con su clip. Avisa del cambio.

PASO 5 – ESTRUCTURA DE CADA PUESTO
a) CLIP con su audio original y sin voz (incluye el golpe, el portazo o el grito final).
b) REPETICIÓN del momento clave a 0,45–0,6x, con zoom suave de 1,0 a 1,2. La primera mitad de la frase entra 0,15 s después del corte. Encima, gato superpuesto abajo a la derecha (400 px de alto a 1080×1920) que aparece con rebote en 0,22 s. Vibración de 0,2 s y golpe sonoro en el impacto. Audio original ralentizado a −17 dB.
c) ESCENA APARTE sobre fondo menta con textura de papel, que empieza justo con la segunda mitad de la frase. Lleva objetos dibujados que ilustran el chiste (cartel, trofeo, interruptor…). El gato entra desde la derecha. La escena dura lo que la frase más 0,4–0,8 s.
- El zoom se ancla a la izquierda y se calcula para que el ranking quede siempre entre el título y los subtítulos.
- CIERRE: último fotograma con el ranking completo nítido y el resto desenfocado y oscurecido; marco amarillo que late alrededor del ranking; gato señalándolo; frase «¿Y tú cuál habrías puesto en el número uno?».

PASO 6 – POSES (fila y columna, contando desde 0)
- Pensando r0c2 · Señalando r0c4 · Presentando r0c3 · Gafas r0c1
- Sorprendido r1c3 · Riendo r1c1 · Brazos cruzados r1c4 · Saludando r1c0
- Ojos entornados r2c0 · Brazos abiertos r2c2 · Brazos en jarra r2c4
- Triste r3c0 · Asustado r3c1 · Celebrando r3c2

PASO 7 – SUBTÍTULOS
- Palabra a palabra, uniendo las palabras de 1–2 letras con la siguiente.
- Poppins
