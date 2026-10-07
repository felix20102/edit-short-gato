"""Monta el Short «Ranking mejores desastres del año» siguiendo HOJA_DE_EDICION.md.

Uso:  python3 herramientas/montar.py [salida.mp4]   (desde la carpeta montaje/)

Todo recurso que no esté en recursos/ se sustituye por un provisional dibujado aquí
y se lista al terminar. Con el vídeo fuente y los PNG reales, el mismo comando
produce el vídeo final.
"""
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar import DURACION, SUBS  # noqa: E402

W, H, FPS = 1080, 1920, 30
N = round(DURACION * FPS)
AJ = json.load(open("ajustes.json", encoding="utf-8"))
REC = "recursos"
FUENTE_NEGRA = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FUENTE_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

CREMA = (250, 244, 230)
MENTA = (158, 217, 195)
MARRON = (51, 35, 20)
AMARILLO = (255, 212, 0)
ROJO = (229, 37, 42)
VERDE = (30, 158, 74)

FALTAN = set()
_fuentes = {}


def fuente(tam, ruta=FUENTE_NEGRA):
    if (ruta, tam) not in _fuentes:
        _fuentes[(ruta, tam)] = ImageFont.truetype(ruta, tam)
    return _fuentes[(ruta, tam)]


def recurso(sub, nombre):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = os.path.join(REC, sub, nombre + ext)
        if os.path.exists(p):
            return Image.open(p).convert("RGBA")
    FALTAN.add(f"{sub}/{nombre}.png")
    return None


# ───────────────────────── animación ─────────────────────────

def lerp(a, b, k):
    return a + (b - a) * max(0.0, min(1.0, k))


def tramo(t, t0, d):
    return max(0.0, min(1.0, (t - t0) / d)) if d > 0 else float(t >= t0)


def suave(k):
    return k * k * (3 - 2 * k)


def pop(t, t0, d=0.15):
    """Escala 0 → 1,1 → 1."""
    if t < t0:
        return 0.0
    k = tramo(t, t0, d)
    return 1.1 * suave(k / 0.7) if k < 0.7 else lerp(1.1, 1.0, (k - 0.7) / 0.3)


def rebote(t, t0, d=0.2):
    """Escala 1 → 0,92 → 1,04 → 1."""
    if t < t0 or t > t0 + d:
        return 1.0
    k = (t - t0) / d
    pts = [(0, 1.0), (0.3, 0.92), (0.65, 1.04), (1, 1.0)]
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


# ───────────────────────── utilidades de dibujo ─────────────────────────

def pegar(lienzo, img, cx, cy, escala=1.0, rot=0.0, alfa=1.0):
    if img is None or escala <= 0.01:
        return
    if escala != 1.0:
        img = img.resize((max(1, int(img.width * escala)), max(1, int(img.height * escala))), Image.BICUBIC)
    if rot:
        img = img.rotate(rot, Image.BICUBIC, expand=True)
    if alfa < 1.0:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alfa)))
    _pegar_recortado(lienzo, img, int(cx - img.width / 2), int(cy - img.height / 2))


