from test5 import *
from CFRNodes import CFRNode
import random
from Canonicalize import canonical
from WeightedCombos import *
import pickle
import pandas as pd
from NumbaKernels import *

NodeMap = {}

with open("BucketDict.pickle", "rb") as f:
    Buckets = pickle.load(f)
    f.close()

CANON_CACHE = {}
def getCanon(state):
    key = state.boards[state.street].mask
    if key not in CANON_CACHE:
        CANON_CACHE[key] = canonical(state.boards[state.street].cards)

    return CANON_CACHE[key]


def InfoSet(state):
    if state.street == 0:
        return (state.street, state.history, state.current_player)
    else:
        canon = getCanon(state)
        Bucket = Buckets[canon[0]]
        return (state.street, Bucket, state.history, state.current_player)

class TestNode:
    __slots__ = ("Combos", "Strategy", "Regrets", "Legal")

    def __init__(self, state):
        player = state.current_player
        self.Combos = state.integers[player]
        self.Legal = state.legal_actions()

        combos = len(self.Combos)
        number = len(self.Legal)

        self.Strategy = np.zeros((combos, number), dtype=np.float32)
        self.Regrets = np.zeros((combos, number), dtype=np.float32)

def GetNode(state):
    key = InfoSet(state)

    if key not in NodeMap:
        NodeMap[key] = TestNode(state)

    return NodeMap[key]

def CFR(state, player, reachs):

    current = state.current_player

    active = state.Active_Cache[state.boards[state.street].mask]

    opp = numba_sum(reachs[(player+1)%2][active[(player+1)%2]])

    #if opp == 0:
        #return np.zeros(len(state.ranges[player]))

    node = GetNode(state)

    legal = node.Legal
    num_actions = len(legal)

    freqs = reachs[current][active[current]]

    regrets = node.Regrets[active[current]]

    Action_Freq = regret2strat(regrets)

    node.Strategy[active[current]] += freqs[:, None] * Action_Freq

    if player == current:
        Action_Util = np.zeros((len(state.integers[player]), num_actions), dtype=np.float32)
        for a, action in enumerate(legal):
            state.apply_action(action)

            old = reachs[current][active[current]] * 1
            reachs[current][active[current]] = update_reach(reachs[current][active[current]], Action_Freq, a)


            if reachs[current][active[current]].max() < 1e-8:
                reachs[current][active[current]] = old
                state.undo_action()
                continue


            if state.terminal:
                cfv = state.payoff(player, reachs)

            else:
                cfv = CFR(state, player, reachs)

            Action_Util[:, a] = cfv

            reachs[current][active[current]] = old
            state.undo_action()

        Node_Util = np.zeros(len(state.integers[player]), dtype=np.float32)

        Node_Util[active[current]] = action2node(Action_Util[active[current]], Action_Freq)

        node.Regrets[active[current]] = util2regret(Node_Util[active[current]], Action_Util[active[current]],
                                                    node.Regrets[active[current]], opp)
    else:
        action_prob = (freqs[:, None] * Action_Freq).sum(axis=0)

        normal = action_prob.sum()
        if normal > 0:
            action_prob /= normal
        else:
            action_prob[:] = 1 / num_actions

        Action_Util = np.zeros(len(state.integers[player]), dtype=np.float32)

        a = np.random.choice(num_actions, p=action_prob)
        action = legal[a]

        state.apply_action(action)

        old = reachs[current][active[current]] * 1
        reachs[current][active[current]] = update_reach(reachs[current][active[current]], Action_Freq, a)

        if state.terminal:
            cfv = state.payoff(player, reachs)

        else:
            cfv = CFR(state, player, reachs)

        Node_Util = cfv

        reachs[current][active] = old
        state.undo_action()

        #Node_Util = np.zeros(len(state.integers[player]), dtype=np.float32)

        #Node_Util = opp_action2node2(freqs, Action_Freq, Action_Util)

    return Node_Util

