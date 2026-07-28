from itertools import permutations

SUIT_PERMS = tuple(permutations((0, 1, 2, 3)))
CARD_MASKS = [1 << c for c in range(52)]

def canonical(board=(), hands=()):
    best = None

    for perm in SUIT_PERMS:

        transformed_hands = []

        for hand in hands:

            h = []

            for card in hand:
                rank = card % 13
                suit = card // 13

                h.append(rank + 13 * perm[suit])

            transformed_hands.append(tuple(sorted(h)))

        transformed_hands.sort()

        if board:

            transformed_board = []

            for card in board:
                rank = card % 13
                suit = card // 13

                transformed_board.append(
                    rank + 13 * perm[suit]
                )

            transformed_board = tuple(sorted(transformed_board))

            state = (transformed_board, tuple(transformed_hands))

        else:
            state = tuple(transformed_hands)

        if best is None or state < best:
            best = state

    return best

def canonical_hand(board, hand):

    suit_count = [0, 0, 0, 0]
    board_mask = 0

    for card in board:
        suit_count[card // 13] += 1

    suit_map = [-1] * 4

    next_suit = 0

    for suit in range(4):
        if len(board) == 3:
            if suit_count[suit] + (hand[0] // 13 == suit) + (hand[1] // 13 == suit) > 2:
                suit_map[suit] = next_suit
                next_suit += 1
            elif suit_count[suit] > 0:
                next_suit += 1


        else:
            if suit_count[suit] + (hand[0] // 13 == suit) + (hand[1] // 13 == suit) > 3:
                suit_map[suit] = next_suit
                next_suit += 1
            elif suit_count[suit] > 0:
                next_suit += 1

    if next_suit == 4:
        canon = []
        board_mask = 0
        for card in board:
            board_mask |= CARD_MASKS[card]

        for card in hand:
            rank = card % 13
            for suit in range(4):
                new_card = rank + 13 * suit
                if CARD_MASKS[new_card] & board_mask:
                    continue
                else:
                    canon.append(new_card)
                    board_mask |= CARD_MASKS[new_card]
                    break

        canon.sort()
        return tuple(canon)

    absent_rep = next_suit

    for suit in range(4):
        if suit_map[suit] == -1:
            suit_map[suit] = absent_rep

    if hand[0] % 13 == hand[1] % 13:
        canon = []
        board_mask = 0
        for card in board:
            board_mask |= CARD_MASKS[card]

        rank1 = hand[0] % 13
        suit1 = hand[0] // 13

        canon.append(rank1 + 13 * suit_map[suit1])
        board_mask |= CARD_MASKS[rank1 + 13 * suit_map[suit1]]

        rank2 = hand[1] % 13

        for x in range(4):
            suit2 = (suit_map[suit1] + x) % 4
            new_card = rank2 + 13 * suit2
            if CARD_MASKS[new_card] & board_mask:
                continue
            else:
                canon.append(new_card)
                break

        canon.sort()
        return tuple(canon)

    canon = []

    for card in hand:

        rank = card % 13
        suit = card // 13

        new_suit = suit_map[suit]

        canon.append(rank + 13 * new_suit)

    canon.sort()
    return tuple(canon)

