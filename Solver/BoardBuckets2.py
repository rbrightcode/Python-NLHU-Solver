from datetime import datetime

from sklearn.cluster import MiniBatchKMeans
import numpy as np
from itertools import combinations
from WeightedCombos import *
from Canonicalize import *
from test5 import BoardInfo
from HandEvaluator import EvaluateHandHE
import sqlite3

CARD_MASKS = [1 << c for c in range(52)]
DECK = [x for x in range(52)]

Histograms = {}
Flop_Buckets = {}
"""
Hands = NumpyCombos()
Deck = [c for c in range(52)]
number = len(Hands[0])

canon_flops = set()
canon_hands = {}

Flops = combinations(Deck, 3)
for flop in Flops:
    canon_flop = canonical(flop, ())[0]
    brd = BoardInfo(canon_flop)
    key = brd.mask

    if canon_flop not in canon_flops:
        valid = (Hands[1] & key) == 0
        vidx = np.flatnonzero(valid)
        valid_hands = Hands[0][vidx]
        canon_flops.add(canon_flop)
        cnn_hnds = set()
        for hand in valid_hands:
            canon_hand = canonical(canon_flop, (tuple(hand),))[1][0]
            if canon_hand not in cnn_hnds:
                cnn_hnds.add(canon_hand)

        canon_hands[key] = list(cnn_hnds)
    else:
        continue

canon_flops = list(canon_flops)
bin_edges = np.linspace(0.0, 1.0, 21)

print("Canonicalized")
z = 0
for flop in canon_flops:
    z += 1
    if z % 10 == 0:
        print(z)

    brd = BoardInfo(flop)
    key = brd.mask

    hands = canon_hands[key]
    turn_eq = np.zeros((len(hands), 49), dtype=np.float32)

    turn_cards = [c for c in range(52) if not (CARD_MASKS[c] & key)]

    for turn_idx, turn in enumerate(turn_cards):
        turn_board = brd.update((turn,))
        turn_mask = turn_board.mask

        river_cards = [c for c in range(52) if not (CARD_MASKS[c] & turn_mask)]

        river_sum = np.zeros(len(hands), dtype=np.float32)

        river_count = 48

        for river in river_cards:
            board = turn_board.update((river,))
            board_mask = board.mask

            hero_scores = np.full(len(hands), -1, np.int16)

            for h, hand in enumerate(hands):
                hand_mask = CARD_MASKS[hand[0]] | CARD_MASKS[hand[1]]

                if hand_mask & board_mask:
                    continue

                hero_scores[h] = EvaluateHandHE(hand, board)

            villain_valid = (Hands[1] & board_mask) == 0
            vidx = np.flatnonzero(villain_valid)
            villain_scores = np.empty(len(vidx), dtype=np.int16)

            for i, v in enumerate(vidx):
                villain_scores[i] = EvaluateHandHE(Hands[0][v], board)

            for h in range(len(hands)):
                hs = hero_scores[h]

                if hs < 0:
                    continue

                wins = np.count_nonzero(hs > villain_scores)

                ties = np.count_nonzero(hs == villain_scores)

                river_sum[h] += (wins + 0.5 * ties) / len(villain_scores)


        turn_eq[:, turn_idx] = river_sum / river_count

    for k, hand in enumerate(hands):
        hist, _ = np.histogram(turn_eq[k], bins=bin_edges)

        hist = hist.astype(np.float32)

        total = hist.sum()

        if total > 0:
            hist /= total

        Histograms[(key, hand)] = hist

print("Starting Kmeans")

hist_keys = list(Histograms.keys())

X = np.vstack([Histograms[k] for k in hist_keys])

kmeans = MiniBatchKMeans(
    n_clusters=1000,
    batch_size=10000,
    random_state=42
)

bucket_ids = kmeans.fit_predict(X)

for key, bucket in zip(hist_keys, bucket_ids):
    Flop_Buckets[key] = bucket

with open("Flop_Buckets.pickle", "wb") as f:
    pickle.dump(Flop_Buckets, f)

"""

