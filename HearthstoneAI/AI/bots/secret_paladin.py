import random
from AI.utils import *
from fireplace.utils import *
from fireplace.card import *

class Secret_paladin(Player):
    
    ''' Current version of the bot. Should be updated after significant changes. '''
    version = 1
    
    ''' It is useful to store original deck here. It is needed for replays. '''
    original_deck = []
    
    ''' Name of the file containing deck. The file must be located in HearthstoneAI\AI\decks '''
    deck_id = None
    
    
    def __init__(self, name, deck_id):
        hero = get_hero(deck_id)
        self.deck_id = deck_id
        self.original_deck = get_deck_by_id(deck_id)
        super(Secret_paladin, self).__init__(name, self.original_deck, hero)
    
    ''' This should return unique id of AI that consists of its name and version'''
    def get_id(self):
        return self.__class__.__name__ + "_" +  str(self.version)
    
    ''' This should return the original deck, that bot had before the start of game. '''
    def get_deck(self):
        return self.original_deck
    
    ''' This should return deck_id '''
    def get_deck_id(self):
        return self.deck_id
    
    '''
    Choose a list of cards to mulligan.
    I should return the list of the cards you want to discard.
    This is called only before the first turn of each game.
    If you leave it unchanged, it will choose randomly.
    '''
    def get_mulligans(self, choice_cards):
        mull_count = random.randint(0, len(choice_cards))
        return random.sample(choice_cards, mull_count)
    
    """
    Choose next action to do.
    Action patterns:
    Play card: [0, card, target]
       Attack: [9, attacker, defender]
    Hero Pow.: [19, target]
    Spell attack: [16, card, target]
     End Turn: []
    """
    def get_next_turn(self, game):
        current_player = game.current_player
        if (has_specific_card(current_player,"The Coin")):
            use_coin = True
        else:
            use_coin = False
            
        hand_copy = []
        if (current_player.hero.power.is_usable()):
            hand_copy.append(current_player.hero.power)
        for card in current_player.hand:
            hand_copy.append(card)
        cards_to_play = self.get_cards_to_play(hand_copy, [], current_player.mana, current_player, use_coin)
        if (len(cards_to_play[0]) != 0):
            target = None
            card = cards_to_play[0][0]
            if (card.has_target()):
                if (card.name == "Keeper of Uldaman"):
                    target = self.get_keeper_target(current_player)
                else:
                    target = random.choice(card.targets)
            if (card.__class__ is HeroPower):
                return get_turn_item_hero_power(card, target)
            else:
                return get_turn_item_play_card(card, target)
        else:
            return self.get_next_attack(current_player)
        
    def get_next_attack(self, player):
        turn =  get_valuest_attack(player)
        return turn
    
    def get_cards_to_play(self, cards_left, cards_chosen, max_cost, player, use_coin):
    
        if (get_cards_cost(cards_chosen) > max_cost):
            return [[], -1]
        
        result_cards = cards_chosen
        result_score = self.get_cards_score(result_cards, player)
        
        results = []
        for card in cards_left:
            if (card.is_playable()):
                left_new = []
                chosen_new = []
                
                for card_1 in cards_left:
                    if (card_1 != card):
                        left_new.append(card_1)
                
                for card_2 in cards_chosen:
                    chosen_new.append(card_2)
                chosen_new.append(card)
                
                [possible_cards, possible_score] = self.get_cards_to_play(left_new, chosen_new, max_cost, player, use_coin)
                if (possible_score > result_score):
                    result_score = possible_score
                    result_cards = possible_cards
            
        return [result_cards,result_score]
    
    def get_cards_score(self, cards, player):
        result = 0
        for card in cards:
            if (card.is_playable):
                to_be_added = 0
                if (card.__class__ is Minion):
                    to_be_added = card.health + card.atk
                    if (card.taunt):
                        to_be_added = to_be_added + 1
                    if (card.divine_shield):
                        to_be_added = to_be_added * 1.5
                    if (card.has_deathrattle):
                        to_be_added = to_be_added * 1.5
                    
                    if (card.name == "Mysterious Challenger"):
                        to_be_added = to_be_added + 15
                    elif (card.name == "Dr. Boom"):
                        to_be_added = to_be_added + 8
                    elif (card.name == "Keeper of Uldaman"):
                        to_be_added = to_be_added + self.get_keeper_bonus_score(player)
                elif (card.__class__ is Weapon):
                    if (player.weapon != None):
                        to_be_added = -10
                    else:
                        to_be_added = card.atk * card.durability
                        if (card.name == "Coghammer" and len(player.field) > 0):
                            to_be_added = to_be_added + 3
                elif (card.__class__ is Spell):
                    if (card.name == "Muster for Battle"):
                        to_be_added = 10
                        if (has_specific_minion(player, "Knife Juggler")):
                            to_be_added = to_be_added + 50
                    elif (card.name == "Blessing of Kings"):
                        if (len(player.field) > 0):
                            to_be_added = 8
                        else:
                            to_be_added = -8
                elif (card.__class__ is Secret):
                    if (card.name == "Avenge"):
                        to_be_added = 5
                    elif (card.name == "Noble Sacrifice"):
                        to_be_added = 3
                    elif (card.name == "Redemption"):
                        to_be_added = self.get_redemption_score(player)
                    elif (card.name == "Competitive Spirit"):
                        to_be_added = len(player.field) - len(player.opponent.field) - 2
                else:
                    to_be_added = 1
                
                result = result + to_be_added        
        
        return result
    
    def get_redemption_score(self, player):
        result = -2
        for minion in player.field:
            if (minion.atk < 2):
                return -1
            else:
                result = minion.atk
        return result + 1
    
    def get_keeper_bonus_score(self, player):
        result = -100
        for friedly_minion in player.field:
            score = 3 - friedly_minion.health + 3 - friedly_minion.atk
            if (score > result):
                result = score
        for enemy_minion in player.opponent.field:
            score = enemy_minion.health - 3 + enemy_minion.atk - 3
            if (score > result):
                result = score
        return result
    
    def get_keeper_target(self, player):
        best_score = -100
        best_target = None
        for friedly_minion in player.field:
            score = 3 - friedly_minion.health + 3 - friedly_minion.atk
            if (score > best_score):
                best_score = score
                best_target = friedly_minion
        for enemy_minion in player.opponent.field:
            score = enemy_minion.health - 3 + enemy_minion.atk - 3
            if (score > best_score):
                best_score = score
                best_target = enemy_minion
        return best_target
        