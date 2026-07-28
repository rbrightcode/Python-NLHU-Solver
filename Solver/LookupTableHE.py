def has_straight(mask):
    for start in range(9):
        if mask & (0b11111 << start) == (0b11111 << start):
            return True

    # wheel
    wheel = (1 << 12) | (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3)
    return (mask & wheel) == wheel


i = -1

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

HighCard = {}
bit_old = 0
for a in range(6, 13):
    for b in range(5, a):
        for c in range(4, b):
            for d in range(3, c):
                for e in range(2, d):
                    for f in range(1, e):
                        for g in range(0, f):
                            mask = ((1 << a) | (1 << b) | (1 << c) | (1 << d) | (1 << e) | (1 << f) | (1 << g))
                            if has_straight(mask):
                                continue
                            bit_eff = primes[a] * primes[b] * primes[c] * primes[d] * primes[e]
                            if bit_eff != bit_old:
                                i += 1
                                bit_old = bit_eff
                            bit = primes[a] * primes[b] * primes[c] * primes[d] * primes[e] * primes[f] * primes[g]
                            HighCard.update({bit: i})

Pair = {}
bit_old = 0
for a in range(0, 13):
    for b in range(4, 13):
        for c in range(3, b):
            for d in range(2, c):
                for e in range(1, d):
                    for f in range(0, e):
                        mask = ((1 << a) | (1 << b) | (1 << c) | (1 << d) | (1 << e) | (1 << f))
                        if has_straight(mask) or (a == b) or (a == c) or (a == d) or (a == e) or (a == f):
                            continue
                        bit_eff = (primes[a] ** 2) * primes[b] * primes[c] * primes[d]
                        if bit_eff != bit_old:
                            i += 1
                            bit_old = bit_eff
                        bit = (primes[a] ** 2) * primes[b] * primes[c] * primes[d] * primes[e] * primes[f]
                        Pair.update({bit: i})

TwoPair = {}
bit_old = 0
for a in range(1, 13):
    for b in range(0, a):
        for c in range(1, 13):
            for d in range(0, c):
                for e in range(0, c):
                    mask = ((1 << a) | (1 << b) | (1 << c) | (1 << d) | (1 << e))
                    if has_straight(mask) or (len(set([a, b, c, d, e])) != 5):
                        continue
                    bit_eff = (primes[a] ** 2) * (primes[b] ** 2) * primes[c]
                    if bit_eff != bit_old:
                        i += 1
                        bit_old = bit_eff
                    bit = (primes[a] ** 2) * (primes[b] ** 2) * primes[c] * primes[d] * primes[e]
                    TwoPair.update({bit: i})
                    if c < b:
                        bit = (primes[a] ** 2) * (primes[b] ** 2) * (primes[c] ** 2) * primes[d]
                        TwoPair.update({bit: i})
                        bit = (primes[a] ** 2) * (primes[b] ** 2) * (primes[c] ** 2) * primes[e]
                        TwoPair.update({bit: i})
                    if d < b:
                        bit = (primes[a] ** 2) * (primes[b] ** 2) * (primes[d] ** 2) * primes[c]
                        TwoPair.update({bit: i})
                        bit = (primes[a] ** 2) * (primes[b] ** 2) * (primes[d] ** 2) * primes[e]
                        TwoPair.update({bit: i})

Trips = {}
bit_old = 0
for a in range(0, 13):
    for b in range(3, 13):
        for c in range(2, b):
            for d in range(1, c):
                for e in range(0, d):
                    mask = ((1 << a) | (1 << b) | (1 << c) | (1 << d) | (1 << e))
                    if has_straight(mask) or (len(set([a, b, c, d, e])) != 5):
                        continue
                    bit_eff = (primes[a] ** 3) * primes[b] * primes[c]
                    if bit_eff != bit_old:
                        i += 1
                        bit_old = bit_eff
                    bit = (primes[a] ** 3) * primes[b] * primes[c] * primes[d] * primes[e]
                    Trips.update({bit: i})

Straight = {}
bit_old = 0
# Start with the low Straight
i += 1
for a in range(0, 13):
    for b in range(0, 13):
        bit_eff = primes[12] * primes[3] * primes[2] * primes[1] * primes[0]
        bit = bit_eff * primes[a] * primes[b]
        if a != 4 and b != 4:
            Straight.update({bit: i})

