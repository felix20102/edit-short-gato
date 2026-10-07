# Montaje · Ranking mejores desastres del año

## Versión sencilla (la pedida)

Clips originales tal cual (imagen y sonido, sin título traducido, zooms, repeticiones ni logo) y, entre clip y clip, el gato hablando sobre papel claro, con su voz y subtítulos. Sin efectos ni sonidos añadidos.

```
cd montaje
python3 herramientas/montar_simple.py salida/ranking_desastres_simple.mp4
```

Resultado: `salida/ranking_desastres_simple.mp4` (35,9 s).

| Tramo | Contenido |
|---|---|
| 0,00–2,57 | Clip puesto 5 (orig. 0,00–2,56) |
| 2,57–7,73 | Gato: «Soy el perito del seguro. Hay que reconstruir el accidente. A ver, trae.» |
| 7,73–11,20 | Clip puesto 4 (orig. 5,67–9,13) |
| 11,20–16,20 | Gato en primer plano: «Señorita, para el parte: ¿esto qué es exactamente?» · 0,8 s de silencio · «Bizcocho.» |
| 16,20–19,57 | Clip puesto 3 (orig. 12,80–16,17) |
| 19,57–23,00 | Gato: «Ese partido lo cubrí yo, ¿eh? Me pusieron de pelota.» (cambia de pose en «pelota») |
| 23,00–24,97 | Clip puesto 2 (orig. 20,00–21,97) |
| 24,97–29,00 | Gato: «Revisión de la caseta. Me han dado chaleco, así que aquí no me pue—» (corte seco) |
| 29,00–31,50 | Clip puesto 1 (orig. 24,60–27,10) |
| 31,50–35,87 | Gato chamuscado: «Estoy bien, ¿eh? Estoy bien.» · «Lo he probado para el parte.» |

## Versión completa (con efectos)

```
cd montaje
python3 herramientas/extraer_poses.py        # recorta las poses de recursos/hojas/
python3 herramientas/montar.py salida/ranking_desastres.mp4
```

Lo que falte en `recursos/` se sustituye por un provisional y aparece listado al terminar.

| Carpeta | Archivos esperados |
|---|---|
| `recursos/fuente/` | `ssstik.io_memepremeo_1791393753702.mp4` |
| `recursos/hojas/` | Tus dos hojas de poses (de ahí salen las de `recursos/poses/`) |
| `recursos/poses/` (PNG con transparencia) | `perito_habla` (hoja 2 · 6), `perito_golpe` (hoja 2 · 4), `perito_serio` (hoja 2 · 1), `seco` (hoja 1 · fila 3, col. 1), `perito_confuso` (hoja 2 · 3), `brazos_cruzados` (hoja 1 · fila 2, col. 5), `espaldas` (nueva), `chamuscado` y `chamuscado_erizado` (nuevas) |
| `recursos/fondos/` | `papel_arrugado`, `papel`, `pista`, `feria` (1080×1920) |
| `recursos/props/` | `portapapeles`, `acreditacion`, `bate`, `tirita`, `pelota_beisbol`, `venda`, `chaleco`, `chaleco_quemado`, `pelota_feria`, `cable`, `hoja_parte` |
| `recursos/sfx/` | `whoosh`, `pop`, `blip`, `pum_suave`, `pum_seco`, `pum_fuerte`, `bonk`, `boing`, `golpe`, `chisporroteo`, `zap` (.wav o .mp3) |
| `recursos/logo.png` | Logo del canal |

Encuadres, zooms, título traducido y anclas de los accesorios en cada pose: `ajustes.json`.
Requisitos: ffmpeg, Python 3 con `numpy`, `Pillow` y `opencv-python-headless`.

Emoji 📋: Twemoji (CC-BY 4.0). Fuente del título: Roboto Condensed (Apache 2.0).
