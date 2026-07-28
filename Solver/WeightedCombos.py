import pandas as pd
from RangeParser import RangeParser
import numpy as np

Ranks = "23456789TJQKA"
Suits = "schd"

i = 1
Int_Hands = []
Masks = []
Weights = []
Strings = []

while i < 52:
    j = 0
    while j < i:
        Int_Hands.append((i,j))
        Masks.append(1 << i | 1 << j)
        Weights.append(1.0)
        Strings.append(Ranks[i%13]+Suits[i//13]+Ranks[j%13]+Suits[j//13])
        j+=1
    i+=1

def NumpyCombos():
    Integers = np.array(Int_Hands)
    NPMasks = np.array(Masks)
    NPWeights = np.array(Weights)
    return Integers, NPMasks, NPWeights

def NumpyRemoveBlocked(Integers, Masks, Weights, Block_Mask):
    valid = (Masks & Block_Mask) == 0
    idx = np.flatnonzero(valid)
    Integers = Integers[idx]
    Masks = Masks[idx]
    Weights = Weights[idx]
    return Integers, Masks, Weights

def NumpyParse(Integers, Masks, Weights, Range):
    Parsed = RangeParser(Range)

    idx = []
    for combo in Parsed:
        if combo[0] < combo[1]:
            hand = (combo[1], combo[0])
        else:
            hand = (combo[0], combo[1])

        match = np.where((Integers[:, 0] == hand[0]) & (Integers[:, 1] == hand[1]))[0]

        if len(match):
            idx.append(match[0])

    idx = np.array(idx, dtype=np.int32)

    return Integers[idx], Masks[idx], Weights[idx]



def Combos():
    Dict = {
        "Name" : Strings,
        "Integers" : Int_Hands,
        "Bit Masks" : Masks,
        "Frequency" : Weights,
    }

    Combos_DF = pd.DataFrame(Dict)
    return Combos_DF

def Normalize(DF, name):
    Total = DF[name].sum()
    if not Total == 0:
        DF[name] = DF[name]/Total
    return DF

def Remove_Blocked(DF, Block_Mask):
    BF = DF[DF["Bit Masks"] & ~Block_Mask == DF["Bit Masks"]]
    return BF

def Parse(DF, Range):
    Parsed = RangeParser(Range)
    Parsed_Sorted = []
    for hand in Parsed:
        if hand[0] > hand[1]:
            Parsed_Sorted.append(hand)
        else:
            Parsed_Sorted.append(hand[::-1])

    DF = DF[DF["Integers"].isin(Parsed_Sorted)]
    return DF

def Clean(DF, Name, Threshhold = 1e-6):
    DF = DF[DF[Name] > Threshhold]
    return DF

