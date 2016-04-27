import random
import pybrain
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from AI.utils import *
from fireplace.utils import *
from pybrain.datasets.supervised import SupervisedDataSet
from pybrain.tools.customxml import NetworkWriter
from pybrain.tools.customxml import NetworkReader

class Q_learner(Player):
    
    ''' Current version of the bot. Should be updated after significant changes. '''
    version = 1
    
    ''' It is useful to store original deck here. It is needed for replays. '''
    original_deck = []
    
    ''' Name of the file containing deck. The file must be located in HearthstoneAI\AI\decks '''
    deck_id = None
    
    neural_network = None
    learning_rate = 0.9
    discount_factor = 0.9
    states_and_actions_num = 77 + 31 + 1 + 64
    previous_q_value = None
    previous_action = None
    previous_state = None
    previous_opp_hero_hp = 30
    
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
        super(Q_learner, self).__init__(name, self.original_deck, hero)
    
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
        self.previous_opp_hero_hp = self.opponent.hero.health;
        return turn
    
    def get_reward(self, turn):
        if (turn == [] and has_playable_card_of_max_cost(self,self.mana)):
            return -10
        result = (self.used_mana/self.max_mana)*300
        result = result + ((self.previous_opp_hero_hp - self.opponent.hero.health)*10)
        return result
    
    def get_state(self):
        state = []
        #cards in hand
        sorted_hand = sorted(self.hand,key=lambda card: card.entity_id)
        for card in sorted_hand:
            state.append(card.entity_id)
        while (len(state) < 10):
            state.append(-1)
        #my hero
        state.append(self.hero.health)
        state.append(self.hero.atk)
        #my minions
        for minion in self.field:
            state.append(minion.entity_id)
            state.append(minion.health)
            state.append(minion.atk)
            state.append(self.get_int_from_bool(minion.taunt))
            state.append(self.get_int_from_bool(minion.divine_shield))
        while(len(state) < 47):
            state.append(-1)
        #enemy hero
        state.append(self.opponent.hero.health)
        state.append(self.opponent.hero.atk)
        #enemy minions
        for minion in self.opponent.field:
            state.append(minion.health)
            state.append(minion.atk)
            state.append(self.get_int_from_bool(minion.taunt))
            state.append(self.get_int_from_bool(minion.divine_shield))
        while(len(state) < 77):
            state.append(-1)
        return state
    
    def get_int_from_bool(self, boolean_value):
        if (boolean_value):
            return 1
        else:
            return 0
    
    def get_best_action(self, state):
        action = [-1] * (31 + 1 + 64)
        q_max = self.neural_network.activate(state + action)
        best_turn = []
        for card in self.hand:
            if (card.is_playable()):
                if (card in self.original_deck):
                    index = self.original_deck.index(card)
                else:
                    index = 30
                action[index] = 1
                q_candidate = self.neural_network.activate(state + action)
                if (q_candidate > q_max):
                    q_max = q_candidate
                    if card.choose_cards:
                        card = random.choice(card.choose_cards)
                    target = self.get_best_target(card)
                    best_turn = get_turn_item_play_card(card,target)
                action[index] = -1
                
        if (self.hero.power.is_usable()):
            action[31] = 1
            q_candidate = self.neural_network.activate(state + action)
            if (q_candidate > q_max):
                    q_max = q_candidate
                    target = self.get_best_target(self.hero.power)
                    best_turn = get_turn_item_hero_power(self.hero.power,target)
            action[31] = -1
        
        for character in self.characters:
            if (character.__class__ is Hero):
                index1 = 8
            else:
                index1 = self.field.index(character) + 1
            for target in character.targets:
                if (character.can_attack(target)):
                    if (target.__class__ is Hero):
                        index2 = 8
                    else:
                        index2 = self.opponent.field.index(target) + 1
                    index = 31 + index1 * index2 
                    action[index] = 1
                    q_candidate = self.neural_network.activate(state + action)
                    if (q_candidate > q_max):
                        q_max = q_candidate
                        best_turn = get_turn_item_attack(character,target)
                    action[index] = -1
             
        return [best_turn,q_max, action]
    
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
       
        
        
        
        