#!/usr/bin/python
suits = ["Diamonds","Hearts","Spades","Clubs"]
is_fail = lambda x: True
is_trump = lambda x: False
fail_order = lambda x,y: cmp(*map(lambda s:["Jack","Queen","King","10","Ace"].index(s.rank), [x,y]))
def trump_order(x, y):
    return fail_order(x,y)
def total_order(x, y):
    return cmp(suits.index(x.suit), suits.index(y.suit)) or fail_order(x,y)

def player_order(specialist, players):
    return players[players.index(specialist):] + players[:players.index(specialist)]


