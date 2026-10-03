/*
 * Problema 1 - Laboratorio 8, Teoría de la Computación
 * Uso: ./problema1 <n>
 * Imprime en stdout: n, counter, tiempo_en_segundos
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

/* volatile evita que el compilador elimine o colapse los ciclos */
static volatile long long counter;

void function(int n) {
    int i, j, k;
    counter = 0;
    for (i = n / 2; i <= n; i++) {
        for (j = 1; j + n / 2 <= n; j++) {
            for (k = 1; k <= n; k = k * 2) {
                counter++;
            }
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
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double secs = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
    printf("%d,%lld,%.9f\n", n, counter, secs);
    return 0;
}
