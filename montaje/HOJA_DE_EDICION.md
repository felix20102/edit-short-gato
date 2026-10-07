# Hoja de edición · «Ranking mejores desastres del año»

Canal: Miau con Criterio · 1080×1920 · 30 fps · Solo cortes secos
Vídeo fuente: `ssstik.io_memepremeo_1791393753702.mp4` (31,3 s, 576×1024, escalado ×1,875 a 1080×1920).

## Estado del montaje

| Pieza | Estado |
|---|---|
| Voz del gato (7 tomas) | ✅ Recibida, medida y colocada → `voz_gato_montada.wav` |
| Subtítulos | ✅ `subtitulos.ass` (estilo del canal) y `subtitulos.srt` |
| Hoja de edición con tiempos reales | ✅ Este documento |
| Script de montaje | ✅ `herramientas/montar.py` monta el vídeo entero con los recursos que haya en `recursos/` |
| Borrador completo | ✅ `salida/ranking_desastres_borrador.mp4`: clips reales, título traducido, ranking original, voz, subtítulos, efectos y SFX; gato, fondos y props provisionales |
| Vídeo fuente | ✅ Recibido y revisado fotograma a fotograma |
| Poses en archivos separados (PNG con transparencia) | ❌ Solo llegaron como imagen en el chat, no como archivo |
| Poses nuevas, fondos, props, logo | ❌ No recibidos (ver lista al final) |
| **Vídeo final** | ⏳ Montado con el vídeo real; faltan los PNG del gato, fondos y props (hoy provisionales) |

## Cambio de duración: 35,5 s → 40,6 s (+5,1 s)

Las locuciones son más largas que las tarjetas del guion. He conservado las palabras y las pausas grabadas, así que las tarjetas se alargan y los clips se desplazan. Los clips y sus repeticiones no cambian de duración.

| Tarjeta | Guion | Voz real (+ pausas y remates del guion) | Montaje |
|---|---|---|---|
| Gato 1 | 3,50 s | 4,66 s de voz + bate, golpe y tirita | 5,52 s (+2,02) |
| Gato 2 | 3,50 s | 3,18 s + 0,8 s de silencio + «Bizcocho» 0,47 s + sello | 5,10 s (+1,60) |
| Gato 3 | 3,40 s | 3,62 s de voz útil | 3,49 s (+0,09) |
| Gato 4 | 3,00 s | 3,87 s hasta «pue—» | 4,01 s (+1,01) |
| Gato 5 | 3,50 s | 2,17 s + 0,4 s + 1,62 s | 3,88 s (+0,38) |
| Cierre | 2,00 s | sin voz | 2,00 s |

**Opción para volver a ~37 s:** acortar las pausas internas de las tomas (gato_1 0,43→0,20 s y 0,32→0,15 s; gato_2 0,44→0,25 s y 0,32→0,15 s; gato_4 0,47→0,25 s; gato_5 0,33→0,15 s y 0,24→0,12 s). Se ganan unos 1,3 s sin tocar ninguna palabra. No lo he aplicado: dímelo si lo quieres.

## Mapa de tomas de voz

| Archivo | Frase exacta | Voz dentro del archivo | Colocado en |
|---|---|---|---|
| gato_1 | «Soy el perito del seguro. Hay que reconstruir el accidente. A ver, trae.» | 0,03–4,66 | 3,65 |
| gato_2 | «Señorita, para el parte: ¿esto qué es exactamente?» | 0,00–3,18 | 12,40 |
| gato_3 | «Bizcocho.» | 0,13–0,60 | 16,25 |
| gato_4 | «Ese partido lo cubrí yo, ¿eh? Me pusieron de pelota.» | 0,07–2,92 | 20,70 |
| gato_5 | «Revisión de la caseta. Me han dado chaleco, así que aquí no me pue—» | 0,03–3,87 (cortado) | 27,25 |
| gato_6 | «Estoy bien, ¿eh? Estoy bien.» | 0,20–1,89 | 34,80 |
| gato_7 | «Lo he probado para el parte.» | 0,05–1,33 | 37,04 |

