# Ranking mejores momentos de mal día · Miau con Criterio

```
python3 mal_dia/herramientas/montar.py                  # vídeo → mal_dia/salida/ranking_mal_dia.mp4
python3 mal_dia/herramientas/montar.py --hoja 5.0,13.5   # hoja de fotogramas de control
```

Necesita `mal_dia/recursos/fuente/ssstik.io_memepremeo_1791465337459.mp4` (no se sube al repositorio), ffmpeg, numpy, Pillow y opencv-python-headless. Las poses salen de `montaje/recursos/poses/catalogo/`.

## Qué hace

- **Clip y luego la frase del gato**, sin zooms ni repeticiones en los clips.
- **Clips:** el original con su sonido. El título se traduce con la misma letra y colores («Ranking **Mejores** / Momentos de **Mal Día**»). El ranking de la izquierda queda tal cual.
- **Tarjetas del gato:** el papel arrugado de los vídeos de referencia, gato en plano normal, subtítulo de una palabra en colores, cortes secos, música de fondo y SFX.
- **Narración:** ninguna palabra se corta («perfecto» se oye entero).

## Línea de tiempo (41,0 s)

| Tramo | Contenido |
|---|---|
| 0,00–3,20 | Clip 5 (orig. 0,00–3,20) |
| 3,20–7,93 | Gato 1 · «Asesor de la suerte. Con este trébol, el móvil nunca se cae.» Se le cae el móvil y pierde una hoja (4 → 3) |
| 7,93–10,27 | Clip 4 (orig. 6,00–8,35) |
| 10,27–15,07 | Gato 2 · «Yo conozco esa persiana. Ayer intenté pasar agachado.» Se gira y sale con rayas y la oreja doblada · «Agaché poco.» |
| 15,07–17,80 | Clip 3 (orig. 9,10–10,30 y 12,90–14,45) |
| 17,80–22,27 | Gato 3 · «A ver, dejadme a mí. Palillo arriba, golpe seco y queda perfecto.» Revienta el vaso (3 → 2) |
| 22,27–26,87 | Clip 2 (orig. 17,60–20,40 y 25,80–27,60) |
| 26,87–31,43 | Gato 4 · «Tranquilos, yo solo grababa. Al que graba nunca le hacen nada.» Placaje (2 → 1) |
| 31,43–34,03 | Clip 1 (orig. 29,10–31,70) |
| 34,03–38,60 | Gato 5 · «Estoy bien, ¿eh? Estoy bien. Aún me queda una hoja.» Se cae la última hoja (1 → 0) |
| 38,60–41,00 | Cierre sin voz · gato negro · «dun dun DUUUN» |

## Recursos

- Poses: tu hoja básica (fila 1 col. 1, fila 3 col. 1, fila 1 col. 5, fila 2 col. 3, fila 1 col. 4 y fila 4 col. 5).
- Recortes del propio vídeo: el tío de la nieve (orig. 26,5, GrabCut guiado) y las máscaras del ranking.
- Fondo: el papel arrugado de los vídeos de referencia (`recursos/fondo_papel.png`).
- Dibujados por el script: trébol, móvil, palillo, vaso de bubble tea, tapioca, manchas, rayas de persiana, oreja doblada, cartel y gato negro (tu pose en negro).
- Sintetizados por el script: música de fondo y todos los SFX.
- Emoji 🍀: Twemoji (CC-BY 4.0).
