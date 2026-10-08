"""Versión sencilla: clips originales sin tocar y, entre ellos, el gato hablando.

Uso (desde montaje/):  python3 herramientas/montar_simple.py [salida.mp4]

- Clips: el vídeo fuente tal cual (imagen y sonido), sin dibujos a lápiz ni
  pantallas en negro entre puestos. Sin zooms, repeticiones, título ni logo.
- Gato: fondo de papel claro, la pose de cada comentario, su voz y subtítulos.
  Solo se mueve al hablar (rebote suave según el volumen de la voz).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar as m  # noqa: E402
from generar import SUBS, VOCES  # noqa: E402

FPS, SR, W, H = m.FPS, 48000, m.W, m.H
VOZ_DIR = "recursos/voz"

# Clips completos del original (inicio, fin en s), sin las partes en negro ni los dibujos.
CLIPS = {"p5": (0.00, 2.56), "p4": (5.67, 9.13), "p3": (12.80, 16.17), "p2": (20.00, 21.97), "p1": (24.60, 27.10)}

# Tarjetas del gato: voces (archivo, retraso desde el inicio de la tarjeta), cambios de pose y cola final.
TARJETAS = [
    {"voces": [("gato_1", 0.15)], "poses": [(0, "perito_habla")], "cola": 0.10},
    {"voces": [("gato_2", 0.15), ("gato_3", 4.00)], "poses": [(0, "perito_serio")], "cola": 0.15, "primer_plano": True},
    {"voces": [("gato_4", 0.15)], "poses": [(0, "espaldas"), (2.65, "perito_confuso")], "cola": 0.10},
    {"voces": [("gato_5", 0.15)], "poses": [(0, "brazos_cruzados")], "cola": 0.0, "corte_voz": 3.87},
    {"voces": [("gato_6", 0.0), ("gato_7", 2.24)], "poses": [(0, "chamuscado")], "cola": 0.50},
]
ORDEN = ["p5", 0, "p4", 1, "p3", 2, "p2", 3, "p1", 4]


def leer_voz(nombre):
    ruta = next(os.path.join(VOZ_DIR, f) for f in os.listdir(VOZ_DIR) if f.endswith(nombre + ".mp3"))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(float)


def snap(t):
    return round(t * FPS) / FPS


def linea_de_tiempo():
    """Devuelve los tramos [(inicio, fin, tipo, dato)], la pista de voz y los subtítulos desplazados."""
    tramos, t = [], 0.0
    voz = np.zeros(int(60 * SR))
    subs = []
    pos_antigua = {nombre: pos for nombre, pos, _ in VOCES}
    for paso in ORDEN:
        if isinstance(paso, str):
            a, b = CLIPS[paso]
            fin = snap(t + b - a)
            tramos.append((t, fin, "clip", (paso, a)))
            t = fin
            continue
        tj = TARJETAS[paso]
        fin_voz = t
        for nombre, retraso in tj["voces"]:
            x = leer_voz(nombre)
            if tj.get("corte_voz"):
                x = x[:int(tj["corte_voz"] * SR)]
                x[-300:] *= np.linspace(1, 0, 300)
            i = int((t + retraso) * SR)
            voz[i:i + len(x)] += x
            fin_voz = max(fin_voz, t + retraso + len(x) / SR)
            delta = t + retraso - pos_antigua[nombre]
            ini_old = pos_antigua[nombre]
            fin_old = ini_old + len(x) / SR + 0.05
            subs += [(a + delta, min(b, fin_old) + delta, txt, clave) for a, b, txt, clave in SUBS
                     if ini_old <= a < fin_old]
        fin = snap(fin_voz + tj["cola"])
        tramos.append((t, fin, "gato", (paso, t)))
        t = fin
    return tramos, voz[:int(t * SR)], subs, t


def envolvente(voz):
    """Volumen de la voz por fotograma (0–1), suavizado."""
    paso = SR // FPS
    v = np.array([np.sqrt(np.mean(voz[i:i + paso] ** 2) + 1e-12) for i in range(0, len(voz) - paso + 1, paso)] + [0.0])
    v = np.clip(v / (np.percentile(v[v > 1e-4], 90) + 1e-9), 0, 1)
    return np.convolve(v, np.ones(3) / 3, "same")


def frame_gato(paso, t_local, t, env, subs, fondo):
    tj = TARJETAS[paso]
    pose = [p for t0, p in tj["poses"] if t_local >= t0][-1]
    img = fondo.copy()
    k = env[min(len(env) - 1, int(t * FPS))]
    escala = m.pop(t_local, 0.0, 0.15) * (1 + 0.03 * k)
    if tj.get("primer_plano"):  # corte directo al primer plano, sin pop
        m.gato_en(img, pose, [], 2600, 430, 1250, 1 + 0.03 * k)
        sub_y = 1560
    else:
        m.gato_en(img, pose, [], 1150, 540, 900 - 25 * k, escala)
        sub_y = 1640
    m.subtitulo(img, t, W / 2, sub_y, subs)
    return img


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else "salida/ranking_desastres_simple.mp4"
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    tramos, voz, subs, total = linea_de_tiempo()
    env = envolvente(voz)
    tmp = tempfile.mkdtemp(prefix="simple_")
    try:
        fuente = m.Fuente(m.AJ["fuente"], tmp)
        if not fuente.ruta:
            sys.exit("Falta el vídeo fuente en " + m.AJ["fuente"])
        fondo = m.fondo("papel")
        mudo = os.path.join(tmp, "mudo.mp4")
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                "-pix_fmt", "yuv420p", mudo], stdin=subprocess.PIPE)
        for i in range(round(total * FPS)):
            t = i / FPS
            a, b, tipo, dato = next(tr for tr in tramos if tr[0] <= t + 1e-6 < tr[1])
            if tipo == "clip":
                img = fuente.frame(dato[1] + (t - a), "")
            else:
                img = frame_gato(dato[0], t - a, t, env, subs, fondo)
            enc.stdin.write(img.convert("RGB").tobytes())
        enc.stdin.close()
        if enc.wait():
            raise RuntimeError("ffmpeg falló al codificar el vídeo")

        ruta_voz = os.path.join(tmp, "voz.wav")
        with wave.open(ruta_voz, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes())
        filtros, mezcla = ["[1:a]aformat=sample_rates=48000:channel_layouts=stereo[voz]"], ["[voz]"]
        for k, (a, b, tipo, dato) in enumerate(tr for tr in tramos if tr[2] == "clip"):
            o0 = dato[1]
            filtros.append(f"[2:a]atrim={o0}:{o0 + b - a},asetpts=PTS-STARTPTS,"
                           f"aformat=sample_rates=48000:channel_layouts=stereo,"
                           f"afade=t=in:d=0.01,afade=t=out:st={b - a - 0.01}:d=0.01,adelay={round(a * 1000)}:all=1[c{k}]")
            mezcla.append(f"[c{k}]")
        filtros.append("".join(mezcla) + f"amix=inputs={len(mezcla)}:normalize=0,apad,atrim=end={total},"
                       "alimiter=limit=0.79:level=disabled[a]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mudo, "-i", ruta_voz, "-i", fuente.ruta,
                        "-filter_complex", ";".join(filtros), "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", salida], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"Listo: {salida} ({total:.2f} s)")
    for a, b, tipo, dato in tramos:
        print(f"  {a:6.2f}–{b:6.2f}  {tipo:5s}  {dato[0] if tipo == 'clip' else 'gato ' + str(dato[0] + 1)}")


if __name__ == "__main__":
    main()
