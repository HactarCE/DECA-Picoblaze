    load    s0, 00
    load    s1, 00
loop:
    output  s0, 00
    output  s1, 01
    add     s0, 01
    addcy   s1, 00
    jump    nc, loop
halt:
    jump    halt
