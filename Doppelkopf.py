#!/usr/bin/python
#TODO
# - support version w/ 9s
# - move mainloop stuff to mainloop.py (and use functions) to make more generic?
# - if 2 people go JackSolo or QueenSolo, who takes precedence?  first - probably?
# - does QueenSolo beat JackSolo?
# - add team bids/no-90/no-60/no-30/no-nothing
#   - take this into account when displaying message on Fox
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

def trick_winner(trick):
    winner = trick[0]
    i = 0
    while i < (len(trick)-1):
        i += 1
        if is_fail(winner) and is_trump(trick[i]):
            winner = trick[i]
        elif is_trump(winner) and is_fail(trick[i]):
            continue
        elif is_fail(winner) and is_fail(trick[i]) and winner.suit == trick[i].suit:
            winner = trick[i] if fail_order(winner, trick[i]) < 0 else winner
        elif is_trump(winner) and is_trump(trick[i]):
            winner = trick[i] if trump_order(winner, trick[i]) < 0 else winner
        # if fail fail but contender is not winner's suit, no change
    return trick.index(winner)

class DoppelkopfPlayer(Player):
    def __init__(self, *args, **kwargs):
        super(DoppelkopfPlayer, self).__init__(*args, **kwargs)
        self.special = None
        self.tricks = []
        self.turn_points = []
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
        if len(valid) == 1:
            print "Playing {0} because it is the only valid option.".format(valid[0])
            return self.hand.pop(self.hand.index(valid[0]))
        print "Which card? "
        return self.hand.pop(self.hand.index(valid[get_option(valid)]))

DkP = DoppelkopfPlayer

fox = Card(rank="Ace", suit="Diamonds")
charlie = Card(rank="Jack", suit="Clubs")

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
players = [DkP("Nathan"), DkP("Easton"), DkP("Seth"), DkP("Wes")] # (North, East, South, West)

dealer = players[0]
scoreboard.update(zip(players,[0 for _ in range(4)]))
present = players[:] # TODO: allow for people to leave after a hand(? or just after a round?)
while len(present) == len(players):
    # round
    while dealer in players: #  (dealer is set = None after last person to quit this loop)
        from NotSpecial import * # every turn uses NotSpecial rules by default
        
        # turn
        turn_players = players[(players.index(dealer)+1)%4:]+players[:players.index(dealer)+1]
        dd.shuffle()
        turn_players[-2].cut(dd)
        hands = dd.deal()

        # TODO: animate deal here if desired

        max_special = None
        for player in turn_players:
            player.hand = sorted(hands[players.index(player)], cmp=total_order)
            print player.name
            player.show_hand() # TODO: fancy graphics go here if desired (override the base class from common in the DoppelkopfPlayer class)
            player.declare_special()

        re = [p for p in players if "QC" in map(lambda x:x.short(),p.hand)]
        kontra = [p for p in players if p not in re]

        print
        for player in turn_players:
            if player.special:
                max_special = max(max_special, player.reveal_special(max_special), key=lambda x:specials[x])
        specialist = [p for p in turn_players if p.special==max_special][0]

        print specialist.name, max_special
        
        if "Solo" in str(max_special):
            re = [specialist]
            kontra = [p for p in players if p not in re]
        pregame_set_up = post_turn = lambda *_: None # by default, take a variable number of args and do nothing
        if max_special == "No-Trump Solo":
            from NoTrumpSolo import *
        elif max_special == "Jack Solo":
            from JackSolo import *
        elif max_special == "Queen Solo":
            from QueenSolo import *
        elif max_special == "Marriage":
            from Marriage import *
        elif max_special == "Poor":
            from Poor import *

        for i in range(len(turn_players)):
            turn_players[i].hand.sort(cmp=total_order)
        
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
            winner = turn_players[trick_winner(current_trick)]
            winner.tricks += current_trick
            print "{0}'s trick".format(winner.name)
            if "Solo" not in str(max_special):
                if fox in current_trick:
                    print "Fox(?)" # Leave it ambiguous so as not to inadvertantly reveal teams; TODO: if teams are known, don't bother leaving it ambiguous
                    foxers = [p for i, p in enumerate(turn_players) if current_trick[i] == fox]
                    for foxer in foxers:
                        if (winner in re and foxer in kontra) or (winner in kontra and foxer in re):
                            winner.turn_points.append("Fox")
                if sum(map(lambda c:c.points,current_trick)) >= 40:
                    print "Doppelkopf!"
                    winner.turn_points.append("Doppelkopf")
                if not winner.hand and current_trick[turn_players.index(winner)] == charlie:
                    print "Charlie!"
                    winner.turn_points.append("Charlie")
            post_turn(winner, current_trick)
            turn_players = players[players.index(winner):] + players[:players.index(winner)]

        print

        # inner points
        re_score = sum(sum(map(lambda c:points[c.rank], player.tricks)) for player in re)
        kontra_score = sum(sum(map(lambda c:points[c.rank], player.tricks)) for player in kontra)
        print "Re: {0} points\n{1}".format(re_score, sorted([c for c in dd if c in re[0].tricks or c in re[1].tricks], key=lambda c:c.points))
        print "Kontra: {0} points\n{1}".format(kontra_score, sorted([c for c in dd if c in kontra[0].tricks or c in kontra[1].tricks], key=lambda c:c.points))
        print "{0} wins!".format("Re" if re_score > kontra_score else "Kontra")

        # outer points
        re_points = []
        for p in re:
            re_points.extend(p.turn_points)
        kontra_points = []
        for p in kontra:
            kontra_points.extend(p.turn_points)
        win,fail = max(re_score, kontra_score+1), min(re_score,kontra_score+1)
        game_points = 1
        print "{0}: win".format(game_points)
        if fail < 90:   # no-90
            game_points += 1
            print "{0}: no 90".format(game_points)
        if fail < 60:   # no-60
            game_points += 1
            print "{0}: no 60".format(game_points)
        if fail < 30:   # no-30
            game_points += 1
            print "{0}: no 30".format(game_points)
        if fail == 0:   # no-nothing
            game_points += 1
            print "{0}: no nothing".format(game_points)
        if win != re_score:
            game_points += 1 # geigen die alten/against the elders/against the odds
            print "{0}: geigen die alten".format(game_points)
            for point in kontra_points:
                game_points += 1
                print "{0}: {1}".format(game_points, point)
            for point in re_points:
                game_points -= 1
                print "{0}: minus {1}".format(game_points, point)
            game_points *= -1
        else:
            for point in re_points:
                game_points += 1
                print "{0}: {1}".format(game_points, point)
            for point in kontra_points:
                game_points -= 1
                print "{0}: minus {1}".format(game_points, point)
        for player in re:
            scoreboard[player] += game_points
        for player in kontra:
            scoreboard[player] -= game_points

        assert(not sum(scoreboard.values()))
        print "\nScores:"
        print "\n".join("\t{0}: {1}".format(p.name,s) for p, s in scoreboard.items())
        print

        # update_dealer
        if (players == player_order(specialist, players)) and (players[1:] + [players[0]] == player_order(specialist, players[1:]+[players[0]])): # TODO: if leader goes Solo, does dealer change?
            dealer = (players+[None])[players.index(dealer)+1]
        
    # get_current_players
    assert(sum(scoreboard.values())==0)
    break
dd.cmp = total_order
dd.order()
