"""Monta «Ranking mejores momentos de mal día» con el gato ASESOR DE LA SUERTE.

Uso (desde la raíz del repositorio):
    python3 mal_dia/herramientas/montar.py                 # vídeo completo
    python3 mal_dia/herramientas/montar.py --hoja 4.5,9.8  # hoja de fotogramas de control

- Clips: el original con su sonido. Solo se traduce el título (misma letra y colores)
  y el ranking de la izquierda se deja tal cual (en los zooms no se amplía).
- Tarjetas del gato: estilo de las referencias (papel arrugado o fondo del sitio,
  personaje grande, reencuadres, subtítulo de una palabra, cortes secos, SFX y música).
- Ninguna palabra de la narración se corta.
"""
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import wave

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(RAIZ)
FUENTE = os.path.join(RAIZ, "recursos/fuente/ssstik.io_memepremeo_1791465337459.mp4")
NARRACION = os.path.join(RAIZ, "recursos/narracion.mp3")
POSES = os.path.join(REPO, "montaje/recursos/poses/catalogo")
LETRA_TITULO = os.path.join(REPO, "montaje/recursos/fuentes/RobotoCondensed-Bold.woff")
LETRA_NEGRA = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
TREBOL_EMOJI = os.path.join(RAIZ, "recursos/emoji/1f340.png")

W, H, FPS, SR = 1080, 1920, 30, 48000
CREMA = (247, 233, 212)
CONTORNO = (28, 22, 20)

# ───────────────────────── vídeo original ─────────────────────────
BANDA = (0, 366, 1080, 1805)              # zona de vídeo (el resto es negro)
TITULO_CAJA = (110, 120, 970, 362)
TITULO = [([("Ranking ", "#FFFFFF"), ("Mejores", "#EC1B1E")], 230),
          ([("Momentos de ", "#FFFFFF"), ("Mal Día", "#EFFD00")], 337)]
TITULO_TAM = 106
RANKING_CAJA = (0, 470, 720, 1440)
MASCARA_T = {"p5": 5.40, "p4": 8.70, "p3": 14.80, "p2": 27.90, "p1": 32.50}

# (puesto, orig. inicio, orig. fin, velocidad, zoom (x, y, factor) o None)
CLIPS = {
    "p5": [("p5", 0.00, 3.20, 1.0, None), ("p5", 1.40, 2.00, 0.60, (640, 900, 1.8))],
    "p4": [("p4", 6.00, 8.35, 1.0, None), ("p4", 7.55, 8.15, 0.60, (420, 1000, 1.7))],
    "p3": [("p3", 9.10, 10.30, 1.0, None), ("p3", 12.90, 14.45, 1.0, None), ("p3", 13.95, 14.45, 0.55, (330, 1420, 1.7))],
    "p2": [("p2", 17.60, 20.40, 1.0, None), ("p2", 19.00, 19.60, 0.55, (700, 1150, 1.6)),
           ("p2", 25.80, 27.60, 1.0, None)],
    "p1": [("p1", 29.10, 31.70, 1.0, None), ("p1", 30.40, 31.00, 0.50, (520, 1020, 1.6))],
}

# ───────────────────────── narración ─────────────────────────
# Frases medidas en el archivo de ElevenLabs (inicio, fin, texto).
FRASES = [
    (0.09, 1.09, "Asesor de la suerte."), (1.43, 2.12, "Con este trébol,"), (2.29, 3.37, "el móvil nunca se cae."),
    (3.72, 4.74, "Yo conozco esa persiana."), (5.35, 6.78, "Ayer intenté pasar agachado."), (7.20, 7.78, "Agaché poco."),
    (8.24, 8.45, "A ver,"), (8.68, 9.24, "dejadme a mí."), (9.73, 10.37, "Palillo arriba,"),
    (10.58, 11.13, "golpe seco"), (11.30, 12.07, "y queda perfecto."),
    (12.77, 13.18, "Tranquilos,"), (13.41, 14.14, "yo solo grababa."), (14.90, 16.18, "Al que graba nunca le hacen nada."),
    (16.85, 17.45, "Estoy bien, ¿eh?"), (18.04, 18.51, "Estoy bien."), (18.76, 20.06, "Aún me queda una hoja."),
]


def silabas(palabra):
    p = palabra.lower()
    grupos, previa = 0, False
    for ch in p:
        v = ch in "aeiouáéíóúü"
        if v and not previa:
            grupos += 1
        previa = v
    return max(1, grupos)


def palabras():
    """[(inicio, fin, palabra)] en tiempo del archivo, repartiendo cada frase por sílabas."""
    out = []
    for a, b, txt in FRASES:
        ps = txt.split()
        pesos = [silabas(p) + 0.4 for p in ps]
        t = a
        for p, w in zip(ps, pesos):
            d = (b - a) * w / sum(pesos)
            out.append((t, t + d, p))
            t += d
    return out


PALABRAS = palabras()


def t_palabra(palabra, despues=0.0):
    """Inicio en el archivo de la primera palabra que empieza por `palabra` tras `despues`."""
    for a, b, p in PALABRAS:
        if a >= despues and p.lower().strip("¿?,.").startswith(palabra):
            return a, b
    raise KeyError(palabra)


# ───────────────────────── utilidades ─────────────────────────
_letras = {}


def letra(ruta, tam):
    if (ruta, tam) not in _letras:
        _letras[(ruta, tam)] = ImageFont.truetype(ruta, tam)
    return _letras[(ruta, tam)]


def lerp(a, b, k):
    return a + (b - a) * max(0.0, min(1.0, k))


def tramo(t, t0, d):
    return max(0.0, min(1.0, (t - t0) / d)) if d > 0 else float(t >= t0)


def suave(k):
    return k * k * (3 - 2 * k)


def pop(t, t0, d=0.15):
    if t < t0:
        return 0.0
    k = tramo(t, t0, d)
    return 1.12 * suave(k / 0.7) if k < 0.7 else lerp(1.12, 1.0, (k - 0.7) / 0.3)


def rebote(t, t0, d=0.22):
    if t < t0 or t > t0 + d:
        return 1.0
    k = (t - t0) / d
    pts = [(0, 1.0), (0.3, 0.9), (0.65, 1.05), (1, 1.0)]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if k <= b:
            return lerp(va, vb, (k - a) / (b - a))
    return 1.0


def temblor(t, t0, d, amp):
    if t < t0 or t >= t0 + d:
        return 0, 0
    r = random.Random(int(t * FPS) * 7919)
    a = amp * (1 - (t - t0) / d)
    return int(r.uniform(-a, a)), int(r.uniform(-a, a))