def _pegar_recortado(lienzo, img, x, y):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(lienzo.width, x + img.width), min(lienzo.height, y + img.height)
    if x1 <= x0 or y1 <= y0:
        return
    lienzo.alpha_composite(img.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def capa_color(color, alfa):
    return Image.new("RGBA", (W, H), color + (int(255 * alfa),))


_vineta = None


def vineta(fuerza):
    global _vineta
    if _vineta is None:
        y, x = np.mgrid[0:H, 0:W]
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _vineta = np.clip((r - 0.25) / 0.6, 0, 1) ** 1.6
    a = (np.clip(_vineta * fuerza * 1.4, 0, 0.95) * 255).astype(np.uint8)
    capa = Image.new("RGBA", (W, H), (10, 8, 6, 0))
    capa.putalpha(Image.fromarray(a))
    return capa


# ───────────────────────── fondos provisionales ─────────────────────────

def fondo_papel(arrugas):
    r = np.random.default_rng(3)
    base = np.ones((H, W, 3)) * np.array([244, 238, 223])
    base += r.normal(0, 4, (H, W, 1))
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    if arrugas:
        capa = Image.new("L", (W, H), 128)
        d = ImageDraw.Draw(capa)
        rr = random.Random(5)
        for _ in range(26):
            p = [(rr.uniform(-200, W + 200), rr.uniform(-200, H + 200))]
            for _ in range(3):
                p.append((p[-1][0] + rr.uniform(-500, 500), p[-1][1] + rr.uniform(-500, 500)))
            d.line(p, fill=rr.choice([100, 160]), width=rr.randint(2, 5))
        capa = capa.filter(ImageFilter.GaussianBlur(3))
        a = np.asarray(img).astype(float) + (np.asarray(capa).astype(float)[..., None] - 128) * 0.35
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return img.convert("RGBA")


def fondo_pista():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        if y < 700:
            c = (int(lerp(150, 205, y / 700)), int(lerp(200, 230, y / 700)), 245)
        else:
            c = (196, 110, 70) if y > 1350 else (80, 140, 70)
        d.line([(0, y), (W, y)], fill=c)
    for x in range(-40, W + 40, 60):
        d.line([(x, 650), (x + 160, 1350)], fill=(20, 90, 50), width=6)
        d.line([(x + 160, 650), (x, 1350)], fill=(20, 90, 50), width=6)
    d.rectangle([0, 640, W, 660], fill=(20, 80, 45))
    d.line([(0, 1600), (W, 1500)], fill=(245, 245, 245), width=14)
    return img.filter(ImageFilter.GaussianBlur(8)).convert("RGBA")


def fondo_feria():
    img = Image.new("RGB", (W, H), (60, 30, 50))
    d = ImageDraw.Draw(img)
    for i in range(0, W, 120):
        d.rectangle([i, 0, i + 60, 380], fill=(220, 40, 50))
        d.rectangle([i + 60, 0, i + 120, 380], fill=(250, 245, 235))
    rr = random.Random(9)
    for fila, y in enumerate((700, 1100, 1500)):
        d.rectangle([0, y + 160, W, y + 200], fill=(150, 100, 60))
        for x in range(40, W, 150):
            if (x // 150 + fila) % 3 == 0:
                d.ellipse([x, y, x + 120, y + 160], fill=rr.choice([(240, 150, 190), (130, 200, 240), (250, 220, 90)]))
            else:
                for k in range(2):
                    d.rectangle([x + k * 60, y + 40, x + k * 60 + 50, y + 160], fill=(185, 190, 200))
    return img.filter(ImageFilter.GaussianBlur(8)).convert("RGBA")


def fondo(nombre):
    img = recurso("fondos", nombre)
    if img is not None:
        return img.resize((W, H), Image.LANCZOS) if img.size != (W, H) else img
    return {"papel_arrugado": lambda: fondo_papel(True), "papel": lambda: fondo_papel(False),
            "pista": fondo_pista, "feria": fondo_feria}[nombre]()


# ───────────────────────── gato provisional ─────────────────────────

ALTO_POSE = 1600
CUERPO = (247, 233, 212)


def gato_provisional(pose):
    w, h = 1200, ALTO_POSE
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    quemado = pose.startswith("chamuscado")
    piel = (70, 62, 58) if quemado else CUERPO
    linea = (25, 20, 18)
    g = 12
    # cola, cuerpo y cabeza
    d.arc([780, 900, 1080, 1400], 200, 80, fill=linea, width=60)
    d.arc([786, 906, 1074, 1394], 200, 80, fill=piel, width=40)
    d.ellipse([300, 900, 900, 1560], fill=piel, outline=linea, width=g)
    for s in (-1, 1):
        ox = 600 + s * 290
        d.polygon([(ox - s * 150, 330), (ox + s * 10, 40), (ox + s * 110, 360)], fill=piel, outline=linea, width=g)
        if not quemado:
            d.polygon([(ox - s * 90, 320), (ox + s * 10, 120), (ox + s * 70, 330)], fill=(244, 170, 170))
    d.ellipse([150, 200, 1050, 980], fill=piel, outline=linea, width=g)
    if quemado:  # pelo de punta
        rr = random.Random(2)
        extra = 1.35 if pose.endswith("erizado") else 1.0
        for x in range(200, 1010, 55):
            alto = rr.uniform(90, 170) * extra
            d.polygon([(x - 35, 300), (x + rr.uniform(-25, 25), 300 - alto), (x + 35, 300)], fill=piel, outline=linea, width=8)
    if pose == "espaldas":
        # de espaldas, mirando por encima del hombro: solo asoma un ojo y la gafa
        d.ellipse([760, 470, 940, 650], outline=linea, width=14)
        d.ellipse([840, 520, 900, 590], fill=(120, 70, 30))
        d.polygon([(820, 700), (850, 680), (870, 705)], fill=(240, 150, 150))
        d.arc([350, 350, 700, 800], 200, 330, fill=(220, 205, 185), width=10)
    else:
        for cx in (420, 780):
            d.ellipse([cx - 130, 450, cx + 130, 710], fill=(255, 255, 255, 90), outline=linea, width=16)
            if pose in ("perito_golpe",):
                d.line([(cx - 50, 530), (cx + 50, 630)], fill=linea, width=14)
                d.line([(cx - 50, 630), (cx + 50, 530)], fill=linea, width=14)
            elif pose == "seco":
                d.chord([cx - 55, 545, cx + 55, 655], 0, 180, fill=(120, 70, 30))
                d.line([(cx - 60, 590), (cx + 60, 590)], fill=linea, width=10)
            else:
                d.ellipse([cx - 55, 520, cx + 55, 650], fill=(120, 70, 30))
                d.ellipse([cx - 15, 540, cx + 15, 575], fill=(255, 255, 255))
        d.line([(550, 580), (650, 580)], fill=linea, width=14)
        if quemado:  # gafas rotas
            d.line([(330, 480), (470, 690)], fill=(230, 230, 230), width=6)
            d.line([(720, 470), (840, 600)], fill=(230, 230, 230), width=6)
        d.polygon([(575, 715), (625, 715), (600, 745)], fill=(240, 150, 150))
        boca = {"perito_habla": "abierta", "perito_confuso": "o", "perito_golpe": "ondas"}.get(pose, "recta")
        if boca == "abierta":
            d.chord([550, 760, 650, 850], 0, 180, fill=(170, 60, 60), outline=linea, width=8)
        elif boca == "o":
            d.ellipse([575, 765, 625, 825], fill=(170, 60, 60), outline=linea, width=8)
        elif boca == "ondas":
            d.line([(540, 800), (570, 780), (600, 800), (630, 780), (660, 800)], fill=linea, width=8)
        else:
            d.line([(560, 795), (640, 795)], fill=linea, width=9)
        for s in (-1, 1):
            for k in (-1, 0, 1):
                d.line([(600 + s * 200, 760 + k * 25), (600 + s * 400, 740 + k * 45)], fill=linea, width=5)
    if pose == "brazos_cruzados":
        d.rounded_rectangle([360, 1080, 840, 1230], 70, fill=piel, outline=linea, width=g)
        d.line([(430, 1100), (770, 1210)], fill=linea, width=8)
    else:
        d.ellipse([820, 960, 960, 1100], fill=piel, outline=linea, width=g)
        if pose != "espaldas":
            d.ellipse([240, 960, 380, 1100], fill=piel, outline=linea, width=g)
    if quemado:  # pulgar arriba
        d.rounded_rectangle([880, 870, 930, 980], 25, fill=piel, outline=linea, width=10)
    # rótulo de provisional
    f = fuente(54, FUENTE_BOLD)
    d.rounded_rectangle([170, 1480, 1030, 1590], 30, fill=(255, 255, 255, 220), outline=(229, 37, 42), width=6)
    d.text((600, 1535), f"PROVISIONAL · {pose}", font=f, fill=(229, 37, 42), anchor="mm")
    return img


_poses = {}


def pose_img(nombre):
    if nombre not in _poses:
        img = recurso("poses", nombre)
        if img is None:
            img = gato_provisional(nombre)
        else:
            img = img.crop(img.getbbox())
            img = img.resize((int(img.width * ALTO_POSE / img.height), ALTO_POSE), Image.LANCZOS)
            img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
        _poses[nombre] = img
    return _poses[nombre]


def ancla(pose, punto):
    a = AJ["anclas"].get(pose, AJ["anclas"]["defecto"]).get(punto, AJ["anclas"]["defecto"][punto])
    img = pose_img(pose)
    return a[0] * img.width, a[1] * img.height


# ───────────────────────── props provisionales ─────────────────────────

def prop_provisional(nombre):
    if nombre == "tirita":
        img = Image.new("RGBA", (260, 90))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([2, 2, 258, 88], 40, fill=(232, 195, 158), outline=MARRON, width=6)
        d.rectangle([95, 14, 165, 76], fill=(245, 222, 196))
        for x in (40, 60, 200, 220):
            d.ellipse([x - 4, 41, x + 4, 49], fill=(190, 150, 115))
    elif nombre == "pelota_beisbol":
        img = Image.new("RGBA", (220, 220))
        d = ImageDraw.Draw(img)
        d.ellipse([4, 4, 216, 216], fill=(250, 250, 245), outline=MARRON, width=7)
        d.arc([-80, 20, 90, 200], -60, 60, fill=ROJO, width=7)
        d.arc([130, 20, 300, 200], 120, 240, fill=ROJO, width=7)
    elif nombre == "venda":
        img = Image.new("RGBA", (240, 110))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([3, 3, 237, 107], 30, fill=(250, 250, 250), outline=MARRON, width=6)
        for x in range(30, 220, 30):
            d.line([(x, 10), (x - 10, 100)], fill=(210, 210, 210), width=4)
        for x in (60, 95, 130, 165):
            d.arc([x - 14, -8, x + 14, 22], 0, 180, fill=ROJO, width=5)
    elif nombre in ("chaleco", "chaleco_quemado"):
        img = Image.new("RGBA", (620, 520))
        d = ImageDraw.Draw(img)
        c = (245, 217, 10) if nombre == "chaleco" else (120, 105, 30)
        d.polygon([(40, 60), (230, 20), (310, 230), (390, 20), (580, 60), (600, 510), (20, 510)], fill=c, outline=MARRON)
        for y in (300, 400):
            d.rectangle([20, y, 600, y + 34], fill=(205, 210, 215))
        if nombre == "chaleco_quemado":
            for x, y in ((120, 150), (470, 220), (300, 450)):
                d.ellipse([x - 40, y - 30, x + 40, y + 30], fill=(40, 30, 25))
    elif nombre == "portapapeles":
        img = Image.new("RGBA", (300, 400))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 20, 300, 400], 20, fill=(140, 90, 50), outline=MARRON, width=6)
        d.rectangle([30, 60, 270, 380], fill=(255, 255, 255))
        for y in range(110, 360, 40):
            d.line([(55, y), (245, y)], fill=(170, 170, 170), width=5)
        d.rounded_rectangle([95, 0, 205, 60], 12, fill=(190, 190, 195), outline=MARRON, width=5)
    elif nombre == "acreditacion":
        img = Image.new("RGBA", (190, 250))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([5, 60, 185, 245], 14, fill=(255, 255, 255), outline=MARRON, width=5)
        d.rectangle([10, 65, 180, 110], fill=MENTA)
        d.text((95, 88), "PERITO", font=fuente(30), fill=MARRON, anchor="mm")
        d.line([(30, 70), (95, 0), (160, 70)], fill=(40, 90, 200), width=7)
    elif nombre == "bate":
        img = Image.new("RGBA", (90, 620))
        d = ImageDraw.Draw(img)
        d.polygon([(35, 610), (55, 610), (82, 30), (45, 4), (8, 30)], fill=(196, 140, 80), outline=MARRON)
        d.ellipse([22, 590, 68, 618], fill=(150, 100, 55))
    elif nombre == "pelota_feria":
        img = Image.new("RGBA", (200, 200))
        d = ImageDraw.Draw(img)
        d.ellipse([4, 4, 196, 196], fill=(235, 70, 120), outline=MARRON, width=6)
        d.ellipse([45, 35, 95, 80], fill=(255, 190, 210))
    elif nombre == "hoja_parte":
        img = Image.new("RGBA", (560, 700))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 560, 700], fill=(255, 255, 252), outline=MARRON, width=6)
        d.text((280, 70), "PARTE DE SINIESTRO", font=fuente(44), fill=MARRON, anchor="mm")
        d.text((280, 140), "Solicitante: el perito", font=fuente(34, FUENTE_BOLD), fill=MARRON, anchor="mm")
        for y in range(220, 660, 55):
            d.line([(50, y), (510, y)], fill=(180, 180, 180), width=5)
    else:
        raise KeyError(nombre)
    return img


