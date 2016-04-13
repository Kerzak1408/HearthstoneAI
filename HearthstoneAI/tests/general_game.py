#!/usr/bin/env python

global __last_turn__
import sys, inspect; sys.path.append("..")
import random
import zipfile
import os
import csv
import json
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
from fireplace.card import Spell, Secret, Weapon, HeroPower
from _datetime import date, datetime

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

player1 = None
player2 = None

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
        
        path_to_result = os.path.join(os.path.dirname(os.getcwd()),"game_results","results_summary.csv")
       
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
    result = None
    for module_name in globals():
        module = globals()[module_name]
        if (inspect.ismodule(module)):
            module_path = module.__name__
            splitted_path = module_path.split(".")
            if (len(splitted_path) > 1 and splitted_path[0] == "AI" and splitted_path[1] == "bots"):
                for (class_name,class_dynamic) in inspect.getmembers(module):
                    if (class_name == ai_id):
                        result = class_dynamic(ai_id, deck_id)
    return result

def main():
    global AI_1_ID
    global DECK_1_ID
    global AI_2_ID
    global DECK_2_ID
    global NUM_GAMES
    global CLEAR_RESULTS
    
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
        
    if (len(sys.argv) > 6):
        sixth_arg = sys.argv[6]
        if (sixth_arg == "T"):
            clear_results = True

    if (len(sys.argv) <= 5):
        print("!!! WARNING: Wrong number of arguments. Default values were used. !!!")

    if not numgames.isdigit():
            sys.stderr.write("Usage: %s [NUMGAMES]\n" % (sys.argv[0]))
            exit(1)
    for i in range(int(numgames)):
            if (i == 0):
                test_full_game(ai_1_id,deck_1_id,ai_2_id,deck_2_id, clear_results)
            else:
                test_full_game(ai_1_id,deck_1_id,ai_2_id,deck_2_id, False)
            
if __name__ == "__main__":
    main()