def pegar(lienzo, img, cx, cy, escala=1.0, rot=0.0, alfa=1.0, espejo=False):
    if img is None or escala <= 0.01:
        return
    if espejo:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if abs(escala - 1.0) > 1e-3:
        img = img.resize((max(1, int(img.width * escala)), max(1, int(img.height * escala))), Image.BICUBIC)
    if rot:
        img = img.rotate(rot, Image.BICUBIC, expand=True)
    if alfa < 1.0:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alfa)))
    x, y = int(cx - img.width / 2), int(cy - img.height / 2)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(lienzo.width, x + img.width), min(lienzo.height, y + img.height)
    if x1 > x0 and y1 > y0:
        lienzo.alpha_composite(img.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def desenfoque_mov(lienzo, img, cx, cy, dx, dy, escala=1.0, rot=0.0):
    acum = Image.new("RGBA", lienzo.size)
    for k in range(6):
        pegar(acum, img, cx - dx * k / 5, cy - dy * k / 5, escala, rot, alfa=0.4 if k else 1.0)
    lienzo.alpha_composite(acum)


def color(c, a=1.0):
    return Image.new("RGBA", (W, H), c + (int(255 * a),))


_vin = None


def vineta(fuerza):
    global _vin
    if _vin is None:
        y, x = np.mgrid[0:H, 0:W]
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _vin = np.clip((r - 0.2) / 0.6, 0, 1) ** 1.5
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    capa.putalpha(Image.fromarray((np.clip(_vin * fuerza * 1.5, 0, 0.97) * 255).astype(np.uint8)))
    return capa


# ───────────────────────── fondos ─────────────────────────

def ruido(shape, escala, semilla):
    r = np.random.default_rng(semilla)
    peq = r.normal(0, 1, (shape[0] // escala + 2, shape[1] // escala + 2)).astype(np.float32)
    return cv2.resize(peq, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)


def fondo_papel():
    """Papel arrugado claro, como en las referencias."""
    base = np.full((H, W), 232.0)
    base += ruido((H, W), 160, 1) * 9 + ruido((H, W), 40, 2) * 4 + ruido((H, W), 6, 3) * 2
    capa = Image.new("L", (W, H), 128)
    d = ImageDraw.Draw(capa)
    rr = random.Random(7)
    for _ in range(60):
        p = [(rr.uniform(-100, W + 100), rr.uniform(-100, H + 100))]
        for _ in range(rr.randint(2, 4)):
            p.append((p[-1][0] + rr.uniform(-380, 380), p[-1][1] + rr.uniform(-380, 380)))
        d.line(p, fill=rr.choice([90, 170, 185]), width=rr.randint(2, 6))
    capa = np.asarray(capa.filter(ImageFilter.GaussianBlur(5))).astype(float) - 128
    base += capa * 0.5
    g = np.clip(base, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([g, g, np.clip(g.astype(int) + 3, 0, 255).astype(np.uint8)])).convert("RGBA")


def fondo_rejilla():
    img = Image.new("RGB", (W, H), (40, 42, 46))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 72):
        d.rectangle([0, y, W, y + 16], fill=(150, 154, 160))
        d.line([(0, y), (W, y)], fill=(205, 208, 214), width=3)
    for x in range(0, W, 30):
        d.rectangle([x, 0, x + 7, H], fill=(120, 124, 130))
    a = np.asarray(img).astype(float) + ruido((H, W), 50, 5)[..., None] * 10
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)).convert("RGBA")


def barrotes_delante():
    """Barrotes de la rejilla por delante del gato (parte de abajo)."""
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(1540, H + 120, 120):
        d.rectangle([0, y, W, y + 30], fill=(125, 130, 138, 255))
        d.line([(0, y), (W, y)], fill=(215, 218, 224, 255), width=5)
        d.line([(0, y + 30), (W, y + 30)], fill=(60, 62, 66, 255), width=5)
    for x in range(-20, W + 60, 54):
        d.rectangle([x, 1540, x + 13, H], fill=(105, 110, 118, 255))
    return img


def fondo_cafeteria():
    a = np.zeros((H, W, 3))
    for y in range(H):
        k = y / H
        a[y] = [lerp(55, 120, k), lerp(32, 68, k), lerp(20, 32, k)]
    img = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    luces = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(luces)
    rr = random.Random(11)
    for _ in range(26):
        x, y, r = rr.uniform(0, W), rr.uniform(0, 1150), rr.uniform(35, 110)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, rr.randint(170, 215), rr.randint(80, 130), rr.randint(90, 170)))
    img.alpha_composite(luces.filter(ImageFilter.GaussianBlur(22)))
    return img.filter(ImageFilter.GaussianBlur(4))


def mesa():
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1390, W, H], fill=(110, 66, 34, 255))
    d.rectangle([0, 1390, W, 1420], fill=(150, 95, 52, 255))
    rr = random.Random(3)
    for _ in range(40):
        y = rr.uniform(1430, H)
        d.line([(0, y), (W, y + rr.uniform(-20, 20))], fill=(90, 52, 26, 255), width=rr.randint(2, 5))
    return img


def fondo_nieve():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        c = (int(lerp(178, 214, y / 900)), int(lerp(188, 220, y / 900)), int(lerp(200, 228, y / 900))) if y < 900 \
            else (int(lerp(236, 248, (y - 900) / 1000)),) * 2 + (252,)
        d.line([(0, y), (W, y)], fill=c)
    rr = random.Random(5)
    for x in range(-60, W + 60, 90):
        h = rr.uniform(240, 420)
        d.polygon([(x, 930), (x + 55, 930 - h), (x + 110, 930)], fill=(35, 58, 45))
    d.rectangle([600, 760, 960, 930], fill=(225, 225, 230))
    d.polygon([(570, 770), (780, 640), (990, 770)], fill=(250, 250, 252))
    d.rectangle([640, 820, 700, 880], fill=(90, 100, 110))
    d.rectangle([860, 820, 920, 880], fill=(90, 100, 110))
    d.ellipse([-300, 880, 1400, 1100], fill=(242, 246, 252))
    return img.filter(ImageFilter.GaussianBlur(9)).convert("RGBA")


def fondo_barro():
    base = np.zeros((H, W, 3))
    n1, n2 = ruido((H, W), 120, 21), ruido((H, W), 20, 22)
    barro = np.array([96, 74, 52]) + (n1[..., None] * 8 + n2[..., None] * 4)
    agua = np.clip((n1 - 0.2) * 3, 0, 1)[..., None]
    base = barro * (1 - agua) + (np.array([132, 118, 102]) + n2[..., None] * 5) * agua
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    rr = random.Random(9)
    for _ in range(30):
        x, y = rr.uniform(0, W), rr.uniform(0, H)
        d.arc([x - 120, y - 30, x + 120, y + 30], 200, 340, fill=(175, 162, 145), width=4)
    return img.filter(ImageFilter.GaussianBlur(10)).convert("RGBA")


# ───────────────────────── poses y marcas ─────────────────────────
ALTO = 1600
# Fracciones (x, y) de cada pose: oreja = punta de la oreja que se dobla.
ANCLAS = {
    "basica_f1c1": dict(nariz=(0.43, 0.49), frente=(0.45, 0.28), cabeza=(0.45, 0.10), pecho=(0.45, 0.70),
                        pata_i=(0.18, 0.78), pata_d=(0.64, 0.72), oreja=(0.20, 0.03), cuello=0.60,
                        ojos=[(0.27, 0.43), (0.60, 0.47)]),
    "basica_f3c1": dict(nariz=(0.38, 0.48), frente=(0.40, 0.28), cabeza=(0.40, 0.10), pecho=(0.40, 0.72),
                        pata_i=(0.25, 0.92), pata_d=(0.55, 0.92), oreja=(0.15, 0.03), cuello=0.60),
    "basica_f1c5": dict(nariz=(0.45, 0.47), frente=(0.50, 0.28), cabeza=(0.48, 0.10), pecho=(0.45, 0.75),
                        pata_i=(0.09, 0.44), pata_d=(0.62, 0.70), oreja=(0.30, 0.03), cuello=0.60),
    "basica_f2c3": dict(nariz=(0.55, 0.49), frente=(0.55, 0.30), cabeza=(0.60, 0.12), pecho=(0.60, 0.74),
                        pata_i=(0.30, 0.85), pata_d=(0.60, 0.73), oreja=(0.83, 0.03), cuello=0.62),
    "basica_f1c4": dict(nariz=(0.50, 0.47), frente=(0.50, 0.30), cabeza=(0.50, 0.10), pecho=(0.50, 0.72),
                        pata_i=(0.30, 0.75), pata_d=(0.88, 0.60), oreja=(0.12, 0.03), cuello=0.60),
    "basica_f4c5": dict(nariz=(0.42, 0.62), frente=(0.55, 0.35), cabeza=(0.55, 0.22), pecho=(0.50, 0.80),
                        pata_i=(0.15, 0.55), pata_d=(0.70, 0.85), oreja=(0.10, 0.22), cuello=0.75),
}
_poses = {}


