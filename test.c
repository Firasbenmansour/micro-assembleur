#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// Flags
int8_t ZF = 0, SF = 0, OF = 0;

// Stack implementation
#define STACK_SIZE 500
int8_t stack[STACK_SIZE];
int stack_pointer = 0;

void push(int8_t value) {
    if (stack_pointer >= STACK_SIZE) {
        printf("Stack overflow\n");
        exit(1);
    }
    stack[stack_pointer++] = value;
}

int8_t pop(void) {
    if (stack_pointer <= 0) {
        printf("Stack underflow\n");
        exit(1);
    }
    return stack[--stack_pointer];
}

void update_flags(int value) {
    ZF = (value == 0);
    SF = (value < 0);
    OF = (value < -127 || value > 128);
}

int main(void) {
    int8_t x = 0;
    int8_t y[10] = {0};

    x = 5;
    x += 3;
    update_flags(x);
    printf("%d\n", x);
    y[0] = 42;
    printf("%d\n", y[0]);
    exit(0);

    return 0;
}