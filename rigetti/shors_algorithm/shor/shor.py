import fourier
import math
import numpy as np
import random
import sys

from fractions import Fraction

from pyquil import Program, get_qc
from pyquil.gates import MEASURE, I, X, CNOT, H, CCNOT, PHASE
from pyquil.quil import address_qubits
from pyquil.quilatom import QubitPlaceholder

import time

qvm = get_qc('15q-qvm')
qvm.compiler.client.timeout = 60  # seconds


def to_control(matrix):
    size = len(matrix)
    ret = []
    I = np.eye(size)
    for i in range(size):
        ret.append(np.concatenate([I[i], np.zeros(size)]))
    for i in range(size):
        ret.append(np.concatenate([np.zeros(size), matrix[i]]))
    return np.asarray(ret)


def bitfield(a, N):
    bits = [1 if digit == '1' else 0 for digit in bin(a)[2:]]
    prefix = [0] * (N - len(bits))
    return prefix + bits


def to_qubits(b, N):
    pq = Program()
    bits = bitfield(b, N)
    placeholders = []
    for i in bits:
        x = QubitPlaceholder()
        if i == 1:
            pq += X(x)
        else:
            pq += I(x)
        placeholders.append(x)
    return pq, placeholders


# https://www.geeksforgeeks.org/multiplicative-inverse-under-modulo-m/
def mod_inverse(a, m):
    m0 = m
    y = 0
    x = 1

    if (m == 1):
        return 0

    while (a > 1 and m > 0):
        # q is quotient 
        q = a // m

        t = m

        # m is remainder now, process 
        # same as Euclid's algo 
        m = a % m
        a = t
        t = y

        # Update x and y 
        y = x - q * y
        x = t

        # Make x positive
    if (x < 0):
        x = x + m0

    return x


