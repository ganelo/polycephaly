#!/usr/bin/python
#TODO
# - support version w/ 9s
# - move mainloop stuff to mainloop.py (and use functions) to make more generic?
# - subclass Player to have special bid method, custom go method
from common import *
from NotSpecial import total_order, is_fail, is_trump

class DoppelkopfPlayer(Player):
    def __init__(self, *args, **kwargs):
        super(DoppelkopfPlayer, self).__init__(*args, **kwargs)
        self.special = None
    def declare_special(self):
        sps = [i for i in sorted(specials.keys(), key=specials.__getitem__) if i not in [None, "Poor"]]
        if is_poor(self.hand):
            self.special = "Poor"
            print "Poor hand - no choice."
            return True
        elif not is_marriage(self.hand):
            sps = [i for i in sps if i != "Marriage"]
        print "Which special? [None]"
        special_type = get_option(sps+["None"])
        self.special = (sps+[None])[special_type]
        print self.special
        return bool(self.special)
    def reveal_special(self, other):
        if other < specials[self.special]:
            print self.special
        return self.special
    def go(self, trick):
        try:
            lead = trick[0]
            if is_fail(lead):
                valid = filter(lambda c: c.suit == lead.suit and is_fail(c), self.hand)
            else:
                valid = filter(lambda c: is_trump(c))
            if not valid:
                raise IndexError
        except IndexError:
            valid = self.hand
        print "Which card? "
        return self.hand.pop(self.hand.index(valid[get_option(valid)]))

DkP = DoppelkopfPlayer

specials = {None:0, "No-Trump Solo":1, "Jack Solo":1, "Queen Solo":1, "Marriage":2, "Poor":3}
points = {"Ace":11, "King":4, "Queen":3, "Jack":2, "10":10}
DoppelkopfDeck = Deck(suits=suits*2, ranks=ranks,
                      drop=lambda x:x.rank in map(str,range(2,10))+["Joker"],
                      points=lambda x:points[x.rank])
dd = DoppelkopfDeck
dd.players = 4
dd.deals = [3, 4, 3]
is_marriage = lambda x: x.count(Card(rank="Queen",suit="Clubs")) == 2
is_poor = lambda x: map(is_trump, x).count(True) < 3
scoreboard = {}
players = [DkP("Nathan"), DkP("Edward"), DkP("Solomon"), DkP("Wesley")] # get_players
dealer = players[0]
scoreboard.update(zip(map(lambda x:x.name,players),[0 for _ in range(4)]))
present = players[:]
while len(present) == len(players):
    # round
    while dealer in players: #  (dealer is set = None after last person to quit this loop)
        # turn
        turn_players = players[(players.index(dealer)+1)%4:]+players[:players.index(dealer)+1]
        hands = dd.deal()
        max_special = specials[None]
        for player in turn_players:
            player.hand = sorted(hands[i], cmp=total_order)
            print player.name
            player.show_hand()
            player.declare_special()
        for player in turn_players:
            if player.special:
                print player.name
                max_special = max(max_special, specials[player.reveal_special(max_special)])
        pregame_setup = turns_set_up = lambda *_: None
        if max_special == "No-Trump Solo":
            from NoTrumpSolo import total_order, is_fail, is_trump
        elif max_special == "Jack Solo":
            from JackSolo import total_order, is_fail, is_trump
        elif max_special == "Queen Solo":
            from QueenSolo import total_order, is_fail, is_trump
        elif max_special == "Marriage":
            from Marriage import pregame as turns_set_up
        elif max_special == "Poor":
            from Poor import pregame as pregame_set_up
        pregame_set_up(turn_players)
        while players[0].hand:
            current_trick = []
            for player in turn_players:
                current_trick += [player.go(current_trick[:])]
            

        # update_dealer 
        break
    # get_current_players
    assert(sum(scoreboard.values())==0)
    break
dd.cmp = total_order
dd.order()
