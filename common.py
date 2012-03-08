#!/usr/bin/python
import random

suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
ranks = [str(i) for i in range(2,11)] + ["Jack", "Queen", "King", "Ace", "Joker"]
shorts = dict(zip(ranks,[str(i) for i in range(2,10)]+["0","J","Q","K","A","*"]))
players = 4

class Card:
    def __init__(self, rank="Ace", suit="Spades", points=0):
        self.rank = rank
        self.suit = suit
        self.points = points
    def __cmp__(self, other):
        return cmp(self.rank, other.rank) or cmp(self.suit, other.suit)
    def __repr__(self):
        return "{0} of {1}".format(self.rank, self.suit)
    def short(self):
        return "{0}{1}".format(shorts[self.rank], self.suit[0])

class Deck:
    def __init__(self, suits=suits, ranks=ranks, drop=lambda x:x.rank=="Joker", cmp=lambda x,y: cmp(ranks.index(x.rank),ranks.index(y.rank)) or cmp(suits.index(x.suit), suits.index(y.suit)),players=players,deals=[1],drawing=False,points=lambda x:0):
        self.cards = [Card(rank=rank, suit=suit) for suit in suits for rank in ranks]
        self.cards = [card for card in self.cards if not drop(card)]
        for card in self.cards:
            card.points = points(card)
        self.cmp = cmp
        self.players = players
        self.deals = deals
        self.drawing = drawing
        self.discard = []
    def __iter__(self):
        return iter(self.cards)
    def __len__(self):
        return len(self.cards)
    def __repr__(self):
        return "\n".join(str(card) for card in self.cards)
    def order(self):
        self.cards.sort(cmp=self.cmp)
    def shuffle(self):
        random.shuffle(self.cards)
    def short(self):
        return "\n".join(card.short() for card in self.cards)
    def deal(self):
        hands = [[] for _ in range(self.players)]
        deck = self.cards[:]
        for d in self.deals:
            for h in hands:
                n = min(d, len(deck))
                th, deck = deck[:n], deck[n:]
                h.extend(th)
        if not self.drawing:
            while deck:
                for h in hands:
                    h.append(deck.pop(0))
        else:
            self.cards = deck
        return hands
    def cut(self, i):
        self.cards = self.cards[i:] + self.cards[:i]

class Player(object):
    def __init__(self, name):
        self.name = name
        self.hand = []
    def show_hand(self):
        print "\t{0}".format(self.hand)
    def cut(self, deck):
        print "Please select a cut."
        print self.name
        deck.cut(get_option(["" for _ in range(len(deck))]))

def get_option(seq, default=-1):
    seq = (seq[:default]+["[{0}]".format(seq[default])]+seq[default+1:])[:len(seq)]
    print "\n".join(map(lambda x:" ".join(x),zip(map(str,range(1,len(seq)+1)),map(str,seq))))
    ind = ""
    while not isinstance(ind, int):
        try:
            ind = raw_input("> ")
            if not ind:
                return default
            ind = int(ind)
            if ind < 0:
                raise ValueError
        except ValueError:
            print "Enter a positive number."
    return ind-1

