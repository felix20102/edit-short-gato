"""Genera la pista de voz colocada en la línea de tiempo final y los subtítulos.

Uso: python3 generar.py <carpeta_con_gato_1..7.mp3> <carpeta_salida>
"""
import os
import subprocess
import sys
from glob import glob

DURACION = 40.60
FPS = 30

# (archivo, posición en el montaje, recorte de fin dentro del archivo o None)
VOCES = [
    ("gato_1", 3.65, None),   # Soy el perito… A ver, trae.
    ("gato_2", 12.40, None),  # Señorita, para el parte: ¿esto qué es exactamente?
    ("gato_3", 16.25, None),  # Bizcocho.
    ("gato_4", 20.70, None),  # Ese partido lo cubrí yo, ¿eh? Me pusieron de pelota.
    ("gato_5", 27.25, 3.87),  # Revisión de la caseta… no me pue— (corte seco en 31,12)
    ("gato_6", 34.80, None),  # Estoy bien, ¿eh? Estoy bien.
    ("gato_7", 37.04, None),  # Lo he probado para el parte.
]

# (entrada, salida, texto, palabra destacada o None)
SUBS = [
    (3.68, 4.45, "SOY EL PERITO", "PERITO"),
    (4.45, 5.15, "DEL SEGURO", None),
    (5.47, 6.22, "HAY QUE RECONSTRUIR", None),
    (6.22, 7.12, "EL ACCIDENTE", None),
    (7.56, 7.90, "A VER,", None),
    (7.96, 8.33, "TRAE.", "TRAE."),
    (12.40, 13.02, "SEÑORITA,", None),
    (13.34, 13.97, "PARA EL PARTE:", None),
    (14.41, 14.95, "¿ESTO QUÉ ES", None),
    (14.95, 15.58, "EXACTAMENTE?", None),
    (16.38, 16.90, "BIZCOCHO.", "BIZCOCHO."),
    (20.77, 21.40, "ESE PARTIDO", None),
    (21.40, 22.05, "LO CUBRÍ YO, ¿EH?", None),
    (22.52, 23.12, "ME PUSIERON", None),
    (23.12, 23.62, "DE PELOTA.", "PELOTA."),
    (27.28, 27.95, "REVISIÓN", None),
    (27.95, 28.39, "DE LA CASETA.", None),
    (28.71, 29.18, "ME HAN DADO", None),
    (29.18, 29.64, "CHALECO,", "CHALECO,"),
    (29.88, 30.40, "ASÍ QUE AQUÍ", None),
    (30.40, 31.12, "NO ME PUE—", None),
    (35.00, 35.76, "ESTOY BIEN, ¿EH?", None),
    (36.10, 36.69, "ESTOY BIEN.", None),
    (37.09, 37.95, "LO HE PROBADO", None),
    (37.95, 38.40, "PARA EL PARTE.", "PARTE."),
]


def fotograma(t):
    return round(t * FPS) / FPS


def srt_t(t):
    ms = round(fotograma(t) * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def ass_t(t):
    cs = round(fotograma(t) * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def pista_voz(entrada, salida):
    args, filtros = [], []
    for i, (nombre, pos, fin) in enumerate(VOCES):
        args += ["-i", glob(os.path.join(entrada, f"*{nombre}.mp3"))[0]]
        recorte = f"atrim=end={fin},afade=t=out:st={fin - 0.006}:d=0.006," if fin else ""
        retardo = round(pos * 1000)
        filtros.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,{recorte}adelay={retardo}[v{i}]")
    mezcla = "".join(f"[v{i}]" for i in range(len(VOCES)))
    filtros.append(f"{mezcla}amix=inputs={len(VOCES)}:normalize=0,apad,atrim=end={DURACION}[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", ";".join(filtros),
                    "-map", "[out]", "-c:a", "pcm_s16le", os.path.join(salida, "voz_gato_montada.wav")],
                   check=True)


def subtitulos(salida):
    with open(os.path.join(salida, "subtitulos.srt"), "w", encoding="utf-8") as f:
        for n, (a, b, texto, _) in enumerate(SUBS, 1):
            f.write(f"{n}\n{srt_t(a)} --> {srt_t(b)}\n{texto}\n\n")

    # Crema con contorno marrón oscuro; palabra clave en amarillo de acento (#FFD400).
    # ASS usa &HAABBGGRR. Altura 1300 px: por debajo del gato y por encima del logo.
    cabecera = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Gato,Montserrat Black,92,&H00E6F4FA,&H00E6F4FA,&H00142333,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,2,80,80,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(os.path.join(salida, "subtitulos.ass"), "w", encoding="utf-8") as f:
        f.write(cabecera)
        for a, b, texto, clave in SUBS:
            if clave:
                texto = texto.replace(clave, "{\\c&H00D4FF&}" + clave + "{\\c&HE6F4FA&}")
            # pop de entrada: 115 % → 100 % en 0,1 s
            f.write(f"Dialogue: 0,{ass_t(a)},{ass_t(b)},Gato,,0,0,0,,"
                    f"{{\\fscx115\\fscy115\\t(0,100,\\fscx100\\fscy100)}}{texto}\n")


if __name__ == "__main__":
    entrada, salida = sys.argv[1], sys.argv[2]
    os.makedirs(salida, exist_ok=True)
    pista_voz(entrada, salida)
    subtitulos(salida)
