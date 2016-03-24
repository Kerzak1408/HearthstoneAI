import sys; sys.path.append("..")
import random
from fireplace.cards.heroes import *
from fireplace.exceptions import GameOver
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import *
from hearthstone.enums import Zone, Rarity
from fireplace.dsl.selector import CURRENT_HEALTH, FRIENDLY_HERO, ENEMY_MINIONS,\
    FRIENDLY_MINIONS, CONTROLLED_BY, Selector, IN_HAND
from behaviors.face_hunter import *
from fireplace.card import Spell, Secret, Weapon, HeroPower, Hero
from _datetime import date, datetime

""" 
idCounter - probably unnecessary
type - type of action: 0 == play, 1 == draw, 2 == discard, 9 == attack
id - id of the entity related to the action
attacker_id - id of attacker, in case o type 9, otherwise use None
defender_id - id of defender, in case o type 9, otherwise use None
"""
def get_hash_map(game, player1, player2, type, id, attacker_id, defender_id, played_card):
    hashmap = {}
    dataArray = []
    gameData = get_game_data(game, attacker_id, defender_id)
    dataArray.append(gameData)
    player1Data = get_player_data(player1)
    dataArray.append(player1Data)
    player2Data = get_player_data(player2)
    dataArray.append(player2Data)
    
    for card in player1.hand:
        cardData = get_card_data(card)
        dataArray.append(cardData)
        
    for card in player2.hand:
        cardData = get_card_data(card)
        dataArray.append(cardData)
        
    for card in player1.deck:
        cardData = get_card_data(card)
        dataArray.append(cardData)
        
    for card in player2.deck:
        cardData = get_card_data(card)
        dataArray.append(cardData)
    
    for character in player1.characters:
        characterData = get_character_data(character, attacker_id)
        dataArray.append(characterData)
    
    for character in player2.characters:
        characterData = get_character_data(character, attacker_id)
        dataArray.append(characterData)
        
    for secret in player1.secrets:
        if (played_card != secret):
            secretData = get_card_data(secret)
            dataArray.append(secretData)
    
    for secret in player2.secrets:
        if (played_card != secret):
            secretData = get_card_data(secret)
            dataArray.append(secretData)
    
    if ((played_card.__class__ is Spell) or (played_card.__class__ is Secret) or (played_card.__class__ is Weapon) or played_card.__class__ is HeroPower):
        played_card_data = get_card_data(played_card)
        dataArray.append(played_card_data)
                         
    if (player1.weapon != None):
        weaponData = get_weapon_data(player1.weapon)
        dataArray.append(weaponData)
        
    if (player2.weapon != None):
        weaponData = get_weapon_data(player2.weapon)
        dataArray.append(weaponData)
        
    hashmap["Data"] = dataArray
    hashmap["Id"] = id # ID of entity related to action
    hashmap["Player"] = game.current_player.entity_id - 2
    hashmap["Type"] = type # type of action
    hashmap["Turn"] = game.turn
    
    return hashmap

def get_player_data(player):
    result = {}
    
    tags = {}
    tags["TIMEOUT"] = player.timeout
    tags["PLAYSTATE"] = player.playstate.value
    tags["CURRENT_PLAYER"] = player.entity_id
    if (player.first_player):
        tags["FIRST_PLAYER"] = player.entity_id
    else:
        tags["FIRST_PLAYER"] = player.opponent.entity_id
    tags["HERO_ENTITY"] = player.hero.entity_id
    tags["MAXHANDSIZE"] = player.max_hand_size
    tags["STARTHANDSIZE"] = player.start_hand_size
    tags["PLAYER_ID"] = player.entity_id
    tags["TEAM_ID"] = 0
    tags["ZONE"] = player.zone.value
    
    tags["CONTROLLER"] = player.controller.entity_id
    tags["ENTITY_ID"] = player.entity_id
    tags["MAXRESOURCES"] = player.max_resources
    tags["CARDTYPE"] = 2
    tags["NUM_TURNS_LEFT"] = 1
    tags["NUM_CARDS_DRAWN_THIS_TURN"] = player.cards_drawn_this_turn
    tags["MULLIGAN_STATE"] = 0
    tags["RESOURCES"] = player._max_mana
    tags["NUM_OPTIONS"] = 0
    tags["NUM_RESOURCES_SPENT_THIS_GAME"] = player.used_mana
    tags["RESOURCES_USED"] = player.used_mana
    tags["NUM_CARDS_PLAYED_THIS_TURN"] = 0
    tags["NUM_MINIONS_PLAYED_THIS_TURN"] = player.minions_killed_this_turn
    if (player.last_card_played != None):
        tags["LAST_CARD_PLAYED"] = player.last_card_played.entity_id
    if (player.weapon != None):
        tags["EQUIPPED_WEAPON"] = player.weapon.entity_id
    tags["COMBO_ACTIVE"] = 0
    tags["NUM_OPTIONS_PLAYED_THIS_TURN"] = 0
    
    result["Tags"] = tags
    result["Name"] = player.name
    result["Id"] = player.entity_id
    result["CardId"] = "null"
    if (player.first_player):
        result["IsPlayer"] = "true"
    else:
        result["IsPlayer"] = "false"
    result["IsSecret"] = "false"
    return result

