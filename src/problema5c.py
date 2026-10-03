"""
Verificación empírica del Problema 5c.
Mide el tiempo de A(n) y lo compara contra n^2 y n^3.
Si f(n) fuera Θ(n²), duplicar n multiplicaría el tiempo por ~4;
si es Θ(n³), lo multiplica por ~8.

Uso: python3 src/problema5c.py
"""
import time


def A(n):
    atupla = tuple(range(0, n))
    S = set()
    for i in range(0, n):
        for j in range(i + 1, n):
            S.add(atupla[i:j])


def medir(n, reps=3):
    mejor = float("inf")
    for _ in range(reps):
        t0 = time.perf_counter()
        A(n)
        mejor = min(mejor, time.perf_counter() - t0)
    return mejor


if __name__ == "__main__":
    print(f"{'n':>6} {'tiempo (s)':>12} {'t(n)/t(n/2)':>12} {'t/n^2 (ns)':>12} {'t/n^3 (ns)':>12}")
    previo = None
    for n in [100, 200, 400, 800, 1600]:
        t = medir(n)
        razon = f"{t / previo:.2f}" if previo else "-"
        print(f"{n:>6} {t:>12.4f} {razon:>12} {t / n**2 * 1e9:>12.2f} {t / n**3 * 1e9:>12.3f}")
        previo = t
