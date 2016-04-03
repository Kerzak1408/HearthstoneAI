import fireplace.cards
import random
import os
from fireplace.card import Spell
from hearthstone.enums import Race
from fireplace.player import Player
from fireplace.cards.heroes import *

def get_field_names_of_result():
    result = []
    result.append("Player_1_id")
    result.append("Player_1_deck_id")
    result.append("Player_1_final_hp")
    result.append("Player_2_id")
    result.append("Player_2_deck_id")
    result.append("Player_2_final_hp")
    result.append("Final_turn")
    return result
    

def get_result_of_game(game):
    result = {}
    result["Player_1_id"] = game.player1.get_id()
    result["Player_1_deck_id"] = game.player1.get_deck_id()
    result["Player_1_final_hp"] = game.player1.hero.health
    result["Player_2_id"] = game.player2.get_id()
    result["Player_2_deck_id"] = game.player2.get_deck_id()
    result["Player_2_final_hp"] = game.player2.hero.health
    result["Final_turn"] = game.turn
    return result

'''
Returns hero according to deck_id.
(deck_id specifies hero in its composition: HeroName_whatever)
'''
def get_hero(deck_id):
    hero_name = deck_id.split("_")[0]
    
    if (hero_name == "mage"):
        return MAGE
    elif (hero_name == "druid"):
        return DRUID
    elif (hero_name == "rogue"):
        return ROGUE
    elif (hero_name == "shaman"):
        return SHAMAN
    elif (hero_name == "hunter"):
        return HUNTER
    elif (hero_name == "priest"):
        return PRIEST
    elif (hero_name == "paladin"):
        return PALADIN
    elif (hero_name == "warrior"):
        return WARRIOR
    elif (hero_name == "warlock"):
        return WARLOCK
    
    return None

'''
deck_id is the name of the .txt file containing deck. I must be in AI/decks.
The file must consist of 30 lines (each line = card name)
Returns deck by its ID.
'''
def get_deck_by_id(deck_id):
    result = []
    path_to_dir = os.path.dirname(__file__)
    file_name = deck_id + ".txt"
    path_to_deck = os.path.join(path_to_dir, 'decks', file_name)
    card_names = [line.rstrip('\n') for line in open(path_to_deck)]
    for card_name in card_names:
        result.append(fireplace.cards.filter(name = card_name,collectible = True)[0])
    return result
'''
Returns random hero
'''
def get_random_hero():
    hero = None
    random_num = random.random()
    if (random_num < 1/9):
        hero = MAGE
    elif (random_num < 2/9):
        hero = DRUID
    elif (random_num < 2/9):
        hero = ROGUE
    elif (random_num < 2/9):
        hero = SHAMAN
    elif (random_num < 2/9):
        hero = HUNTER
    elif (random_num < 2/9):
        hero = PRIEST
    elif (random_num < 2/9):
        hero = PALADIN
    elif (random_num < 2/9):
        hero = WARRIOR
    else:
        hero = WARLOCK
    return hero

"""
Returns turn item for action 0 = play card
Play card: [0, card, target]
"""
def get_turn_item_play_card(card, target):
    result = [0]
    result.append(card)
    result.append(target)
    print(result)
    return result

"""
Returns turn item for action 19 = hero power use
Hero Power: [19, target]
"""
def get_turn_item_hero_power(hero_power, target):
    result = [19]
    result.append(hero_power)
    result.append(target)
    print(result)
    return result

"""
Returns turn item for action 9 = attack
Attack: [9, attacker, defender]
"""
def get_turn_item_attack(attacker, defender):
    result = [9]
    result.append(attacker)
    result.append(defender)
    print(result)
    return result
    
"""
Return True if there is a beast among cards,
       False otherwise
"""
def has_beast(cards):
    result = False
    for card in cards:
        if (card.data.race == Race.BEAST):
            result = True
    return result

"""
Returns True if player has card with given name,
        False otherwise
"""
def has_specific_card(player, name):
    for card in player.hand:
        if (card.name == name):
            return True
    return False

"""
Returns card with given name.
If player doesn't have such card, returns None.
"""
def get_specific_card(player, name):
    for card in player.hand:
        if (card.name == name):
            return card
    return None

"""
Returns True if player has minion with Taunt in a field,
        False otherwise
"""
def has_taunt_minion(player):
    for minion in player.field:
        if minion.taunt:
             return True
    return False

"""
Returns minion with Taunt from player's minions
or None if player doesn't have such minion
"""
def get_taunt_minion(player):
    for minion in player.field:
        if minion.taunt:
             return minion
    return None

'''
Returns count of taunt minions among minions
'''
def get_taunt_count(minions):
    result = 0
    for minion in minions:
        if (minion.taunt):
            result = result + 1
    return result

"""
Returns cards without first card that costs given amount of mana
"""
def remove_specific_cost_card(cards, cost):
    result = []
    removed = False
    for card in cards:
        if (not(removed) and card.cost == cost):
            removed = True
        else:
            result.append(card)
    return result

"""
Return first card with specific cost,
if there is no such card among cards, returns None.
"""
def get_specific_cost_card(cards, cost):
    for card in cards:
        if (card.cost == cost):
            return card
    return None

"""
Returns True if there is card with specific cost among cards,
        False otherwise.
"""
def has_specific_cost_card(cards, cost):
    for card in cards:
        if (card.cost == cost):
            return True
    return False
  
  
"""
cards - list of cards
returns sum of costs of cards in the list
"""
def get_cards_cost(cards):
    result = 0
    for card in cards:
        #tuple [card, target]
        if (isinstance(card, list)):
            result = result + card[0].cost
        else:
            result = result + card.cost
    return result      
