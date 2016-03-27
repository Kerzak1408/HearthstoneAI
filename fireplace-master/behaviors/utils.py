import fireplace.cards
import random
from fireplace.card import Spell
from hearthstone.enums import Race
from fireplace.player import Player


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
