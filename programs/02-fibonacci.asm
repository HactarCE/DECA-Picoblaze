; s0, s1 = smaller number or sum
; s2, s3 = bigger number
; s4, s5 = sum / scratch space for BCD
; sA, sB, sC = BCD


    load    s2, 01

loop:

    ;; compute next number (sum <-- small + big)

    load    s4, s0
    load    s5, s1
    add     s4, s2
    addcy   s5, s3

    ;; halt on overflow

    jump    c, halt

    ;; rearrange numbers (small <-- big; big <-- sum)

    load    s0, s2
    load    s1, s3
    load    s2, s4
    load    s3, s5

    ;; compute BCD

    load    sA, 0
    load    sB, 0
    load    sC, 0

divide_10000:
    ; 10000'd = 0x2710
    add     sC, 01
    sub     s4, 10
    subcy   s5, 27
    jump    nc, divide_10000
    sub     sC, 01
    add     s4, 10
    addcy   s5, 27

divide_1000:
    ; 1000'd = 0x03E8
    add     sB, 10
    sub     s4, E8
    subcy   s5, 03
    jump    nc, divide_1000
    sub     sB, 10
    add     s4, E8
    addcy   s5, 03

divide_100:
    add     sB, 01
    sub     s4, 100'd
    subcy   s5, 00
    jump nc, divide_100
    sub     sB, 01
    add     s4, 100'd
    addcy   s5, 00

divide_10:
    add     sA, 10
    sub     s4, 10'd
    jump nc, divide_10
    sub     sA, 10
    add     s4, 10'd

divide_1:
    add     sA, s4

    ;; output

    output  sA, 00
    output  sB, 01
    output  sC, 02

    jump loop

halt:

    jump    halt
