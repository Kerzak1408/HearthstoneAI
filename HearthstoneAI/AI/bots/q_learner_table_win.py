import random
import numpy
import sys
from AI.utils import *
from fireplace.utils import *
from fireplace.card import Minion, HeroPower

class Q_learner_table_win(Player):
    
    ''' Current version of the bot. Should be updated after significant changes. '''
    version = 1
    
    ''' It is useful to store original deck here. It is needed for replays. '''
    original_deck = []
    
    ''' Name of the file containing deck. The file must be located in HearthstoneAI\AI\decks '''
    deck_id = None
    states_num = 1
    actions_num = 168
    table = None
    learning_rate = 0.8
    discount_factor = 0.8
    previous_q_value = None
    previous_action = None
    previous_state = None
    previous_opp_hero_hp = 30
    previous_my_hero_hp = 30
    previous_opp_hero_armor = 0
    previous_my_hero_armor = 0
    previous_turn = []
    old_value = 0
    
    sorted_original_deck = None
    
    ''' Change Bot_template to your class name '''
    def __init__(self, name, deck_id, existing_table):
        if (existing_table == None):
            self.table = numpy.zeros((self.states_num,self.actions_num))
        else:
            self.table = existing_table
      
        hero = get_hero(deck_id)
        self.deck_id = deck_id
        self.original_deck = get_deck_by_id(deck_id)
        super(Q_learner_table_win, self).__init__(name, self.original_deck, hero)
    
    ''' This should return unique id of AI that consists of its name and version'''
    def get_id(self):
        return self.__class__.__name__ + "_" +  str(self.version)
    
    ''' This should return the original deck, that bot had before the start of game. '''
    def get_deck(self):
        return self.original_deck
    
    ''' This should return deck_id '''
    def get_deck_id(self):
        return self.deck_id
    
    '''
    Choose a list of cards to mulligan.
    It should return the list of the cards you want to discard.
    This is called only before the first turn of each game.
    If you leave it unchanged, it will choose randomly.
    '''
    def get_mulligans(self, choice_cards):
        mull_count = random.randint(0, len(choice_cards))
        return random.sample(choice_cards, mull_count)
    
    """
    Choose next action to do.
    Action patterns:
    Play card: [0, card, target]
       Attack: [9, attacker, defender]
    Hero Pow.: [19, target]
    Spell attack: [16, card, target]
     End Turn: []
    """
    def get_next_turn(self, game):
        state = self.get_state()
        [turn, q_value, action] = self.get_best_action(state)
        reward = self.get_reward(self.previous_turn)
        self.update_table(self.previous_state, state, self.previous_action, reward)
        self.previous_action = action
        self.previous_state = state
        self.previous_opp_hero_hp = self.opponent.hero.health
        self.previous_opp_hero_armor = self.opponent.hero.armor
        self.previous_my_hero_hp = self.hero.health
        self.previous_my_hero_armor = self.hero.armor
        self.previous_turn = turn
        return turn
    
    def get_reward(self, turn):
        result = 0
        if (turn == []):
            if (has_playable_card_of_max_cost(self, self.mana) or can_any_character_attack_hero(self)):
                result = result - 10
            else:
                result = result + (self.used_mana/self.max_mana) * 10
        if (turn != [] and turn[0] == 9):
            if (turn[2].__class__ == Hero or (turn[2].__class__ == Minion and turn[2].taunt)):
                result = result + 10  
            else:
                result = result - 10
        opp_hero_damage_done = self.previous_opp_hero_armor + self.previous_opp_hero_hp - self.opponent.hero.health - self.opponent.hero.armor
        if (opp_hero_damage_done > 0):
            result = result + opp_hero_damage_done
        my_hero_damage_done = self.previous_my_hero_armor + self.previous_my_hero_hp - self.hero.health - self.hero.armor
        if (my_hero_damage_done > 0):
            result = result - 10
        for character in self.characters:
            result = result + character.atk
        
        return result
    
    def get_character_value(self, character):
        value = 1
        value = value + character.atk * 10
        value = value + character.health
        if (character.__class__ is Minion):
            if (character.taunt):
                value = value + 5
            if (character.divine_shield):
                value = value + 10
        return value
    
    def get_state(self):
        state = 0
        
        mana_vector = [0]
        return state
    
    def get_int_from_bool(self, boolean_value):
        if (boolean_value):
            return 1
        else:
            return 0
    
    def get_best_action(self, state):
        best_action = self.get_action(None, None)
        q_max = self.table[state,best_action]
        best_turn = []
        for card in self.hand:
            if (card.is_playable()):
                if (card.has_target()):
                    for target in card.targets:
                        action = self.get_action(card, target)
                        q_candidate = self.table[state,action]
                        if (q_candidate > q_max):
                            best_action = action
                            q_max = q_candidate
                            if card.choose_cards:
                                card = random.choice(card.choose_cards)
                            best_turn = get_turn_item_play_card(card,target)
                else:
                    action = self.get_action(card, None)
                    q_candidate = self.table[state,action]
                    if (q_candidate > q_max):
                        best_action = action
                        q_max = q_candidate
                        if card.choose_cards:
                            card = random.choice(card.choose_cards)
                        best_turn = get_turn_item_play_card(card,None)
                
        if (self.hero.power.is_usable()):
            if (self.hero.power.has_target()):
                for target in self.hero.power.targets:
                    action = self.get_action(self.hero.power, target)
                    q_candidate = self.table[state,action]
                    if (q_candidate > q_max):
                        best_action = action
                        q_max = q_candidate
                        best_turn = get_turn_item_hero_power(self.hero.power,target)
            else:
                action = self.get_action(self.hero.power, None)
                q_candidate = self.table[state,action]
                if (q_candidate > q_max):
                    best_action = action
                    q_max = q_candidate
                    best_turn = get_turn_item_hero_power(self.hero.power,None)
        
        for character in self.characters:
            for target in character.targets:
                if (character.can_attack(target)):
                    action = self.get_action(character, target)
                    q_candidate = self.table[state,action]
                    if (q_candidate > q_max):
                        best_action = action
                        q_max = q_candidate
                        best_turn = get_turn_item_attack(character,target)
             
        return [best_turn,q_max, best_action]
    
    def get_action(self, my_entity, target_character):
        result = -1
        cards_actions_num = 150
        if (my_entity == None and target_character == None):
            return 0
        elif (my_entity in self.hand):
            # playing a card
            cost = my_entity.cost + 1
            if (not(my_entity in self.original_deck)):
                # unknown card - probably The Coin
                return 167
            else:
                index = self.original_deck.index(my_entity) + 1
                if (target_character == None):
                    # no target
                    return index
                elif (target_character.__class__ is Minion):
                    #targetting a minion
                    if (target_character.controller == self):
                        # targetting own minion
                        return index + 30
                    else:
                        # targetting enemy minion
                        return index + 60
                elif (target_character.__class__ is Hero):
                    if (target_character.controller == self):
                        # targetting own hero
                        return index + 90
                    else:
                        # targetting enemy hero
                        return index + 120
        elif (my_entity.__class__ is Minion):            
            
            if (target_character.__class__ is Hero):
                # attacking a hero
                return cards_actions_num + 1
            elif (target_character.__class__ is Minion):
                # attacking a minion
                if (target_character.atk >= my_entity.health and not(my_entity.divine_shield)):
                    # my character is going to die
                    if (target_character.health < my_entity.atk and not(target_character.divine_shield)):
                        # both characters are going to die
                        return cards_actions_num + 2
                    else:
                        # I am going to lose character, my opponent is not
                        return cards_actions_num + 3
                else:
                    # my character is going to survive
                    if (target_character.health < my_entity.atk and not(target_character.divine_shield)):
                        # My opponent is going to lose character but not me
                        return cards_actions_num + 4
                    else:
                        # Both character are going to survive
                        return cards_actions_num + 5
        elif (my_entity.__class__ is Hero):
            if  (target_character.__class__ is Hero):
                # attacking a hero
                return cards_actions_num + 6
            elif (target_character.__class__ is Minion):
                # attacking a minion
                if (target_character.atk >= my_entity.health):
                    # my hero is going to die
                    if (target_character.health < my_entity.atk and not(target_character.divine_shield)):
                        # both my hero and the target are going to die
                        return cards_actions_num + 7
                    else:
                        # my hero is going to die, the target is not
                        return cards_actions_num + 8
                else:
                    # my hero is going to survive
                    if (target_character.health < my_entity.atk and not(target_character.divine_shield)):
                        # My opponent is going to lose character but not me
                        return cards_actions_num + 9
                    else:
                        # Both character are going to survive
                        return cards_actions_num + 10
        
        elif (my_entity.__class__ is HeroPower):
            if (target_character == None):
                # no target
                return cards_actions_num + 11
            elif (target_character.__class__ is Hero):
                # target is Hero
                if (target_character.controller == self):
                    # targetting my hero
                    return cards_actions_num + 12
                else:
                    #targetting opp hero
                    return cards_actions_num + 13
            elif (target_character.__class__ is Minion):
                if (target_character.controller == self):
                    # targetting my hero
                    return cards_actions_num + 14
                else:
                    #targetting opp hero
                    return cards_actions_num + 15
        else:
            # only unexpected actions
            print ("Unexpected action. MY_ENTITY: " + str(my_entity) + " TARGET: " + str(target_character))
            return cards_actions_num + 16
        return -1
            
    
    def get_best_target(self, card):
        if (card.has_target()):
            target = None
            if (self.opponent.hero in card.targets):
                target = self.opponent.hero
            else:
                for minion in self.opponent.field:
                    if (minion in card.targets): 
                        target = minion
                if (target == None):
                    target = random.choice(card.targets)
        else:
            target = None
        return target
    
    def update_table(self, old_state, new_state,action, reward):
        if (old_state != None):
            old_value = self.table[old_state, action]
            desired_value = old_value + self.learning_rate * (reward + self.discount_factor * self.get_best_action(new_state)[1] - old_value)
           
            self.table[old_state,action] = desired_value
    
        
        
        
        