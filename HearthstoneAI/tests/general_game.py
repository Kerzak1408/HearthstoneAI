#!/usr/bin/env python
import numpy

global __last_turn__
import pickle
import sys, inspect; sys.path.append("..")
import random
import zipfile
import os
import csv
import json
import sys; sys.path.append("..")
from fireplace import cards
from fireplace.exceptions import GameOver
from fireplace.utils import play_full_game
from os.path import dirname, basename, isfile
from replays.replays import *
from fireplace.cards.heroes import *
from fireplace.exceptions import GameOver
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import *
from hearthstone.enums import Zone, Rarity
from fireplace.dsl.selector import CURRENT_HEALTH, FRIENDLY_HERO, ENEMY_MINIONS,\
    FRIENDLY_MINIONS, CONTROLLED_BY, Selector, IN_HAND
from AI.bots import *
from AI.bots.q_learner import *
from AI.bots.q_learner_super_makro import *
from AI.bots.q_learner_super_makro_alt import *
from AI.bots.q_learner_table import *
from AI.bots.q_learner_table_08 import *
from AI.bots.q_learner_table_win import *
from fireplace.card import Spell, Secret, Weapon, HeroPower
from _datetime import date, datetime
# from pybrain.tools.customxml import NetworkWriter
# from pybrain.tools.customxml import NetworkReader

''' Following attributes will only be applied if no command prompt arguments were given. '''
''' !!! AIs to be used !!! '''
AI_1_ID = "Face_hunter"
AI_2_ID = "Random_bot"
''' !!! Decks !!! '''
DECK_1_ID = "hunter_face"
DECK_2_ID = "hunter_face"
''' !!! Number of games to be simulated. !!! '''
NUM_GAMES = 1
''' Whether to clear result file before the first simulation. '''
CLEAR_RESULTS = False

path_to_result = os.path.join(os.path.dirname(os.getcwd()),"game_results","results_summary.csv")

player1 = None
player2 = None

neural_net = None
table = None

# leave unchanged
REPLAY_JSON_PATH = 'replay.json'

def play_full_game(my_json, game, csv_writer):
    global __last_turn__
    global path_to_text_output
    global player1
    global player2
    
    for player in game.players:
#        print("Can mulligan %r" % (player.choice.cards))
        cards_to_mulligan = player.get_mulligans(player.choice.cards)
        player.choice.choose(*cards_to_mulligan)

    while True:
        player = game.current_player
        
        turn = player.get_next_turn(game)
        """
        Choose next action to do.
        Action patterns:
        Play card: [0, card, target]
           Attack: [9, attacker, defender]
        Hero Pow.: [19, hero_power, target]
         End Turn: []
        """
        while (turn != []):
            
            game_state = get_game_state(game)
            csv_writer.writerow(game_state)
            
            turn_type = turn[0]
            if (turn_type == 0 or turn_type == 16):
                "Play card"
                card = turn[1]
                target = turn[2]
                if (card.name == "Abusive Sergeant" and target == None):
                    print(card.name)
                    print(card.targets)
                    print(player.field)
                    print(player.opponent.field)
                __last_turn__ = [card,target,turn_type]
                if card.choose_cards:
                    card = random.choice(card.choose_cards)
                else:
                    if (target != None):
                        card.play(target=target)
                        hashmap = get_hash_map(game, player1, player2, turn_type, card.entity_id, card, target, card)
                        my_json.append(hashmap)
                    else:
                        card.play()
                        hashmap = get_hash_map(game, player1, player2, turn_type, card.entity_id, None, None, card)
                        my_json.append(hashmap)    
                
                   
            elif (turn_type == 19):
                "Hero Power"
                hero_power = turn[1]
                target = turn[2]
                __last_turn__ = [hero_power,target,turn_type]
                if player.hero.power.has_target():
                    player.hero.power.use(target)
                else:
                    player.hero.power.use()
                if (target != None):
                    hashmap = get_hash_map(game, player1, player2, turn_type, hero_power.entity_id, hero_power, target, hero_power)
                else:
                    hashmap = get_hash_map(game, player1, player2, turn_type, hero_power.entity_id, None, None, hero_power)
                my_json.append(hashmap)
            else:
                "Attack"
                attacker = turn[1]
                defender = turn[2]
                __last_turn__ = [attacker,defender,turn_type]
                attacker.attack(defender)
                hashmap = get_hash_map(game, player1, player2, turn_type, attacker.entity_id, attacker, defender, None)
                my_json.append(hashmap)
                
            "next players turn according to selected behavior"
            turn = player.get_next_turn(game)

        game.end_turn()
    