"""
Turn_Buckets = {}

Hands = NumpyCombos()
Deck = [c for c in range(52)]
number = len(Hands[0])

canon_turns = set()
canon_hands = {}

Turns = combinations(Deck, 4)
for turn in Turns:
    canon_turn = canonical(turn, ())[0]
    brd = BoardInfo(canon_turn)
    key = brd.mask

    if canon_turn not in canon_turns:
        valid = (Hands[1] & key) == 0
        vidx = np.flatnonzero(valid)
        valid_hands = Hands[0][vidx]
        canon_turns.add(canon_turn)
        cnn_hnds = set()
        for hand in valid_hands:
            canon_hand = canonical(canon_turn, (tuple(hand),))[1][0]
            if canon_hand not in cnn_hnds:
                cnn_hnds.add(canon_hand)

        canon_hands[key] = list(cnn_hnds)
    else:
        continue

canon_turns = list(canon_turns)
print(len(canon_turns))
bin_edges = np.linspace(0.0, 1.0, 21)

print("Canonicalized")
z = 0
for turn in canon_turns:
    z += 1
    if z % 100 == 0 or z < 5:
        print(z)

    brd = BoardInfo(turn)
    key = brd.mask

    hands = canon_hands[key]
    river_eq = np.zeros((len(hands), 48), dtype=np.float32)

    river_cards = [c for c in range(52) if not (CARD_MASKS[c] & key)]

    for river_idx, river in enumerate(river_cards):
        board = brd.update((river,))
        board_mask = board.mask

        hero_scores = np.full(len(hands), -1, np.int16)

        for h, hand in enumerate(hands):
            hand_mask = CARD_MASKS[hand[0]] | CARD_MASKS[hand[1]]

            if hand_mask & board_mask:
                continue

            hero_scores[h] = EvaluateHandHE(hand, board)

        villain_valid = (Hands[1] & board_mask) == 0
        vidx = np.flatnonzero(villain_valid)
        villain_scores = np.empty(len(vidx), dtype=np.int16)

        for i, v in enumerate(vidx):
            villain_scores[i] = EvaluateHandHE(Hands[0][v], board)

        for h in range(len(hands)):
            hs = hero_scores[h]

            if hs < 0:
                continue

            wins = np.count_nonzero(hs > villain_scores)

            ties = np.count_nonzero(hs == villain_scores)

            river_eq[h, river_idx] += (wins + 0.5 * ties) / len(villain_scores)

    for k, hand in enumerate(hands):
        hist, _ = np.histogram(river_eq[k], bins=bin_edges)

        hist = hist.astype(np.float32)

        total = hist.sum()

        if total > 0:
            hist /= total

        Histograms[(key, hand)] = hist

print("Starting Kmeans")

hist_keys = list(Histograms.keys())

X = np.vstack([Histograms[k] for k in hist_keys])

kmeans = MiniBatchKMeans(
    n_clusters=1000,
    batch_size=10000,
    random_state=42
)

bucket_ids = kmeans.fit_predict(X)

for key, bucket in zip(hist_keys, bucket_ids):
    Turn_Buckets[key] = bucket

with open("Turn_Buckets.pickle", "wb") as f:
    pickle.dump(Turn_Buckets, f)
    
Flop_Buckets = {}

Hands = NumpyCombos()
Deck = [c for c in range(52)]
number = len(Hands[0])

canon_flops = set()
canon_hands = {}

Flops = combinations(Deck, 3)
for flop in Flops:
    canon_flop = canonical(flop, ())[0]
    brd = BoardInfo(canon_flop)
    key = brd.mask

    if canon_flop not in canon_flops:
        valid = (Hands[1] & key) == 0
        vidx = np.flatnonzero(valid)
        valid_hands = Hands[0][vidx]
        canon_flops.add(canon_flop)
        cnn_hnds = set()
        for hand in valid_hands:
            canon_hand = canonical(canon_flop, (tuple(hand),))[1][0]
            if canon_hand not in cnn_hnds:
                cnn_hnds.add(canon_hand)

        canon_hands[key] = list(cnn_hnds)
    else:
        continue

canon_flops = list(canon_flops)
bin_edges = np.linspace(0.0, 1.0, 21)

print("Canonicalized")
z = 0
for flop in canon_flops:
    z += 1
    if z % 10 == 0:
        print(z)

    brd = BoardInfo(flop)
    key = brd.mask

    hands = canon_hands[key]
    turn_eq = np.zeros((len(hands), 49), dtype=np.float32)

    turn_cards = [c for c in range(52) if not (CARD_MASKS[c] & key)]

    for turn_idx, turn in enumerate(turn_cards):
        turn_board = brd.update((turn,))
        turn_mask = turn_board.mask

        river_cards = [c for c in range(52) if not (CARD_MASKS[c] & turn_mask)]

        river_sum = np.zeros(len(hands), dtype=np.float32)

        river_count = 48

        for river in river_cards:
            board = turn_board.update((river,))
            board_mask = board.mask

            hero_scores = np.full(len(hands), -1, np.int16)

            for h, hand in enumerate(hands):
                hand_mask = CARD_MASKS[hand[0]] | CARD_MASKS[hand[1]]

                if hand_mask & board_mask:
                    continue

                hero_scores[h] = EvaluateHandHE(hand, board)

            villain_valid = (Hands[1] & board_mask) == 0
            vidx = np.flatnonzero(villain_valid)
            villain_scores = np.empty(len(vidx), dtype=np.int16)

            for i, v in enumerate(vidx):
                villain_scores[i] = EvaluateHandHE(Hands[0][v], board)

            for h in range(len(hands)):
                hs = hero_scores[h]

                if hs < 0:
                    continue

                wins = np.count_nonzero(hs > villain_scores)

                ties = np.count_nonzero(hs == villain_scores)

                river_sum[h] += (wins + 0.5 * ties) / len(villain_scores)


        turn_eq[:, turn_idx] = river_sum / river_count

    for k, hand in enumerate(hands):
        hist, _ = np.histogram(turn_eq[k], bins=bin_edges)

        hist = hist.astype(np.float32)

        total = hist.sum()

        if total > 0:
            hist /= total

        Histograms[(key, hand)] = hist

print("Starting Kmeans")

hist_keys = list(Histograms.keys())

X = np.vstack([Histograms[k] for k in hist_keys])

kmeans = MiniBatchKMeans(
    n_clusters=1000,
    batch_size=10000,
    random_state=42
)

bucket_ids = kmeans.fit_predict(X)

for key, bucket in zip(hist_keys, bucket_ids):
    Flop_Buckets[key] = bucket

with open("Flop_Buckets.pickle", "wb") as f:
    pickle.dump(Flop_Buckets, f)

"""