_props = {}


def prop(nombre):
    if nombre not in _props:
        img = recurso("props", nombre)
        _props[nombre] = img.crop(img.getbbox()) if img is not None else prop_provisional(nombre)
    return _props[nombre]


def prop_ancho(nombre, ancho):
    img = prop(nombre)
    return img.resize((int(ancho), int(img.height * ancho / img.width)), Image.LANCZOS)


# ───────────────────────── textos del canal ─────────────────────────

_emoji_portapapeles = Image.open(os.path.join(REC, "emoji", "1f4cb.png")).convert("RGBA")


def cartel_perito():
    f = fuente(66)
    w, h = 860, 170
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, w - 6, h - 6], 30, fill=CREMA, outline=MARRON, width=9)
    d.rounded_rectangle([6, 6, w - 6, 40], 16, fill=MENTA)
    d.text((w / 2 - 45, h / 2 + 12), "PERITO DE SEGUROS", font=f, fill=MARRON, anchor="mm")
    e = _emoji_portapapeles.resize((84, 84), Image.LANCZOS)
    img.alpha_composite(e, (w - 125, h // 2 - 30))
    return img


def sello(texto, color, ancho):
    f = fuente(130)
    tw = int(f.getlength(texto))
    img = Image.new("RGBA", (tw + 120, 240))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([8, 8, img.width - 8, img.height - 8], 26, outline=color, width=16)
    d.rounded_rectangle([34, 34, img.width - 34, img.height - 34], 16, outline=color, width=6)
    d.text((img.width / 2, img.height / 2 + 6), texto, font=f, fill=color, anchor="mm")
    # textura de tinta
    r = np.random.default_rng(len(texto))
    a = np.asarray(img.getchannel("A")).astype(float) * np.clip(r.normal(0.9, 0.15, (img.height, img.width)), 0.35, 1)
    img.putalpha(Image.fromarray(a.astype(np.uint8)))
    img = img.resize((ancho, int(img.height * ancho / img.width)), Image.LANCZOS)
    return img.rotate(14, Image.BICUBIC, expand=True)


SELLO_APROBADO = sello("APROBADO", VERDE, 520)
SELLO_RECHAZADO = sello("RECHAZADO", ROJO, 860)
CARTEL = cartel_perito()


def dibuja_sello(lienzo, img, cx, cy, t, t0, d=0.08):
    if t < t0:
        return
    k = tramo(t, t0, d)
    pegar(lienzo, img, cx, cy, escala=lerp(2.2, 1.0, k), alfa=lerp(0.2, 0.95, k))


def logo():
    img = recurso("", "logo")
    if img is None:
        f = fuente(56)
        tw = int(f.getlength("Miau con Criterio"))
        img = Image.new("RGBA", (tw + 90, 110))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, img.width - 1, 109], 55, fill=MENTA + (235,), outline=MARRON, width=6)
        d.text((img.width / 2, 57), "Miau con Criterio", font=f, fill=MARRON, anchor="mm")
    img = img.crop(img.getbbox())
    return img.resize((int(img.width * 0.6), int(img.height * 0.6)), Image.LANCZOS)


