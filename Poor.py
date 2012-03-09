#!/usr/bin/python
def pregame_set_up(poor, players):
    for i, player in enumerate(players):
        if player != poor:
            print player.name
            print player.hand
            if player.take_poor():
                return i+1
    return -1
def player_order(specialist, players):
    return (players[(players.index(specialist)+1)%len(players):]+players[:players.index(specialist)+1])[:len(players)]