conn = sqlite3.connect('Buckets.db')

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS River_Buckets (
    board_mask Integer,
    hand_mask Integer,
    bucket Integer,
    PRIMARY KEY(board_mask, hand_mask)
    )
""")

conn.commit()

kmeans = MiniBatchKMeans(
    n_clusters=1000,
    batch_size=10000,
    random_state=42
)

print("Start River Canon")

batch = []
batch_rows = 0

Deck = [c for c in range(52)]
Hands = NumpyCombos()

canon_rivers = set()

Rivers = combinations(Deck, 5)
for river in Rivers:
    canon_river = canonical(river, ())[0]
    brd = BoardInfo(canon_river)
    key = brd.mask

    if canon_river not in canon_rivers:
        valid = (Hands[1] & key) == 0
        vidx = np.flatnonzero(valid)
        valid_hands = Hands[0][vidx]
        canon_rivers.add(canon_river)

    else:
        continue

Rivers = None

canon_rivers = list(canon_rivers)
print(len(canon_rivers))

print("Canonicalized")
z = 0
for river in canon_rivers:
    z += 1
    if z % 1000 == 0 or z < 50:
        print(z)

    board = BoardInfo(river)
    key = board.mask

    hands = set()

    Hero_Valid = (Hands[1] & key) == 0
    Hero_idx = np.flatnonzero(Hero_Valid)

    valid_hands = Hands[0][Hero_idx]
    for hand in valid_hands:
        canon_hand = canonical(river, (tuple(hand),))[1][0]
        if canon_hand not in hands:
            hands.add(canon_hand)

    hands = list(hands)

    hero_scores = np.zeros(len(hands), dtype=np.uint16)

    for h, hand in enumerate(hands):
        hero_scores[h] = EvaluateHandHE(hand, board)

    villain_scores = np.zeros(len(Hands[0]), dtype=np.int16)

    for v, hand in enumerate(Hands[0]):
        if (key & Hands[1][v]) == 0:
            villain_scores[v] = EvaluateHandHE(hand, board)

    hero_masks = np.array([CARD_MASKS[h[0]] | CARD_MASKS[h[1]]
        for h in hands], dtype=np.int64)

    hero_villain_legal = ((hero_masks[:, None] & Hands[1][None, :]) == 0)
    villain_board_legal = (Hands[1] & key) == 0

    wins = hero_scores[:, None] > villain_scores[None, :]
    ties = hero_scores[:, None] == villain_scores[None, :]

    features = wins.astype(np.float16)
    features += 0.5 * ties.astype(np.float16)
    features[~hero_villain_legal] = -1
    features[:, ~villain_board_legal] = -1

    batch.append(features)
    batch_rows += len(features)

    if batch_rows >= 10000:
        X = np.vstack(batch)
        kmeans.partial_fit(X)
        batch.clear()
        batch_rows = 0

if batch_rows > 0:
    X = np.vstack(batch)
    kmeans.partial_fit(X)
    batch.clear()
    batch_rows = 0

print("Trained")
z = 0
for river in canon_rivers:
    z += 1
    if z % 1000 == 0 or z < 50:
        print(z)

    board = BoardInfo(river)
    key = board.mask

    hands = set()

    Hero_Valid = (Hands[1] & key) == 0
    Hero_idx = np.flatnonzero(Hero_Valid)

    valid_hands = Hands[0][Hero_idx]
    for hand in valid_hands:
        canon_hand = canonical(river, (tuple(hand),))[1][0]
        if canon_hand not in hands:
            hands.add(canon_hand)

    hands = list(hands)

    hero_scores = np.zeros(len(hands), dtype=np.uint16)

    for h, hand in enumerate(hands):
        hero_scores[h] = EvaluateHandHE(hand, board)

    villain_scores = np.zeros(len(Hands[0]), dtype=np.int16)

    for v, hand in enumerate(Hands[0]):
        if (key & Hands[1][v]) == 0:
            villain_scores[v] = EvaluateHandHE(hand, board)

    hero_masks = np.array([CARD_MASKS[h[0]] | CARD_MASKS[h[1]]
                           for h in hands], dtype=np.int64)

    hero_villain_legal = ((hero_masks[:, None] & Hands[1][None, :]) == 0)
    villain_board_legal = (Hands[1] & key) == 0

    wins = hero_scores[:, None] > villain_scores[None, :]
    ties = hero_scores[:, None] == villain_scores[None, :]

    features = wins.astype(np.float16)
    features += 0.5 * ties.astype(np.float16)
    features[~hero_villain_legal] = -1
    features[:, ~villain_board_legal] = -1

    bucket_ids = kmeans.predict(features)

    for mask, bucket in zip(hero_masks, bucket_ids):
        batch.append((int(key), int(mask), int(bucket)))

    if len(batch) >= 100000:
        cur.executemany("""
        INSERT OR REPLACE INTO River_Buckets
        VALUES (?, ?, ?)
        """, batch)

        conn.commit()

        batch.clear()

if len(batch) > 0:
    cur.executemany("""
            INSERT OR REPLACE INTO River_Buckets
            VALUES (?, ?, ?)
            """, batch)

    conn.commit()

    batch.clear()

print("Exported")


"""
    Top10 = NumpyParse(Hands[0], Hands[1], Hands[2], ["66+", "ATs+", "KTs+", "AJo+", "KQo"])