LOGO = logo()


def subtitulo(lienzo, t, cx, cy):
    for a, b, txt, clave in SUBS:
        if a <= t < b:
            break
    else:
        return
    f = fuente(92)
    trozos = [(txt, CREMA)]
    if clave:
        i = txt.index(clave)
        trozos = [(txt[:i], CREMA), (clave, AMARILLO), (txt[i + len(clave):], CREMA)]
    ancho = sum(f.getlength(s) for s, _ in trozos)
    img = Image.new("RGBA", (int(ancho) + 40, 150))
    d = ImageDraw.Draw(img)
    x = 20
    for s, c in trozos:
        d.text((x + 6, 81), s, font=f, fill=(0, 0, 0, 110), stroke_width=7, stroke_fill=(0, 0, 0, 110), anchor="lm")
        d.text((x, 75), s, font=f, fill=c, stroke_width=7, stroke_fill=MARRON, anchor="lm")
        x += f.getlength(s)
    if img.width > W - 80:
        img = img.resize((W - 80, int(img.height * (W - 80) / img.width)), Image.LANCZOS)
    pegar(lienzo, img, cx, cy, escala=lerp(1.15, 1.0, tramo(t, a, 0.1)))


# ───────────────────────── vídeo fuente ─────────────────────────

class Fuente:
    def __init__(self, ruta, tmp):
        self.ruta = ruta if os.path.exists(ruta) else None
        self.cache = {}
        if self.ruta:
            self.dir = os.path.join(tmp, "fuente")
            os.makedirs(self.dir)
            subprocess.run(["ffmpeg", "-v", "error", "-i", self.ruta, "-vf",
                            f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=decrease,"
                            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2", "-q:v", "2",
                            os.path.join(self.dir, "%05d.jpg")], check=True)
            self.n = len(os.listdir(self.dir))
        else:
            FALTAN.add(ruta)

    def frame(self, t_orig, etiqueta):
        if not self.ruta:
            return self.provisional(t_orig, etiqueta)
        i = min(self.n, max(1, round(t_orig * FPS) + 1))
        if i not in self.cache:
            if len(self.cache) > 90:
                self.cache.clear()
            self.cache[i] = Image.open(os.path.join(self.dir, f"{i:05d}.jpg")).convert("RGBA")
        return self.cache[i]

    def provisional(self, t_orig, etiqueta):
        img = Image.new("RGBA", (W, H), (48, 52, 58, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, AJ["banda_video"][1]], fill=(0, 0, 0))
        d.text((540, 125), "Ranking Funniest Scribble Moments", font=fuente(54), fill=(255, 255, 255), anchor="mm")
        x0, y0, x1, y1 = AJ["ranking"]["caja"]
        d.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], outline=(200, 200, 200), width=4)
        for k in range(5):
            d.text((x0 + 40, y0 + 90 + k * 170), f"{k + 1}.", font=fuente(70), fill=(230, 230, 230), anchor="lm")
        d.text(((x0 + x1) / 2, y1 - 40), "ranking original", font=fuente(30, FUENTE_BOLD), fill=(200, 200, 200), anchor="mm")
        d.text((700, 860), "VÍDEO FUENTE", font=fuente(70), fill=(255, 255, 255), anchor="mm")
        d.text((700, 960), "PENDIENTE", font=fuente(70), fill=(255, 255, 255), anchor="mm")
        d.text((700, 1090), etiqueta, font=fuente(50, FUENTE_BOLD), fill=AMARILLO, anchor="mm")
        d.text((700, 1170), f"orig. {t_orig:5.2f} s", font=fuente(56, FUENTE_BOLD), fill=(220, 220, 220), anchor="mm")
        x = 380 + (t_orig % 2.0) / 2.0 * 640
        d.ellipse([x - 30, 1300, x + 30, 1360], fill=MENTA)
        return img


