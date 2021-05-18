import random

size = 80 

# The rule is one unit transaction (buy or sell) allowed
# at one time
def optimal(market):
    distrib = sorted(market)
    bp = int(round(len(market)/2))
    return sum(distrib[bp:]) - sum(distrib[:bp])

def rand(market, iterations=20):
    avg = 0 
    bp = int(round(len(market)/2))
    for i in range(iterations):
        random.shuffle(market)
        avg += sum(market[bp:]) - sum(market[:bp])
    return avg / iterations
    
def rw(count, start=5, delta=0.25):
   ret = []
   for i in range(count):
       ix = random.random()
       if ix > 2.0/3.0:
           start += delta
       elif ix < 1.0/3.0:
           start -= delta

       ret.append(start)

   return ret

market = rw(100)

print(market)
print(optimal(market))
print(rand(market))
"""
for b in range(1, size):
    p = [20.0] + [5.0 for i in range(b)] + [6.0 for i in range(b)]
    s = [ 5.8 for i in range(b) ]

    print ("{:>2} {:5.2f} {:5.2f} {:7.2f} {:7.2f}".format(
        b, (sum(p) / len(p)), (sum(p) - sum(s)) / (len(p) - len(s)),
        sum(p), sum(p) - sum(s)
        ))
"""
