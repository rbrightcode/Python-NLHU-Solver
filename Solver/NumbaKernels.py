# This file is for a bunch of numba programs which hopefully go super fast fire
from numba import njit
import numpy as np

@njit(cache=True)
def regret2strat(regrets):
    rows, cols = regrets.shape
    strategy = np.empty_like(regrets)

    uniform = 1.0 / cols

    for r in range(rows):
        total = 0.0

        for c in range(cols):
            total += regrets[r,c]

        if total > 0:
            inv = 1.0 / total

            for c in range(cols):
                strategy[r,c] = regrets[r,c] * inv

        else:
            for c in range(cols):
                strategy[r,c] = uniform

    return strategy

@njit(cache=True)
def action2node(action_util, action_freq):
    rows, cols = action_util.shape
    node_util = np.zeros(rows, dtype=np.float32)

    for r in range(rows):
        total = 0.0
        for c in range(cols):
            total += action_util[r,c] * action_freq[r,c]
        node_util[r] = total

    return node_util

@njit(cache=True)
def util2regret(Node, Action, Regrets, reach):
    rows, cols = Action.shape
    for r in range(rows):
        for c in range(cols):
            temp = Regrets[r,c] + ((Action[r,c] - Node[r]) * reach)
            if temp > 0:
                Regrets[r,c] = temp
            else:
                Regrets[r,c] = 0.0

    return Regrets

@njit(cache=True)
def numba_sum(array):
    rows = len(array)
    total = 0.0
    for r in range(rows):
        total += array[r]

    return total

@njit(cache=True)
def update_reach(reachs, freqs, a):
    rows = len(reachs)
    for r in range(rows):
        reachs[r] *= freqs[r, a]

    return reachs

@njit(cache=True)
def eq2bucket(hand_buckets, villain_buckets, valid_idx, scores, villain_scores, villain_idx, legal_matrix, EQ_matrix, Count_Matrix):
    rows = len(villain_scores)
    for h in valid_idx:
        hb = hand_buckets[h]
        hs = scores[h]

        for r in range(rows):
            if not legal_matrix[h, villain_idx[r]]:
                continue

            score = villain_scores[r]
            eq = 0
            eq += (hs > score) + (0.5 * (hs == score))

            vb = villain_buckets[r]

            EQ_matrix[hb, vb] += eq
            Count_Matrix[hb, vb] += 1

    return (EQ_matrix, Count_Matrix)
