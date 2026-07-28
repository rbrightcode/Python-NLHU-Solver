from HandConverter import *

RANKS = {
    "2": 0, "3": 1, "4": 2, "5": 3,
    "6": 4, "7": 5, "8": 6, "9": 7,
    "T": 8, "J": 9, "Q": 10, "K": 11,
    "A": 12
}

PAIR_COMBOS = {}
SUITED_COMBOS = {}
OFFSUIT_COMBOS = {}

for r in range(13):

    pairs = []

    for s1 in range(4):
        for s2 in range(s1 + 1, 4):
            pairs.append(
                (r + s1 * 13,
                 r + s2 * 13)
            )

    PAIR_COMBOS[r] = pairs

for hi in range(13):
    for lo in range(hi):

        suited = []
        offsuit = []

        for s1 in range(4):

            suited.append(
                (hi + s1 * 13,
                 lo + s1 * 13)
            )

            for s2 in range(4):

                if s1 == s2:
                    continue

                offsuit.append(
                    (hi + s1 * 13,
                     lo + s2 * 13)
                )

        SUITED_COMBOS[(hi, lo)] = suited
        OFFSUIT_COMBOS[(hi, lo)] = offsuit

def RangeParser(tokens):

    combos = []

    for token in tokens:

        plus = token.endswith("+")
        if plus:
            token = token[:-1]

        r1 = RANKS[token[0]]
        r2 = RANKS[token[1]]

        pair = r1 == r2
        suited = len(token) == 3 and token[2] == "s"
        offsuit = len(token) == 3 and token[2] == "o"
        All = not (pair or suited or offsuit)

        if pair:
            ranks = range(r1, 13) if plus else [r1]

            for r in ranks:
                combos.extend(PAIR_COMBOS[r])

        elif suited:
            if plus:
                for r in range(r2, r1):
                    combos.extend(SUITED_COMBOS[(r1, r)])
            else:
                combos.extend(SUITED_COMBOS[(r1, r2)])

        elif offsuit:
            if plus:
                for r in range(r2, r1):
                    combos.extend(OFFSUIT_COMBOS[(r1, r)])
            else:
                combos.extend(OFFSUIT_COMBOS[(r1, r2)])

        elif All:
            if plus:
                for r in range(r2, r1):
                    combos.extend(SUITED_COMBOS[(r1, r)])
                    combos.extend(OFFSUIT_COMBOS[(r1, r)])
            else:
                combos.extend(SUITED_COMBOS[(r1, r2)])
                combos.extend(OFFSUIT_COMBOS[(r1, r2)])

    return combos