# ───────────────────────── línea de tiempo ─────────────────────────
# (inicio, fin, puesto, orig_inicio, velocidad, zoom_hasta, zoom_inicio, zoom_dur, etiqueta)
CLIPS = [
    (0.00, 2.36, "p5", 0.20, 1.0, None, 0, 0, "P5 · clip"),
    (2.36, 3.48, "p5", 2.00, 0.5, 1.6, 2.36, 0.34, "P5 · repetición 50 %"),
    (9.00, 10.50, "p4", 5.67, 1.0, None, 0, 0, "P4 · clip A"),
    (10.50, 11.60, "p4", 7.80, 1.0, None, 0, 0, "P4 · clip B"),
    (11.60, 12.30, "p4", 8.20, 1.0, 2.2, 11.60, 0.25, "P4 · repetición"),
    (17.40, 18.30, "p3", 13.00, 1.0, None, 0, 0, "P3 · clip A"),
    (18.30, 19.57, "p3", 14.90, 1.0, None, 0, 0, "P3 · clip B"),
    (19.57, 20.61, "p3", 15.65, 0.5, 1.7, 19.57, 0.33, "P3 · repetición 50 %"),
    (24.10, 26.07, "p2", 20.00, 1.0, None, 0, 0, "P2 · clip"),
    (26.07, 27.11, "p2", 21.45, 0.5, 1.6, 26.07, 0.33, "P2 · repetición 50 %"),
    (31.12, 33.62, "p1", 24.60, 1.0, None, 0, 0, "P1 · clip"),
    (33.62, 34.72, "p1", 26.55, 0.5, 1.7, 33.62, 0.33, "P1 · repetición 50 %"),
]


def zoom(img, escala, cx, cy):
    """Amplía solo la banda de vídeo; la franja negra con el título queda fija."""
    if escala <= 1.001:
        return img
    bx0, by0, bx1, by1 = AJ["banda_video"]
    bw, bh = bx1 - bx0, by1 - by0
    w, h = bw / escala, bh / escala
    x0 = min(max(bx0, cx - w / 2), bx1 - w)
    y0 = min(max(by0, cy - h / 2), by1 - h)
    img = img.copy()
    img.paste(img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((bw, bh), Image.BICUBIC), (bx0, by0))
    return img


_mascaras = {}


def mascara_ranking(fuente_v, puesto):
    """Silueta del ranking original, sacada de un fotograma en negro del mismo tramo."""
    if puesto not in _mascaras:
        cfg = AJ["ranking"]
        negro = fuente_v.frame(cfg["mascara_t"][puesto], "máscara").convert("L").crop(cfg["caja"])
        m = negro.point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(13))
        _mascaras[puesto] = m.filter(ImageFilter.GaussianBlur(2))
    return _mascaras[puesto]


def sin_ranking(recorte, mascara):
    import cv2
    rgb = np.asarray(recorte.convert("RGB"))
    m = (np.asarray(mascara) > 20).astype(np.uint8) * 255
    return Image.fromarray(cv2.inpaint(rgb, m, 7, cv2.INPAINT_TELEA)).convert("RGBA")


def titulo_traducido(lienzo):
    cfg = AJ["titulo"]
    d = ImageDraw.Draw(lienzo)
    d.rectangle(cfg["caja"], fill=cfg["parche"])
    f = fuente(cfg["tamano"], cfg["fuente"])
    for trozos, base in zip(cfg["lineas"], cfg["bases"]):
        x = W / 2 - sum(f.getlength(txt) for txt, _ in trozos) / 2
        for txt, color in trozos:
            d.text((x, base), txt, font=f, fill=color, anchor="ls")
            x += f.getlength(txt)


def frame_clip(fuente_v, t):
    for (a, b, puesto, o0, vel, zh, zt0, zd, etiqueta) in CLIPS:
        if a <= t < b:
            break
    else:
        return None
    original = fuente_v.frame(o0 + (t - a) * vel, etiqueta)
    img = original.copy()
    if zh:
        cx, cy = AJ["zooms"][puesto]
        if fuente_v.ruta:  # el ranking se borra antes de ampliar y se repone sin ampliar
            caja = AJ["ranking"]["caja"]
            mascara = mascara_ranking(fuente_v, puesto)
            img.paste(sin_ranking(original.crop(caja), mascara), caja[:2])
        img = zoom(img, lerp(1.0, zh, suave(tramo(t, zt0, zd))), cx, cy)
        if fuente_v.ruta:
            img.paste(original.crop(caja), caja[:2], mascara)
    titulo_traducido(img)
    pegar(img, LOGO, W / 2, AJ["logo_y"])
    return img


# ───────────────────────── tarjetas del gato ─────────────────────────

FONDOS = {}


def capa_gato(pose, props, rot_bate=None, bate_escala=1.0):
    """Pose + accesorios pegados en sus anclas (coordenadas de la propia pose)."""
    base = pose_img(pose).copy()
    L = ALTO_POSE
    colocacion = {
        "chaleco": ("pecho", 0.40, 0, 0.02), "chaleco_quemado": ("pecho", 0.40, 0, 0.02),
        "acreditacion": ("pecho", 0.11, 0, -0.04), "portapapeles": ("pata", 0.17, -8, 0.02),
        "tirita": ("nariz", 0.11, -10, 0), "pelota_beisbol": ("frente", 0.12, 0, 0),
        "venda": ("oreja", 0.13, 30, 0), "hoja_parte": ("pecho", 0.32, 4, 0.04),
    }
    for p in (p for p in props if p != "cable"):
        punto, ancho, rot, dy = colocacion[p]
        x, y = ancla(pose, punto)
        pegar(base, prop_ancho(p, ancho * L), x, y + dy * L, rot=rot)
    if "cable" in props and recurso("props", "cable") is None:
        d = ImageDraw.Draw(base)
        x, y = ancla(pose, "boca")
        d.line([(x, y), (x + 40, y + 120), (x - 30, y + 260), (x + 20, y + 420)], fill=(240, 120, 20), width=26, joint="curve")
        d.rectangle([x - 10, y + 400, x + 50, y + 470], fill=(90, 90, 90))
    elif "cable" in props:
        x, y = ancla(pose, "boca")
        pegar(base, prop_ancho("cable", 0.12 * L), x, y + 0.13 * L)
    if rot_bate is not None:
        x, y = ancla(pose, "pata")
        pegar(base, prop_ancho("bate", 0.06 * L), x, y - 0.12 * L * bate_escala, escala=bate_escala, rot=rot_bate)
    return base