def get_game_data(game, attacker_id, defender_id):
    result = {}
    tags = {}
    tags["10"] = 85 #NO IDEA WHY
    tags["TURN"] = game.turn
    tags["ZONE"] = game.zone.value
    tags["ENTITY_ID"] = game.entity_id
    tags["NEXT_STEP"] = 0
    tags["CARDTYPE"] = 1
    tags["STATE"] = 0
    tags["STEP"] = 0
    if (attacker_id != None):
        tags["PROPOSED_ATTACKER"] = attacker_id
    if (defender_id != None):
        tags["PROPOSED_DEFENDER"] = defender_id
        
    result["Tags"] = tags
    result["Name"] = "GameEntity"
    result["Id"] = game.entity_id
    result["CardId"] = "null"
    result["IsPlayer"] = "false"
    result["IsSecret"] = "false"
    return result

def get_weapon_data(card):
    result = {}
    
    tags = {}
    tags["ZONE"] =  card.zone.value
    tags["CONTROLLER"] =  card.controller.entity_id
    tags["ENTITY_ID"] =  card.entity_id
    tags["ZONE_POSITION"] =  card.zone_position + 1
    tags["CANT_PLAY"] =  0
    tags["REVEALED"] =  0
    tags["ATK"] =  card.atk
    tags["COST"] =  card.cost
    tags["DURABILITY"] =  card.durability
    tags["FACTION"] =  0
    tags["CARDTYPE"] =  card.type
    if (card.turns_in_play == 0):
        tags["JUST_PLAYED"] = 1
    else:
        tags["JUST_PLAYED"] = 0
    tags["PREDAMAGE"] =  0
    tags["LAST_AFFECTED_BY"] =  card.controller.entity_id
    tags["DAMAGE"] =  card.damage
    if (card.exhausted):
        tags["EXHAUSTED"] = 1
    else:
        tags["EXHAUSTED"] = 0
    
    result["Tags"] = tags
    result["Name"] = "null"
    result["Id"] = card.entity_id
    result["CardId"] = card.id
    result["IsPlayer"] = "false"
    result["IsSecret"] = "false"
    
    return result
    
def get_card_data(card):
    result = {}
    
    tags = {}
    tags["ZONE"] = card.zone.value
    tags["CONTROLLER"] = card.controller.entity_id
    tags["ENTITY_ID"] = card.entity_id
    tags["ZONE_POSITION"] = card.zone_position + 1
    tags["CANT_PLAY"] = 0
    tags["REVEALED"] = 0
    
    result["Tags"] = tags
    result["Name"] = "null"
    result["Id"] = card.entity_id
    result["CardId"] = card.id
    result["IsPlayer"] = "false"
    result["IsSecret"] = "false"
    return result

def get_character_data(character, attacking_id):
    result = {}
    
    tags = {}
    tags["ZONE"] = character.zone.value
    tags["CONTROLLER"] = character.controller.entity_id
    tags["ENTITY_ID"] = character.entity_id
    tags["ZONE_POSITION"] = character.zone_position + 1
    tags["CANT_PLAY"] = 0
    tags["REVEALED"] = 0
    tags["HEALTH"] = character.health
    tags["ATK"] = character.atk
    tags["COST"] = character.cost
    tags["CARDTYPE"] = character.type
    if (character.rarity == Rarity.INVALID):
        tags["RARITY"] = 0
    else:    
        tags["RARITY"] = character.rarity
    tags["INSPIRE"] = 0
    if (character.exhausted):
        tags["EXHAUSTED"] = 1
    else:
        tags["EXHAUSTED"] = 0
    if (character.turns_in_play == 0):
        tags["JUST_PLAYED"] = 1
    else:
        tags["JUST_PLAYED"] = 0 
    if(character.entity_id == attacking_id):
        tags["NUM_TURNS_IN_PLAY"] = character.turns_in_play
        tags["ATTACKING"] = 1
        tags["NUM_ATTACKS_THIS_TURN"] = character.num_attacks
    if(character.__class__ is Hero):
        tags["ARMOR"] = character.armor
        
    result["Tags"] = tags
    result["Name"] = "null"
    result["Id"] = character.entity_id
    result["CardId"] = character.id
    result["IsPlayer"] = "false"
    result["IsSecret"] = "false"
    return result