Top50 = NumpyParse(Hands[0], Hands[1], Hands[2], ["22+", "A2s+", "K2s+", "Q2s+", "J5s+", "T7s+", "98s", "A2o+", "K2o+", "J8o+", "T9o"])

Mid40_Idx = []
for i, mask in enumerate(Top50[1]):
    for block in Top10[1]:
        blocked = False
        if mask == block:
            blocked = True
            break

    if blocked:
        continue

    Mid40_Idx.append(i)

Mid40 = (Top50[0][Mid40_Idx], Top50[1][Mid40_Idx], Top50[2][Mid40_Idx])

Bottom50_Idx = []
for i, mask in enumerate(Hands[1]):
    for block in Top50[1]:
        blocked = False
        if mask == block:
            blocked = True
            break

    if blocked:
        continue

    Bottom50_Idx.append(i)

Bottom50 = (Hands[0][Bottom50_Idx], Hands[1][Bottom50_Idx], Hands[2][Bottom50_Idx])

    hands = set()

    All_Valid = (Hands[1] & key) == 0
    All_idx = np.flatnonzero(All_Valid)
    All_scores = np.empty(len(All_idx), dtype=np.int16)

    valid_hands = Hands[0][All_idx]
    for hand in valid_hands:
        canon_hand = canonical(river, (tuple(hand),))[1][0]
        if canon_hand not in hands:
            hands.add(canon_hand)

    features = np.zeros((len(hands), 8), dtype=np.float16)

    hero_scores = np.full(len(hands), -1, np.int16)

    for h, hand in enumerate(hands):
        hand_mask = CARD_MASKS[hand[0]] | CARD_MASKS[hand[1]]

        if hand_mask & key:
            continue

        hero_scores[h] = EvaluateHandHE(hand, board)



    for i, v in enumerate(All_idx):
        All_scores[i] = EvaluateHandHE(Hands[0][v], board)

    T10_valid = (Top10[1] & key) == 0
    T10idx = np.flatnonzero(T10_valid)
    T10_scores = np.empty(len(T10idx), dtype=np.int16)

    for i, v in enumerate(T10idx):
        T10_scores[i] = EvaluateHandHE(Top10[0][v], board)

    M40_valid = (Mid40[1] & key) == 0
    M40idx = np.flatnonzero(M40_valid)
    M40_scores = np.empty(len(M40idx), dtype=np.int16)

    for i, v in enumerate(M40idx):
        M40_scores[i] = EvaluateHandHE(Mid40[0][v], board)

    B50_valid = (Bottom50[1] & key) == 0
    B50idx = np.flatnonzero(B50_valid)
    B50_scores = np.empty(len(B50idx), dtype=np.int16)

    for i, v in enumerate(B50idx):
        B50_scores[i] = EvaluateHandHE(Bottom50[0][v], board)

    Nuts = np.max(All_scores)
    Worst = np.min(All_scores)

    texture_mask = 0
    suit_count = [0,0,0,0]
    for card in board.cards:
        texture_mask |= CARD_MASKS[card % 13]
        suit_count[card // 13] += 1

    features[:, 6] += texture_mask.bit_count() / 5

    features[:, 7] += max(suit_count) / 5

    Nut_Mask = (All_scores == Nuts)
    Nut_Combos = Hands[1][All_idx[Nut_Mask]]

    for h in range(len(hands)):
        hs = hero_scores[h]

        if hs < 0:
            continue

        T10wins = np.count_nonzero(hs > T10_scores)
        M40wins = np.count_nonzero(hs > M40_scores)
        B50wins = np.count_nonzero(hs > B50_scores)

        T10ties = np.count_nonzero(hs == T10_scores)
        M40ties = np.count_nonzero(hs == M40_scores)
        B50ties = np.count_nonzero(hs == B50_scores)

        features[h, 0] += (T10wins + M40wins + B50wins + (0.5 * (T10ties + M40ties + B50ties))) / (len(T10_scores) + len(M40_scores) + len(B50_scores))
        features[h, 1] += (T10wins + (0.5 * T10ties)) / len(T10_scores)
        features[h, 2] += (M40wins + (0.5 * M40ties)) / len(M40_scores)
        features[h, 3] += (B50wins + (0.5 * B50ties)) / len(B50_scores)
        features[h, 4] += (Nuts - hs) / (Nuts - Worst + 1)

        hero_mask = CARD_MASKS[hands[h][0]] | CARD_MASKS[hands[h][1]]
        blocked_nuts = np.count_nonzero((Nut_Combos & hero_mask) != 0)

        features[h, 5] += blocked_nuts / len(Nut_Combos)

    for k, hand in enumerate(hands):
        River_Features[(key, hand)] = features[k]

print("Starting Kmeans")

feat_keys = list(River_Features.keys())

X = np.vstack([River_Features[k] for k in feat_keys])

kmeans = MiniBatchKMeans(
    n_clusters=1000,
    batch_size=10000,
    random_state=42
)

bucket_ids = kmeans.fit_predict(X)

for key, bucket in zip(feat_keys, bucket_ids):
    River_Buckets[key] = bucket
    
"""






