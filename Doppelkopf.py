#!/usr/bin/python
#TODO
# - support version w/ 9s
# - move mainloop stuff to mainloop.py (and use functions) to make more generic?
# - if 2 people go JackSolo or QueenSolo, who takes precedence?  first - probably?
# - add team bids/no-90/no-60/no-30/no-nothing
# - add Charlie point
# - add Fox point
# - add scoring for non-solo games
# - finish adding support for marriage and poor
# - only show each player his/her own info
#   - maybe have each player run join_game.py or something?
#       - join_game would write the username, etc. to a standard file (name=pid), look for a running Doppelkopf.py and send a SIGRTMIN (using os.kill) to register itself, then spin until it receives SIGRTMIN
#       - Doppelkopf spins until it has received 4 registrations - it ignores subsequent registrations until someone quits (SIGRTMIN+1)
#       - if Doppelkopf receives a SIGRTMIN, it scans the user dir for new pid files, reads them, and stores the info in a dict if that username doesn't already have a score (for example)
#           - if the username already exists and is deleted, mark as undeleted
#           - if the username already exists and is not deleted, Doppelkopf will modify the pid file with a modified username and send join_game a SIGRTMIN+1
#       - if Doppelkops receives a SIGRTMIN+1, it scans the user dir for missing pid files, marks them as deleted in the dict, and spins until it has 4 users again
#           - alternatively, use SIGUSR1 and SIGUSR2 (though SIGRTMIN probably makes more sense)
#       - once there are 4 players, Doppelkopf will send a SIGRTMIN to all player pids (at which point they will rescan their own pid files to get updated usernames and display a "starting" message to the user)
#       - join_game would contain the DoppelkopfPlayer code, so all calls would have to go through SIGRTMIN+n signals . . . (it's your turn, please declare a special, please show your special, etc.)
#       - in the other direction, when a player made a team bid/etc., join_game would have to send a SIGRTMIN to have Doppelkops scan the pid files for modifications to the pids it cares about?
from common import *
from NotSpecial import total_order, is_fail, is_trump, trick_order

class DoppelkopfPlayer(Player):
    def __init__(self, *args, **kwargs):
        super(DoppelkopfPlayer, self).__init__(*args, **kwargs)
        self.special = None
        self.tricks = []
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
    def reveal_special(self, other): # TODO: not quite correct currently
        if specials[other] < specials[self.special]:
            print self.name
            print self.special
        return self.special
    def go(self, trick):
        print self.name
        try:
            lead = trick[0]
            if is_fail(lead):
                valid = filter(lambda c: c.suit == lead.suit and is_fail(c), self.hand)
            else:
                valid = filter(is_trump, self.hand)
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

# get_players
players = [DkP("Nathan"), DkP("Edward"), DkP("Solomon"), DkP("Wesley")] # (North, East, South, West)

dealer = players[0]
scoreboard.update(zip(map(lambda x:x.name,players),[0 for _ in range(4)]))
present = players[:] # TODO: allow for people to leave after a hand(? or just after a round?)
while len(present) == len(players):
    # round
    while dealer in players: #  (dealer is set = None after last person to quit this loop)
        # turn
        turn_players = players[(players.index(dealer)+1)%4:]+players[:players.index(dealer)+1]
        hands = dd.deal()

        # TODO: animate deal here if desired

        max_special = None
        for player in turn_players:
            player.hand = sorted(hands[players.index(player)], cmp=total_order)
            print player.name
            player.show_hand() # TODO: fancy graphics go here if desired (override the base class from common in the DoppelkopfPlayer class)
            player.declare_special()
        for player in turn_players:
            if player.special:
                max_special = max(max_special, player.reveal_special(max_special), key=lambda x:specials[x])
        specialist = [p for p in turn_players if p.special==max_special][0]
        pregame_set_up = post_turn = lambda *_: None # by default, take a variable number of args and do nothing
        if max_special == "No-Trump Solo":
            from NoTrumpSolo import total_order, is_fail, is_trump, player_order
        elif max_special == "Jack Solo":
            from JackSolo import total_order, is_fail, is_trump, player_order
        elif max_special == "Queen Solo":
            from QueenSolo import total_order, is_fail, is_trump, player_order
        elif max_special == "Marriage":
            from Marriage import post_turn as post_turn, player_order
        elif max_special == "Poor":
            from Poor import pregame as pregame_set_up, player_order
        turn_players = player_order(specialist, turn_players) # different specials have different rules for who goes first (Marriage vs. Solos)
        if pregame_set_up(turn_players) == -1: # just for Poor
            break # re-deal without changing dealers
        while players[0].hand:
            current_trick = []
            for player in turn_players:
                print                   # TODO: fancy graphics go here - everyone can see the current trick
                print current_trick
                current_trick += [player.go(current_trick[:])]
            print current_trick
            winner = turn_players[current_trick.index(sorted(current_trick, cmp=trick_order)[-1])]
            winner.tricks += current_trick
            print "{0}'s trick".format(winner.name)
            post_turn(winner, current_trick)
            turn_players = players[players.index(winner):] + players[:players.index(winner)]

        # update scores
        if "Solo" in max_special:
            re_score = sum(sum(map(points.__getitem__, trick)) for trick in specialist.tricks)
            kontra_score = sum(sum(sum(map(points.__getitem__, trick)) for trick in player.tricks) for player in players if player != specialist)
            if re_score > kontra_score:
                scoreboard[specialist] += 3
                for player in players:
                    if player != specialist:
                        scoreboard[player] -= 1
        assert(not sum(scoreboard.values()))

        # update_dealer
        if players == player_order(specialist, players) == player_order(specialist, players[1:]+players[0]): # TODO: if leader goes Solo, does dealer change?
            dealer = (players+[None])[players.index(dealer)+1]
 
        
    # get_current_players
    assert(sum(scoreboard.values())==0)
    break
dd.cmp = total_order
dd.order()
