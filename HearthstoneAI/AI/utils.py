import fireplace.cards
import random
import os
from .character_model import *
from fireplace.card import Spell, Hero
from hearthstone.enums import Race
from fireplace.player import Player
from fireplace.cards.heroes import *
from tkinter.tix import INTEGER

def get_valuest_attack(player):
    '''model characters'''
    my_characters = [Character_model(player.hero)]
    opponent_characters = [Character_model(player.opponent.hero)]
    for minion in player.field:
        if (minion.can_attack()):
            ''' [minion, HP, ATK, has_taunt, has_divine_shield, can_attack] '''
            my_characters.append(Character_model(minion))        
    
    for minion in player.opponent.field:
        ''' [minion, HP, ATK, has_taunt, has_divine_shield, can_attack] '''
        opponent_characters.append(Character_model(minion))
    
    targets = get_attackable_characters(opponent_characters)
    
    best_attack = []
    best_score = 0
    for target in targets:
        my_characters = [Character_model(player.hero)]
        for minion in player.field:
            if (minion.can_attack()):
                ''' [minion, HP, ATK, has_taunt, has_divine_shield, can_attack] '''
                my_characters.append(Character_model(minion))
        [attack,score] = destroy_target(target, [], my_characters)
        if (score > best_score):
            best_score = score
            best_attack = attack
    
    if (best_attack == []):
        for character in player.field:
            if (character.can_attack(player.opponent.hero)):
                return get_turn_item_attack(character, player.opponent.hero)
        if (player.hero.can_attack(player.opponent.hero)):
            return get_turn_item_attack(player.hero, player.opponent.hero)
    return best_attack

def destroy_target(target, first_attack, attacking_characters):
    if (target.is_dead()):
        return [first_attack,get_score_after_destroying(attacking_characters, target)]
    if (not(can_any_model_attack(attacking_characters))):
        return [first_attack, -1]
    
    best_score = 0
    best_attack = first_attack
    
    for attacker in attacking_characters:
        if (not(target.character in attacker.character.targets)):
            attacker.can_attack = False
        if (attacker.can_attack):
            new_attacker = attacker.get_copy()
            new_attacker.deal_damage(target.atk)
            new_attacker.set_attacked()
            new_target = target.get_copy()
            new_target.deal_damage(attacker.atk)
            new_my_characters = get_characters_with_replacement(attacking_characters, new_attacker)
            
            if (first_attack == []):
                [result_attack, score] = destroy_target(new_target,get_turn_item_attack(attacker.character, target.character), new_my_characters)
            else:
                [result_attack, score] = destroy_target(new_target, first_attack, new_my_characters)
            
            if (score > best_score):
                best_score = score
                best_attack = result_attack
    
    return [best_attack, best_score]
                    
            
            
    
def get_score_after_destroying(attacking_characters, destroyed):
    if (destroyed.character.__class__ is Hero):
        return 1000000
    score = destroyed.character.atk + 0.5
    for attacker in attacking_characters:
        if (attacker.is_dead()):
            score = score - attacker.atk
    score = score + destroyed.health/10.0
    return score
    
    

''' Deprecated. Recursion - too long to compute '''            
def get_best_attacks(my_characters, opponent_characters, first_attack, depth):
    if (depth > 7 or not(can_any_model_attack(my_characters))):
        return [first_attack, get_model_state_value(my_characters, opponent_characters)]
    
    best_turn = None
    best_score = -1000000
    
    for character in my_characters:
        if (character.can_attack):
            targets = get_attackable_characters(opponent_characters)
            for target in targets:
                if (first_attack != None or target.character in character.character.targets):
                    new_attacker = character.get_copy()
                    new_attacker.deal_damage(target.atk)
                    new_attacker.set_attacked()
                    new_target = target.get_copy()
                    new_target.deal_damage(character.atk)
                    new_my_characters = get_characters_with_replacement(my_characters, new_attacker)
                    new_opponent_characters = get_characters_with_replacement(opponent_characters, new_target)
                    
                    if (first_attack == None):
                        [result_attack, score] = get_best_attacks(new_my_characters, new_opponent_characters, [character.character,target.character], depth + 1)
                    else:
                        [result_attack, score] = get_best_attacks(new_my_characters, new_opponent_characters, first_attack, depth + 1)
                    
                    if (score > best_score):
                        best_score = score
                        best_turn = result_attack
    
    current_score = get_model_state_value(my_characters, opponent_characters)
    if (current_score > best_score):
        best_score = current_score
        best_turn = first_attack
    
    return [best_turn, best_score]
                
