from Canonicalize import canonical
import sqlite3
from test5 import BoardInfo
from itertools import combinations
import numpy as np
from WeightedCombos import *
from HandEvaluator import EvaluateHandHE
import datetime
from NumbaKernels import eq2bucket

conn = sqlite3.connect('Buckets.db')

cur = conn.cursor()

Deck = [c for c in range(52)]
CARD_MASKS = [1 << c for c in range(52)]

Hands = NumpyCombos()

canon_rivers = set()

Rivers = combinations(Deck, 5)
for river in Rivers:
    canon_river = canonical(river, ())[0]

    if canon_river not in canon_rivers:
        canon_rivers.add(canon_river)

canon_rivers = list(canon_rivers)

print("Canonicalized", len(canon_rivers))

number = len(Hands[0])

river_EQ = np.zeros((1000, 1000), dtype=np.float32)
river_count = np.zeros_like(river_EQ, dtype=np.uint32)

z = 0
for river in canon_rivers:
    z += 1
    if z % 1000 == 0 or z < 50:
        print(z)

    brd = BoardInfo(river)
    key = brd.mask

    cur.execute("""
    SELECT hand_mask, bucket
    FROM River_Buckets
    WHERE board_mask = ?
    """, (key,))

    BoardBuckets = {
        hand_mask: bucket
        for hand_mask, bucket in cur.fetchall()
    }

    hands_set = set()
    hands = []
    hand_buckets = []

    Hero_Valid = (Hands[1] & key) == 0
    valid_idx = np.flatnonzero(Hero_Valid)
    valid_hands = Hands[0][valid_idx]

    canon_cache = {}
    canon_to_bucket = {}

    for hand in valid_hands:
        canon_hand = canonical(river, (tuple(hand),))[1][0]
        canon_cache[tuple(hand)] = canon_hand
        if canon_hand not in hands_set:
            hands_set.add(canon_hand)
            hands.append(canon_hand)
            hand_mask = CARD_MASKS[canon_hand[0]] | CARD_MASKS[canon_hand[1]]
            canon_to_bucket[canon_hand] = BoardBuckets[hand_mask]
            hand_buckets.append(canon_to_bucket[canon_hand])

    masks = np.array([CARD_MASKS[h[0]] | CARD_MASKS[h[1]] for h in hands])
    hero_villain_legal = ((masks[:, None] & Hands[1][None, :]) == 0)

    hidx = np.arange(len(hands), dtype=np.int32)

    villain_buckets = np.full(number, -1, dtype=np.int16)
    for v in valid_idx:
        cn = canon_cache[tuple(Hands[0][v])]
        villain_buckets[v] = canon_to_bucket[cn]

    scores = np.empty(len(hands), dtype=np.int16)
    for i, hand in enumerate(hands):
        scores[i] = EvaluateHandHE(hand, brd)

    villain_scores = np.zeros(len(valid_idx), dtype=np.int16)
    vbuckets = villain_buckets[valid_idx]

    for i, idx in enumerate(valid_idx):
        villain_scores[i] = EvaluateHandHE(Hands[0][idx], brd)

    temp = eq2bucket(hand_buckets, vbuckets, hidx, scores, villain_scores, valid_idx, hero_villain_legal, river_EQ, river_count)

    river_EQ = temp[0]
    river_count = temp[1]


mask = river_count > 0
river_EQ[mask] /= river_count[mask]

print("River Done")

print("Downloading")

np.save("RiverEquities.npy", river_EQ)


