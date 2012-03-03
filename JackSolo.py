#!/usr/bin/python
suits = ["Diamonds","Hearts","Spades","Clubs"]
is_fail = lambda x: (x.rank in ["King", "Ace"] or (x.rank=="10" and x.suit != "Hearts")) and (x.suit != "Diamonds")
is_trump = lambda x: not is_fail(x)
fail_order = lambda x,y: cmp(["King","10","Ace"].index(x.rank), ["King","10","Ace"].index(y.rank))
def trump_order(x, y):
    if x.short() == y.short():
        return 0
    if x.short() == "0H":
        return 1
    if y.short() == "0H":
        return -1
    if x.rank in ["Jack", "Queen"]:
        if y.rank not in ["Jack","Queen"] or x.rank > y.rank:
            return 1
        if x.rank < y.rank:
            return -1
        return cmp(suits.index(x.suit), suits.index(y.suit))
    if y.rank in ["Jack", "Queen"]:
        return -1
    return fail_order(x, y)
def total_order(x, y):
    if is_fail(x) and is_fail(y):
        return cmp(suits.index(x.suit), suits.index(y.suit)) or fail_order(x,y)
    if is_fail(x) and is_trump(y):
        return -1
    if is_trump(x) and is_fail(y):
        return 1
    return trump_order(x,y)
def player_order(specialist, players):
    return players[players.index(specialist):] + players[:players.index(specialist)]

