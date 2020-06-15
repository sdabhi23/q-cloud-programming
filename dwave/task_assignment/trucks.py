from dwave.system import DWaveSampler, EmbeddingComposite

Q = {}

for i in range(1, 5):
    Q[(i, i)] = -1

Q[(1,2)] = 1
Q[(1,3)] = 1
Q[(2,4)] = 1
Q[(3,4)] = 1

sampler = EmbeddingComposite(DWaveSampler(solver={'qpu': True}))

res = sampler.sample_qubo(Q,  chain_strength=8, num_reads=10)

print(res)