class ShorCircuit(object):
    def __init__(self, N):
        self.N = N
        # + 1 to prevent overflow in addition
        self.n = len([1 if digit == '1' else 0 for digit in bin(N)[2:]])
        self.add_ancilla = QubitPlaceholder()
        self.add_gate = lambda k: (lambda q: PHASE(math.pi / (2 ** (k - 1)), q))

    # Adding
    def add(self, b, a, c1=None, c2=None):
        pq = Program()
        a_bits = bitfield(a, len(b))
        for i in range(0, len(b)):
            for j in range(i, len(b)):
                if a_bits[j] == 1:
                    gate = self.add_gate(j - i + 1)(b[i])
                    if c1 is not None:
                        gate = gate.controlled(c1)
                        if c2 is not None:
                            gate = gate.controlled(c2)
                    pq += gate
        return pq

    def inv_add(self, b, a, c1=None, c2=None):
        pq = Program()
        a_bits = bitfield(a, len(b))
        for i in range(len(b) - 1, -1, -1):
            for j in range(len(b) - 1, i - 1, -1):
                if a_bits[j] == 1:
                    gate = self.add_gate(j - i + 1)(b[i]).dagger()
                    if c1 is not None:
                        gate = gate.controlled(c1)
                        if c2 is not None:
                            gate = gate.controlled(c2)
                    pq += gate
        return pq

    # Quantum Fourier Transform
    def qft(self, b):
        pq = Program()
        for j in range(0, len(b)):
            pq += H(b[j])
            for k in range(j + 1, len(b)):
                diff = k - j
                pq += self.add_gate(diff + 1)(b[j]).controlled(b[k])
        return pq

    def inv_qft(self, b):
        pq = Program()
        for j in range(len(b) - 1, -1, -1):
            for k in range(len(b) - 1, j, -1):
                diff = k - j
                pq += self.add_gate(diff + 1)(b[j]).controlled(b[k]).dagger()
            pq += H(b[j])
        return pq

    # Add mod
    def add_mod(self, b, a, c1, c2):
        pq = Program()

        pq += self.add(b, a, c1, c2)
        pq += self.inv_add(b, self.N)
        pq += self.inv_qft(b)
        b_msb = b[0]
        pq += CNOT(b_msb, self.add_ancilla)
        pq += self.qft(b)

        pq += self.add(b, self.N, self.add_ancilla)
        pq += self.inv_add(b, a, c1, c2)

        pq += self.inv_qft(b)
        pq += X(b_msb)
        pq += CNOT(b_msb, self.add_ancilla)
        pq += X(b_msb)
        pq += self.qft(b)

        pq += self.add(b, a, c1, c2)
        return pq

    def inv_add_mod(self, b, a, c1, c2):
        pq = Program()
        pq += self.inv_add(b, a, c1, c2)

        pq += self.inv_qft(b)
        b_msb = b[0]
        pq += X(b_msb)
        pq += CNOT(b_msb, self.add_ancilla)
        pq += X(b_msb)
        pq += self.qft(b)

        pq += self.add(b, a, c1, c2)
        pq += self.inv_add(b, self.N, self.add_ancilla)

        pq += self.inv_qft(b)
        pq += CNOT(b_msb, self.add_ancilla)
        pq += self.qft(b)
        pq += self.add(b, self.N)
        pq += self.inv_add(b, a, c1, c2)
        return pq

    # b + ax mod N
    def cmult(self, b, a, c, x):
        pq = Program()

        pq += self.qft(b)
        a_bits = bitfield(a, self.N)[::-1]
        rev_x = x[::-1]
        for i in range(len(x)):
            a_mod = (2 ** i) * a % self.N
            pq += self.add_mod(b, a_mod, c, rev_x[i])
        pq += self.inv_qft(b)

        return pq

    def inv_cmult(self, b, a, c, x):
        pq = Program()

        pq += self.qft(b)
        a_bits = bitfield(a, self.N)[::-1]
        rev_x = x[::-1]
        for i in range(len(x) - 1, -1, -1):
            a_mod = (2 ** i) * a % self.N
            pq += self.inv_add_mod(b, a_mod, c, rev_x[i])
        pq += self.inv_qft(b)

        return pq

    def cswap(self, x, b, c):
        pq = Program()
        for i in range(len(x)):
            ind = -(i + 1)
            b_i = b[ind]
            x_i = x[ind]
            pq += CNOT(b_i, x_i)
            pq += CCNOT(c, x_i, b_i)
            pq += CNOT(b_i, x_i)
        return pq

    def u_a(self, b_qubits, a, c, x):
        pq = Program()

        pq += self.cmult(b_qubits, a, c, x)
        pq += self.cswap(x, b_qubits, c)
        pq += self.inv_cmult(b_qubits, mod_inverse(a, self.N), c, x)
        return pq

    def partial_inv_qft(self, c, i, ro, total_iters):
        pq = Program()
        for k in range(total_iters - 1, i, -1):
            then_prog = Program(self.add_gate(k - i + 1)(c).dagger())
            pq.if_then(ro[k], then_prog)
        pq += H(c)
        return pq

    # Quantum Fourier Transform
    def end_qft(self, b):
        pq = Program()
        for j in range(0, len(b)):
            pq += H(b[j])
            for k in range(j + 1, len(b)):
                diff = k - j
                pq += self.add_gate(diff + 1)(b[j]).controlled(b[k])
        return pq

    # Builds the circuit for Shor's algorithm.
    def build(self, a):
        pq = Program()

        code, x_qubits = to_qubits(1, self.n)
        pq += code
        code, b_qubits = to_qubits(0, self.n + 1)
        pq += code

        total_iters = 2 * (self.n)
        ro = pq.declare('ro', 'BIT', total_iters + len(x_qubits))

        c = QubitPlaceholder()
        curr_a = a

        '''
        code, ctrl_qubits = to_qubits(0, total_iters)
        pq += code
        for i in range(total_iters):
            ind = total_iters - 1 - i
            c = ctrl_qubits[ind]
            pq += H(c)
            pq += self.u_a(b_qubits, curr_a, c, x_qubits)
            curr_a = curr_a ** 2 % self.N
        for i in range(len(x_qubits)):
            pq += MEASURE(x_qubits[i], ro[total_iters + i])
        ctrl_qubits = ctrl_qubits[::-1]
        pq += self.inv_qft(ctrl_qubits)
        #print(wave.wavefunction(address_qubits(pq)))
        for i in range(total_iters):
            pq += MEASURE(ctrl_qubits[i], ro[i])
        '''
        a_vals = []
        for i in range(total_iters):
            a_vals.append(curr_a)
            curr_a = pow(curr_a, 2, self.N)
        for ind in range(total_iters - 1, -1, -1):
            pq += H(c)
            pq += self.u_a(b_qubits, a_vals[ind], c, x_qubits)
            pq += self.partial_inv_qft(c, ind, ro, total_iters)
            pq += MEASURE(c, ro[ind])

            then_prog = Program(X(c))
            pq.if_then(ro[ind], then_prog)

        return address_qubits(pq)


