import random

def flip(p):
    p = float(p)
    if p.is_integer():
        p = p / 10
        print(p)
    return (random.random() < p)