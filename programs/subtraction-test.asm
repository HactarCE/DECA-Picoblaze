    load s5, 60
    output s5, 00
    sub s5, 3F
    output s5, 00
    sub s5, 22
    jump nc, end
    output s5, 00
end:
