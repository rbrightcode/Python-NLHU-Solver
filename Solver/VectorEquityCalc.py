import random
from HandEvaluator import EvaluateHandHE
import numpy as np
from test5 import *
import pickle
from Canonicalize import *

with open("PREFLOP_TABLE.pickle", "rb") as f:
    PREFLOP_TABLE = pickle.load(f)
    f.close()

with open("CANON_FLOP_TABLE.pickle", "rb") as f:
    FLOP_TABLE = pickle.load(f)
    f.close()

score_cache = {}

CARD_MASKS = [1 << x for x in range(52)]
def VecCalc(Hero_RNG, Ranges, Samples=100000, Board = ()):
    # Static board information

    board_mask = Board.mask

    deck = [
        c for c in range(52)
        if not (board_mask & (CARD_MASKS[c]))]

    missing = 5 - len(Board.cards)

    num_players = len(Ranges) + 1

    equities = np.zeros(len(Hero_RNG[0]), dtype=np.float32)
    counts = np.zeros(len(Hero_RNG[0]), dtype=np.int32)

    # -----------------------------
    # Main Monte Carlo
    # -----------------------------

    if missing == 5:
        villain_weights = [None]*len(Ranges)
        for i, rng in enumerate(Ranges):
            villain_weights[i] = rng[1]/rng[1].sum()

        for i, hand in enumerate(Hero_RNG[0]):
            canon_hand = canonical(hands=(tuple(hand),))[0]

            eq = 1.0
            for weights in villain_weights:
                eq *= (PREFLOP_TABLE[canon_hand] * weights).sum()

            equities[i] = eq

    elif missing == 0:
        villain_masks = [None]*len(Ranges)
        villain_weights = [None]*len(Ranges)
        villain_scores = [None]*len(Ranges)
        for i, rng in enumerate(Ranges):
            masks = rng[2]
            valid = (board_mask & masks) == 0
            vidx = np.flatnonzero(valid)

            masks = masks[vidx]
            hands = rng[0][vidx]
            weights = rng[1][vidx]
            scores = np.empty(len(vidx), dtype=np.int16)
            for j, hand in enumerate(hands):
                scores[j] = EvaluateHandHE(hand, Board)
            villain_masks[i] = masks
            villain_weights[i] = weights
            villain_scores[i] = scores

        hero_masks = Hero_RNG[2]

        valid = (hero_masks & board_mask) == 0
        hidx = np.flatnonzero(valid)

        hero_hands = Hero_RNG[0]
        for idx in hidx:
            hero_score = EvaluateHandHE(hero_hands[idx], Board)
            equities[idx] = 1.0

            for i, masks in enumerate(villain_masks):
                villain_valid = (hero_masks[idx] & masks) == 0

                valid_scores = villain_scores[i][villain_valid]
                valid_weights = villain_weights[i][villain_valid].copy()

                normal = valid_weights.sum()

                if normal == 0:
                    valid_weights[:] = 1/len(valid_weights)
                else:
                    valid_weights /= normal


                wins = valid_scores < hero_score
                ties = valid_scores == hero_score

                equities[idx] *= (valid_weights[wins].sum() + 0.5 * valid_weights[ties].sum())
                counts[idx] += 1

    elif missing == 1:
        for c in deck:
            full_board = Board.update((c,))
            board_mask = full_board.mask
            villain_masks = [None] * len(Ranges)
            villain_weights = [None] * len(Ranges)
            villain_scores = [None] * len(Ranges)
            for i, rng in enumerate(Ranges):
                masks = rng[2]
                valid = (board_mask & masks) == 0
                vidx = np.flatnonzero(valid)

                masks = masks[vidx]
                hands = rng[0][vidx]
                weights = rng[1][vidx]
                scores = np.empty(len(vidx), dtype=np.int16)
                for j, hand in enumerate(hands):
                    scores[j] = EvaluateHandHE(hand, full_board)
                villain_masks[i] = masks
                villain_weights[i] = weights
                villain_scores[i] = scores

            hero_masks = Hero_RNG[2]

            valid = (hero_masks & board_mask) == 0
            hidx = np.flatnonzero(valid)

            hero_hands = Hero_RNG[0]
            for idx in hidx:
                hero_score = EvaluateHandHE(hero_hands[idx], full_board)
                temp = 1.0

                for i, masks in enumerate(villain_masks):
                    villain_valid = (hero_masks[idx] & masks) == 0

                    valid_scores = villain_scores[i][villain_valid]
                    valid_weights = villain_weights[i][villain_valid].copy()

                    normal = valid_weights.sum()

                    if normal == 0:
                        valid_weights[:] = 1 / len(valid_weights)
                    else:
                        valid_weights /= normal

                    wins = valid_scores < hero_score
                    ties = valid_scores == hero_score

                    temp *= (valid_weights[wins].sum() + 0.5 * valid_weights[ties].sum())

                    equities[idx] += temp
                    counts[idx] += 1

    elif missing == 2:
        villain_weights = [None] * len(Ranges)
        for i, rng in enumerate(Ranges):
            villain_weights[i] = rng[1]/rng[1].sum()

        for i, hand in enumerate(Hero_RNG[0]):
            canon = canonical(Board.cards, hands=(hand,))
            brd = canon[0]
            canon_hand = canon[1][0]

            key = CARD_MASKS[brd[0]] | CARD_MASKS[brd[1]] | CARD_MASKS[brd[2]]

            eq = 1.0
            for weights in villain_weights:
                eq *= (FLOP_TABLE[key][canon_hand] * weights).sum()

            equities[i] += eq
            counts[i] += 1

    mask = counts > 0
    equities[mask] /= counts[mask]

    return equities
