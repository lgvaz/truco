# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02d_engine.ipynb.

# %% auto 0
__all__ = ['Player', 'HumanPlayer', 'BotPlayer', 'FixedOrderBotPlayer', 'turn_finish', 'calculate_round_score', 'RoundManager']

# %% ../nbs/02d_engine.ipynb 4
from fastcore.all import *
import polvo as pv
import truco as tr
import numpy as np
import random
from copy import deepcopy
from collections import deque

# %% ../nbs/02d_engine.ipynb 5
class Player:
    def __init__(self, team): 
        self.team, self.hand = team, []
        self.team_sign = dict(t1=1, t2=-1)[team]
    def new_hand(self, hand): self.hand = hand
    def __repr__(self): return f'Player {self.team}: {self.hand}'
    def play_card(self, turn_cards): 
        ...

# %% ../nbs/02d_engine.ipynb 6
class HumanPlayer(Player):
    def play_card(self, turn_cards):
        card = input(f'Table: {turn_cards} | Hand: {self.hand}')
        self.hand.remove(card)
        return card

# %% ../nbs/02d_engine.ipynb 7
class BotPlayer(Player):
    def play_card(self, turn_cards):
        return self.hand.pop(0)

# %% ../nbs/02d_engine.ipynb 8
class FixedOrderBotPlayer(Player):
    def __init__(self, team, order):
        self.order = np.array(order)
        super().__init__(team=team)
        
    def play_card(self, turn_cards):
        idx, self.order = self.order[0], self.order[1:]
        self.order[self.order>idx] -= 1 # Adjust index for cards that were after current one being popped
        return self.hand.pop(idx)

# %% ../nbs/02d_engine.ipynb 11
def turn_finish(turn_cards, player_order, round_rank):
    ranks = tr.cards2ranks(turn_cards, round_rank)
    # necessary to get 0 if two cards of the same rank are played
    winners_mask = ranks==ranks.max()
    turn_score = sum(set([p.team_sign for p, w in zip (player_order, winners_mask) if w]))

    rotation = np.argwhere(winners_mask).flatten()[-1]
    if sum(winners_mask)>1: rotation += 1
    
    return turn_score, -rotation

# %% ../nbs/02d_engine.ipynb 21
def calculate_round_score(turn_scores):
    ts = np.asarray(turn_scores)
    nonzero_idx = np.nonzero(ts)[0]
    if nonzero_idx.size > 0: ts[ts==0] = ts[nonzero_idx[0]]
    return sum(ts)

# %% ../nbs/02d_engine.ipynb 23
# TODO: I want to remove class methods and make it functional
class RoundManager:
    def __init__(self, p11, p12, p21, p22):
        self.p11, self.p12, self.p21, self.p22 = map(deepcopy, (p11, p12, p21, p22))
        
        # TODO: Dynamic
        self.player_order = deque([self.p11, self.p21, self.p12, self.p22])
        
    def new_round(self):
        self.score = []
        self.history = []
        
    def play_turn(self, round_rank):
        turn_cards = {}
        for p in self.player_order:
            card = p.play_card(turn_cards)
            turn_cards[p] = card
            self.history.append((p.team, card))
        turn_score, rotation = turn_finish(turn_cards.values(), self.player_order, round_rank)
        self.score.append(turn_score)
        self.player_order.rotate(rotation)
            
    def play_round(self, round_rank):
        self.new_round()
        for _ in range(3): self.play_turn(round_rank)
        return calculate_round_score(self.score)
