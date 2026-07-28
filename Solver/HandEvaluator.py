from LookupTableHE import All_Hands, Flush_Hands
# Precompute everything possible
PRIMES = (2,3,5,7,11,13,17,19,23,29,31,37,41)

CARD_RANK = tuple(i % 13 for i in range(52))
CARD_SUIT = tuple(i // 13 for i in range(52))

CARD_PRIME = tuple(PRIMES[i % 13] for i in range(52))


def EvaluateHandHE(cards, board):

    c0,c1 = cards

    # Inline all 7 cards
    p0 = CARD_PRIME[c0]
    p1 = CARD_PRIME[c1]

    # Total prime product
    rank_mask = (board.prime * p0 * p1)

    if board.flush == -1:
        return All_Hands[rank_mask]

    # Suit counts
    s0 = CARD_SUIT[c0]
    s1 = CARD_SUIT[c1]

    if board.suit_count == 3 and (s0 != s1 or s0 != board.flush):
        return All_Hands[rank_mask]
    elif board.suit_count == 4 and (s0 != board.flush and s1 != board.flush):
        return All_Hands[rank_mask]

    flush_product = board.flush_prime
    if s0 == board.flush: flush_product *= p0
    if s1 == board.flush: flush_product *= p1
    return Flush_Hands[flush_product]