# Now for all other straights
bit_old = 0
for a in range(4, 13):
    for b in range(3, a):
        for c in range(2, b):
            for d in range(1, c):
                for e in range(0, d):
                    for f in range(0, 13):
                        for g in range(0, 13):
                            if a - e == 4 and f != a + 1 and g != a + 1:
                                bit_eff = primes[a] * primes[b] * primes[c] * primes[d] * primes[e]
                                if bit_old != bit_eff:
                                    bit_old = bit_eff
                                    i += 1
                                bit = bit_eff * primes[f] * primes[g]
                                Straight.update({bit: i})

primes_flush = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

Flush = {}
bit_old = 0
for a in range(5, 14):
    for b in range(4, a):
        for c in range(3, b):
            for d in range(2, c):
                for e in range(1, d):
                    for f in range(0, e):
                        for g in range(0, f + 1):
                            if a - e != 4 and not (b - f == 4 and f != 0) and not (c - g == 4 and g != 0) and not (
                                    a == 13 and b == 4 and c == 3 and d == 2 and e == 1) and not (f == g and f != 0):
                                bit_eff = primes_flush[a] * primes_flush[b] * primes_flush[c] * primes_flush[d] * \
                                          primes_flush[e]
                                if bit_eff != bit_old:
                                    i += 1
                                    bit_old = bit_eff
                                bit = bit_eff * primes_flush[f] * primes_flush[g]
                                Flush.update({bit: i})

FullHouse = {}
bit_old = 0
for a in range(0, 13):
    for b in range(0, 13):
        for c in range(0, 13):
            for d in range(0, 13):
                if a != b and a != c and a != d and not (b > a and (b == c or b == d)) and not (c == d and c > b):
                    bit_eff = (primes[a] ** 3) * (primes[b] ** 2)
                    if bit_eff != bit_old:
                        i += 1
                        bit_old = bit_eff
                    bit = bit_eff * primes[c] * primes[d]
                    FullHouse.update({bit: i})

Quads = {}
bit_old = 0
for a in range(0, 13):
    for b in range(0, 13):
        for c in range(0, b + 1):
            for d in range(0, c + 1):
                if a != b and a != c and a != d:
                    bit_eff = (primes[a] ** 4) * primes[b]
                    if bit_eff != bit_old:
                        i += 1
                        bit_old = bit_eff
                    bit = bit_eff * primes[c] * primes[d]
                    Quads.update({bit: i})

StraightFlush = {}
bit_old = 0
# Start with the low Straight
i += 1
for a in range(0, 14):
    for b in range(0, a + 1):
        bit_eff = primes_flush[13] * primes_flush[4] * primes_flush[3] * primes_flush[2] * primes_flush[1]
        bit = bit_eff * primes_flush[a] * primes_flush[b]
        if a != 1 and a != 2 and a != 3 and a != 4 and a != 5 and a != 13 and b != 1 and b != 2 and b != 3 and b != 4 and b != 5 and b != 13 and not (
                a == b and a != 0):
            StraightFlush.update({bit: i})

bit_old = 0
for a in range(5, 14):
    for b in range(4, a):
        for c in range(3, b):
            for d in range(2, c):
                for e in range(1, d):
                    for f in range(0, 14):
                        for g in range(0, f + 1):
                            if a - e == 4 and f != a + 1 and g != a + 1 and not (f == g and f != 0):
                                bit_eff = primes_flush[a] * primes_flush[b] * primes_flush[c] * primes_flush[d] * \
                                          primes_flush[e]
                                if bit_old != bit_eff:
                                    bit_old = bit_eff
                                    i += 1
                                bit = bit_eff * primes_flush[f] * primes_flush[g]
                                StraightFlush.update({bit: i})

All_Hands = {}
All_Hands.update(HighCard)
All_Hands.update(Pair)
All_Hands.update(TwoPair)
All_Hands.update(Trips)
All_Hands.update(Straight)
All_Hands.update(FullHouse)
All_Hands.update(Quads)
Flush_Hands = {}
Flush_Hands.update(Flush)
Flush_Hands.update(StraightFlush)

