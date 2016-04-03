import random
from AI.utils import *
from fireplace.utils import *
'''
Created on Mar 24, 2016

@author: Kerzak
'''
from fireplace.cards.heroes import *
from fireplace.cards import heroes

class Random_bot(Player):
    
    original_deck = []
    
    deck_id = None
    
    version = 1
    
    def __init__(self, name, deck_id):
        hero = get_random_hero()
        self.deck_id = deck_id
        self.original_deck = random_draft(hero = hero)
        super(Random_bot, self).__init__(name, self.original_deck, hero)
    
    def get_id(self):
        return self.__class__.__name__ + "_" +  str(self.version)
    
    def get_deck(self):
        return self.original_deck
    
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
        player = game.current_player
        heropower = player.hero.power
        if heropower.is_usable() and random.random() < 0.1:
            if heropower.has_target():
                return get_turn_item_hero_power(heropower, random.choice(heropower.targets))
            else:
                return get_turn_item_hero_power(heropower, None)
            
        # iterate over our hand and play whatever is playable
        for card in player.hand:
            if card.is_playable()  and random.random() < 0.5:
                target = None
                if card.choose_cards:
                    card = random.choice(card.choose_cards)
                if card.has_target():
                    target = random.choice(card.targets)
                return get_turn_item_play_card(card, target)
                
            
        # Randomly attack with whatever can attack
        for character in player.characters:
            if character.can_attack():
                target = random.choice(character.targets)
                return get_turn_item_attack(character, target)
            continue
        
        if player.choice:
            choice = random.choice(player.choice.cards)
#                print("Choosing card %r" % (choice))
            player.choice.choose(choice)
        return []