_capas = {}


def gato_en(lienzo, pose, props, alto, cx, cy, escala=1.0, rot=0.0, rot_bate=None, bate_escala=1.0, blur_x=0, blur_y=0):
    clave = (pose, tuple(props), None if rot_bate is None else round(rot_bate), round(bate_escala, 2), alto)
    if clave not in _capas:
        if len(_capas) > 40:
            _capas.clear()
        c = capa_gato(pose, props, rot_bate, bate_escala)
        _capas[clave] = c.resize((int(c.width * alto / c.height), alto), Image.LANCZOS)
    img = _capas[clave]
    if blur_x or blur_y:  # desenfoque de movimiento: copias desplazadas
        acum = Image.new("RGBA", lienzo.size)
        for k in range(5):
            pegar(acum, img, cx - blur_x * k / 4, cy - blur_y * k / 4, escala, rot, alfa=0.45 if k else 1.0)
        lienzo.alpha_composite(acum)
    else:
        pegar(lienzo, img, cx, cy, escala, rot)
    return img


def punto_en_lienzo(pose, punto, alto, cx, cy, escala=1.0):
    img = pose_img(pose)
    x, y = ancla(pose, punto)
    f = alto / img.height * escala
    return cx + (x - img.width / 2) * f, cy + (y - img.height / 2) * f


def tarjeta1(t):  # 3,48–9,00 · perito, bate y tirita
    l = FONDOS["papel_arrugado"].copy()
    pose = "perito_golpe" if t >= 8.33 else "perito_habla"
    props = ["acreditacion"] + (["tirita"] if t >= 8.60 else [])  # el portapapeles ya está en la pose
    rot_bate, bate_esc = None, 1.0
    if 7.96 <= t < 8.50:
        bate_esc = min(1.0, pop(t, 7.96, 0.1)) if t < 8.06 else 1.0
        rot_bate = 0.0 if t < 8.17 else -360 * tramo(t, 8.17, 0.16)
        if t >= 8.33:
            rot_bate, bate_esc = 40 + 300 * tramo(t, 8.33, 0.17), 1 - tramo(t, 8.33, 0.17)
    escala = pop(t, 3.48) * rebote(t, 8.60, 0.15)
    gato_en(l, pose, props, 760, 330, 870, escala, rot=-8 if t >= 8.33 else 0, rot_bate=rot_bate, bate_escala=bate_esc)
    if t >= 8.60 and t < 8.70:  # pop de la tirita
        x, y = punto_en_lienzo(pose, "nariz", 760, 330, 870)
        pegar(l, prop_ancho("tirita", 0.11 * 760), x, y, escala=pop(t, 8.60, 0.1) * 0.4, alfa=0.6)
    if t >= 4.20:
        k = tramo(t, 4.20, 0.20)
        y = lerp(-250, 330, suave(k)) if t < 4.40 else lerp(330, 300, tramo(t, 4.40, 0.15))
        pegar(l, CARTEL, 600, y)
    if 8.33 <= t < 8.43:
        l.alpha_composite(capa_color((230, 30, 30), 0.5))
    return l, temblor(t, 8.33, 0.25, 12), 1420


def recorte_nina(fuente_v):
    cfg = AJ["recorte_nina"]
    src = fuente_v.frame(cfg["t_orig"], "P4 · recorte niña")
    cara = src.crop(cfg["caja"]).resize((360, 360), Image.LANCZOS)
    if not fuente_v.ruta:
        cara = Image.new("RGBA", (360, 360), (200, 170, 150, 255))
        d = ImageDraw.Draw(cara)
        d.text((180, 150), "NIÑA", font=fuente(56), fill=MARRON, anchor="mm")
        d.text((180, 215), "DE REOJO", font=fuente(44), fill=MARRON, anchor="mm")
    m = Image.new("L", (360, 360), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 359, 359], fill=255)
    cara.putalpha(m)
    marco = Image.new("RGBA", (384, 384))
    ImageDraw.Draw(marco).ellipse([0, 0, 383, 383], fill=(255, 255, 255, 255), outline=MARRON, width=8)
    marco.alpha_composite(cara, (12, 12))
    return marco


def tarjeta2(t, extras):  # 12,30–17,40 · «Señorita…» + «Bizcocho.»
    l = FONDOS["papel"].copy()
    pose = "perito_serio"  # serio a cámara durante toda la tarjeta; ya lleva portapapeles
    alto, cy = 2600, 1250  # la mesa «ENTREVISTAS» queda fuera de cuadro
    x = lerp(-1300, 430, suave(tramo(t, 12.30, 0.20)))
    blur = 70 if t < 12.50 else 0
    gato_en(l, pose, ["tirita"], alto, x, cy, blur_x=blur)
    if t >= 14.95:
        xr = lerp(1260, 870, suave(tramo(t, 14.95, 0.15)))
        pegar(l, extras["nina"], xr, 560, escala=rebote(t, 15.10, 0.15))
        l.alpha_composite(vineta(lerp(0, 0.6, tramo(t, 14.95, 0.63))))
    sx, sy = punto_en_lienzo(pose, "portapapeles", alto, 430, cy)
    dibuja_sello(l, SELLO_APROBADO, min(sx, W - SELLO_APROBADO.width / 2 - 20), sy, t, 16.72)
    return l, temblor(t, 16.80, 0.15, 6), 1560


def tarjeta3(t):  # 20,61–24,10 · «Me pusieron de pelota.»
    l = FONDOS["pista"].copy()
    pose = "perito_confuso" if t >= 23.20 else "espaldas"
    props = ["tirita"] + (["pelota_beisbol"] if t >= 23.20 else []) + (["venda"] if t >= 23.37 else [])
    escala = pop(t, 20.61) * rebote(t, 23.37, 0.2)
    gato_en(l, pose, props, 1300, 760, 1270, escala)
    return l, (0, 0), 330


