"""
Profiling de los problemas 1, 2 y 3 del Laboratorio 8.

Ejecuta cada programa compilado (bin/problemaX) con
n en {1, 10, 100, 1000, 10000, 100000, 1000000}, mide el tiempo de la
función (medido dentro del programa con clock_gettime) y genera:
  - resultados/problemaX.csv   (tabla)
  - resultados/problemaX.md    (tabla en markdown)
  - resultados/problemaX.png   (gráfica n vs tiempo)

Si una corrida supera el TIMEOUT, el tiempo se ESTIMA a partir de la
complejidad teórica y la corrida medida más grande (se marca como "estimado").

Uso:
    make
    python3 profiling.py            # los tres problemas
    python3 profiling.py 1 3        # solo los problemas 1 y 3
    TIMEOUT=600 python3 profiling.py
"""
import csv
import math
import os
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NS = [1, 10, 100, 1000, 10000, 100000, 1000000]
TIMEOUT = float(os.environ.get("TIMEOUT", "1500"))  # segundos por corrida
REPS_RAPIDAS = 5  # repeticiones (mediana) cuando la corrida tarda < 1 s
OUT = "resultados"


def ops_p1(n):
    """Número exacto de veces que se ejecuta counter++."""
    if n < 1:
        return 0
    externo = n - n // 2 + 1
    medio = n - n // 2  # j recorre 1..(n - n/2)
    interno = n.bit_length()  # k = 1,2,4,...,<= n  -> floor(log2 n) + 1
    return externo * medio * interno


def ops_p2(n):
    return n if n > 1 else 0


def ops_p3(n):
    return (n // 3) * ((n + 3) // 4)


PROBLEMAS = {
    1: {"ops": ops_p1, "salida": "stdout", "teorica": "O(n² log n)",
        "f": lambda n: n * n * math.log2(n) if n > 1 else 1},
    2: {"ops": ops_p2, "salida": "stderr", "teorica": "O(n)",
        "f": lambda n: n},
    3: {"ops": ops_p3, "salida": "stderr", "teorica": "O(n²)",
        "f": lambda n: n * n},
}


def correr(p, n):
    """Devuelve (operaciones, segundos) o None si excede el timeout."""
    cmd = [f"./bin/problema{p}", str(n)]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE if PROBLEMAS[p]["salida"] == "stdout" else subprocess.DEVNULL,
                           stderr=subprocess.PIPE, timeout=TIMEOUT, text=True, check=True)
    except subprocess.TimeoutExpired:
        return None
    linea = (r.stdout if PROBLEMAS[p]["salida"] == "stdout" else r.stderr).strip().splitlines()[-1]
    _, ops, t = linea.split(",")
    return int(ops), float(t)


def medir(p, n):
    res = correr(p, n)
    if res is None:
        return None
    ops, t = res
    if t < 1.0:  # corridas rápidas: mediana de varias repeticiones
        tiempos = [t] + [correr(p, n)[1] for _ in range(REPS_RAPIDAS - 1)]
        t = sorted(tiempos)[len(tiempos) // 2]
    return ops, t


def profile(p):
    info = PROBLEMAS[p]
    filas = []
    for n in NS:
        print(f"Problema {p}: n = {n} ...", flush=True)
        res = medir(p, n)
        if res is None:
            # Estimar con la última corrida medida: t(n) ≈ t(m) * ops(n) / ops(m)
            ref = [f for f in filas if f["tipo"] == "medido" and f["ops"] > 0][-1]
            t = ref["tiempo_s"] * info["ops"](n) / ref["ops"]
            filas.append({"n": n, "ops": info["ops"](n), "tiempo_s": t, "tipo": "estimado"})
            print(f"   > timeout ({TIMEOUT:.0f}s). Estimado: {t:.2f} s")
        else:
            ops, t = res
            assert ops == info["ops"](n), f"conteo inesperado p{p} n={n}: {ops} vs {info['ops'](n)}"
            filas.append({"n": n, "ops": ops, "tiempo_s": t, "tipo": "medido"})
            print(f"   > {t:.6f} s  ({ops} operaciones)")
    guardar(p, filas)
    graficar(p, filas)
    return filas


def fmt_t(t):
    if t < 1e-3:
        return f"{t * 1e6:.2f} µs"
    if t < 1:
        return f"{t * 1e3:.3f} ms"
    if t < 3600:
        return f"{t:.3f} s"
    return f"{t:,.0f} s (≈ {t / 3600:.1f} h)"


def guardar(p, filas):
    with open(f"{OUT}/problema{p}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["n", "ops", "tiempo_s", "tipo"])
        w.writeheader()
        w.writerows(filas)
    with open(f"{OUT}/problema{p}.md", "w") as fh:
        fh.write(f"| n | Operaciones | Tiempo | Tipo |\n|---:|---:|---:|:---|\n")
        for f in filas:
            fh.write(f"| {f['n']:,} | {f['ops']:,} | {fmt_t(f['tiempo_s'])} | {f['tipo']} |\n")


def graficar(p, filas):
    info = PROBLEMAS[p]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    validas = [f for f in filas if f["tiempo_s"] > 0]
    med = [f for f in validas if f["tipo"] == "medido"]
    est = [f for f in validas if f["tipo"] == "estimado"]
    ax.plot([f["n"] for f in med], [f["tiempo_s"] for f in med], "o-", color="#2563eb", label="Medido")
    if est:
        puente = [med[-1]] + est
        ax.plot([f["n"] for f in puente], [f["tiempo_s"] for f in puente], "--", color="#dc2626")
        ax.plot([f["n"] for f in est], [f["tiempo_s"] for f in est], "s", color="#dc2626",
                label="Estimado (excede timeout)")
    # Curva teórica escalada a la corrida medida más grande
    ref = med[-1]
    c = ref["tiempo_s"] / info["f"](ref["n"])
    xs = [n for n in NS if n >= 10]
    ax.plot(xs, [c * info["f"](n) for n in xs], ":", color="#6b7280", label=f"Teórica {info['teorica']}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Tamaño del input n (escala log)")
    ax.set_ylabel("Tiempo (s, escala log)")
    ax.set_title(f"Problema {p}: tamaño de input vs. tiempo")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{OUT}/problema{p}.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    args = sys.argv[1:]
    solo_graficas = "--solo-graficas" in args  # regenera tablas/gráficas desde los CSV
    problemas = [int(a) for a in args if a.isdigit()] or [1, 2, 3]
    for p in problemas:
        if solo_graficas:
            with open(f"{OUT}/problema{p}.csv") as fh:
                filas = [{"n": int(r["n"]), "ops": int(r["ops"]), "tiempo_s": float(r["tiempo_s"]),
                          "tipo": r["tipo"]} for r in csv.DictReader(fh)]
            guardar(p, filas)
            graficar(p, filas)
        else:
            profile(p)