Las pausas entre frases salen del análisis de silencios del audio (fiables). Los límites entre palabras dentro de una misma frase (por ejemplo, el inicio de «exactamente», «pelota», «pue» o «parte») están estimados por la envolvente de volumen, con un margen de unos ±0,08 s. **Hay que confirmarlos de oído** en el editor antes de fijar los efectos que van sobre esas palabras.

## Poses: equivalencia con tus hojas

Hoja 1 (cuadrícula de 4×5, sin corbata) = **F**ila/**C**olumna. Hoja 2 (perito con corbata roja) = letra o número impreso.

| Uso en el guion | Pose propuesta | Motivo |
|---|---|---|
| Gato 1 · de frente hablando | Hoja 2 · **6** (sonriendo con portapapeles) | Ya lleva corbata y portapapeles: es el perito |
| Gato 1 · tras el golpe | Hoja 2 · **4** (agarrándose la cabeza, rayitas) | Remate del bate sin dibujar pose nueva |
| Gato 2 · «Señorita…» | Hoja 2 · **1** recortada en primerísimo plano (la mesa queda fuera del encuadre) | Serio, con el portapapeles en la mano |
| Gato 2 · «Bizcocho.» | Hoja 1 · **F3C1** (párpados caídos) | Mirada seca a cámara |
| Gato 3 · de espaldas | **NUEVA** | No hay ninguna de espaldas |
| Gato 3 · tras «pelota» | Hoja 2 · **3** (confuso, corbata) | Corte seco a frente |
| Gato 4 · brazos cruzados | Hoja 1 · **F2C5** | Brazos cruzados y gesto de suficiencia |
| Gato 5 y cierre · chamuscado | **NUEVA**. Base: Hoja 2 · **B** (pelo revuelto) | Hay que añadir el negro, el humo, las gafas rotas, el cable y el pulgar arriba |

Problema: las poses de la hoja 1 no llevan corbata y las de la hoja 2 sí. En el puesto 2 el chaleco tapa el pecho y no se nota. En el resto de tarjetas uso la hoja 2.

## Pantalla fija durante clips y repeticiones

*Cambio pedido: el ranking del original y el estilo del título se mantienen.*

Medidas tomadas del original:
- Franja negra superior: y 0–375. Banda de vídeo: y 375–1815. Franja negra inferior: y 1815–1920.
- Título original: «Ranking Funniest / Scribble Moments». Letra condensada en negrita, sin contorno. Bases de línea en y = 250 y 343. Colores: blanco + rojo #F60F10 / amarillo #ECFF00 + blanco.
- Ranking original: a la izquierda, en x 0–580 e y 500–1500, con etiquetas en inglés (Trickshot 💀, Baking 🤩, Play ball 😳, On target 👀, The end 😱).

Qué se hace:
- **Título:** solo se traduce, con el mismo tamaño, posición, tipografía (Roboto Condensed Bold, la más parecida disponible) y patrón de color: «Ranking» blanco + «Garabatos» rojo / «Más» amarillo + «Graciosos» blanco. Se puede cambiar en `ajustes.json → titulo`.
- **Ranking:** el original queda **sin tocar**. En los zooms de repetición se borra antes de ampliar y se repone sin ampliar, con una máscara sacada de los fotogramas en negro del original. Así se ve fijo y nítido.
- **Zooms:** solo amplían la banda de vídeo. Centros: P5 cara del niño (500, 880), P4 ojos (600, 780), P3 morro del perro (560, 820), P2 encargado (880, 950), P1 boca y destello (640, 900).
- **Logo «Miau con Criterio»:** al 60 %, centrado en la franja negra inferior (y = 1867), así no tapa la acción.
- **Subtítulos:** crema #FAF4E6, contorno marrón #332314 de 7 px y palabra clave en #FFD400. Solo aparecen en las tarjetas del gato. Altura: 1420 (gato 1), 1720 (gatos 2, 4 y 5) y 330 (gato 3).
- **Recorte de la niña de reojo:** sale del fotograma orig. 8,5 s, caja (600, 560)–(1000, 960).
- Los dibujos a lápiz del original no se usan: los cortes de origen ya los excluyen. Comprobado fotograma a fotograma.

## Línea de tiempo

Tiempos en segundos del montaje final. Ajustar al fotograma más cercano a 30 fps (1 f = 0,033 s).

| Entrada–salida | Vídeo base | Frase exacta | Tipo | Pose | Movimiento | Efecto visual (elemento · inicio · duración) | Subtítulo | SFX | Ranking |
|---|---|---|---|---|---|---|---|---|---|
| **0,00–2,36** | P5 clip. orig. 0,20–2,56. Lanza, gira y se da en la cara (orig. 2,53 → 2,33) | — | Clip | — | — | — | — | Audio original | Original |
| **2,36–3,48** | Repetición orig. 2,00–2,56 al 50 % | — | Clip | — | — | Zoom a la cara del niño, del 100 % al 160 %, 2,36–2,70; se mantiene | — | Audio original al 50 % o silenciado si suena raro | Original |
| **3,48–9,00** | — | (ver sub-filas) | Escena aparte · papel arrugado | Hoja 2 · 6, plano entero pequeño a la izquierda (≈ 35 % del ancho) | Pop 3,48–3,63 (escala 0→110→100 %) | — | — | whoosh corto 3,48 | — (tarjeta a pantalla completa) |
| 4,20 | | «…perito…» | | | | Cartel «PERITO DE SEGUROS 📋» cae desde arriba 4,20–4,40 con rebote hasta 4,55 | SOY EL **PERITO** 3,68–4,45 | PUM suave 4,40 | |
| 3,48 | | | | | | Portapapeles real en la pata y acreditación al cuello, desde 3,48 | DEL SEGURO 4,45–5,15 · HAY QUE RECONSTRUIR 5,47–6,22 · EL ACCIDENTE 6,22–7,12 · A VER, 7,56–7,90 | — | |
| 7,96 | | «trae.» | | | | Bate real en la pata, pop 7,96–8,06 | **TRAE.** 7,96–8,33 | pop 7,96 | |
| 8,17–8,33 | | | | | | El bate da una vuelta (360°) en 5 f y golpea la cara en 8,33 | — | bonk metálico 8,33 | |
| 8,33 | | | | → Hoja 2 · 4, gafas torcidas 12° | | Flash rojo de 3 f (8,33–8,43) · temblor ±12 px 8,33–8,58 | — | | |
| 8,60 | | | | | Rebote mínimo | Tirita en la nariz, pop 8,60–8,70 (**se queda hasta el final**) | — | blip 8,60 | |
| **9,00–10,50** | P4 clip A. orig. **5,67–7,17** (el guion decía 5,60, pero 5,60–5,63 es negro en el original). Vuelca el vaso | — | Clip | — | — | — | — | Audio original | Original |
| **10,50–11,60** | P4 clip B. orig. 7,80–8,90. Mirada de reojo | — | Clip | — | — | — | — | Audio original | Original |
| **11,60–12,30** | Repetición orig. 8,20–8,90 a velocidad normal | — | Clip | — | — | Zoom rápido a los ojos, del 100 % al 220 %, 11,60–11,85 | — | Audio original | Original |
| **12,30–17,40** | — | (ver sub-filas) | Escena aparte · papel | Hoja 2 · 1 en primerísimo plano descentrado a la izquierda, con las orejas cortadas por arriba. Portapapeles y tirita | Desliza desde la izquierda 12,30–12,50, con desenfoque de movimiento | — | SEÑORITA, 12,40–13,02 · PARA EL PARTE: 13,34–13,97 · ¿ESTO QUÉ ES 14,41–14,95 | whoosh 12,30 | — (tarjeta a pantalla completa) |
| 14,95 | | «exactamente» | | | | Recorte de la niña de reojo (fotograma orig. ≈ 8,5) entra con pop por el borde derecho 14,95–15,10 y se queda · viñeta oscura del 0 al 60 %, 14,95–15,58 | EXACTAMENTE? 14,95–15,58 | — | |
| 15,58–16,38 | | **Silencio real 0,8 s** | | → Hoja 1 · F3C1 (corte seco en 15,58) | Quieto | — | — (sin subtítulo) | Nada | |
| 16,38 | | «Bizcocho.» | | | | Sello verde «APROBADO» cae sobre el portapapeles 16,72–16,80 · temblor ±6 px 16,80–16,95 | **BIZCOCHO.** 16,38–16,90 | PUM seco 16,80 | |
| **17,40–18,30** | P3 clip A. orig. 13,00–13,90. Niña con bate y perro esperando | — | Clip | — | — | — | — | Audio original | Original |
| **18,30–19,57** | P3 clip B. orig. 14,90–16,17. Bate en el morro (orig. ~16,0 → ~19,40) | — | Clip | — | — | — | — | Audio original | Original |
| **19,57–20,61** | Repetición orig. 15,65–16,17 al 50 % | — | Clip | — | — | Zoom al morro, del 100 % al 170 %, 19,57–19,90 | — | Audio original | Original |
| **20,61–24,10** | — | «Ese partido lo cubrí yo, ¿eh? Me pusieron de…» | Escena aparte · pista deportiva con valla verde (desenfoque gaussiano de 8 px) | **NUEVA**, de espaldas mirando por encima del hombro; plano medio a la derecha. Tirita | Pop 20,61–20,76 | — | ESE PARTIDO 20,77–21,40 · LO CUBRÍ YO, ¿EH? 21,40–22,05 · ME PUSIERON 22,52–23,12 | pop 20,61 | — (tarjeta a pantalla completa) |
| 23,20 | | «pelota.» | | → Hoja 2 · 3 (corte seco, sin animación) | Rebote 23,37–23,57 (escala 100→92→104→100 %) | Pelota de béisbol real pegada en la frente, aparece en 23,20 · venda con mordiscos en la oreja, pop 23,37 | DE **PELOTA.** 23,12–23,62 | boing 23,20 · blip 23,37 | |
| **24,10–26,07** | P2 clip. orig. 20,00–21,97. Pelotazo al encargado de chaleco amarillo | — | Clip | — | — | — | — | Audio original | Original |
| **26,07–27,11** | Repetición orig. 21,45–21,97 al 50 % | — | Clip | — | — | Zoom al encargado, del 100 % al 160 %, 26,07–26,40 | — | Audio original | Original |
| **27,11–31,12** | — | «Revisión de la caseta. Me han dado chaleco, así que aquí no me pue—» | Escena aparte · caseta de feria con latas y peluches (desenfoque de 8 px) | Hoja 1 · F2C5 + chaleco amarillo reflectante + tirita, pelota en la frente y venda | Desliza desde abajo 27,11–27,31, con desenfoque | — | REVISIÓN 27,28–27,95 · DE LA CASETA. 27,95–28,39 · ME HAN DADO 28,71–29,18 · **CHALECO,** 29,18–29,64 · ASÍ QUE AQUÍ 29,88–30,40 · NO ME PUE— 30,40–31,12 | whoosh 27,11 | — (tarjeta a pantalla completa) |
| 30,95–31,12 | | «pue—» | | | | Pelota de feria real cruza de izquierda a derecha en 5 f (30,95–31,12) con desenfoque de movimiento · flash rosa de 3 f (31,02–31,12) en el impacto | | golpe seco 31,02 | |
| **31,12** | | | | | | **CORTE SECO de vídeo y voz** (la toma gato_5 ya va cortada en este punto) | | | |
| **31,12–33,62** | P1 clip. orig. 24,60–27,10. Muerde el cable (chispa orig. ~26,9 → ~33,42) | — | Clip | — | — | — | — | Chispazo original subido a −4 dB | Original |
| **33,62–34,72** | Repetición orig. 26,55–27,10 al 50 % | — | Clip | — | — | Zoom a la boca y el destello, del 100 % al 170 %, 33,62–33,95 | — | Audio original | Original |
| **34,72–38,60** | — | «Estoy bien, ¿eh? Estoy bien.» · [0,4 s] · «Lo he probado para el parte.» | Escena aparte · papel | **NUEVA** chamuscada, con pulgar arriba, cable en la boca y todos los accesorios | Desliza desde abajo 34,72–34,97 dejando humo | Viñeta oscura del 0 % (34,72) al 70 % (40,60), lineal | ESTOY BIEN, ¿EH? 35,00–35,76 · ESTOY BIEN. 36,10–36,69 · LO HE PROBADO 37,09–37,95 | chisporroteo corto 34,72 | — (tarjeta a pantalla completa) |
| 38,16 | | «parte.» | | | Rebote 38,16–38,40 | Chispa desde la oreja, 38,16–38,36 · pelos más erizados (pose B o deformar 105 %) | PARA EL **PARTE.** 37,95–38,40 | zap 38,16 | |
| **38,60–40,60** | Cierre sin voz | — (**sin voz del gato**) | Escena aparte · mismo fondo | Misma pose | Hoja «PARTE DE SINIESTRO · Solicitante: el perito», pop 38,60–38,80 | — | — | blip 38,60 | — (tarjeta a pantalla completa) |
| 38,80–39,10 | | Silencio real 0,3 s | | | Quieto | — | — | Nada | |
| 39,10–39,20 | | | | | | Sello rojo «RECHAZADO» cae sobre la hoja y media cara (impacto en 39,20) · temblor ±14 px 39,20–39,45 | — | **PUM fuerte −6 dB** 39,20 | |
| 39,45–40,60 | | | | | Quieto mirando a cámara | — | — | Nada | FIN |

## Mezcla de audio

- Voz: `voz_gato_montada.wav`, pico −2,1 dBFS. En la mezcla final, normalizar a −14 LUFS integrados con pico real ≤ −1 dBTP.
- Audio original de los clips: a −6 dB respecto a la voz. Va a 0 dB en los golpes (orig. 2,53, 16,0 y 21,9) y el chispazo (orig. 26,9), que sube a −4 dB.
- No hay música en el guion. Si se añade, bajarla a −24 dB durante las tarjetas del gato.
- SFX entre −12 y −8 dB, salvo el «PUM» del cierre (−6 dB). Ninguno coincide con una sílaba importante, excepto el golpe seco de 31,02, que corta a propósito «pue—».

## Recursos que faltan para montar

1. El vídeo fuente `ssstik.io_memepremeo_1791393753702.mp4`.
2. Las poses como PNG con fondo transparente, una por archivo: Hoja 2 · 1, 3, 4, 6 y B, y Hoja 1 · F2C5 y F3C1. Las hojas me llegaron como imagen en el chat, pero no como archivo.
3. Poses nuevas: de espaldas mirando por encima del hombro, y chamuscada con pulgar arriba.
4. Fondos: papel arrugado, pista deportiva con valla verde y caseta de feria.
5. Props (PNG): portapapeles, acreditación, bate, tirita, pelota de béisbol, venda con mordiscos, chaleco amarillo, pelota de feria, cable naranja y hoja «PARTE DE SINIESTRO».
6. Logo «Miau con Criterio».
7. SFX: whoosh, PUM suave, pop, bonk metálico, blip, boing, golpe seco, chisporroteo, zap y PUM fuerte.
8. Tipografía gruesa (los subtítulos usan Montserrat Black; se puede cambiar en `subtitulos.ass`).

Los textos («PERITO DE SEGUROS 📋», «APROBADO», «RECHAZADO» y el título traducido) los genero yo. El recorte de la niña sale del propio clip.
