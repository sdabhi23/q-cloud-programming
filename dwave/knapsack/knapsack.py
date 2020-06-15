from dwave.system import DWaveSampler, EmbeddingComposite

Q = {}
g = 36

Q[(0, 0)] = 17 - 3 * g
Q[(1, 1)] = 21 - 3 * g
Q[(2, 2)] = 19 - 3 * g

Q[(0, 1)] = 2 * g
Q[(0, 2)] = 2 * g
Q[(1, 2)] = 2 * g

sampler = EmbeddingComposite(DWaveSampler(solver={'qpu': True}))

res = sampler.sample_qubo(Q,  chain_strength=30, num_reads=10)

print(res)
