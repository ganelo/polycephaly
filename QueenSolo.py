#!/usr/bin/python
suits = ["Diamonds","Hearts","Spades","Clubs"]
is_fail = lambda x: x.rank!="Queen"
is_trump = lambda x: not is_fail(x)
fail_order = lambda x,y: cmp(*map(lambda s:["Jack","King","10","Ace"].index(s.rank), [x,y]))
def trump_order(x, y):
    return cmp(suits.index(x.suit), suits.index(y.suit))
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

