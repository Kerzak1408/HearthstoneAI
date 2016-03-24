#!/usr/bin/env python

global __last_turn__
import sys; sys.path.append("..")
import random
import zipfile
from replays.replays import *
from fireplace.cards.heroes import *
from fireplace.exceptions import GameOver
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import *
from hearthstone.enums import Zone, Rarity
from fireplace.dsl.selector import CURRENT_HEALTH, FRIENDLY_HERO, ENEMY_MINIONS,\
    FRIENDLY_MINIONS, CONTROLLED_BY, Selector, IN_HAND
from behaviors.malygos_mage import *
from fireplace.card import Spell, Secret, Weapon, HeroPower
from _datetime import date, datetime

REPLAY_JSON_PATH = 'replay.json'

def play_full_game(json, game, player1, player2):
    global __last_turn__
    f1 = open('C:\\Users\\Lubko\\OneDrive\\Documents\\matfyz\\bakalarka\\Hearthstone-Deck-Tracker-master\\Hearthstone Deck Tracker\\obj\\Debug\\Replay\\Replays\\log.txt', 'w')

    for player in game.players:
#        print("Can mulligan %r" % (player.choice.cards))
        mull_count = random.randint(0, len(player.choice.cards))
        cards_to_mulligan = random.sample(player.choice.cards, mull_count)
        player.choice.choose(*cards_to_mulligan)

    while True:
        player = game.current_player

        if (player1 == player):
            
            ctp = get_cards_to_play(game, player1, player2)
            
            # iterate over our hand and play whatever is playable
            for [card,target] in ctp:
                __last_turn__ = [card,target,0]
                if card.is_playable():
                    if card.choose_cards:
                        card = random.choice(card.choose_cards)
#                    print("Playing %r on %r" % (card, target))
                    if (player.hero.power == card and player.hero.power.is_usable()):
                        if player.hero.power.has_target():
                            player.hero.power.use(target=random.choice(player.hero.power.targets))
                        else:
                            player.hero.power.use()
                        hashmap = get_hash_map(game, player1, player2, 19, card.entity_id, None, None, card)
                        json.append(hashmap)
                    else:
                        card.play(target=target)
                        hashmap = get_hash_map(game, player1, player2, 0, card.entity_id, None, None, card)
                        json.append(hashmap)
                    continue
                
            # Randomly attack with whatever can attack
            for character in player.characters:
                if character.can_attack(target = player2.hero):
                    __last_turn__ = [character,player2.hero, 9]
                    character.attack(player2.hero)
                    hashmap = get_hash_map(game, player1, player2, 9, character.entity_id, character.entity_id, player2.hero.entity_id, None)
                    json.append(hashmap)
                    continue
                else:
                    if character.can_attack():
                        target = random.choice(character.targets)
                        __last_turn__ = [character, target, 9]
                        character.attack(target)
                        hashmap = get_hash_map(game, player1, player2, 9, character.entity_id, character.entity_id, player2.hero.entity_id, None)
                        json.append(hashmap)
                        continue
                
            if player.choice:
                choice = random.choice(player.choice.cards)
#                print("Choosing card %r" % (choice))
                player.choice.choose(choice)
                continue
            
        else:
            heropower = player.hero.power
            if heropower.is_usable() and random.random() < 0.1:
                if heropower.has_target():
                    heropower.use(target=random.choice(heropower.targets))
                else:
                    heropower.use()
                hashmap = get_hash_map(game, player1, player2, 19, heropower.entity_id, None, None, heropower)
                json.append(hashmap)
                continue
    
            # iterate over our hand and play whatever is playable
            for card in player.hand:
                if card.is_playable() and random.random() < 0.5:
                    target = None
                    if card.choose_cards:
                        card = random.choice(card.choose_cards)
                    if card.has_target():
                        target = random.choice(card.targets)
#                    print("Playing %r on %r" % (card, target))
                    card.play(target=target)
                    hashmap = get_hash_map(game, player1, player2, 0, card.entity_id, None, None, card)
                    json.append(hashmap)
                    continue
    
            # Randomly attack with whatever can attack
            for character in player.characters:
                if character.can_attack():
                    target = random.choice(character.targets)
                    character.attack(target)
                    hashmap = get_hash_map(game, player1, player2, 9, character.entity_id, character.entity_id, target.entity_id, None)
                    json.append(hashmap)
                continue
    
            if player.choice:
                choice = random.choice(player.choice.cards)
#                print("Choosing card %r" % (choice))
                player.choice.choose(choice)
                continue
    
        game.end_turn()

def write_line_to_file(file, line):
    file.write(line + "\n")
    

def test_full_game():
    global __last_turn__
    __last_turn__ = [None,None,None]
    try:
        json = []
        
        deck1 = get_face_hunter_deck()
        deck2 = random_draft(hero=WARRIOR)
        player1 = Player("Player1", deck1, HUNTER)
        player2 = Player("Player2", deck2, WARRIOR)

        game = Game(players=(player1, player2))
        game.start()
        play_full_game(json, game, player1, player2)
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
        my_datetime = datetime.now()
        path_to_zip = "C:\\Users\\Lubko\\OneDrive\\Documents\\matfyz\\bakalarka\\Hearthstone-Deck-Tracker-master\\Hearthstone Deck Tracker\\obj\\Debug\\Replay\\Replays\\" + my_datetime.strftime("%d_%B_%Y__%H_%M.hdtreplay")
        my_zip_file = zipfile.ZipFile(path_to_zip, mode='w')
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