def get_characters_with_replacement(characters, replacement):
    result = []
    for character in characters:
        if (character.character == replacement.character):
            result.append(replacement)
        else:
            result.append(character.get_copy())
    return result        
                            
    
def get_model_state_value(my_characters, opponent_characters):
    result = 0
    for character in my_characters:
        if (character.character.__class__ is Hero):
            if (character.is_dead()):
                return -1000
            else:
                to_be_added = character.health/30.0
        else:
            to_be_added = character.health + character.atk
            if (character.has_divine_shield):
                to_be_added = to_be_added * 1.5
        result = result + to_be_added
        
    for character in opponent_characters:
        if (character.character.__class__ is Hero):
            if (character.is_dead()):
                return 1000
            else:
                to_be_added = character.health/30.0
        else:
            to_be_added = -character.health - character.atk
            if (character.has_divine_shield):
                to_be_added = to_be_added * 1.5
        result = result + to_be_added
    
    return result
        
def can_any_model_attack(models):
    for model in models:
        if (model.can_attack):
            return True     
    return False   
        
def get_attackable_characters(possible_targets):
    result = []
    if (is_taunt_among_models(possible_targets)):
        for target in possible_targets:
            if (target.has_taunt):
                result.append(target)
    else:
        result = possible_targets
    return result
        
def is_taunt_among_models(model_characters):
    for model_character in model_characters:
        if (model_character.can_attack):
            return True
    return False



'''
Description is a string that contains number preceded by "$".
Returns this number.
'''
def get_damage_from_description(description):
    array = description.split()
    for substring in array:
        if substring[0] == "$":
            result_str = substring
            break
    result_str = result_str[1:]
    return int(result_str)        

'''
Returns True iff there is a character among enemy characters with HP 
equal to attacker's attack.
'''
def has_enemy_worthy_to_attack(attacker, player):
    atk = attacker.atk
    for character in player.opponent.characters:
        if (character in attacker.targets and atk == character.health):
            return True
    return False

'''
Returns an enemy character such that its HP are equal to attacker's
attack if there is such. Otherwise return None.
'''
def get_enemy_worthy_to_attack(attacker, player):
    atk = attacker.atk
    for character in player.opponent.characters:
        if (character in attacker.targets and atk == character.health):
            return character
    return None

'''

USE ONLY for the spell cards that deal damage to a single target.
'''
def has_enemy_worthy_to_destroy(card, player):
    damage = get_damage_from_description(card.data.description)
    for character in player.opponent.characters:
        if (character.__class__ is Hero):
            if (character in card.targets and damage >= character.health):
                return True
        else:
            if (character in card.targets and damage >= character.health and damage <= character.health + damage/2):
                return True
    return False

'''
If there is no such enemy returns None.
USE ONLY for the spell cards that deal damage to a single target.
'''
def get_enemy_worthy_to_destroy(card, player):
    damage = get_damage_from_description(card.data.description)
    target = None
    for character in player.opponent.characters:
        if (character.__class__ is Hero):
            if (character in card.targets and (damage + get_total_player_attack(player)) >= character.health):
                return character
        else:
            if (character in card.targets and damage >= character.health and damage <= character.health + damage/2):
                if (target == None or character.health > target.health or 
                    (character.health == target.health and character.atk > target.atk)):
                    target = character
    return target

'''
Returns the sum of attack of all player's characters
'''
def get_total_player_attack(player):
    result = 0
    for character in player.characters:
        result = result + character.atk
    return result

def get_field_names_of_result():
    result = []
    result.append("Player_1_id")
    result.append("Player_1_deck_id")
    result.append("Player_1_final_hp")
    result.append("Player_2_id")
    result.append("Player_2_deck_id")
    result.append("Player_2_final_hp")
    result.append("Final_turn")
    result.append("Winner")
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
    if (game.player1.hero.health < 1):
        if (game.player2.hero.health < 1):
            winner = "None"
        else:
            winner = game.player2.get_id()
    else:
        if (game.player2.hero.health < 1):
            winner = game.player1.get_id()
        else:
            winner = "Error"
    result["Winner"] = winner    
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
Returns turn item for action 16 = attack with spell
Play card: [16, card, target]
"""
def get_turn_item_spell_attack(card, target):
    result = [16]
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
Returns True if player has minion with given name,
        False otherwise
"""
def has_specific_minion(player, name):
    for card in player.field:
        if (card.name == name):
            return True
    return False

"""
Returns True if player has card with given name,
        False otherwise
"""
def has_specific_card(player, name):
    for card in player.hand:
        if (card.name == name):
            return True
    return False

def has_specific_playable_card(player,name):
    for card in player.hand:
        if (card.name == name and card.is_playable()):
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
