#!/usr/bin/env python

global __last_turn__
import sys; sys.path.append("..")
import random
import zipfile
import os
import csv
from replays.replays import *
from fireplace.cards.heroes import *
from fireplace.exceptions import GameOver
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import *
from hearthstone.enums import Zone, Rarity
from fireplace.dsl.selector import CURRENT_HEALTH, FRIENDLY_HERO, ENEMY_MINIONS,\
    FRIENDLY_MINIONS, CONTROLLED_BY, Selector, IN_HAND
from behaviors.face_hunter import *
from behaviors.random import *
from fireplace.card import Spell, Secret, Weapon, HeroPower
from _datetime import date, datetime

''' !!! CHOOSE PLAYERS !!! '''
player1 = Face_hunter("Player1")
player2 = Random("Player2", WARLOCK)


# leave unchanged
REPLAY_JSON_PATH = 'replay.json'

def play_full_game(json, game, csv_writer):
    global __last_turn__
    global path_to_text_output
    global player1
    global player2
    
    for player in game.players:
#        print("Can mulligan %r" % (player.choice.cards))
        mull_count = random.randint(0, len(player.choice.cards))
        cards_to_mulligan = random.sample(player.choice.cards, mull_count)
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
            if (turn_type == 0):
                "Play card"
                card = turn[1]
                target = turn[2]
                __last_turn__ = [card,target,turn_type]
                if card.choose_cards:
                    card = random.choice(card.choose_cards)
                else:
                    if (target != None):
                        card.play(target=target)
                    else:
                        card.play()    
                hashmap = get_hash_map(game, player1, player2, turn_type, card.entity_id, None, None, card)
                json.append(hashmap)
                   
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
                    hashmap = get_hash_map(game, player1, player2, turn_type, hero_power.entity_id, None, None, hero_power)
                else:
                    hashmap = get_hash_map(game, player1, player2, turn_type, hero_power.entity_id, None, None, hero_power)
                json.append(hashmap)
            else:
                "Attack"
                attacker = turn[1]
                defender = turn[2]
                __last_turn__ = [attacker,defender,turn_type]
                attacker.attack(defender)
                hashmap = get_hash_map(game, player1, player2, turn_type, attacker.entity_id, attacker.entity_id, defender.entity_id, None)
                json.append(hashmap)
                
            "next players turn according to selected behavior"
            turn = player.get_next_turn(game)

        game.end_turn()
    
def test_full_game():
    global __last_turn__
    global player1
    global player2
    
    __last_turn__ = [None,None,None]
    try:
        my_datetime = datetime.now()
        path_to_dir = os.path.dirname(os.getcwd()) + "\\game_results\\game"  + my_datetime.strftime("_%d_%B_%Y__%H_%M\\")
        if not os.path.exists(path_to_dir):
            os.makedirs(path_to_dir)
        json = []
        
        path_to_csv = path_to_dir + my_datetime.strftime("%d_%B_%Y__%H_%M.csv")
        csv_file = open(path_to_csv,"w")
        fieldnames = get_field_names()
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader() 
        
        path_to_deck1 = path_to_dir + type(player1).__name__ + "_" + my_datetime.strftime("%d_%B_%Y__%H_%M.hsdeck.txt")
        deck1_file = open(path_to_deck1,"w")
        log_deck(deck1_file, player1)
        
        path_to_deck2 = path_to_dir + type(player2).__name__ + "_" + my_datetime.strftime("%d_%B_%Y__%H_%M.hsdeck.txt")
        deck2_file = open(path_to_deck2,"w")
        log_deck(deck2_file, player2) 
            
        game = Game(players=(player1, player2))
        game.start()
        
        play_full_game(json, game, csv_writer)
    except GameOver:
        #LAST TURN
        if (__last_turn__[1] != None):
            hashmap = get_hash_map(game, player1, player2, __last_turn__[2], __last_turn__[0].entity_id,__last_turn__[0].entity_id, __last_turn__[1].entity_id, __last_turn__[0])
            json.append(hashmap)
        else:
            hashmap = get_hash_map(game, player1, player2, __last_turn__[2], __last_turn__[0].entity_id,__last_turn__[0].entity_id, None, __last_turn__[0])
            json.append(hashmap)
        
        #RESULT
        if (game.current_player.hero.health < 1):
            hashmap = get_hash_map(game, player1, player2, 21, game.current_player.hero.entity_id, None, None, None)
            json.append(hashmap)
        else:
            hashmap = get_hash_map(game, player1, player2, 20, game.current_player.hero.entity_id, None, None, None)
            json.append(hashmap)
        
        f = open(REPLAY_JSON_PATH, 'w')
        write_line_to_file(f,json.__str__())
        path_to_replay = path_to_dir + my_datetime.strftime("%d_%B_%Y__%H_%M.hdtreplay")
        my_zip_file = zipfile.ZipFile(path_to_replay, mode='w')
        my_zip_file.write(REPLAY_JSON_PATH)
        f.close()
        my_zip_file.close()

def main():
    if len(sys.argv) > 1:
        numgames = sys.argv[1]
        if not numgames.isdigit():
            sys.stderr.write("Usage: %s [NUMGAMES]\n" % (sys.argv[0]))
            exit(1)
        for i in range(int(numgames)):
            test_full_game()
    else:
        test_full_game()


if __name__ == "__main__":
    main()


