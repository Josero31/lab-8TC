/*
 * Problema 2 - Laboratorio 8, Teoría de la Computación
 * Uso: ./problema2 <n> > /dev/null
 * Los printf de "Sequence" van a stdout; el resultado (n, impresiones, tiempo)
 * va a stderr para no mezclarse con la salida del algoritmo.
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static long long impresiones = 0;

void function(int n) {
    if (n <= 1) return;
    int i, j;
    for (i = 1; i <= n; i++) {
        for (j = 1; j <= n; j++) {
            printf("Sequence\n");
            impresiones++;
            break;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: %s <n>\n", argv[0]);
        return 1;
    }
    int n = atoi(argv[1]);
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    function(n);
    fflush(stdout);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double secs = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
    fprintf(stderr, "%d,%lld,%.9f\n", n, impresiones, secs);
    return 0;
}