def find_r(q, c, N):
    frac = Fraction(c, q)
    close_frac = frac.limit_denominator(N)
    return close_frac.denominator


def factor(N):
    print("Factoring {}".format(N))
    if N % 2 == 0:
        print("Factorization: ({}, {})".format(2, N // 2))
        return
    iters = 0
    circuit = ShorCircuit(N)
    q = 2 ** (2 * circuit.n)
    while iters < N:
        y = random.randint(2, N - 1)
        print("y: {}".format(y))
        gcd = math.gcd(y, N)
        if gcd > 1:
            print("Factorization: ({}, {})".format(gcd, N // gcd))
            return
        iters += 1

        pq = circuit.build(y)
        #         for QPU based lattices
        #         result = qvm.run(qvm.compile(pq))
        result = qvm.run(pq)
        c = int(''.join(map(str, result[0])), 2)
        r = find_r(q, c, N)
        print("c: {}; r: {}".format(c, r))

        if r % 2 == 1:
            print("r odd; continuing")
            continue
        factor = pow(y, math.floor(r / 2), N)
        print("factor: {}".format(factor))
        if factor == N - 1:
            print("trivial factor; continuing")
            continue
        f1 = math.gcd(factor - 1, N)
        f2 = math.gcd(factor + 1, N)
        print("f1: {}; f2: {}".format(f1, f2))
        if f1 == 1 or f1 == N - 1:
            if f2 == 1 or f2 == N - 1:
                print("trivial factor, continuing")
                continue
            else:
                print("Factorization: ({}, {})".format(f2, N // f2))
                return
        else:
            print("Factorization: ({}, {})".format(f1, N // f1))
            return
    print("Giving up. =/")


def main():
    N = 25
    y = 4
    r = 10
    # N = 15
    # y = 13
    # r = 4
    # N = 65
    # y = 17
    # r = 12
    circuit = ShorCircuit(N)
    q = 2 ** (2 * circuit.n)
    total_iters = 2 * circuit.n

    pq = circuit.build(y)
    good = []
    bad = []
    num_trials = 10
    times = []
    correct = 0
    close = 0
    wrong = 0

    for i in range(num_trials):
        start_time = time.time()
        result = qvm.run(pq)
        end_time = time.time()
        runtime = end_time - start_time
        times.append(runtime)
        print("Runtime: {}".format(runtime))
        for b in result:
            dec_result = int(''.join(map(str, b[:total_iters])), 2)

            frac = Fraction(dec_result, q)
            close_frac = frac.limit_denominator(N)
            c_prime = close_frac.numerator
            r_prime = close_frac.denominator
            if r_prime == r:
                correct += 1
            elif r % r_prime == 0:
                close += 1
            else:
                wrong += 1

            prob_result = fourier.prob(dec_result, q, r)
            print("Result: {}".format(dec_result))
            print("Probability: {}".format(prob_result))
            if prob_result >= 0.01:
                good.append((dec_result, prob_result))
            else:
                bad.append((dec_result, prob_result))
            print("Good: {}; Bad: {}".format(len(good), len(bad)))
    print("Average runtime: {}s".format(np.mean(times)))
    print("Std: {}".format(np.std(times)))
    print("Correct: {}, Close: {}, Wrong: {}".format(correct, close, wrong))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python shor.py N")
        exit()
    try:
        N = int(sys.argv[1])
        if N < 3:
            print("Please use an N >= 3.")
            exit()
        factor(N)
    except:
        print("Error: N must be an integer")
        exit()
