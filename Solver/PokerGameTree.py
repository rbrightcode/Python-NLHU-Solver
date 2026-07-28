# This is the beginning of the poker game tree
import random
from HandVRangesCalc import HVRCalc
from Canonicalize import canonical
from WeightedCombos import *
from VectorEquityCalc import VecCalc
import copy
Equity_CACHE = {}
ACTIVE_CACHE = {}
NEXT_STREET = {
    0 : 1,
    1 : 2,
    2 : 3
}

CARD_MASKS = [1 << c for c in range(52)]
BET_SIZES = (0.33, 0.5, 0.75, 1)

PRIMES = (2,3,5,7,11,13,17,19,23,29,31,37,41)
CARD_RANK = tuple(i % 13 for i in range(52))
CARD_SUIT = tuple(i // 13 for i in range(52))
CARD_PRIME = tuple(PRIMES[i % 13] for i in range(52))

class BoardInfo:

    def __init__(
        self,
        cards = ()):

        self.cards = cards

        self.mask = 0
        self.prime = 1
        suits = [0, 0, 0, 0]
        for c in self.cards:
            self.mask |= CARD_MASKS[c]
            self.prime *= CARD_PRIME[c]
            suits[CARD_SUIT[c]] += 1

        self.suit_count = max(suits)
        if self.suit_count >= 3:
            self.flush = suits.index(self.suit_count)
        else:
            self.flush = -1

        self.flush_prime = 1
        if self.flush >= 0:
            for c in self.cards:
                if CARD_SUIT[c] == self.flush:
                    self.flush_prime *= CARD_PRIME[c]

    def update(self, cards):
        NewBoard = BoardInfo(self.cards + cards)
        return NewBoard

class GameState:

    def __init__(
        self,
        players,
        last_bet,
        folds,
        all_in,
        stacks,
        board,
        street,
        current_player,
        contributions,
        pot,
        utility,
        history,
        undo_stack = None,
        terminal = False
    ):

        self.players = players
        self.last_bet = last_bet
        self.folds = folds
        self.all_in = all_in
        self.stacks = stacks
        self.boards = [BoardInfo(()), BoardInfo(board[:3]), BoardInfo(board[:4]), BoardInfo(board[:5])]
        self.street = street

        self.current_player = current_player
        self.contributions = contributions
        self.pot = pot

        combos = [NumpyCombos() for _ in range(self.players)]

        self.integers = [rng[0] for rng in combos]
        self.masks = [rng[1] for rng in combos]
        self.weights = [rng[2] for rng in combos]


        self.history = history
        self.undo_stack = [] if undo_stack is None else undo_stack
        self.terminal = terminal
        self.Active_Cache = ACTIVE_CACHE

        key = self.boards[self.street].mask
        if key not in ACTIVE_CACHE:
            ACTIVE_CACHE[key] = [np.flatnonzero((m & self.boards[self.street].mask) == 0)
                        for m in self.masks]

        self.Active_Players = self.players - sum((self.folds[i] or self.all_in[i]) for i in range(self.players))
        self.players_to_act = self.Active_Players

        self.next_player = [(i+1)%self.players for i in range(self.players)]
        self.prev_player = [(i-1)%self.players for i in range(self.players)]


    def GetEquity(self, Hero, Ranges = [], board = ()):
        #Canon_Idx= {}
        #for combo in Hero[2]:
        key = hash((self.boards[self.street].mask, Hero[2].tobytes(), Ranges[0][2].tobytes(), np.round(Ranges[0][1]).tobytes()))
        if key not in Equity_CACHE:
            Equity_CACHE[key] = VecCalc(Hero_RNG=Hero, Ranges=Ranges, Samples=10000, Board=board)

        return Equity_CACHE[key]


    def legal_actions(self):
        call = self.last_bet - self.contributions[self.current_player]

        stack_eff = self.stacks[self.current_player] - call
        pot = self.pot
        pot_eff = pot + call
        actions = []

        if call == 0:
            actions.append(1)
        elif stack_eff <= 0:
            actions.extend([0,2])
            return actions
        else:
            actions.extend([0,2])

        allin = False
        for i, x in enumerate(BET_SIZES):
            if stack_eff > round(pot_eff * x):
                actions.append(i+3)
                continue
            elif stack_eff == round(pot_eff * x):
                actions.append(7)
                allin = True
                break

        if not allin:
            actions.append(7)

        return actions

    def apply_action(self, action):

        player = self.current_player
        record = (player, self.contributions[player],
            self.history, self.stacks[player],
            self.folds[player], self.all_in[player], self.street,
            self.terminal, self.pot,
            self.Active_Players, self.players_to_act, self.last_bet,
            self.next_player[player], self.prev_player[player],)

        self.undo_stack.append(record)

        call = self.last_bet - self.contributions[self.current_player]
        pot = self.pot
        pot_eff = pot + call

        Next_Round = False
        Inactive = False

        self.history = self.history * 10 + action
        self.players_to_act -= 1

        if action == 0:
            self.folds[player] = True
            Inactive = True
            self.Active_Players -= 1

            if sum(self.folds) == self.players - 1:
                self.terminal = True
                return

        elif action == 2:
            if call >= self.stacks[player]:
                Bet = self.stacks[player]
                self.all_in[player] = True
                Inactive = True
                self.Active_Players -= 1
            else:
                Bet = call

        elif 3 <= action <= 6:
            Bet = round(call + pot_eff * BET_SIZES[action-3])
            self.players_to_act = self.Active_Players - 1

        elif action == 7:
            Bet = self.stacks[player]
            self.players_to_act = self.Active_Players - 1
            self.all_in[player] = True
            Inactive = True
            self.Active_Players -= 1

        if 2 <= action <= 7:
            self.contributions[player] += Bet
            self.pot += Bet
            self.stacks[player] -= Bet

            if action > 2:
                self.last_bet = self.contributions[player]

        if Inactive:
            if self.Active_Players == 0:
                self.terminal = True

            nxt = self.next_player[player]
            prv = self.prev_player[player]

            if nxt == prv:
                if self.players_to_act > 0:
                    self.current_player = self.next_player[player]
                    return
                else:
                    self.terminal = True
                    return

            self.next_player[prv] = nxt
            self.prev_player[nxt] = prv

        if self.players_to_act == 0:
            Next_Round = True

        if Next_Round:
            if self.Active_Players <= 1:
                self.terminal = True
                return

            if self.street == 3:
                self.terminal = True
                return

            self.street = NEXT_STREET[self.street]
            key = self.boards[self.street].mask
            if key not in self.Active_Cache:
                self.Active_Cache[key] = [np.flatnonzero((m & key) == 0)
                                          for m in self.masks]


            self.players_to_act = self.Active_Players
            self.current_player = 0
            return

        self.current_player = self.next_player[player]
        return


    def undo_action(self):

        record = self.undo_stack.pop()

        p = record[0]

        self.current_player = p
        self.contributions[p] = record[1]
        self.history = record[2]
        self.stacks[p] = record[3]
        self.folds[p] = record[4]
        self.all_in[p] = record[5]
        self.street = record[6]
        self.terminal = record[7]
        self.pot = record[8]
        self.Active_Players = record[9]
        self.players_to_act = record[10]
        self.last_bet = record[11]
        self.next_player[p] = record[12]
        self.prev_player[p] = record[13]

    def payoff(self, player, reachs):

        active = ACTIVE_CACHE[self.boards[self.street].mask][player]

        util = np.zeros(len(self.integers[player]))

        util[active] -= self.contributions[player]
        board = self.boards[self.street]

        alive_players = np.flatnonzero(~np.array(self.folds))

        pot = self.pot
        # Everyone folded
        if len(alive_players) == 1:

            if not self.folds[player]:
                util[active] += pot

            return util

        # Build Hero Range
        hero_range = (self.integers[player][active], reachs[player][active], self.masks[player][active])

        # Build villain ranges
        villain_ranges = [(self.integers[i], reachs[i], self.masks[i])
            for i in alive_players
            if i != player]

        # Sidepot handling
        if any(self.all_in):

            contributions = self.contributions

            levels = sorted(
                set(c for c in contributions if c > 0)
            )

            prev = 0

            for level in levels:

                eligible = [
                    i
                    for i, c in enumerate(contributions)
                    if c >= level and not self.folds[i]
                ]

                pot_size = sum(
                    min(c, level) - min(c, prev)
                    for c in contributions
                )

                prev = level

                # Hero not eligible
                if player not in eligible:
                    continue

                # Hero wins entire sidepot
                if len(eligible) == 1:
                    util[active] += pot_size
                    continue

                sidepot_ranges = [(self.integers[i], reachs[i], self.masks[i])
                                    for i in eligible
                                    if i != player and not self.folds[i]]

                eq = self.GetEquity(Hero=hero_range, Ranges=sidepot_ranges, board=board)

                util[active] += pot_size * eq

        else:
            eq = self.GetEquity(Hero=hero_range, Ranges=villain_ranges, board=board)

            util[active] += pot * eq

        return util