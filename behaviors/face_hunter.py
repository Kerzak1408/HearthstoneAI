import fireplace.cards
import random
from fireplace.card import Spell
from hearthstone.enums import Race

def get_cards_to_play(game, player, opponent):
    cards = []
    mana = player.mana
    hand_copy = []
    hand_copy.append(player.hero.power)
    for card in player.hand:
        hand_copy.append(card)
    
    result = []
        
    if (has_taunt_minion(opponent)):
        #try to silence taunt minion
        if (has_specific_card(player, "Ironbeak Owl")):
            ironbeak_owl = get_specific_card(player, "Ironbeak Owl")
            result.append([ironbeak_owl,get_taunt_minion(opponent)])
            mana = mana - ironbeak_owl.cost
            hand_copy.remove(ironbeak_owl)
    
    if (has_specific_card(player, "The Coin")):
        [cards,mana_cost] = get_min_loss_card_costs(hand_copy,[], mana + 1, game, True)
    if (get_cards_cost(cards) < mana):
        [cards,mana_cost] = get_min_loss_card_costs(hand_copy,[], mana, game, False)
    
    for card in cards:
        if (card.has_target()):
            if (card.name == "Abusive Sergeant"):
                if (len(player.field) > 0):
                    result.append([card,random.choice(player.field)])
                else:
                    result.append([card,random.choice(card.targets)])
            elif (opponent.hero in card.targets):
                result.append([card,opponent.hero])
            else:
                target = random.choice(card.targets)
                result.append([card,target])
        else:
            result.append([card,None])
    return result

#choose cards to maximize mana usage
def get_min_loss_card_costs(cards_left, cards_chosen, max_cost, game, use_coin):
    
    if (get_cards_cost(cards_chosen) > max_cost):
        return [[], -1]
    
    results = []
    for card in cards_left:
        left_new = []
        chosen_new = []
        
        for card_1 in cards_left:
            if (card_1 != card):
                left_new.append(card_1)
        
        for card_2 in cards_chosen:
            chosen_new.append(card_2)
        chosen_new.append(card)
        
        results.append(get_min_loss_card_costs(left_new, chosen_new, max_cost, game, use_coin))
    
    result = cards_chosen
    mana_cost = get_cards_cost(result)
    
    #get the cards with maximum mana cost
    for [possibly_chosen, possible_cost] in results:
        if (possible_cost > mana_cost):
            mana_cost = possible_cost
            result = possibly_chosen
        elif (possible_cost == mana_cost and get_secondary_score(possibly_chosen, game, use_coin) > get_secondary_score(result, game, use_coin)):
            result = possibly_chosen
   
    return [result,mana_cost]

def remove_specific_cost_card(cards, cost):
    result = []
    removed = False
    for card in cards:
        if (not(removed) and card.cost == cost):
            removed = True
        else:
            result.append(card)
    return result

def get_specific_cost_card(cards, cost):
    for card in cards:
        if (card.cost == cost):
            return card
    return None

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

def get_secondary_score(cards, game, use_coin):
    result = 0
    for card in cards:
        to_be_added = 0
        if (card.name == "The Coin"):
            if (use_coin):
                to_be_added = 1
            else:
                to_be_added = -1
        elif (card.name == "Leper Gnome"):
            to_be_added = 3
        elif (card.name == "Worgen Infiltrator"):
            to_be_added = 2
        elif (card.name == "Abusive Sergeant"):
            to_be_added = 1
        elif (card.name == "Mad Scientist"):
            to_be_added = 8
        elif (card.name == "Haunted Creeper"):
            to_be_added = 7
        elif (card.name == "Knife Juggler"):
            to_be_added = 6
        elif (card.name == "Bear Trap"):
            to_be_added = 5
        elif (card.name == "Glaivezooka"):
            if (game.current_player.weapon == None):
                to_be_added = 4
            else:
                to_be_added = 0
        elif (card.name == "Explosive Trap"):
            to_be_added = 3
        elif (card.name == "Ironbeak Owl"):
            to_be_added = 2
        elif (card.name == "Steady Shot"):
            to_be_added = 1
        elif (card.name == "Eaglehorn Bow"):
            if (game.current_player.weapon == None):
                to_be_added = 7
            else:
                to_be_added = 0
        elif (card.name == "Animal Companion"):
            to_be_added = 6
        elif (card.name == "Arcane Golem"):
            to_be_added = 5
        elif (card.name == "Argent Horserider"):
            to_be_added = 4
        elif (card.name == "Quick Shot"):
            to_be_added = 3
        elif (card.name == "Kill Command"):
            if (has_beast(game.current_player.field)):
                to_be_added = 8
            else:
                to_be_added = 2
        elif (card.name == "Unleash the Hounds"):
            if (len(game.current_player.opponent.field) > 2):
                to_be_added = 9
            else:
                to_be_added = 1
       
        result = result + to_be_added
    return result

def has_beast(cards):
    result = False
    for card in cards:
        if (card.data.race == Race.BEAST):
            result = True
    return result

def has_specific_card(player, name):
    for card in player.hand:
        if (card.name == name):
            return True
    return False

def get_specific_card(player, name):
    for card in player.hand:
        if (card.name == name):
            return card
    return None

def has_taunt_minion(player):
    for minion in player.field:
        if minion.taunt:
             return True
    return False

def get_taunt_minion(player):
    for minion in player.field:
        if minion.taunt:
             return minion
    return None

def get_face_hunter_deck():
    
    deck = []
    
    deck.append(fireplace.cards.filter(name = "Glaivezooka",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Glaivezooka",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Bear Trap",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Explosive Trap",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Quick Shot",collectible = True)[0])
    
    deck.append(fireplace.cards.filter(name = "Quick Shot",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Eaglehorn Bow",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Eaglehorn Bow",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Animal Companion",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Animal Companion",collectible = True)[0])
    
    deck.append(fireplace.cards.filter(name = "Kill Command",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Kill Command",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Unleash the Hounds",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Unleash the Hounds",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Abusive Sergeant",collectible = True)[0])
    
    deck.append(fireplace.cards.filter(name = "Abusive Sergeant",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Leper Gnome",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Leper Gnome",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Worgen Infiltrator",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Haunted Creeper",collectible = True)[0])
    
    deck.append(fireplace.cards.filter(name = "Haunted Creeper",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Ironbeak Owl",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Knife Juggler",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Knife Juggler",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Mad Scientist",collectible = True)[0])
    
    deck.append(fireplace.cards.filter(name = "Mad Scientist",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Arcane Golem",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Arcane Golem",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Argent Horserider",collectible = True)[0])
    deck.append(fireplace.cards.filter(name = "Argent Horserider",collectible = True)[0])
    
    return deck