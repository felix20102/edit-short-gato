"""Separa las poses de las dos hojas del gato en PNG con fondo transparente.

Uso (desde montaje/):  python3 herramientas/extraer_poses.py
Crea recursos/poses/catalogo/*.png (todas) y las poses que usa el montaje.
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

HOJAS = "recursos/hojas"
SALIDA = "recursos/poses"


def recortar(rgb, x0, y0, x1, y1):
    """Recorta una celda y quita el fondo exterior sin dejar halo blanco alrededor del contorno.

    El blanco de dentro (gafas, ojos) se conserva. Los píxeles grisáceos del antialias entre el
    contorno negro y el fondo se convierten en contorno semitransparente en vez de quedar claros.
    """
    celda = rgb[y0:y1, x0:x1]
    pad = cv2.copyMakeBorder(celda, 6, 6, 6, 6, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    mx, mn = pad.max(axis=2).astype(int), pad.min(axis=2).astype(int)
    claro = ((mn > 150) & (mx - mn < 28)).astype(np.uint8)  # blanco o gris claro sin color
    relleno = claro.copy()
    cv2.floodFill(relleno, np.zeros((pad.shape[0] + 2, pad.shape[1] + 2), np.uint8), (0, 0), 2)
    fondo = relleno == 2
    figura = ~fondo
    # descarta motas sueltas y trozos de la pose vecina que asoman por los bordes
    n, etiquetas, stats, _ = cv2.connectedComponentsWithStats(figura.astype(np.uint8), 8)
    mayor = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    alto, ancho = figura.shape
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        toca = x <= 7 or y <= 7 or x + w >= ancho - 7 or y + h >= alto - 7
        if i != mayor and (area < 25 or toca):
            figura[etiquetas == i] = False
    # huecos de fondo encerrados (entre brazo y cuerpo): blanco grande → transparente
    blanco = (mn > 236) & (mx - mn < 12)  # blanco puro: el crema del gato no entra
    n, etiquetas, stats, _ = cv2.connectedComponentsWithStats((blanco & figura).astype(np.uint8), 4)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > 350:
            figura[etiquetas == i] = False
            fondo[etiquetas == i] = True
    alfa = np.where(figura, 255, 0).astype(np.float32)
    color = pad.astype(np.float32)
    # franja de antialias (3 px fuera de la figura): alfa según lo oscuro, color del contorno
    cerca = cv2.dilate(figura.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~figura
    lum = pad.mean(axis=2)
    a_borde = np.clip((215 - lum) / (215 - 55), 0, 1) * 255
    alfa[cerca] = a_borde[cerca]
    color[cerca] = (28, 24, 24)
    # el primer píxel claro pegado por dentro al fondo también se oscurece (sin halo)
    borde_int = figura & cv2.dilate(fondo.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    claros = borde_int & (lum > 120)
    alfa[claros] = np.clip((215 - lum[claros]) / (215 - 55), 0, 1) * 255
    color[claros] = (28, 24, 24)
    img = Image.fromarray(np.dstack([color, alfa]).astype(np.uint8), "RGBA")
    return img.crop(img.getbbox())


def hoja_perito():
    """Hoja con letras: A B C 1 2 / 3 4 5 6 7. Las letras de abajo se excluyen."""
    rgb = np.asarray(Image.open(os.path.join(HOJAS, "hoja_perito.webp")).convert("RGB"))
    nombres = [["A", "B", "C", "1", "2"], ["3", "4", "5", "6", "7"]]
    filas = [(0, 401), (447, 821)]
    ancho = rgb.shape[1] / 5
    out = {}
    for r, (y0, y1) in enumerate(filas):
        for c in range(5):
            out[f"perito_{nombres[r][c]}"] = recortar(rgb, int(c * ancho), y0, int((c + 1) * ancho), y1)
    return out


def hoja_basica():
    """Cuadrícula 4×5 sin corbata: f<fila>c<columna>."""
    rgb = np.asarray(Image.open(os.path.join(HOJAS, "hoja_basica.webp")).convert("RGB"))
    cols = [(0, 246), (246, 489), (489, 740), (740, 972), (972, 1225)]
    filas = [(0, 242), (242, 484), (484, 729), (729, 980)]
    out = {}
    for r, (y0, y1) in enumerate(filas):
        for c, (x0, x1) in enumerate(cols):
            out[f"basica_f{r + 1}c{c + 1}"] = recortar(rgb, x0, y0, x1, y1)
    return out


def tiznar(img, fuerza=0.78):
    """Oscurece el pelaje crema (y las orejas rosas) como si estuviera chamuscado."""
    a = np.asarray(img).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    piel = (r > 170) & (g > 150) & (b > 120) & ((r - b) > 8)
    hollin = np.array([62, 56, 52], float)
    rr = np.random.default_rng(1)
    k = np.clip(fuerza + rr.normal(0, 0.05, r.shape), 0, 1)[..., None]
    a[..., :3] = np.where(piel[..., None], a[..., :3] * (1 - k) + hollin * k, a[..., :3])
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def pelos_de_punta(img, alto=0.16, color=(55, 50, 47)):
    """Añade mechones de punta detrás del contorno superior de la cabeza."""
    w, h = img.size
    alfa = np.asarray(img.getchannel("A"))
    fondo = Image.new("RGBA", (w, int(h * (1 + alto))), (0, 0, 0, 0))
    dy = fondo.height - h
    d = ImageDraw.Draw(fondo)
    rr = np.random.default_rng(4)
    xs = range(int(w * 0.2), int(w * 0.8), max(6, w // 28))
    for x in xs:
        col = np.where(alfa[: h // 2, x] > 128)[0]
        if not len(col):
            continue
        y = col[0] + dy + 6
        punta = (x + rr.uniform(-0.03, 0.03) * w, y - rr.uniform(0.5, 1.0) * alto * h)
        d.polygon([(x - w * 0.03, y), punta, (x + w * 0.03, y)], fill=color, outline=(20, 18, 16), width=3)
    fondo.alpha_composite(img, (0, dy))
    return fondo


def gafas_rotas(img, centros):
    """Grietas blancas en las lentes (centros en fracciones de la imagen)."""
    img = img.copy()
    d = ImageDraw.Draw(img)
    w, h = img.size
    for cx, cy in centros:
        x, y = cx * w, cy * h
        for dx, dy in ((-0.05, -0.04), (0.04, -0.05), (0.05, 0.03), (-0.03, 0.05)):
            d.line([(x, y), (x + dx * w, y + dy * h)], fill=(245, 245, 245, 255), width=3)
    return img


def main():
    os.makedirs(os.path.join(SALIDA, "catalogo"), exist_ok=True)
    todas = {**hoja_perito(), **hoja_basica()}
    for nombre, img in todas.items():
        img.save(os.path.join(SALIDA, "catalogo", nombre + ".png"))
    usadas = {
        "perito_habla": "perito_6",        # de frente hablando, con portapapeles
        "perito_golpe": "perito_4",        # se agarra la cabeza tras el bate
        "perito_serio": "perito_1",        # serio, mesa de entrevistas y portapapeles
        "perito_confuso": "perito_3",      # sorpresa tras «pelota»
        "seco": "basica_f3c1",             # párpados caídos: «Bizcocho.»
        "brazos_cruzados": "basica_f2c5",  # brazos cruzados
        "espaldas": "basica_f4c5",         # de lado mirando a cámara (sustituto de «de espaldas»)
    }
    for destino, origen in usadas.items():
        todas[origen].save(os.path.join(SALIDA, destino + ".png"))
    # chamuscado: pose B (pelo revuelto y capa quemada) tiznada, con gafas rotas
    quemado = gafas_rotas(tiznar(todas["perito_B"]), [(0.36, 0.40), (0.62, 0.40)])
    quemado.save(os.path.join(SALIDA, "chamuscado.png"))
    pelos_de_punta(quemado).save(os.path.join(SALIDA, "chamuscado_erizado.png"))
    print(f"{len(todas)} poses en el catálogo; {len(usadas) + 2} para el montaje.")


if __name__ == "__main__":
    main()