def test_full_game(ai_1_id, deck_1_id, ai_2_id, deck_2_id, clear_results):
    global __last_turn__
    global player1
    global player2
    global my_json
    global neural_net
    global table
    
    player1 = get_instance_by_name(ai_1_id, deck_1_id)
    player2 = get_instance_by_name(ai_2_id, deck_2_id)
    __last_turn__ = [None,None,None]
    
    attributes = get_attributes()
    my_datetime = datetime.now()
    game_id = player1.get_id() + "-" + deck_1_id + "-" +player2.get_id() + "-" + deck_2_id + "-" + my_datetime.strftime("%Y_%m_%d") + "-" + str(attributes["NumGame"]).zfill(7)
    
    try:
        path_to_dir = os.path.dirname(os.getcwd()) + "\\game_results\\" + game_id + "\\"
        if not os.path.exists(path_to_dir):
            os.makedirs(path_to_dir)
        my_json = []
        
        path_to_csv = path_to_dir + game_id + ".csv"
        csv_file = open(path_to_csv,"w")
        fieldnames = get_field_names()
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader() 
        
#        path_to_deck1 = path_to_dir + type(player1).__name__ + "_" + my_datetime.strftime("%d_%B_%Y__%H_%M.hsdeck.txt")
#        deck1_file = open(path_to_deck1,"w")
#        log_deck(deck1_file, player1)
        
#        path_to_deck2 = path_to_dir + type(player2).__name__ + "_" + my_datetime.strftime("%d_%B_%Y__%H_%M.hsdeck.txt")
#        deck2_file = open(path_to_deck2,"w")
#        log_deck(deck2_file, player2) 
            
        game = Game(players=(player1, player2))
        game.start()
        
        play_full_game(my_json, game, csv_writer)
        
    except GameOver:
        win_reward = 0
