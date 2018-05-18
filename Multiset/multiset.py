import collections
import functools
import itertools

def multiset_subset(multiset):
    
    cnt = collections.Counter(multiset.split(','))
    
    def mapper(L):
        return ','.join(functools.reduce(lambda a, b: a + b, [[k] * v for k, v in zip(cnt.keys(), L)]))
    
    res = []
    
    for comb in itertools.product(*[list(range(v + 1)) for v in cnt.values()]):
        if sum(comb) > 0: res.append(mapper(comb))
    
    return res