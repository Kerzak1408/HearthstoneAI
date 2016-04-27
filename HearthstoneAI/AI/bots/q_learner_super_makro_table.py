import random
import pybrain
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from AI.utils import *
from fireplace.utils import *
from pybrain.datasets.supervised import SupervisedDataSet
from pybrain.tools.customxml import NetworkWriter
from pybrain.tools.customxml import NetworkReader
from fireplace.card import Minion, HeroPower

class Q_learner_super_makro_table(Player):
    
    ''' Current version of the bot. Should be updated after significant changes. '''
    version = 1
    
    ''' It is useful to store original deck here. It is needed for replays. '''
    original_deck = []
    
    ''' Name of the file containing deck. The file must be located in HearthstoneAI\AI\decks '''
    deck_id = None
    
    q_table = None
    learning_rate = 0.8
    discount_factor = 0.8
    states_and_actions_num = 0 + 1 + 50 + 5 + 5 + 5 + 1
    previous_q_value = None
    previous_action = None
    previous_state = None
    previous_opp_hero_hp = 30
    previous_my_hero_hp = 30
    
    sorted_original_deck = None
    
    ''' Change Bot_template to your class name '''
    def __init__(self, name, deck_id, neural_net):
        if (neural_net == None):
            path = os.path.join(os.path.dirname(os.getcwd()), 'network.xml')
            self.neural_network = NetworkReader.readFrom(path)
        else:
            self.neural_network = neural_net
      
        hero = get_hero(deck_id)
        self.deck_id = deck_id
        self.original_deck = get_deck_by_id(deck_id)
        super(Q_learner_super_makro_table, self).__init__(name, self.original_deck, hero)
    
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
        if (self.previous_q_value != None):
            self.update_neural_network(self.previous_state, self.previous_q_value, state, self.previous_action, self.get_reward(turn))
        self.previous_action = action
        self.previous_state = state
        self.previous_q_value = q_value
        self.previous_opp_hero_hp = self.opponent.hero.health
        self.previous_my_hero_hp = self.hero.health
        return turn
    
    def get_reward(self, turn):
        if (turn == []):
            result = (self.used_mana/self.max_mana)*30
        else:
            result = 0
        result = result + ((self.previous_opp_hero_hp - self.opponent.hero.health)*10)
        result = result + ((self.opponent.hero.health - self.previous_my_hero_hp)*1)
        return result
    
    def get_state(self):
        state = []
        #cards in hand
        
        return state
    
    def get_int_from_bool(self, boolean_value):
        if (boolean_value):
            return 1
        else:
            return 0
    
    def get_best_action(self, state):
        action = self.get_action(None, None)
        q_max = self.neural_network.activate(state + action)
        best_turn = []
        for card in self.hand:
            if (card.is_playable()):
                if (card.has_target()):
                    for target in card.targets:
                        action = self.get_action(card, target)
                        q_candidate = self.neural_network.activate(state + action)
                        if (q_candidate > q_max):
                            q_max = q_candidate
                            if card.choose_cards:
                                card = random.choice(card.choose_cards)
                            best_turn = get_turn_item_play_card(card,target)
                else:
                    action = self.get_action(card, None)
                    q_candidate = self.neural_network.activate(state + action)
                    if (q_candidate > q_max):
                        q_max = q_candidate
                        if card.choose_cards:
                            card = random.choice(card.choose_cards)
                        best_turn = get_turn_item_play_card(card,None)
                
        if (self.hero.power.is_usable()):
            if (self.hero.power.has_target()):
                for target in self.hero.power.targets:
                    action = self.get_action(self.hero.power, target)
                    q_candidate = self.neural_network.activate(state + action)
                    if (q_candidate > q_max):
                        q_max = q_candidate
                        best_turn = get_turn_item_hero_power(self.hero.power,target)
            else:
                action = self.get_action(self.hero.power, None)
                q_candidate = self.neural_network.activate(state + action)
                if (q_candidate > q_max):
                    q_max = q_candidate
                    best_turn = get_turn_item_hero_power(self.hero.power,None)
        
        for character in self.characters:
            for target in character.targets:
                if (character.can_attack(target)):
                    action = self.get_action(character, target)
                    q_candidate = self.neural_network.activate(state + action)
                    if (q_candidate > q_max):
                        q_max = q_candidate
                        best_turn = get_turn_item_attack(character,target)
             
        return [best_turn,q_max, action]
    
    def get_action(self, my_entity, target_character):
        action = [0] * (1 + 50 + 5 + 5 + 5 + 1)
        if (my_entity == None and target_character == None):
            return action
        elif (my_entity in self.hand):
            # playing a card
            cost = my_entity.cost + 1
            if (not(my_entity in self.original_deck)):
                # unknown card - probably The Coin
                action[0] = 1
            else:
                if (target_character == None):
                    # no target
                    action[cost] = 1
                elif (target_character.__class__ is Minion):
                    #targetting a minion
                    if (target_character.controller == self):
                        # targetting own minion
                        action[cost + 10] = 1
                    else:
                        # targetting enemy minion
                        action[cost + 20] = 1
                elif (target_character.__class__ is Hero):
                    if (target_character.controller == self):
                        # targetting own hero
                        action[cost + 30] = 1
                    else:
                        # targetting enemy hero
                        action[cost + 40] = 1
        elif (my_entity.__class__ is Minion):
            
            if (target_character.__class__ is Hero):
                # attacking a hero
                action[6] = 1
            elif (target_character.__class__ is Minion):
                # attacking a minion
                if (target_character.atk >= my_entity.health and not(my_entity.divine_shield)):
                    # my character is going to die
                    if (target_character.health < my_entity.atk and not(target_character.divine_shield)):
                        # both characters are going to die
                        action[7] = 1
                    else:
                        # I am going to lose character, my opponent is not
                        action[8] = 1
                else:
                    # my character is going to survive
                    if (target_character.health < my_entity.atk and not(target_character.divine_shield)):
                        # My opponent is going to lose character but not me
                        action[9] = 1
                    else:
                        # Both character are going to survive
                        action[10] = 1
        elif (my_entity.__class__ is Hero):
            if  (target_character.__class__ is Hero):
                # attacking a hero
                action[11] = 1
            elif (target_character.__class__ is Minion):
                # attacking a minion
                if (target_character.atk >= my_entity.health):
                    # my hero is going to die
                    if (target_character.health < my_entity.atk and not(target_character.divine_shield)):
                        # both my hero and the target are going to die
                        action[12] = 1
                    else:
                        # my hero is going to die, the target is not
                        action[13] = 1
                else:
                    # my hero is going to survive
                    if (target_character.health < my_entity.atk and not(target_character.divine_shield)):
                        # My opponent is going to lose character but not me
                        action[14] = 1
                    else:
                        # Both character are going to survive
                        action[15] = 1
        
        elif (my_entity.__class__ is HeroPower):
            if (target_character == None):
                # no target
                action[16] = 1
            elif (target_character.__class__ is Hero):
                # target is Hero
                if (target_character.controller == self):
                    # targetting my hero
                    action[17] = 1
                else:
                    #targetting opp hero
                    action[18] = 1
            elif (target_character.__class__ is Minion):
                if (target_character.controller == self):
                    # targetting my hero
                    action[19] = 1
                else:
                    #targetting opp hero
                    action[20] = 1
        else:
            # only unexpected actions
            print ("Unexpected action. MY_ENTITY: " + str(my_entity) + " TARGET: " + str(target_character))
            action[21] = 1
        return action
            
    
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
    
    def update_neural_network(self, old_state, old_value, new_state,action, reward):
       desired_value = old_value + self.learning_rate * (reward + self.discount_factor * self.get_best_action(new_state)[1] - old_value)
       ds = SupervisedDataSet(self.states_and_actions_num,1)
       ds.addSample(old_state + action, desired_value)
       trainer = BackpropTrainer(self.neural_network,ds)
       trainer.train()
       
        
        
        
        