def tarjeta4(t):  # 27,11–31,12 · «…aquí no me pue—»
    l = FONDOS["feria"].copy()
    pose, alto, cx = "brazos_cruzados", 1100, 540
    props = ["chaleco", "tirita", "pelota_beisbol", "venda"]
    cy = lerp(2600, 1050, suave(tramo(t, 27.11, 0.20)))
    gato_en(l, pose, props, alto, cx, cy, blur_y=-90 if t < 27.31 else 0)
    if t >= 30.95:
        fx, fy = punto_en_lienzo(pose, "nariz", alto, cx, 1050)
        k = tramo(t, 30.95, 0.07)
        bx = lerp(-150, fx, k)
        for j in range(4, 0, -1):  # estela
            pegar(l, prop_ancho("pelota_feria", 170), bx - j * 70, fy, alfa=0.12 * (5 - j))
        pegar(l, prop_ancho("pelota_feria", 170), bx, fy, escala=1.0 if k < 1 else 1.15)
    if t >= 31.02:
        l.alpha_composite(capa_color((255, 120, 190), 0.5))
    return l, temblor(t, 31.02, 0.1, 10), 1720


def humo(l, t, t0, x, y):
    for i in range(int((t - t0) / 0.22) + 1):
        e = t0 + i * 0.22
        k = (t - e) / 1.6
        if 0 <= k < 1:
            r = random.Random(i)
            cx = x + r.uniform(-180, 180) + k * r.uniform(-60, 60)
            cy = y - k * 380
            rad = 40 + k * 90
            pegar(l, _bola_humo, cx, cy, escala=rad / 100, alfa=0.55 * (1 - k))


_bola_humo = Image.new("RGBA", (200, 200))
ImageDraw.Draw(_bola_humo).ellipse([40, 40, 159, 159], fill=(120, 120, 120, 255))
_bola_humo = _bola_humo.filter(ImageFilter.GaussianBlur(14))


def chispa(l, t, t0, x, y):
    if not (t0 <= t < t0 + 0.2):
        return
    d = ImageDraw.Draw(l)
    k = tramo(t, t0, 0.2)
    for ang in range(0, 360, 45):
        a = math.radians(ang + 20)
        r0, r1 = 30 + 80 * k, 90 + 140 * k
        p = [(x + math.cos(a) * r0, y + math.sin(a) * r0),
             (x + math.cos(a + 0.2) * (r0 + r1) / 2, y + math.sin(a + 0.2) * (r0 + r1) / 2),
             (x + math.cos(a) * r1, y + math.sin(a) * r1)]
        d.line(p, fill=AMARILLO, width=14)
        d.line(p, fill=(255, 255, 255), width=5)


def tarjeta5(t):  # 34,72–40,60 · chamuscado + cierre sin voz
    l = FONDOS["papel"].copy()
    pose = "chamuscado_erizado" if t >= 38.16 else "chamuscado"
    alto, cx = 1150, 540
    props = ["chaleco_quemado", "tirita", "pelota_beisbol", "venda", "cable"]
    cy = lerp(2600, 1020, suave(tramo(t, 34.72, 0.25)))
    humo(l, t, 34.72, cx, cy - 520)
    gato_en(l, pose, props, alto, cx, cy, escala=rebote(t, 38.16, 0.24), blur_y=-90 if t < 34.97 else 0)
    ox, oy = punto_en_lienzo(pose, "oreja", alto, cx, 1020)
    chispa(l, t, 38.16, ox, oy)
    if t >= 38.60:
        pegar(l, prop_ancho("hoja_parte", 560), 540, 1330, escala=pop(t, 38.60, 0.2), rot=3)
    dibuja_sello(l, SELLO_RECHAZADO, 540, 960, t, 39.10, 0.10)
    l.alpha_composite(vineta(lerp(0, 0.7, tramo(t, 34.72, DURACION - 34.72))))
    return l, temblor(t, 39.20, 0.25, 14), 1720


def frame_tarjeta(t, extras):
    if 3.48 <= t < 9.00:
        return tarjeta1(t)
    if 12.30 <= t < 17.40:
        return tarjeta2(t, extras)
    if 20.61 <= t < 24.10:
        return tarjeta3(t)
    if 27.11 <= t < 31.12:
        return tarjeta4(t)
    if t >= 34.72:
        return tarjeta5(t)
    raise ValueError(t)


# ───────────────────────── sonido ─────────────────────────
SR = 48000


def _env(n, ataque=0.003, caida=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / ataque)
    return e * (np.exp(-t / caida) if caida else 1)


def sfx_sintetico(nombre):
    r = np.random.default_rng(abs(hash(nombre)) % 2**32)

    def sweep(f0, f1, d, forma=np.sin):
        t = np.arange(int(d * SR)) / SR
        f = np.geomspace(f0, f1, len(t))
        return forma(2 * np.pi * np.cumsum(f) / SR)

    def ruido_filtrado(d, ventana):
        x = r.normal(0, 1, int(d * SR))
        return np.convolve(x, np.ones(ventana) / ventana, "same") * math.sqrt(ventana) * 0.5

    if nombre == "whoosh":
        d = 0.32
        x = ruido_filtrado(d, 12)
        t = np.arange(len(x)) / len(x)
        return x * np.sin(np.pi * t) ** 2 * 0.5
    if nombre == "pop":
        x = sweep(500, 1400, 0.07)
        return x * _env(len(x), 0.002, 0.02)
    if nombre == "blip":
        x = sweep(1300, 1700, 0.09)
        return x * _env(len(x), 0.002, 0.04) * 0.8
    if nombre in ("pum_suave", "pum_seco", "pum_fuerte"):
        d, f, c = {"pum_suave": (0.3, 90, 0.08), "pum_seco": (0.25, 75, 0.06), "pum_fuerte": (0.7, 55, 0.18)}[nombre]
        x = sweep(f * 1.8, f, d) * _env(int(d * SR), 0.002, c)
        n = ruido_filtrado(0.03, 6) * _env(int(0.03 * SR), 0.001, 0.008)
        x[:len(n)] += n * 0.6
        return x
    if nombre == "bonk":
        t = np.arange(int(0.45 * SR)) / SR
        x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((520, 1), (1340, 0.6), (2210, 0.35), (3170, 0.2)))
        return x * _env(len(t), 0.001, 0.09) * 0.5
    if nombre == "boing":
        t = np.arange(int(0.55 * SR)) / SR
        f = 220 * (1 + 0.5 * t / 0.55) * (1 + 0.12 * np.sin(2 * np.pi * 14 * t))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.005, 0.25)
    if nombre == "golpe":  # dura 0,10 s: termina justo en el corte seco
        d = 0.10
        x = sweep(160, 70, d) * _env(int(d * SR), 0.001, 0.05)
        n = ruido_filtrado(d, 4) * _env(int(d * SR), 0.001, 0.015)
        return x + n * 0.7
    if nombre == "chisporroteo":
        x = np.zeros(int(0.5 * SR))
        for p in r.integers(0, len(x) - 400, 70):
            x[p:p + 300] += r.normal(0, 1, 300) * np.exp(-np.arange(300) / 40)
        return x * 0.6
    if nombre == "zap":
        x = sweep(2600, 180, 0.22, lambda p: 2 * (p / (2 * np.pi) % 1) - 1)
        return x * _env(len(x), 0.002, 0.08) * 0.6
    raise KeyError(nombre)


