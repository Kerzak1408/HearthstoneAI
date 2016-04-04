import random
from AI.utils import *
from fireplace.utils import *

class Malygos_freeze_mage(Player):
    
    ''' Current version of the bot. Should be updated after significant changes. '''
    version = 1
    
    ''' It is useful to store original deck here. It is needed for replays. '''
    original_deck = []
    
    ''' Name of the file containing deck. The file must be located in HearthstoneAI\AI\decks '''
    deck_id = None
    
    ''' Returns true iff I am performing final combo '''
    performing_combo = False
    
    def __init__(self, name, deck_id):
        hero = get_hero(deck_id)
        self.original_deck = get_deck_by_id(deck_id)
        super(Face_hunter, self).__init__(name, self.original_deck, hero)
    
    ''' Returns unique id of AI that consists of its name and version'''
    def get_id(self):
        return self.__class__.__name__ + "_" +  str(self.version)
    
    ''' Returns the original deck, that bot had before the start of game. '''
    def get_deck(self):
        return self.original_deck
    
    ''' Returns deck_id '''
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
        current_player = game.current_player
        opponent = current_player.opponent
        result = []
        
        if (self.performing_combo):
            result = get_next_combo_turn()
        if (get_available_combo_power(current_player.hand) > opponent.hero.health):
            return []
        
        return result
    
    def get_next_combo_turn(self, game):
        result = []
        
        return result
    
    '''
    Returns True, iff player has Emperor Thaurissan in hand.
    '''
    def has_emperor(self, player):
        return has_specific_card(player,"Emperor Thaurissan")
    
    ''' 
    Returns potential damage of all Frostbolts and Ice Lances in players hand.
    '''
    def get_available_combo_power(self, player):
        result = 0
        if (has_specific_card(player,"Malygos") and has_specific_card(player,"Frostbolt")):
            for card in player.hand:
                if (card.name == "Frostbolt"):
                    result = result + 8
                elif (card.name == "Ice Lance"):
                    result = result + 9
        return result