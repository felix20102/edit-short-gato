# Montaje · Ranking mejores desastres del año

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
