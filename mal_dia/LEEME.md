# Ranking mejores momentos de mal día · Miau con Criterio

```
python3 mal_dia/herramientas/montar.py                  # vídeo → mal_dia/salida/ranking_mal_dia.mp4
python3 mal_dia/herramientas/montar.py --hoja 5.0,13.5   # hoja de fotogramas de control
```

Necesita `mal_dia/recursos/fuente/ssstik.io_memepremeo_1791465337459.mp4` (no se sube al repositorio), ffmpeg, numpy, Pillow y opencv-python-headless. Las poses salen de `montaje/recursos/poses/catalogo/`.

## Qué hace

- **Clips:** el original con su sonido. El título se traduce con la misma letra y los mismos colores («Ranking **Mejores** / Momentos de **Mal Día**»). El ranking de la izquierda queda tal cual; en las repeticiones con zoom no se amplía.
- **Tarjetas del gato** (estilo de las referencias): personaje grande, reencuadres, subtítulo de una palabra en colores, cortes secos, flashes de 2 fotogramas, música de fondo y SFX.
- **Narración:** el archivo de ElevenLabs troceado por frases. **Ninguna palabra se corta**; en la tarjeta 3 «perfecto» se oye entero y el vaso revienta justo después.

## Línea de tiempo (46,2 s)

| Tramo | Contenido |
|---|---|
| 0,00–3,20 | Clip 5 (orig. 0,00–3,20) |
| 3,20–4,20 | Repetición 5 al 60 % con zoom al móvil |
| 4,20–8,93 | Gato 1 · rejilla · «Asesor de la suerte. Con este trébol, el móvil nunca se cae.» Se le cuela el móvil y pierde una hoja (4 → 3) |
| 8,93–11,27 | Clip 4 (orig. 6,00–8,35) |
| 11,27–12,27 | Repetición 4 al 60 % con zoom a la persiana |
| 12,27–17,07 | Gato 2 · papel · «Yo conozco esa persiana. Ayer intenté pasar agachado.» Se gira, corte a la prueba (rayas y oreja doblada) · 0,5 s · «Agaché poco.» |
| 17,07–19,80 | Clip 3 A (orig. 9,10–10,30) + B (orig. 12,90–14,45) |
| 19,80–20,70 | Repetición 3 al 55 % con zoom al vaso |
| 20,70–25,17 | Gato 3 · cafetería · «A ver, dejadme a mí. Palillo arriba, golpe seco y queda perfecto.» El vaso revienta (3 → 2 hojas) |
| 25,17–27,97 | Clip 2 A (orig. 17,60–20,40) |
| 27,97–29,07 | Repetición 2 al 55 % con zoom a la caída |
| 29,07–30,87 | Clip 2 B (orig. 25,80–27,60) |
| 30,87–35,43 | Gato 4 · nieve · «Tranquilos, yo solo grababa. Al que graba nunca le hacen nada.» Placaje del tío recortado del clip (2 → 1 hoja) |
| 35,43–38,03 | Clip 1 (orig. 29,10–31,70) |
| 38,03–39,23 | Repetición 1 al 50 % con zoom al plancha |
| 39,23–43,80 | Gato 5 · barro · «Estoy bien, ¿eh? Estoy bien. Aún me queda una hoja.» Se cae la última hoja (1 → 0) |
| 43,80–46,20 | Cierre sin voz · gato negro cruzando · viñeta y «dun dun DUUUN» |

## Recursos

- Poses: tu hoja básica (fila 1 col. 1, fila 3 col. 1, fila 1 col. 5, fila 2 col. 3, fila 1 col. 4 y fila 4 col. 5).
- Recortes del propio vídeo: el tío de la nieve (orig. 26,5, GrabCut guiado) y las máscaras del ranking.
- Dibujados por el script: fondos (papel arrugado, rejilla, cafetería, jardín nevado, barro), trébol, móvil, palillo, vaso de bubble tea, tapioca, manchas, rayas de persiana, oreja doblada, cartel y gato negro (tu pose en negro).
- Sintetizados por el script: música de fondo y todos los SFX.
- Emoji 🍀: Twemoji (CC-BY 4.0).