def sfx(nombre):
    for ext in (".wav", ".mp3"):
        p = os.path.join(REC, "sfx", nombre + ext)
        if os.path.exists(p):
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True, check=True).stdout
            return np.frombuffer(raw, np.float32).astype(float)
    FALTAN.add(f"sfx/{nombre}.wav")
    x = sfx_sintetico(nombre)
    return x / (np.max(np.abs(x)) + 1e-9)


# (instante, sonido, dB)
EVENTOS_SFX = [
    (3.48, "whoosh", -10), (4.40, "pum_suave", -10), (7.96, "pop", -12), (8.33, "bonk", -8),
    (8.60, "blip", -12), (12.30, "whoosh", -10), (16.80, "pum_seco", -8), (20.61, "pop", -12),
    (23.20, "boing", -10), (23.37, "blip", -12), (27.11, "whoosh", -10), (31.02, "golpe", -6),
    (34.72, "chisporroteo", -12), (38.16, "zap", -10), (38.60, "blip", -12), (39.20, "pum_fuerte", -6),
]


def pista_sfx(ruta):
    total = np.zeros(int(DURACION * SR) + SR)
    for t, nombre, db in EVENTOS_SFX:
        x = sfx(nombre) * 10 ** (db / 20)
        i = int(t * SR)
        if nombre == "golpe":  # corte seco de audio en 31,12
            x = x[:int((31.12 - t) * SR)]
        total[i:i + len(x)] += x
    total = total[:int(DURACION * SR)]
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(total, -1, 1) * 32767).astype(np.int16).tobytes())


def mezcla(tmp, video_mudo, salida, fuente_v):
    ruta_sfx = os.path.join(tmp, "sfx.wav")
    pista_sfx(ruta_sfx)
    entradas = ["-i", video_mudo, "-i", "voz_gato_montada.wav", "-i", ruta_sfx]
    filtros = ["[1:a]aformat=sample_rates=48000:channel_layouts=mono[voz]",
               "[2:a]aformat=sample_rates=48000:channel_layouts=mono[sfx]"]
    mezclar = ["[voz]", "[sfx]"]
    if fuente_v.ruta:
        entradas += ["-i", fuente_v.ruta]
        for k, (a, b, puesto, o0, vel, *_rest) in enumerate(CLIPS):
            dur_o = (b - a) * vel
            tempo = f",atempo={vel}" if vel != 1.0 else ""
            filtros.append(f"[3:a]atrim={o0}:{o0 + dur_o},asetpts=PTS-STARTPTS{tempo},"
                           f"aformat=sample_rates=48000:channel_layouts=mono,"
                           f"afade=t=in:d=0.01,afade=t=out:st={b - a - 0.01}:d=0.01,"
                           f"volume=-3dB,adelay={round(a * 1000)}[c{k}]")
            mezclar.append(f"[c{k}]")
    filtros.append("".join(mezclar) + f"amix=inputs={len(mezclar)}:normalize=0,apad,atrim=end={DURACION},"
                   "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.79:level=disabled,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", salida], check=True)


# ───────────────────────── render ─────────────────────────

def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else "salida/ranking_desastres.mp4"
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="montaje_")
    try:
        fuente_v = Fuente(AJ["fuente"], tmp)
        for nombre in ("papel_arrugado", "papel", "pista", "feria"):
            FONDOS[nombre] = fondo(nombre)
        for p in ("perito_habla", "perito_golpe", "perito_serio", "espaldas", "perito_confuso",
                  "brazos_cruzados", "chamuscado", "chamuscado_erizado"):
            pose_img(p)
        extras = {"nina": recorte_nina(fuente_v)}
        mudo = os.path.join(tmp, "mudo.mp4")
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                "-crf", "18", "-pix_fmt", "yuv420p", mudo], stdin=subprocess.PIPE)
        for i in range(N):
            t = i / FPS
            img = frame_clip(fuente_v, t)
            if img is None:
                img, (dx, dy), sub_y = frame_tarjeta(t, extras)
                subtitulo(img, t, W / 2, sub_y)
                if dx or dy:
                    img = ImageChops.offset(img, dx, dy)
            enc.stdin.write(img.convert("RGB").tobytes())
            if i % 150 == 0:
                print(f"  fotograma {i}/{N}", flush=True)
        enc.stdin.close()
        if enc.wait():
            raise RuntimeError("ffmpeg falló al codificar el vídeo")
        mezcla(tmp, mudo, salida, fuente_v)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"Listo: {salida}")
    if FALTAN:
        print("Provisionales (faltan en recursos/):")
        for f in sorted(FALTAN):
            print("  -", f)


if __name__ == "__main__":
    main()
