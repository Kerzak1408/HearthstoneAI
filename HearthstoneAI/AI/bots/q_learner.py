# import random
# import pybrain
# from pybrain.supervised.trainers import BackpropTrainer
# from pybrain.tools.shortcuts import buildNetwork
# from AI.utils import *
# from fireplace.utils import *
# from pybrain.datasets.supervised import SupervisedDataSet
# from pybrain.tools.customxml import NetworkWriter
# from pybrain.tools.customxml import NetworkReader
# from fireplace.card import Minion, HeroPower
#  
# class Q_learner(Player):
#      
#     ''' Current version of the bot. Should be updated after significant changes. '''
#     version = 1
#      
#     ''' It is useful to store original deck here. It is needed for replays. '''
#     original_deck = []
#      
#     ''' Name of the file containing deck. The file must be located in HearthstoneAI\AI\decks '''
#     deck_id = None
#      
#     neural_network = None
#     learning_rate = 0.1
#     discount_factor = 0.01
#     states_and_actions_num = 10 + 49 + 49 + 5 + 5 + 3 + 2 + 5 + 4 + 1 + 31 * 17 + 8 * 17 + 17
#     previous_q_value = None
#     previous_action = None
#     previous_state = None
#     previous_opp_hero_hp = 30
#      
#     sorted_original_deck = None
#      
#     ''' Change Bot_template to your class name '''
#     def __init__(self, name, deck_id, neural_net):
#         if (neural_net == None):
#             path = os.path.join(os.path.dirname(os.getcwd()), 'network.xml')
#             self.neural_network = NetworkReader.readFrom(path)
#         else:
#             self.neural_network = neural_net
#        
#         hero = get_hero(deck_id)
#         self.deck_id = deck_id
#         self.original_deck = get_deck_by_id(deck_id)
#         super(Q_learner, self).__init__(name, self.original_deck, hero)
#      
#     ''' This should return unique id of AI that consists of its name and version'''
#     def get_id(self):
#         return self.__class__.__name__ + "_" +  str(self.version)
#      
#     ''' This should return the original deck, that bot had before the start of game. '''
#     def get_deck(self):
#         return self.original_deck
#      
#     ''' This should return deck_id '''
#     def get_deck_id(self):
#         return self.deck_id
#      
#     '''
#     Choose a list of cards to mulligan.
#     It should return the list of the cards you want to discard.
#     This is called only before the first turn of each game.
#     If you leave it unchanged, it will choose randomly.
#     '''
#     def get_mulligans(self, choice_cards):
#         mull_count = random.randint(0, len(choice_cards))
#         return random.sample(choice_cards, mull_count)
#      
#     """
#     Choose next action to do.
#     Action patterns:
#     Play card: [0, card, target]
#        Attack: [9, attacker, defender]
#     Hero Pow.: [19, target]
#     Spell attack: [16, card, target]
#      End Turn: []
#     """
#     def get_next_turn(self, game):
#         state = self.get_state()
#         [turn, q_value, action] = self.get_best_action(state)
#         if (self.previous_q_value != None):
#             self.update_neural_network(self.previous_state, self.previous_q_value, state, self.previous_action, self.get_reward(turn))
#         self.previous_action = action
#         self.previous_state = state
#         self.previous_q_value = q_value
#         self.previous_opp_hero_hp = self.opponent.hero.health
#         self.previous_opp_hero_armor = self.opponent.hero.armor
#         self.previous_my_hero_hp = self.hero.health
#         self.previous_my_hero_armor = self.hero.armor
#         self.previous_turn = turn
#         self.was_necessary_last = not has_playable_card_of_max_cost(self, self.mana) and not can_any_character_attack_hero(self)
#         return turn
#      
#     def get_reward(self, turn):
#         result = 0
#         if (turn == []):
#             if (not self.was_necessary_last):
#                 result = result - 100
#             else:
#                 result = result + (self.used_mana/self.max_mana) * 10
#         if (turn != [] and turn[0] == 9):
#             if (turn[2].__class__ == Hero or (turn[2].__class__ == Minion and turn[2].taunt)):
#                 result = result + 10  
#             else:
#                 result = result - 10
#         if (turn != [] and turn[0] == 0):
#             result = result + 10
#         opp_hero_damage_done = self.previous_opp_hero_armor + self.previous_opp_hero_hp - self.opponent.hero.health - self.opponent.hero.armor
#         if (opp_hero_damage_done > 0):
#             result = result + 10
#         my_hero_damage_done = self.previous_my_hero_armor + self.previous_my_hero_hp - self.hero.health - self.hero.armor
#         if (my_hero_damage_done > 0):
#             result = result - 10
#         return result
#     def get_state(self):
#         state = []
#         #cards in hand
#         sorted_hand = sorted(self.hand,key=lambda card: card.entity_id)
#         for card in sorted_hand:
#             state.append(card.entity_id)
#         while (len(state) < 10):
#             state.append(-1)
#  
#         #my minions
#         for minion in self.field:
#             state.append(minion.entity_id)
#             state.append(minion.health)
#             state.append(minion.atk)
#             state.append(self.get_int_from_bool(minion.taunt))
#             state.append(self.get_int_from_bool(minion.divine_shield))
#             state.append(self.get_int_from_bool(minion.silenced))
#             state.append(self.get_int_from_bool(minion.can_attack))
#         while(len(state) < 10 + 49):
#             state.append(-1)
#  
#         #enemy minions
#         for minion in self.opponent.field:
#             state.append(minion.health)
#             state.append(minion.atk)
#             state.append(self.get_int_from_bool(minion.taunt))
#             state.append(self.get_int_from_bool(minion.divine_shield))
#             state.append(self.get_int_from_bool(minion.silenced))
#             state.append(self.get_int_from_bool(minion.can_attack))
#         while(len(state) < 10 + 49 + 49):
#             state.append(-1)
#              
#         # my hero
#         state.append(self.hero.entity_id)
#         state.append(self.hero.health)
#         state.append(self.hero.atk)
#         state.append(self.hero.armor)
#         state.append(self.get_int_from_bool(self.hero.can_attack))
#          
#         # opp hero
#         state.append(self.opponent.hero.entity_id)
#         state.append(self.opponent.hero.health)
#         state.append(self.opponent.hero.atk)
#         state.append(self.opponent.hero.armor)
#         state.append(self.get_int_from_bool(self.opponent.hero.can_attack))
#          
#         #my weapon
#         if (self.weapon != None):
#             state.append(self.weapon.entity_id)
#             state.append(self.weapon.atk)
#             state.append(self.weapon.durability)
#         else:
#             while(len(state) < 10 + 49 + 49 + 5 + 5 + 3):
#                 state.append(-1)
#          
#         #opp weapon
#         if (self.opponent.weapon != None):
#             state.append(self.opponent.weapon.atk)
#             state.append(self.opponent.weapon.durability)
#         else:
#             while(len(state) < 10 + 49 +49 + 5 + 5 + 3 + 2):
#                 state.append(-1)
#                  
#         # my secrets
#         sorted_secrets = sorted(self.secrets,key=lambda secret: secret.entity_id)
#         secret_counter = 0
#         for secret in sorted_secrets:
#             if (secret_counter < 5):
#                 state.append(secret.entity_id)
#                 secret_counter = secret_counter + 1
#          
#         while(len(state) < 10 + 49 + 49 + 5 + 5 + 3 + 2 + 5):
#             state.append(-1)
#          
#         # opp secrets
#         state.append(len(self.opponent.secrets))
#          
#         # my current mana
#         state.append(self.mana)
#          
#         # my max mana
#         state.append(self.max_mana)
#          
#         # opp cards count
#         state.append(len(self.opponent.hand))
#         return state
#      
#     def get_int_from_bool(self, boolean_value):
#         if (boolean_value):
#             return 1
#         else:
#             return 0
#      
#     def get_best_action(self, state):
#         best_action = self.get_action(None, None)
#         q_max = self.neural_network.activate(state + best_action)
#         best_turn = []
#         for card in self.hand:
#             if (card.is_playable()):
#                 if (card.has_target()):
#                     for target in card.targets:
#                         action = self.get_action(card, target)
#                         q_candidate = self.neural_network.activate(state + action)
#                         if (q_candidate > q_max):
#                             best_action = action
#                             q_max = q_candidate
#                             if card.choose_cards:
#                                 card = random.choice(card.choose_cards)
#                             best_turn = get_turn_item_play_card(card,target)
#                 else:
#                     action = self.get_action(card, None)
#                     q_candidate = self.neural_network.activate(state + action)
#                     if (q_candidate > q_max):
#                         best_action = action
#                         q_max = q_candidate
#                         if card.choose_cards:
#                             card = random.choice(card.choose_cards)
#                         best_turn = get_turn_item_play_card(card,None)
#                  
#         if (self.hero.power.is_usable()):
#             if (self.hero.power.has_target()):
#                 for target in self.hero.power.targets:
#                     action = self.get_action(self.hero.power, target)
#                     q_candidate = self.neural_network.activate(state + action)
#                     if (q_candidate > q_max):
#                         best_action = action
#                         q_max = q_candidate
#                         best_turn = get_turn_item_hero_power(self.hero.power,target)
#             else:
#                 action = self.get_action(self.hero.power, None)
#                 q_candidate = self.neural_network.activate(state + action)
#                 if (q_candidate > q_max):
#                     best_action = action
#                     q_max = q_candidate
#                     best_turn = get_turn_item_hero_power(self.hero.power,None)
#      
#         for character in self.characters:
#             for target in character.targets:
#                 if (character.can_attack(target)):
#                     action = self.get_action(character, target)
#                     q_candidate = self.neural_network.activate(state + action)
#                     if (q_candidate > q_max):
#                         best_action = action
#                         q_max = q_candidate
#                         best_turn = get_turn_item_attack(character,target)
#               
#         return [best_turn,q_max, best_action]
#      
#     def get_action(self, my_entity, target_character):
#         action = [0] * (1 + 31 * 17 + 8 * 17 + 17)
#         if (my_entity == None and target_character == None):
#             action[0] = 1
#             return action
#         if (my_entity in self.hand):
#             if (not(my_entity in self.original_deck)):
#                 # unknown card - probably The Coin
#                 index_card = 31
#             else:
#                 index_card = self.original_deck.index(my_entity)
#             index_target = self.get_target_index(target_character)
#             index = index_card * 18 + index_target + 1
#             action[index] = 1
#             return action
#         if (my_entity.__class__ is HeroPower):
#             index_hp = 32
#             index_target = self.get_target_index(target_character)
#             index = index_hp * 18 + index_target + 1
#             action[index] = 1
#             return action
#         if (my_entity.__class__ is Hero):
#             index_attacker = 33
#         else:
#             index_attacker = 34 + self.field.index(my_entity)
#         index_target = self.get_target_index(target_character)
#         index = index_attacker * 18 + index_target + 1
#         action[index] = 1
#         return action
#          
#      
#     def get_target_index(self, target):
#         if (target == None):
#             return 0
#         if (target in self.field):
#             return 1 + self.field.index(target)
#         if (target in self.opponent.field):
#             return 1 + 7 + self.opponent.field.index(target)
#         if (target == self.hero):
#             return 1 + 7 + 7 + 1
#         if (target == seld.opponent.hero):
#             return 1 + 7 +7 + 1 + 1
#         return -1
#          
#      
#     def update_neural_network(self, old_state, old_value, new_state,action, reward):
#         real_old_value = self.neural_network.activate(old_state + action)
#         desired_value = real_old_value + self.learning_rate * (reward + self.discount_factor * self.get_best_action(new_state)[1] - real_old_value)
#         ds = self.create_dataset(old_state, action, desired_value)
#         
#         trainer = BackpropTrainer(self.neural_network,ds)
#         print (self.previous_state)
#         print("Prev. TURN: " + str(self.previous_turn))
#         print("OLD?:" + str(old_value))
#         print("OLD: " + str(self.neural_network.activate(old_state + action)))
#         trainer.train()
#         print("NEW: " + str(self.neural_network.activate(old_state + action)))
#         print("DESIRED: " + str(desired_value))
#          
#     def create_dataset(self, state, action, desired_value):
#         ds = SupervisedDataSet(self.states_and_actions_num,1)
#         ds.addSample(state + action, desired_value)
#          
#         return ds
#         
#          
#          
#          
#          