#         if (player1.__class__ is Q_learner_super_makro or player1.__class__ is Q_learner_super_makro_alt):
#             if (player1.hero.health > 0):
#                 reward = win_reward
#             else:
#                 reward = 0
#             player1.update_neural_network(player1.previous_state, player1.previous_q_value, player1.get_state(), player1.previous_action, reward)
#             net = player1.neural_network
# #            path = os.path.join(os.path.dirname(os.getcwd()), 'network.xml')
# #            NetworkWriter.writeToFile(net, path)
#             neural_net = net
#             
#         if (player2.__class__ is Q_learner_super_makro or player2.__class__ is Q_learner_super_makro_alt):
#             if (player2.hero.health > 0):
#                 reward = win_reward
#             else:
#                 reward = 0
#             player2.update_neural_network(player2.previous_state, player2.previous_q_value, player2.get_state(), player2.previous_action, reward)
#             net = player2.neural_network
# #            path = os.path.join(os.path.dirname(os.getcwd()), 'network.xml')
# #            NetworkWriter.writeToFile(net, path)
#             neural_net = net
            
        if (player1.__class__ is Q_learner_table or player1.__class__ is Q_learner_table_08 or player1.__class__ is Q_learner_table_win):
            if (player1.hero.health > 0):
                reward = 0
            else:
                reward = 0
            player1.update_table(player1.previous_state, player1.get_state(), player1.previous_action, reward)
            table = player1.table
            
        if (player2.__class__ is Q_learner_table or player2.__class__ is Q_learner_table_08 or player2.__class__ is Q_learner_table_win):
            if (player2.hero.health > 0):
                reward = 0
            else:
                reward = 0
            player2.update_table(player2.previous_state, player2.get_state(), player2.previous_action, reward)
            table = player2.table
            
        #LAST TURN
        if (__last_turn__[1] != None):
            hashmap = get_hash_map(game, player1, player2, __last_turn__[2], __last_turn__[0].entity_id,__last_turn__[0], __last_turn__[1], __last_turn__[0])
            my_json.append(hashmap)
        else:
            hashmap = get_hash_map(game, player1, player2, __last_turn__[2], __last_turn__[0].entity_id,__last_turn__[0], None, __last_turn__[0])
            my_json.append(hashmap)
        
        #RESULT
        if (game.current_player.hero.health < 1):
            hashmap = get_hash_map(game, player1, player2, 21, game.current_player.hero.entity_id, None, None, None)
            my_json.append(hashmap)
        else:
            hashmap = get_hash_map(game, player1, player2, 20, game.current_player.hero.entity_id, None, None, None)
            my_json.append(hashmap)
        
        f = open(REPLAY_JSON_PATH, 'w')
        write_line_to_file(f,my_json.__str__())
        path_to_replay = path_to_dir + game_id + ".hdtreplay"
        my_zip_file = zipfile.ZipFile(path_to_replay, mode='w')
        my_zip_file.write(REPLAY_JSON_PATH)
        
        
       
        if (clear_results):
            csv_result_file = open(path_to_result,"w")
            csv_writer = csv.DictWriter(csv_result_file, fieldnames=get_field_names_of_result())
            csv_writer.writeheader()
        else:
            csv_result_file = open(path_to_result,"a")
            csv_writer = csv.DictWriter(csv_result_file, fieldnames=get_field_names_of_result())
        csv_writer.writerow(get_result_of_game(game))
        csv_result_file.close()
        f.close()
        my_zip_file.close()
        
        set_attributes(attributes)
    except:
        print ("UNEXPECTED ERROR:", sys.exc_info())
'''
Returns json that is used for storing result attributes- date, num of games today, num of random decks...
If date isn t equal to the current date, change it and set attributes to default values.
'''
def get_attributes():
    path_to_attributes = os.path.join(os.path.dirname(os.getcwd()), 'attributes.json')
    print(path_to_attributes)
    attributes_file = open(path_to_attributes)
    result = json.load(attributes_file)
    attributes_file.close()
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y_%m_%d")
    attributes_date = result["Date"]
    if (current_date != attributes_date):
        for key in result:
            result[key] = 1
        result["Date"] = current_date
    return result
'''
Writes json_content into attributes.json file
'''
def set_attributes(json_content):
    json_content["NumGame"] = json_content["NumGame"] + 1
    
    path_to_attributes = os.path.join(os.path.dirname(os.getcwd()), 'attributes.json')
    attributes_file = open(path_to_attributes,'w')
    attributes_file.write(json.dumps(json_content))
    attributes_file.close()

''' Returns an instance of the AI specified by its id and id of the deck used. '''
def get_instance_by_name(ai_id, deck_id):
    global neural_net
    result = None
    for module_name in globals():
        module = globals()[module_name]
        if (inspect.ismodule(module)):
            module_path = module.__name__
            splitted_path = module_path.split(".")
            if (len(splitted_path) > 1 and splitted_path[0] == "AI" and splitted_path[1] == "bots"):
                for (class_name,class_dynamic) in inspect.getmembers(module):
                    if (class_name == ai_id):
                        if (class_name == "Q_learner" or class_name == "Q_learner_makro" or class_name == "Q_learner_super_makro"
                            or class_name == "Q_learner_value" or class_name == "Q_learner_super_makro_alt"):
                            result = class_dynamic(ai_id, deck_id, neural_net)
                        elif (class_name == "Q_learner_table" or class_name == "Q_learner_table_08" or class_name == "Q_learner_table_win"):
                            result = class_dynamic(ai_id, deck_id, table)
                        else:
                            result = class_dynamic(ai_id, deck_id)
    return result

