#include <bits/stdc++.h>

#define CONCAT3_NX(x, y, z) x ## y ## z
#define CONCAT3(x, y, z) CONCAT3_NX(x, y, z)
#define VAR(name) CONCAT3(__tmpvar__, name, __LINE__)
#define TYPE(x) __typeof(x)

#define FOR(i, s, n)  for (TYPE(n) i=(s),   VAR(end)=(n);  i <  VAR(end);  i++)
#define FORN(i, n)    FOR(i, 0, n)
#define SCi(a) scanf("%d", &a)
#define SCl(a) scanf("%llu", &a)

unsigned long long N;
unsigned int *sbox;
unsigned int *ddt;
unsigned long long *counts;

void *assert_not_null(void *p) {
    if (!p) {
        perror("error");
        exit(1);
    }
}

int main() {
    scanf("%llu\n", &N);

    sbox = (unsigned int*)calloc(N, sizeof(unsigned int));
    assert_not_null(sbox);
    ddt = (unsigned int*)calloc(N, sizeof(unsigned int));
    assert_not_null(ddt);
    counts = (unsigned long long*)calloc(N + 1024, sizeof(unsigned long long));
    assert_not_null(counts);

    FORN(i, N) {
        SCi(sbox[i]);
    }

    FOR(dx, 1, N) {
        FORN(x, N) {
            int x2 = x ^ dx;
            int y = sbox[x];
            int y2 = sbox[x2];
            int dy = y ^ y2;
            ddt[dy] += 1;
            // printf("  x %d x2 %d dx %d y %d y2 %d dy %d ddt[dy] %d\n", x, x2, dx, y, y2, dy, ddt[dy]);
        }
        FOR(dy, 0, N) {
            // printf("dx: %d dy: %d ddt[dy]: %d counts[]: %d\n", dx, dy, ddt[dy], counts[ddt[dy]]);
            counts[ddt[dy]]++;
            ddt[dy] = 0;
        }
    }

    printf("{");
    FORN(c, N + 1) {
        if (counts[c]) {
            printf("%llu: %llu, ", c, counts[c]);
        }
    }
    printf("}\n");
    return 0;
}
