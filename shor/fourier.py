import cmath
import math

def f_c(c, q, r):
    x = 0
    for i in range(round(q / r)):
        x += cmath.exp(2 * cmath.pi * 1j * i * ((r * c) % q) / q)
    return x

def prob(c, q, r):
    fc = f_c(c, q, r)
    total = fc.real**2 + fc.imag**2
    return total * r / q**2
