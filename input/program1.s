fld  f1, 0(x9)
fmul f2, f3, f4
fld f1, 0(x10)
fdiv f3, f1, f4
fmul f4, f2, f4
fadd f2, f8, f3
fld f1, 0(x2)
fsd f3, 100(x11)
fsd f4, 200(x12)