def pose(nombre):
    if nombre not in _poses:
        img = Image.open(os.path.join(POSES, nombre + ".png")).convert("RGBA")
        img = img.resize((int(img.width * ALTO / img.height), ALTO), Image.LANCZOS)
        _poses[nombre] = img.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    return _poses[nombre]


def px(nombre, punto):
    fx, fy = ANCLAS[nombre][punto]
    img = pose(nombre)
    return fx * img.width, fy * img.height


def rayas_persiana(img, nombre):
    """Rayas horizontales marcadas en la cabeza (multiplicar al 40 %)."""
    a = np.asarray(img).astype(float)
    alfa = a[..., 3] / 255
    y = np.arange(img.height)[:, None]
    raya = ((y % 46) < 16).astype(float)
    cabeza = (y < ANCLAS[nombre]["cuello"] * img.height).astype(float)
    k = 1 - 0.4 * raya * cabeza * (alfa > 0.5)
    a[..., :3] *= k[..., None]
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def oreja_doblada(img, nombre):
    tx, ty = ANCLAS[nombre]["oreja"]
    s = -1 if tx > 0.5 else 1
    w, h = img.size
    T = (tx * w, ty * h)
    A = (T[0] - s * 0.075 * w, T[1] + 0.12 * h)
    B = (T[0] + s * 0.075 * w, T[1] + 0.10 * h)
    F = (T[0] - s * 0.11 * w, T[1] + 0.22 * h)
    img = img.copy()
    alfa = img.getchannel("A")
    ImageDraw.Draw(alfa).polygon([A, B, (B[0], T[1] - 30), (A[0], T[1] - 30)], fill=0)
    img.putalpha(alfa)
    d = ImageDraw.Draw(img)
    d.polygon([A, B, F], fill=CREMA + (255,), outline=CONTORNO + (255,))
    d.line([A, B, F, A], fill=CONTORNO + (255,), width=14, joint="curve")
    d.polygon([((A[0] * 2 + F[0]) / 3, (A[1] * 2 + F[1]) / 3 + 10), ((B[0] * 2 + F[0]) / 3, (B[1] * 2 + F[1]) / 3 + 6),
               ((A[0] + B[0] + F[0] * 4) / 6, (A[1] + B[1] + F[1] * 4) / 6)], fill=(240, 175, 170, 255))
    return img


def perla(r):
    img = Image.new("RGBA", (2 * r + 4, 2 * r + 4))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 2, 2 * r + 2, 2 * r + 2], fill=(52, 30, 22, 255), outline=(20, 12, 10, 255), width=3)
    d.ellipse([r * 0.6, r * 0.5, r * 1.1, r * 0.95], fill=(150, 110, 95, 255))
    return img


def mancha(r, c, semilla):
    img = Image.new("RGBA", (int(r * 2.6), int(r * 2.6)))
    d = ImageDraw.Draw(img)
    rr = random.Random(semilla)
    cx = cy = r * 1.3
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    for _ in range(9):
        a = rr.uniform(0, 6.28)
        dd = r * rr.uniform(0.8, 1.2)
        q = r * rr.uniform(0.18, 0.4)
        x, y = cx + math.cos(a) * dd, cy + math.sin(a) * dd
        d.ellipse([x - q, y - q, x + q, y + q], fill=c)
    return img.filter(ImageFilter.GaussianBlur(1.5))


def con_marcas(nombre, marcas):
    """Pose con las marcas acumuladas: rayas, oreja, tapioca, te, nieve, barro."""
    img = pose(nombre)
    if "rayas" in marcas:
        img = rayas_persiana(img, nombre)
    if "oreja" in marcas:
        img = oreja_doblada(img, nombre)
    w, h = img.size
    nx, ny = px(nombre, "nariz")
    rr = random.Random(hash(nombre) % 999)
    if "te" in marcas:
        m = mancha(int(0.07 * h), (196, 160, 118, 200), 4)
        img.alpha_composite(m, (int(nx + 0.12 * w - m.width / 2), int(ny + 0.02 * h - m.height / 2)))
    if "tapioca" in marcas:
        for dx, dy in ((-0.2, -0.1), (0.18, -0.16), (0.05, 0.08), (-0.25, 0.1), (0.28, 0.05)):
            p = perla(int(0.022 * h))
            img.alpha_composite(p, (int(nx + dx * w), int(ny + dy * h)))
    if "nieve" in marcas:
        cx, cy = px(nombre, "cabeza")
        for k in range(9):
            r = int(0.035 * h * rr.uniform(0.7, 1.3))
            m = mancha(r, (250, 252, 255, 250), k)
            img.alpha_composite(m, (int(cx + (k - 4) * 0.06 * w - m.width / 2), int(cy - m.height / 2 + rr.uniform(-20, 30))))
    if "barro" in marcas:
        for k in range(8):
            r = int(0.022 * h * rr.uniform(0.6, 1.4))
            m = mancha(r, (98, 70, 44, 175), 20 + k)
            x = nx + rr.uniform(-0.36, 0.36) * w
            y = ny + rr.uniform(-0.12, 0.42) * h
            img.alpha_composite(m, (int(x - m.width / 2), int(y - m.height / 2)))
        a = np.asarray(img).copy()
        a[..., 3] = np.asarray(pose(nombre).getchannel("A"))
        if "oreja" in marcas:
            a[..., 3] = np.minimum(a[..., 3], np.asarray(oreja_doblada(pose(nombre), nombre).getchannel("A")))
        img = Image.fromarray(a, "RGBA")
    return img


# ───────────────────────── props dibujados ─────────────────────────

def hoja_trebol(r, color=(58, 168, 72)):
    """Hoja en forma de corazón: lóbulos arriba, punta abajo."""
    n = int(r * 2.6)
    c = n / 2
    m = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(m)
    for sx in (-1, 1):
        x = c + sx * 0.46 * r
        d.ellipse([x - 0.54 * r, c - 0.9 * r, x + 0.54 * r, c + 0.18 * r], fill=255)
    d.polygon([(c - 0.98 * r, c - 0.25 * r), (c + 0.98 * r, c - 0.25 * r), (c, c + 0.95 * r)], fill=255)
    borde = m.filter(ImageFilter.MaxFilter(2 * max(2, r // 12) + 1))
    img = Image.new("RGBA", (n, n), CONTORNO + (0,))
    img.putalpha(borde)
    relleno = Image.new("RGBA", (n, n), color + (255,))
    relleno.putalpha(m)
    img.alpha_composite(relleno)
    d = ImageDraw.Draw(img)
    d.line([(c, c - 0.45 * r), (c, c + 0.7 * r)], fill=(36, 118, 48, 255), width=max(2, r // 12))
    d.ellipse([c - 0.62 * r, c - 0.62 * r, c - 0.3 * r, c - 0.35 * r], fill=(120, 205, 120, 255))
    return img


def trebol(hojas, tam=260, tallo_doblado=False):
    img = Image.new("RGBA", (tam * 2, tam * 2))
    c = tam
    d = ImageDraw.Draw(img)
    fin = (c + tam * 0.45, c + tam * 0.9) if tallo_doblado else (c + tam * 0.1, c + tam * 0.98)
    for ancho, col in ((max(12, tam // 12), CONTORNO), (max(6, tam // 24), (60, 140, 60))):
        d.line([(c, c), (c + tam * 0.06, c + tam * 0.5), fin], fill=col, width=ancho, joint="curve")
    r = int(tam * 0.36)
    hoja = hoja_trebol(r)
    for ang in (315, 45, 225, 135)[:hojas]:  # arriba-izq, arriba-der, abajo-izq, abajo-der
        a = math.radians(ang)
        pegar(img, hoja, c + math.sin(a) * r * 0.78, c - math.cos(a) * r * 0.78, rot=-ang)
    return img


def movil(ancho=170, horizontal=False):
    w, h = ancho, int(ancho * 2.0)
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 2, w - 2, h - 2], int(w * 0.16), fill=(25, 25, 30, 255), outline=(140, 140, 150, 255), width=5)
    d.rounded_rectangle([12, 22, w - 12, h - 22], int(w * 0.08), fill=(60, 120, 200, 255))
    d.ellipse([w / 2 - 8, 8, w / 2 + 8, 18], fill=(10, 10, 12, 255))
    return img.rotate(90, expand=True) if horizontal else img


def palillo(largo=520):
    img = Image.new("RGBA", (40, largo))
    d = ImageDraw.Draw(img)
    d.polygon([(14, 4), (26, 4), (34, largo - 4), (6, largo - 4)], fill=(180, 120, 60, 255), outline=CONTORNO + (255,))
    d.rectangle([6, largo - 110, 34, largo - 4], fill=(150, 30, 30, 255))
    return img


def vaso_bubble(alto=420):
    w = int(alto * 0.62)
    img = Image.new("RGBA", (w + 40, alto + 140))
    d = ImageDraw.Draw(img)
    x0, x1, y0 = 20, w + 20, 120
    d.polygon([(x0, y0), (x1, y0), (x1 - w * 0.12, y0 + alto), (x0 + w * 0.12, y0 + alto)], fill=(214, 180, 140, 235),
              outline=CONTORNO + (255,))
    for k in range(18):
        rr = random.Random(k)
        cx, cy = rr.uniform(x0 + w * 0.2, x1 - w * 0.2), rr.uniform(y0 + alto * 0.7, y0 + alto * 0.95)
        img.alpha_composite(perla(16), (int(cx), int(cy)))
    d.chord([x0 - 6, y0 - 60, x1 + 6, y0 + 40], 180, 360, fill=(240, 240, 245, 200), outline=CONTORNO + (255,), width=5)
    d.rectangle([x0 - 8, y0 - 12, x1 + 8, y0 + 8], fill=(235, 235, 240, 255), outline=CONTORNO + (255,), width=5)
    d.rectangle([w / 2 + 6, 0, w / 2 + 34, y0], fill=(240, 100, 140, 255), outline=CONTORNO + (255,), width=4)
    d.line([(x0 + 14, y0 + 30), (x0 + w * 0.17, y0 + alto - 30)], fill=(255, 255, 255, 140), width=10)
    return img


def cartel_asesor():
    f = letra(LETRA_NEGRA, 50)
    w, h = 560, 170
    img = Image.new("RGBA", (w, h + 120))
    d = ImageDraw.Draw(img)
    d.line([(w * 0.22, 120), (w / 2, 0), (w * 0.78, 120)], fill=(120, 80, 40, 255), width=8)
    d.rounded_rectangle([4, 110, w - 4, 110 + h], 26, fill=(255, 250, 235, 255), outline=CONTORNO + (255,), width=8)
    d.text((w / 2 - 34, 110 + h * 0.34), "ASESOR DE", font=f, fill=(30, 120, 50), anchor="mm")
    d.text((w / 2 - 34, 110 + h * 0.72), "LA SUERTE", font=f, fill=(30, 120, 50), anchor="mm")
    e = Image.open(TREBOL_EMOJI).convert("RGBA").resize((90, 90), Image.LANCZOS)
    img.alpha_composite(e, (w - 120, 110 + h // 2 - 45))
    return img


def gato_negro():
    base = pose("basica_f1c1")
    a = np.asarray(base).astype(float)
    a[..., :3] = a[..., :3] * 0.08 + np.array([18, 18, 22]) * 0.92
    img = Image.fromarray(a.astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(img)
    for fx, fy in ANCLAS["basica_f1c1"]["ojos"]:
        x, y, r = fx * img.width, fy * img.height, 0.045 * img.width
        d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 210, 40, 255))
        d.ellipse([x - r * 0.25, y - r * 0.9, x + r * 0.25, y + r * 0.9], fill=(10, 10, 10, 255))
    return img


def recorte_tio(frames):
    """El tío de la nieve (orig. 26,5), recortado con GrabCut guiado por un contorno."""
    img = cv2.cvtColor(np.asarray(frames.frame(26.5).convert("RGB")), cv2.COLOR_RGB2BGR)
    neg = np.asarray(frames.frame(MASCARA_T["p2"]).convert("L"))
    m = ((neg > 40) * 255).astype(np.uint8)
    m[:400] = 0
    img = cv2.inpaint(img, cv2.dilate(m, np.ones((15, 15), np.uint8)), 7, cv2.INPAINT_TELEA)
    P = [(345, 40), (420, 30), (455, 80), (450, 150), (460, 250), (445, 360), (430, 420), (440, 600), (225, 600),
         (225, 470), (215, 440), (110, 400), (100, 470), (110, 500), (80, 505), (15, 480), (40, 420), (75, 360),
         (110, 300), (160, 250), (230, 180), (300, 150), (330, 120)]
    poly = np.array([(2 * x, 2 * y + 600) for x, y in P], np.int32)
    mask = np.full(img.shape[:2], cv2.GC_BGD, np.uint8)
    fig = np.zeros_like(mask)
    cv2.fillPoly(fig, [poly], 1)
    mask[cv2.dilate(fig, np.ones((41, 41), np.uint8)) == 1] = cv2.GC_PR_BGD
    mask[fig == 1] = cv2.GC_PR_FGD
    mask[cv2.erode(fig, np.ones((45, 45), np.uint8)) == 1] = cv2.GC_FGD
    cv2.grabCut(img, mask, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
    mm = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
    mm = cv2.morphologyEx(mm, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(mm)
    mm = np.where(lab == 1 + np.argmax(st[1:, 4]), 255, 0).astype(np.uint8)
    # quita la nieve que queda bajo el brazo
    claro = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) > 205
    zona = np.zeros_like(mm)
    zona[1080:1380, 220:440] = 1
    mm[(claro & (zona == 1))] = 0
    mm[1800:] = 0
    mm = cv2.GaussianBlur(mm, (5, 5), 0)
    out = Image.fromarray(np.dstack([cv2.cvtColor(img, cv2.COLOR_BGR2RGB), mm]), "RGBA")
    return out.crop(out.getbbox())


# ───────────────────────── fuente y clips ─────────────────────────

class Frames:
    def __init__(self, tmp):
        self.dir = os.path.join(tmp, "src")
        os.makedirs(self.dir)
        subprocess.run(["ffmpeg", "-v", "error", "-i", FUENTE, "-vf", f"fps={FPS},scale={W}:{H}", "-q:v", "2",
                        os.path.join(self.dir, "%05d.jpg")], check=True)
        self.n = len(os.listdir(self.dir))
        self.cache = {}

    def frame(self, t):
        i = min(self.n, max(1, round(t * FPS) + 1))
        if i not in self.cache:
            if len(self.cache) > 60:
                self.cache.clear()
            self.cache[i] = Image.open(os.path.join(self.dir, f"{i:05d}.jpg")).convert("RGBA")
        return self.cache[i]


_masc = {}


def mascara_ranking(frames, puesto):
    if puesto not in _masc:
        neg = frames.frame(MASCARA_T[puesto]).convert("L").crop(RANKING_CAJA)
        m = neg.point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(13))
        _masc[puesto] = m.filter(ImageFilter.GaussianBlur(2))
    return _masc[puesto]


def sin_ranking(recorte, mascara):
    rgb = np.asarray(recorte.convert("RGB"))
    m = (np.asarray(mascara) > 20).astype(np.uint8) * 255
    return Image.fromarray(cv2.inpaint(rgb, m, 7, cv2.INPAINT_TELEA)).convert("RGBA")


def zoom_banda(img, escala, cx, cy):
    bx0, by0, bx1, by1 = BANDA
    bw, bh = bx1 - bx0, by1 - by0
    w, h = bw / escala, bh / escala
    x0 = min(max(bx0, cx - w / 2), bx1 - w)
    y0 = min(max(by0, cy - h / 2), by1 - h)
    img = img.copy()
    img.paste(img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((bw, bh), Image.BICUBIC), (bx0, by0))
    return img


def titulo(img):
    d = ImageDraw.Draw(img)
    d.rectangle(TITULO_CAJA, fill=(0, 0, 0))
    f = letra(LETRA_TITULO, TITULO_TAM)
    for trozos, base in TITULO:
        x = W / 2 - sum(f.getlength(t) for t, _ in trozos) / 2
        for t, c in trozos:
            d.text((x, base), t, font=f, fill=c, anchor="ls")
            x += f.getlength(t)


_marca = None


def marca_agua(img):
    global _marca
    if _marca is None:
        f = letra(LETRA_NEGRA, 34)
        _marca = Image.new("RGBA", (420, 60))
        d = ImageDraw.Draw(_marca)
        d.text((210, 30), "Miau con Criterio", font=f, fill=(255, 255, 255, 150), anchor="mm",
               stroke_width=3, stroke_fill=(0, 0, 0, 110))
    pegar(img, _marca, W / 2, 1850)


def frame_clip(frames, seg, t_local):
    puesto, o0, o1, vel, zoom = seg
    original = frames.frame(o0 + t_local * vel)
    img = original.copy()
    if zoom:
        cx, cy, z = zoom
        mascara = mascara_ranking(frames, puesto)
        img.paste(sin_ranking(original.crop(RANKING_CAJA), mascara), RANKING_CAJA[:2])
        img = zoom_banda(img, lerp(1.0, z, suave(tramo(t_local, 0, 0.3))), cx, cy)
        img.paste(original.crop(RANKING_CAJA), RANKING_CAJA[:2], mascara)
    titulo(img)
    marca_agua(img)
    return img


# ───────────────────────── subtítulos de una palabra ─────────────────────────
COLORES = [(255, 255, 255), (255, 228, 0), (70, 255, 90), (70, 225, 255)]


def subtitulo(img, palabra, k, t_desde, y):
    f = letra(LETRA_NEGRA, 86)
    c = COLORES[k % len(COLORES)] if k % 3 else (255, 255, 255)
    txt = palabra
    ancho = f.getlength(txt) + 40
    capa = Image.new("RGBA", (int(ancho), 140))
    d = ImageDraw.Draw(capa)
    d.text((ancho / 2, 70), txt, font=f, fill=c, anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0))
    if capa.width > W - 60:
        capa = capa.resize((W - 60, int(capa.height * (W - 60) / capa.width)), Image.LANCZOS)
    pegar(img, capa, W / 2, y, escala=lerp(1.25, 1.0, tramo(t_desde, 0, 0.08)))


# ───────────────────────── tarjetas ─────────────────────────
# Cada tarjeta: trozos de narración (inicio y fin en el archivo, instante local), duración y dibujo.

def local(t_archivo, trozo):
    a, b, en = trozo
    return en + (t_archivo - a)


class Tarjeta:
    def __init__(self, trozos, dur, sfx, sub_y):
        self.trozos, self.dur, self.sfx, self.sub_y = trozos, dur, sfx, sub_y

    def palabra_en(self, t):
        for trozo in self.trozos:
            a, b, en = trozo
            for k, (pa, pb, p) in enumerate(PALABRAS):
                if a <= pa < b:
                    la, lb = local(pa, trozo), local(pb, trozo) + 0.06
                    if la <= t < lb:
                        return p, k, t - la
        return None


def L(trozo, palabra, despues=None):
    """Instante local en que empieza `palabra` dentro de un trozo."""
    return local(t_palabra(palabra, trozo[0] if despues is None else despues)[0], trozo)


# Tarjeta 1 ── rejilla
T1 = (0.00, 3.50, 0.20)
T1_TREBOL = L(T1, "con")
T1_MOVIL = L(T1, "el")
T1_CAE = L(T1, "cae")
T1_FIN_VOZ = local(3.37, T1)
T1_HOJA = T1_FIN_VOZ + 0.5

# Tarjeta 2 ── papel, primerísimo plano
T2A = (3.60, 6.95, 0.20)
T2_AGACHADO = L(T2A, "agachado")
T2_FIN_A = local(6.78, T2A)
T2B = (7.10, 7.95, T2_FIN_A + 0.5 - 0.10)
T2_POCO = L(T2B, "poco")

# Tarjeta 3 ── cafetería
T3 = (8.15, 12.15, 0.25)
T3_ARRIBA = L(T3, "arriba")
T3_FIN = local(12.07, T3)

# Tarjeta 4 ── nieve
T4 = (12.70, 16.25, 0.25)
T4_NADA = L(T4, "nada")
T4_IMPACTO = T4_NADA + 0.22

# Tarjeta 5 ── barro
T5 = (16.80, 20.10, 0.35)
T5_HOJA = L(T5, "hoja")
T5_FIN_VOZ = local(20.06, T5)

TARJETAS = {
    1: Tarjeta([T1], T1_HOJA + 0.68,
               [(0.0, "pop", -10), (T1_MOVIL, "blip", -12), (T1_CAE + 0.25, "clinc", -9), (T1_CAE + 0.5, "caida", -12),
                (T1_HOJA, "pluc", -10)], 1560),
    2: Tarjeta([T2A, T2B], local(7.78, T2B) + 0.35,
               [(0.0, "whoosh", -11), (T2_AGACHADO + 0.42, "bonk", -9)], 1600),
    3: Tarjeta([T3], T3_FIN + 0.30,
               [(0.0, "pop", -10), (0.45, "blip", -12), (T3_FIN + 0.08, "splash", -6), (T3_FIN + 0.08, "bonk", -10)], 1180),
    4: Tarjeta([T4], T4_IMPACTO + 0.85,
               [(0.0, "whoosh", -11), (T4_IMPACTO - 0.14, "whoosh_rapido", -8), (T4_IMPACTO, "golpe_nieve", -6),
                (T4_IMPACTO + 0.35, "pluc", -14)], 820),
    5: Tarjeta([T5], T5_FIN_VOZ + 0.95,
               [(0.22, "chof", -7), (T5_HOJA, "blip", -12), (T5_FIN_VOZ + 0.08, "pluc", -10),
                (T5_FIN_VOZ + 0.6, "chof_peque", -12)], 1500),
    6: Tarjeta([], 2.4, [(1.1, "dun", -5)], 0),
}

_capas = {}


def capa(nombre, marcas, alto, espejo=False):
    clave = (nombre, tuple(sorted(marcas)), alto, espejo)
    if clave not in _capas:
        if len(_capas) > 30:
            _capas.clear()
        img = con_marcas(nombre, marcas)
        img = img.resize((int(img.width * alto / img.height), alto), Image.LANCZOS)
        _capas[clave] = img.transpose(Image.FLIP_LEFT_RIGHT) if espejo else img
    return _capas[clave]


def en_lienzo(nombre, punto, alto, cx, cy, escala=1.0):
    img = pose(nombre)
    x, y = px(nombre, punto)
    f = alto / img.height * escala
    return cx + (x - img.width / 2) * f, cy + (y - img.height / 2) * f


class Escena:
    def __init__(self, frames):
        self.papel = fondo_papel()
        self.rejilla = fondo_rejilla()
        self.barrotes = barrotes_delante()
        self.cafe = fondo_cafeteria()
        self.mesa = mesa()
        self.nieve = fondo_nieve()
        self.barro = fondo_barro()
        self.cartel = cartel_asesor()
        self.negro = gato_negro()
        self.tio = recorte_tio(frames)
        self.vaso = vaso_bubble()
        self.palillo = palillo()
        self.movil = movil()
        self.movil_h = movil(150, horizontal=True)
        self.hoja = hoja_trebol(60)

    # ── tarjeta 1: «Asesor de la suerte…» y se le cae el móvil
    def t1(self, t):
        img = self.rejilla.copy()
        nombre = "basica_f1c1"
        if T1_TREBOL <= t < T1_MOVIL:
            alto, cx, cy = 1750, 560, 1220      # reencuadre: más cerca para enseñar el trébol
        else:
            alto, cx, cy = 1300, 540, 1060
        esc = pop(t, 0.0) * rebote(t, T1_HOJA + 0.05)
        gato = capa(nombre, [], alto)
        pegar(img, gato, cx, cy, esc)
        x, y = en_lienzo(nombre, "pecho", alto, cx, cy, esc)
        pegar(img, self.cartel, x, y - 0.06 * alto, esc * alto / 1300)
        hojas = 4 if t < T1_HOJA else 3
        xt, yt = en_lienzo(nombre, "pata_i", alto, cx, cy, esc)
        pegar(img, trebol(hojas, 200), xt, yt - 0.05 * alto, esc * alto / 1300, rot=10)
        xm, ym = en_lienzo(nombre, "pata_d", alto, cx, cy, esc)
        if T1_MOVIL <= t < T1_CAE:
            pegar(img, self.movil, xm, ym, pop(t, T1_MOVIL, 0.12), rot=-12)
        elif t >= T1_CAE:
            k = tramo(t, T1_CAE, 0.55)
            pegar(img, self.movil, xm + 40 * k, lerp(ym, 1720, k ** 1.6), lerp(1.0, 0.55, k), rot=-12 - 200 * k,
                  alfa=1.0 if k < 0.9 else 0.0)
        img.alpha_composite(self.barrotes)
        if t >= T1_HOJA:  # la hoja cae haciendo zigzag
            k = tramo(t, T1_HOJA, 0.62)
            pegar(img, self.hoja, xt + 90 * math.sin(k * 9), yt - 120 + 620 * k, 1.0, rot=35 * math.sin(k * 9))
        return img, (0, 0)

    # ── tarjeta 2: «Yo conozco esa persiana…» con prueba
    def t2(self, t):
        img = self.papel.copy()
        nombre = "basica_f3c1"
        marcas = ["rayas", "oreja"] if t >= T2_AGACHADO + 0.42 else []
        alto, cy = 2750, 1280
        cx = lerp(-900, 640, suave(tramo(t, 0.0, 0.2)))
        girado = T2_AGACHADO + 0.28 <= t < T2_AGACHADO + 0.42
        gato = capa(nombre, marcas, alto, espejo=girado)
        esc = rebote(t, T2_POCO)
        if t < 0.2:
            desenfoque_mov(img, gato, cx, cy, 160, 0, esc)
        else:
            pegar(img, gato, cx, cy, esc)
        pegar(img, trebol(3, 240, tallo_doblado=bool(marcas)), 180, 1790, 1.0, rot=-15)
        return img, (0, 0)

    # ── tarjeta 3: cafetería, palillo y vaso que revienta
    def t3(self, t):
        img = self.cafe.copy()
        nombre = "basica_f1c5"
        alto, cx, cy = 1350, 600, 1060
        esc = pop(t, 0.0)
        gato = capa(nombre, ["rayas", "oreja"], alto)
        pegar(img, gato, cx, cy, esc)
        xt, yt = en_lienzo(nombre, "pata_d", alto, cx, cy, esc)
        pegar(img, trebol(3 if t < T3_FIN + 0.08 else 2, 170), xt + 40, yt - 60, esc, rot=-12)
        xp, yp = en_lienzo(nombre, "pata_i", alto, cx, cy, esc)
        sube = 60 * (1 - rebote(t, T3_ARRIBA, 0.3)) * 4 if t < T3_FIN else 0
        if t < T3_FIN:
            pegar(img, self.palillo, xp, yp - 200 - (40 if t >= T3_ARRIBA else 0) - sube, esc, rot=-8)
        else:  # baja el palillo de golpe hacia el vaso
            k = tramo(t, T3_FIN, 0.08)
            pegar(img, self.palillo, lerp(xp, 330, k), lerp(yp - 240, 1300, k), esc, rot=lerp(-8, 30, k))
        img.alpha_composite(self.mesa)
        if t < T3_FIN + 0.08:
            pegar(img, self.vaso, 300, 1300, pop(t, 0.45, 0.15))
        else:  # revienta: té y tapioca hacia la cámara
            k = tramo(t, T3_FIN + 0.08, 0.12)
            rr = random.Random(5)
            for i in range(16):
                ang, dist = rr.uniform(-2.6, -0.2), rr.uniform(150, 900) * k
                r = int(rr.uniform(70, 220) * (0.3 + k))
                pegar(img, mancha(r, (205, 168, 125, 240), i), 300 + math.cos(ang) * dist, 1250 + math.sin(ang) * dist)
            for i in range(22):
                ang, dist = rr.uniform(-3.0, 0.1), rr.uniform(100, 1000) * k
                pegar(img, perla(int(rr.uniform(26, 60) * (0.5 + k))), 300 + math.cos(ang) * dist, 1250 + math.sin(ang) * dist)
            pegar(img, self.hoja, 300 + 700 * k, 1100 - 600 * k, 1.2, rot=400 * k)
            if t < T3_FIN + 0.08 + 2 / FPS:
                img.alpha_composite(color((255, 120, 190), 0.55))
        return img, temblor(t, T3_FIN + 0.08, 0.2, 14)

    # ── tarjeta 4: nieve, «Al que graba nunca le hacen nada» y placaje
    def t4(self, t):
        img = self.nieve.copy()
        nombre = "basica_f2c3"
        marcas = ["rayas", "oreja", "tapioca", "te"]
        alto, cy = 950, 1250
        cx = lerp(-500, 330, suave(tramo(t, 0.0, 0.2)))
        llegada = T4_IMPACTO - 0.14
        gato = capa(nombre, marcas, alto)
        if t < T4_IMPACTO:
            if t < 0.2:
                desenfoque_mov(img, gato, cx, cy, 140, 0)
            else:
                pegar(img, gato, cx, cy)
            xm, ym = en_lienzo(nombre, "pata_d", alto, cx, cy)
            pegar(img, self.movil_h, xm, ym - 20)
            xt, yt = en_lienzo(nombre, "pata_i", alto, cx, cy)
            pegar(img, trebol(2, 140), xt - 20, yt, rot=15)
        elif t < T4_IMPACTO + 0.2:  # sale volando hacia la izquierda con el tío
            k = tramo(t, T4_IMPACTO, 0.2)
            desenfoque_mov(img, gato, lerp(330, -700, k), cy - 120 * k, -220, 0, rot=25 * k)
        if llegada <= t < T4_IMPACTO + 0.2:
            k = tramo(t, llegada, 0.34)
            x = lerp(1500, -900, k)
            desenfoque_mov(img, self.tio, x, 1150, -260, 0, 1.25)
        if t >= T4_IMPACTO:  # nieve disparada
            k = tramo(t, T4_IMPACTO, 0.35)
            rr = random.Random(3)
            for i in range(26):
                ang, dist = rr.uniform(0, 6.28), rr.uniform(100, 700) * k
                pegar(img, mancha(int(rr.uniform(20, 50)), (250, 252, 255, 240), i), 330 + math.cos(ang) * dist,
                      1150 + math.sin(ang) * dist, alfa=1 - k * 0.8)
        if t >= T4_IMPACTO + 0.3:  # una hoja baja flotando
            k = tramo(t, T4_IMPACTO + 0.3, 0.5)
            pegar(img, self.hoja, 380 + 60 * math.sin(k * 7), 700 + 700 * k, 1.0, rot=30 * math.sin(k * 7))
        if T4_IMPACTO <= t < T4_IMPACTO + 2 / FPS:
            img.alpha_composite(color((255, 120, 190), 0.55))
        return img, temblor(t, T4_IMPACTO, 0.25, 16)

    # ── tarjeta 5: barro, «Estoy bien… aún me queda una hoja»
    def t5(self, t):
        img = self.barro.copy()
        nombre = "basica_f1c4"
        marcas = ["rayas", "oreja", "tapioca", "te", "nieve", "barro"]
        alto, cx = 2500, 540
        cy = lerp(-1400, 1250, tramo(t, 0.0, 0.22) ** 2)
        esc = rebote(t, 0.22, 0.2) * rebote(t, T5_FIN_VOZ + 0.65, 0.22)
        pegar(img, capa(nombre, marcas, alto), cx, cy, esc)
        if 0.22 <= t < 0.6:  # salpicón de barro al caer
            k = tramo(t, 0.22, 0.38)
            rr = random.Random(8)
            for i in range(14):
                ang, dist = rr.uniform(-3.1, 0), rr.uniform(200, 650) * k
                pegar(img, mancha(int(rr.uniform(25, 60)), (90, 64, 40, 230), i), 540 + math.cos(ang) * dist,
                      1850 + math.sin(ang) * dist * 1.2, alfa=1 - k)
        if t >= T5_HOJA:
            hojas = 1 if t < T5_FIN_VOZ + 0.08 else 0
            pegar(img, trebol(hojas, 300, tallo_doblado=True), 840, 1180, pop(t, T5_HOJA, 0.15), rot=-10)
        if t >= T5_FIN_VOZ + 0.08:
            k = tramo(t, T5_FIN_VOZ + 0.08, 0.52)
            pegar(img, self.hoja, 840 + 70 * math.sin(k * 8), 960 + 900 * k, 1.3, rot=30 * math.sin(k * 8))
        return img, (0, 0)

    # ── cierre sin voz: tallo pelado y gato negro
    def t6(self, t):
        img = self.barro.copy()
        nombre = "basica_f1c4" if t < 0.75 else "basica_f4c5"
        marcas = ["rayas", "oreja", "tapioca", "te", "nieve", "barro"]
        z = 1 + 0.08 * tramo(t, 0, 2.4)
        alto = int(1150 * z)
        pegar(img, capa(nombre, marcas, alto), 540, 1150)
        pegar(img, trebol(0, int(220 * z), tallo_doblado=True), 540 + 330 * z, 1180)
        if 0.3 <= t < 1.6:
            k = tramo(t, 0.3, 1.3)
            pegar(img, self.negro, lerp(-250, 1330, k), 1600 + 12 * math.sin(k * 30), 0.32, rot=3 * math.sin(k * 30))
        if t >= 1.1:
            img.alpha_composite(vineta(lerp(0, 0.75, tramo(t, 1.1, 0.8))))
        return img, (0, 0)


# ───────────────────────── sonido sintético ─────────────────────────

def _env(n, ataque=0.003, caida=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / ataque)
    return e * (np.exp(-t / caida) if caida else 1)


def sfx(nombre):
    r = np.random.default_rng(abs(hash(nombre)) % 2**32)

    def sweep(f0, f1, d, forma=np.sin):
        t = np.arange(int(d * SR)) / SR
        return forma(2 * np.pi * np.cumsum(np.geomspace(f0, f1, len(t))) / SR)

    def ruido_f(d, v):
        x = r.normal(0, 1, int(d * SR))
        return np.convolve(x, np.ones(v) / v, "same") * math.sqrt(v) * 0.5

    if nombre == "pop":
        x = sweep(500, 1400, 0.07)
        return x * _env(len(x), 0.002, 0.02)
    if nombre == "blip":
        x = sweep(1300, 1800, 0.09)
        return x * _env(len(x), 0.002, 0.04)
    if nombre in ("whoosh", "whoosh_rapido"):
        d = 0.32 if nombre == "whoosh" else 0.18
        x = ruido_f(d, 10)
        k = np.arange(len(x)) / len(x)
        return x * np.sin(np.pi * k) ** 2 * 0.6
    if nombre == "clinc":
        t = np.arange(int(0.5 * SR)) / SR
        x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((2400, 1), (3700, 0.6), (5300, 0.3)))
        return x * _env(len(t), 0.001, 0.08) * 0.5
    if nombre == "caida":
        x = sweep(200, 60, 0.4) * _env(int(0.4 * SR), 0.01, 0.1)
        return x * 0.6
    if nombre == "pluc":
        x = sweep(700, 300, 0.12)
        return x * _env(len(x), 0.002, 0.04)
    if nombre == "bonk":
        t = np.arange(int(0.35 * SR)) / SR
        x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((420, 1), (1100, 0.5), (1900, 0.25)))
        return x * _env(len(t), 0.001, 0.07) * 0.6
    if nombre == "splash":
        x = ruido_f(0.45, 3) * _env(int(0.45 * SR), 0.003, 0.12)
        for p in r.integers(0, len(x) - 2000, 10):
            x[p:p + 1600] += sweep(400, 1200, 1600 / SR) * np.exp(-np.arange(1600) / 300) * 0.5
        return x
    if nombre == "golpe_nieve":
        x = sweep(120, 45, 0.3) * _env(int(0.3 * SR), 0.002, 0.08)
        n = ruido_f(0.25, 8) * _env(int(0.25 * SR), 0.002, 0.07)
        x[:len(n)] += n * 0.8
        return x
    if nombre in ("chof", "chof_peque"):
        d = 0.35 if nombre == "chof" else 0.18
        x = ruido_f(d, 25) * _env(int(d * SR), 0.003, d / 3)
        return x + sweep(160, 70, d) * _env(int(d * SR), 0.003, d / 4) * 0.7
    if nombre == "dun":  # «dun dun DUUUN»
        out = np.zeros(int(1.6 * SR))
        for t0, d, f in ((0.0, 0.22, 98), (0.26, 0.22, 92.5), (0.52, 1.05, 82.4)):
            t = np.arange(int(d * SR)) / SR
            nota = sum(np.sign(np.sin(2 * np.pi * f * m * t)) * a for m, a in ((1, 1), (1.5, 0.5), (2, 0.4), (3, 0.2)))
            nota = np.convolve(nota, np.ones(12) / 12, "same") * _env(len(t), 0.01, d * 0.8)
            i = int(t0 * SR)
            out[i:i + len(nota)] += nota
        return out * 0.5
    raise KeyError(nombre)


def musica(dur):
    """Base suave y alegre (piano eléctrico, bajo y percusión ligera) a 104 BPM."""
    n = int(dur * SR)
    out = np.zeros(n + SR)
    pulso = 60 / 104
    acordes = [(261.6, 329.6, 392.0), (196.0, 246.9, 293.7), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6)]
    t_comp = 0.0
    k = 0
    while t_comp < dur:
        notas = acordes[k % 4]
        for b in range(4):
            t0 = t_comp + b * pulso
            i = int(t0 * SR)
            t = np.arange(int(pulso * 0.9 * SR)) / SR
            ep = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) for f in notas)
            ep *= _env(len(t), 0.005, 0.25) * (0.16 if b % 2 == 0 else 0.1)
            bajo = np.sin(2 * np.pi * notas[0] / 2 * t) * _env(len(t), 0.005, 0.3) * 0.35
            kick = np.sin(2 * np.pi * np.geomspace(120, 45, len(t)) * t) * _env(len(t), 0.001, 0.05) * (0.5 if b % 2 == 0 else 0)
            seg = ep + bajo + kick
            out[i:i + len(seg)] += seg[:max(0, len(out) - i)]
            ih = int((t0 + pulso / 2) * SR)
            hat = np.random.default_rng(k * 4 + b).normal(0, 1, 1200) * np.exp(-np.arange(1200) / 120) * 0.08
            out[ih:ih + 1200] += hat[:max(0, len(out) - ih)]
        t_comp += 4 * pulso
        k += 1
    return out[:n] / (np.max(np.abs(out)) + 1e-9)


def leer_mp3(ruta):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(float)


# ───────────────────────── línea de tiempo ─────────────────────────
ORDEN = ["p5", 1, "p4", 2, "p3", 3, "p2", 4, "p1", 5, 6]


def linea_de_tiempo():
    tramos, t = [], 0.0
    for paso in ORDEN:
        if isinstance(paso, str):
            for seg in CLIPS[paso]:
                d = round((seg[2] - seg[1]) / seg[3] * FPS) / FPS
                tramos.append((t, t + d, "clip", seg))
                t += d
        else:
            d = round(TARJETAS[paso].dur * FPS) / FPS
            tramos.append((t, t + d, "gato", paso))
            t += d
    return tramos, t


def render(tramos, total, salida, hoja=None):
    tmp = tempfile.mkdtemp(prefix="mal_dia_")
    try:
        frames = Frames(tmp)
        esc = Escena(frames)
        dibujar = {1: esc.t1, 2: esc.t2, 3: esc.t3, 4: esc.t4, 5: esc.t5, 6: esc.t6}

        def frame(t):
            a, b, tipo, dato = next(tr for tr in tramos if tr[0] <= t + 1e-6 < tr[1])
            if tipo == "clip":
                return frame_clip(frames, dato, t - a)
            tj = TARJETAS[dato]
            img, (dx, dy) = dibujar[dato](t - a)
            pal = tj.palabra_en(t - a)
            if pal:
                subtitulo(img, pal[0], pal[1], pal[2], tj.sub_y)
            marca_agua(img)
            if dx or dy:
                img = ImageChops.offset(img, dx, dy)
            return img

        if hoja is not None:
            ims = [frame(t).convert("RGB").resize((270, 480)) for t in hoja]
            cols = 6
            c = Image.new("RGB", (cols * 270, ((len(ims) + cols - 1) // cols) * 500), "white")
            d = ImageDraw.Draw(c)
            for i, (t, im) in enumerate(zip(hoja, ims)):
                x, y = (i % cols) * 270, (i // cols) * 500
                c.paste(im, (x, y))
                d.text((x + 4, y + 484), f"{t:.2f}s", fill="black")
            c.save(salida)
            return

        mudo = os.path.join(tmp, "mudo.mp4")
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                "-pix_fmt", "yuv420p", mudo], stdin=subprocess.PIPE)
        for i in range(round(total * FPS)):
            enc.stdin.write(frame(i / FPS).convert("RGB").tobytes())
            if i % 300 == 0:
                print(f"  fotograma {i}/{round(total * FPS)}", flush=True)
        enc.stdin.close()
        if enc.wait():
            raise RuntimeError("ffmpeg falló al codificar")
        mezcla(tramos, total, tmp, mudo, salida)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def mezcla(tramos, total, tmp, mudo, salida):
    n = int(total * SR) + SR
    voz, efectos = np.zeros(n), np.zeros(n)
    narr = leer_mp3(NARRACION)
    narr = narr / (np.max(np.abs(narr)) + 1e-9) * 0.7
    for a, b, tipo, dato in tramos:
        if tipo != "gato":
            continue
        tj = TARJETAS[dato]
        for fa, fb, en in tj.trozos:
            x = narr[int(fa * SR):int(fb * SR)].copy()
            x[:200] *= np.linspace(0, 1, 200)
            x[-200:] *= np.linspace(1, 0, 200)
            i = int((a + en) * SR)
            voz[i:i + len(x)] += x
        for t0, nombre, db in tj.sfx:
            x = sfx(nombre)
            x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (db / 20)
            i = int((a + t0) * SR)
            fin = int(b * SR) if nombre in ("splash", "bonk", "golpe_nieve") else n  # cortes secos
            x = x[:max(0, min(len(x), fin - i))]
            efectos[i:i + len(x)] += x
    # música: más baja bajo la voz y bajo los clips
    m = musica(total)
    env = np.convolve(np.abs(voz), np.ones(4800) / 4800, "same")
    duck = np.where(env[:len(m)] > 0.01, 0.45, 1.0)
    duck = np.convolve(duck, np.ones(2400) / 2400, "same")
    en_clip = np.ones(len(m))
    for a, b, tipo, _ in tramos:
        if tipo == "clip":
            en_clip[int(a * SR):int(b * SR)] = 0.5
    m = m * 10 ** (-20 / 20) * duck * en_clip
    pista = voz + efectos
    pista[:len(m)] += m
    ruta = os.path.join(tmp, "tarjetas.wav")
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(pista[:int(total * SR)], -1, 1) * 32767).astype(np.int16).tobytes())
    filtros, entradas = ["[1:a]aformat=sample_rates=48000:channel_layouts=stereo[t]"], ["[t]"]
    k = 0
    for a, b, tipo, seg in tramos:
        if tipo != "clip":
            continue
        _, o0, o1, vel, zoom = seg
        tempo = f",atempo={vel}" if vel != 1.0 else ""
        vol = "-4dB" if vel != 1.0 else "0dB"
        filtros.append(f"[2:a]atrim={o0}:{o1},asetpts=PTS-STARTPTS{tempo},aformat=sample_rates=48000:channel_layouts=stereo,"
                       f"afade=t=in:d=0.01,afade=t=out:st={max(0, b - a - 0.012)}:d=0.012,volume={vol},"
                       f"adelay={round(a * 1000)}:all=1[c{k}]")
        entradas.append(f"[c{k}]")
        k += 1
    filtros.append("".join(entradas) + f"amix=inputs={len(entradas)}:normalize=0,apad,atrim=end={total},"
                   "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.79:level=disabled,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mudo, "-i", ruta, "-i", FUENTE, "-filter_complex",
                    ";".join(filtros), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", salida], check=True)


def main():
    tramos, total = linea_de_tiempo()
    if len(sys.argv) > 2 and sys.argv[1] == "--hoja":
        ts = [float(x) for x in sys.argv[2].split(",")]
        salida = sys.argv[3] if len(sys.argv) > 3 else "hoja.png"
        render(tramos, total, salida, ts)
        print(salida)
        return
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "salida/ranking_mal_dia.mp4")
    render(tramos, total, salida)
    print(f"Listo: {salida} ({total:.2f} s)")
    for a, b, tipo, dato in tramos:
        etiqueta = f"{dato[0]} orig. {dato[1]:.2f}–{dato[2]:.2f} x{dato[3]}" if tipo == "clip" else f"gato {dato}"
        print(f"  {a:6.2f}–{b:6.2f}  {etiqueta}")


if __name__ == "__main__":
    main()
