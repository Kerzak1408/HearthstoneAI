import random
from AI.utils import *
from fireplace.utils import *

class Bot_template(Player):
    
    ''' Current version of the bot. Should be updated after significant changes. '''
    version = 1
    
    ''' It is useful to store original deck here. It is needed for replays. '''
    original_deck = []
    
    ''' Name of the file containing deck. The file must be located in HearthstoneAI\AI\decks '''
    deck_id = None
    
    ''' You can change this. But this works if deck file is valid. '''
    def __init__(self, name, deck_id):
        hero = get_hero(deck_id)
        self.original_deck = get_deck_by_id(deck_id)
        super(Face_hunter, self).__init__(name, self.original_deck, hero)
    
    ''' This should return unique id of AI that consists of its name and version'''
    def get_id(self):
        return self.__class__.__name__ + "_" +  str(self.version)
    
    ''' This should return the original deck, that bot had before the start of game. '''
    def get_deck(self):
        return self.original_deck
    
    ''' This should return deck_id '''
    def get_deck_id(self):
        return self.deck_id
    
    """
    Choose next action to do.
    Action patterns:
    Play card: [0, card, target]
       Attack: [9, attacker, defender]
    Hero Pow.: [19, target]
     End Turn: []
    """
    def get_next_turn(self, game):
        return []