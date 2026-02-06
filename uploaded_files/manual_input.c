#include <stdio.h>

int main() {
    int x;   // WARNING: variable declared but never initialized
    int y = 0;

    // CRITICAL: possible division by zero
    int result = 10 / y;

    // INFO: magic number used directly
    for (int i = 0; i < 42; i++) {
        printf("Iteration %d\n", i);
    }

    // WARNING: unused variable
    int unusedVar = 100;

    // CRITICAL: infinite loop (logic error)
    while (1) {
        printf("This will run forever!\n");
        break; // INFO: misleading break (loop still unnecessary)
    }

    return 0;
}
