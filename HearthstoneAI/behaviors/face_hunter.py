import fireplace.cards
import random
from fireplace.card import Spell, HeroPower
from hearthstone.enums import Race
from fireplace.player import Player
from .utils import *
from fireplace.cards.heroes import *

"""
Implementation of face hunter tactics. All damage is done
to the enemy hero while possible.
"""
class Face_hunter(Player):
    
    cards_to_play = []
    
    def __init__(self, name):
        deck = self.get_deck()
        super(Face_hunter, self).__init__(name, deck, HUNTER)
    
    """
    Choose next action to do.
    Action patterns:
    Play card: [0, card, target]
       Attack: [9, attacker, defender]
    Hero Pow.: [19, target]
     End Turn: []
    """
    def get_next_turn(self, game):
        player = game.current_player
        opponent = player.opponent
        
        if (len(self.cards_to_play) == 0):
            # if turns have not been chosen yet
            self.cards_to_play = self.get_cards_to_play(game, game.current_player, game.current_player.opponent)
            self.cards_to_play.append([])
        if (len(self.cards_to_play) > 1):
            go_to_attacks = False
            #play cards first
            card = self.cards_to_play[0]
            self.cards_to_play.remove(card)
            while (not(go_to_attacks) and (not(card.is_playable()) or (card.__class__ is HeroPower and not(card.is_usable())))):
                card = self.cards_to_play[0]
                self.cards_to_play.remove(card)
                if (card == []):
                     go_to_attacks = True
            
            if (not(go_to_attacks)):         
                target = None
                if (card.has_target()):
                    if (card.name == "Abusive Sergeant"):
                        if (len(player.field) > 0):
                            target = random.choice(player.field)
                        else:
                            target = random.choice(card.targets)
                    elif (opponent.hero in card.targets):
                        target = opponent.hero
                    else:
                        target = random.choice(card.targets)
                if (card == player.hero.power):
                    return get_turn_item_hero_power(card,target)
                return get_turn_item_play_card(card,target)
        #attack
        for character in player.characters:
           if character.can_attack(target = player.opponent.hero):
               return get_turn_item_attack(character,player.opponent.hero)
               continue
           else:
               if character.can_attack():
                   target = random.choice(character.targets)
                   return get_turn_item_attack(character,target)
               continue
           
        if player.choice:
           choice = random.choice(player.choice.cards)
           player.choice.choose(choice)
        self.cards_to_play = []
        return [] 
    
    def get_cards_to_play(self, game, player, opponent):
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
            [cards,mana_cost] = self.get_min_loss_card_costs(hand_copy,[], mana + 1, game, True)
        if (get_cards_cost(cards) < mana):
            [cards,mana_cost] = self.get_min_loss_card_costs(hand_copy,[], mana, game, False)
            
        return cards
    
    #choose cards to maximize mana usage
    def get_min_loss_card_costs(self, cards_left, cards_chosen, max_cost, game, use_coin):
    
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
            
            results.append(self.get_min_loss_card_costs(left_new, chosen_new, max_cost, game, use_coin))
        
        result = cards_chosen
        mana_cost = get_cards_cost(result)
        
        #get the cards with maximum mana cost
        for [possibly_chosen, possible_cost] in results:
            if (possible_cost > mana_cost):
                mana_cost = possible_cost
                result = possibly_chosen
            elif (possible_cost == mana_cost and self.get_secondary_score(possibly_chosen, game, use_coin) > self.get_secondary_score(result, game, use_coin)):
                result = possibly_chosen
       
        return [result,mana_cost]
    
    def get_secondary_score(self, cards, game, use_coin):
        result = 0
        for card in cards:
            to_be_added = 0
            if (card.name == "The Coin"):
                if (use_coin):
                    if (cards[0].name == "The Coin"):
                        to_be_added = 1
                    else:
                        to_be_added = 0.5
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
    
    
    
    def get_deck(self):
        
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