def main():
    global player1
    global player2
    
    global AI_1_ID
    global DECK_1_ID
    global AI_2_ID
    global DECK_2_ID
    global NUM_GAMES
    global CLEAR_RESULTS
    global path_to_result
    global neural_net
    
    switch = False
    
    ai_1_id = AI_1_ID
    deck_1_id = DECK_1_ID
    ai_2_id = AI_2_ID
    deck_2_id = DECK_2_ID
    numgames = NUM_GAMES
    clear_results = CLEAR_RESULTS
    
    if (len(sys.argv) > 5):
        ''' Number of games to be simulated '''
        ai_1_id = sys.argv[1]
        deck_1_id = sys.argv[2]
        ai_2_id = sys.argv[3]
        deck_2_id = sys.argv[4]
        numgames = sys.argv[5]
        
        if (ai_2_id == "switch"):
            switch = True
            
    if (len(sys.argv) > 6):
        sixth_arg = sys.argv[6]
        if (sixth_arg == "T"):
            clear_results = True
        elif (sixth_arg == "O"):
            clear_results = True
            path_to_result = os.path.join(os.path.dirname(os.getcwd()),'game_results',ai_1_id + '(' + deck_1_id
                                          + ')_' + ai_2_id + '(' + deck_2_id + ').csv')
        else:
            clear_results = True
            path_to_result = os.path.join(os.path.dirname(os.getcwd()),'game_results',sixth_arg)

    if (len(sys.argv) <= 5):
        print("!!! WARNING: Wrong number of arguments. Default values were used. !!!")

    if not numgames.isdigit():
            sys.stderr.write("Usage: %s [NUMGAMES]\n" % (sys.argv[0]))
            exit(1)
    for i in range(int(numgames)):
            if (switch):
                if (i % 3 == 0):
                    ai_2_id = "Face_hunter"
                    deck_2_id = "hunter_face"
                elif (i % 3 == 1):
                    ai_2_id = "Secret_paladin"
                    deck_2_id = "paladin_secret"
                else:
                    ai_2_id = "Malygos_freeze_mage"
                    deck_2_id = "mage_malygos_freeze"
            if (i == 0):
                test_full_game(ai_1_id,deck_1_id,ai_2_id,deck_2_id, clear_results)
            else:
                test_full_game(ai_1_id,deck_1_id,ai_2_id,deck_2_id, False)
    
    os.path.join(os.getcwd())
    
#     if (player1.__class__ is Q_learner_super_makro or player1.__class__ is Q_learner):
#         net = player1.neural_network
#         path = os.path.join(os.path.dirname(os.getcwd()), 'network.xml')
#         NetworkWriter.writeToFile(net, path)
#         neural_net = net
# 
#     if (player2.__class__ is Q_learner_super_makro or player2.__class__ is Q_learner):
#         net = player2.neural_network
#         path = os.path.join(os.path.dirname(os.getcwd()), 'network.xml')
#         NetworkWriter.writeToFile(net, path)
#         neural_net = net
        
#     if (player1.__class__ is Q_learner_super_makro_alt):
#         net = player1.neural_network
#         path = os.path.join(os.path.dirname(os.getcwd()), 'network_alt.xml')
#         NetworkWriter.writeToFile(net, path)
#         neural_net = net
# 
#     if (player2.__class__ is Q_learner_super_makro_alt):
#         net = player2.neural_network
#         path = os.path.join(os.path.dirname(os.getcwd()), 'network_alt.xml')
#         NetworkWriter.writeToFile(net, path)
#         neural_net = net
        
    if (player1.__class__ is Q_learner_table or player1.__class__ is Q_learner_table_08 or player1.__class__ is Q_learner_table_win):
        table = player1.table
        path = os.path.join(os.path.dirname(os.getcwd()), 'table.txt')
        numpy.save(path, table)
        
    if (player2.__class__ is Q_learner_table or player2.__class__ is Q_learner_table_08 or player2.__class__ is Q_learner_table_win):
        table = player2.table
        path = os.path.join(os.path.dirname(os.getcwd()), 'table.txt')
        numpy.save(path, table)
        
if __name__ == "__main__":
    main()


