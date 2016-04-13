import random
from AI.utils import *
from fireplace.utils import *

class Malygos_freeze_mage(Player):
    
    ''' Current version of the bot. Should be updated after significant changes. '''
    version = 1
    
    ''' It is useful to store original deck here. It is needed for replays. '''
    original_deck = []
    
    ''' Name of the file containing deck. The file must be located in HearthstoneAI\AI\decks '''
    deck_id = None
    
    
    ''' 0 == waiting for combo cards, 1 == emperor phase, 2 == malygos phase '''
    combo_phase = 0
    
    freezed_already = False
    
    previous_turn_num = -1
    
    def __init__(self, name, deck_id):
        hero = get_hero(deck_id)
        self.deck_id = deck_id
        self.original_deck = get_deck_by_id(deck_id)
        super(Malygos_freeze_mage, self).__init__(name, self.original_deck, hero)
    
    ''' Returns unique id of AI that consists of its name and version'''
    def get_id(self):
        return self.__class__.__name__ + "_" +  str(self.version)
    
    ''' Returns the original deck, that bot had before the start of game. '''
    def get_deck(self):
        return self.original_deck
    
    ''' Returns deck_id '''
    def get_deck_id(self):
        return self.deck_id
    
    def get_mulligans(self, choice_cards):
        result = []
        for card in choice_cards:
            if (card.name != "Loot Hoarder" and
                card.name != "Mad Scientist" and
                card.name != "Arcane Intellect" and
                card.name != "Bloodmage Thalnos" and
                card.name != "Doomayer" and
                card.name != "Acolyte of Pain"):
                result.append(card)
        return result
    
    """
    Choose next action to do.
    Action patterns:
    Play card: [0, card, target]
       Attack: [9, attacker, defender]
    Hero Pow.: [19, target]
     End Turn: []
    """
    def get_next_turn(self, game):
        if (self.previous_turn_num != game.turn):
            self.freezed_already = False
            self.previous_turn_num = game.turn
        current_player = game.current_player
        opponent = current_player.opponent
        result = []
        if (self.combo_phase == 2):
            result = self.get_next_malygos_phase_turn(current_player)
        elif (self.combo_phase == 1):
            result = self.get_next_emperor_phase_turn(current_player)
        elif (self.has_emperor(current_player) and current_player.mana > 8 and self.get_available_combo_power(current_player) > opponent.hero.health):
            self.combo_phase = 1
            result = self.get_next_emperor_phase_turn(current_player)
        else:
            result = self.get_next_waiting_phase_turn(current_player) 
        return result
    
    def get_next_attack(self, player):
        result = []
        attacking_minion = None
        target = None
        for minion in player.field:
            if minion.can_attack():
                attacking_minion = minion
                break
        if (attacking_minion == None or len(attacking_minion.targets) == 0):
            return []
        if (attacking_minion.name == "Acolyte of Pain"):
            target = self.get_acolyte_target(attacking_minion)
        if (player.opponent.hero in attacking_minion.targets):
            target = player.opponent.hero
        else:
            target = random.choice(attacking_minion.targets)
        
        return get_turn_item_attack(attacking_minion, target)
    
    def get_acolyte_target(self, acolyte):
        result = None
        for target in acolyte.targets:
            if (result == None):
                result = target
            elif (target.atk > 0 and target.atk < result.atk):
                result = target                    
    
    def get_next_waiting_phase_turn(self, player):
        if (not(self.freezed_already) and get_total_player_attack(player.opponent) > 9):
            if (self.has_playable_freeze_card(player)):
                self.freezed_already = True
                card = self.get_playable_freeze_card(player)
                return get_turn_item_play_card(card,None)
        if (has_specific_card(player,"The Coin")):
            use_coin = True
        else:
            use_coin = False 
        hand_copy = []
        for card in player.hand:
            hand_copy.append(card)
        if (player.hero.power.is_usable()):
            hand_copy.append(player.hero.power)
        cards_to_play = self.get_min_loss_card_costs(hand_copy,[],player.mana, use_coin, player)
        if (len(cards_to_play[0]) > 0):
            next_card = cards_to_play[0][0]
            target = None
            if (next_card.has_target()):
                if (next_card.name == "Alexstrasza"):
                    if ((15 - player.hero.health) > (player.opponent.hero.health - 15)):
                        target = player.hero
                    else:
                        target = player.opponent.hero
                else:
                    if (player.opponent.hero in next_card.targets):
                        target = player.opponent.hero
                    else:
                        target = random.choice(next_card.targets)
            if (next_card == player.hero.power):
                return get_turn_item_hero_power(next_card,target)
            elif (target == None):
                return get_turn_item_play_card(next_card, target)
            else:
                return get_turn_item_spell_attack(next_card, target)
        else:
            return self.get_next_attack(player)        
        #choose cards to maximize mana usage
    def get_min_loss_card_costs(self, cards_left, cards_chosen, max_cost, use_coin, player):
    
        if (get_cards_cost(cards_chosen) > max_cost):
            return [[], -1]
        
        results = []
        for card in cards_left:
            if (self.is_allowed_as_pawn(card, player) and card.is_playable()):
                left_new = []
                chosen_new = []
                
                for card_1 in cards_left:
                    if (card_1 != card):
                        left_new.append(card_1)
                
                for card_2 in cards_chosen:
                    chosen_new.append(card_2)
                chosen_new.append(card)
                
                results.append(self.get_min_loss_card_costs(left_new, chosen_new, max_cost, use_coin, player))
        
        result = cards_chosen
        mana_cost = get_cards_cost(result)
        
        #get the cards with maximum mana cost
        for [possibly_chosen, possible_cost] in results:
            if (possible_cost > mana_cost):
                mana_cost = possible_cost
                result = possibly_chosen
            elif (possible_cost == mana_cost and self.get_secondary_score(possibly_chosen, use_coin) > self.get_secondary_score(result, use_coin)):
                result = possibly_chosen
       
        return [result,mana_cost]
    
    def get_secondary_score(self, cards, use_coin):
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
            elif (card.name == "Doomsayer"):
                to_be_added = -1
                if (self.freezed_already):
                    to_be_added = 10
                if (get_total_player_attack(self.opponent) > 4 and get_total_player_attack(self.opponent) < 7):
                    to_be_added = 5
            elif (card.name == "Ice Block"):
                to_be_added = 5
            elif (card.name == "Ice Barrier"):
                to_be_added = 4
            result = result + to_be_added
        return result
    
    
    def is_allowed_as_pawn(self, card, player):
        return (card.name != "Emperor Thaurissan" and 
                card.name != "Malygos" and
                card.name != "Ice Lance" and 
                card.name != "Frostbolt" and
                card.name != "Frost Nova" and 
                card.name != "Blizzard" and
                card.name != "Flamestrike" and 
                (card.name != "Antique Healbot" or player.hero.health < 26) and
                (card.name != "Doomsayer" or get_total_player_attack(player.opponent) > 4) and
                (card.name != "Arcane Intellect" or len(player.hand) < 10) and
                (card.name != "Doomsayer" or not(has_specific_minion(player,"Doomsayer")))
                )
    
    def get_next_emperor_phase_turn(self, player):
        if (self.has_emperor(player)):
            card = get_specific_card(player,"Emperor Thaurissan")
            return get_turn_item_play_card(card,None)
        elif (has_specific_card(player,"Ice Block") and get_specific_card(player,"Ice Block").is_playable()):
            card = get_specific_card(player,"Ice Block")
            return get_turn_item_play_card(card,None)
        elif (len(player.opponent.field) > 0 and self.has_playable_freeze_card(player)):
            card = self.get_playable_freeze_card(player)
            return get_turn_item_play_card(card, None)
        
        result =  self.get_next_attack(player)
        if (result == []):
            self.combo_phase = 2
        return result
    
    def get_next_malygos_phase_turn(self, player):
        if (has_specific_playable_card(player,"Malygos")):
            card = get_specific_card(player,"Malygos")
            return get_turn_item_spell_attack(card,None)
        elif (has_specific_playable_card(player, "Frostbolt")):
            card = get_specific_card(player,"Frostbolt")
            return get_turn_item_spell_attack(card,player.opponent.hero)
        elif (has_specific_playable_card(player, "Ice Lance")):
            card = get_specific_card(player,"Ice Lance")
            return get_turn_item_spell_attack(card,player.opponent.hero)
        result = self.get_next_attack(player)
        if (result == []):
            self.combo_phase = 0
        return result

    '''
    Returns true iff player's hand contains at least one of following card and that card is playable:
    Frost Nova
    Blizzard
    Flamestrike - not a freeze card, but AOE
    '''
    def has_playable_freeze_card(self, player):
        return (has_specific_playable_card(player,"Blizzard") or has_specific_playable_card(player,"Frost Nova") or has_specific_playable_card(player,"Flamestrike"))

    '''
    Finds one of following cards in hand (ordered b priority): Blizzard, Frost Nova, Flamestrike.
    If none of those is in player's possession returns None. 
    '''
    def get_playable_freeze_card(self, player):
        if (has_specific_playable_card(player,"Blizzard") and get_specific_card(player,"Blizzard").is_playable()):
            return get_specific_card(player,"Blizzard")
        elif (has_specific_playable_card(player,"Frost Nova") and get_specific_card(player,"Frost Nova").is_playable()):
            return get_specific_card(player,"Frost Nova")
        elif (has_specific_playable_card(player,"Flamestrike") and get_specific_card(player,"Flamestrike").is_playable()):
            return get_specific_card(player,"Flamestrike")
        return None
    
    '''
    Returns True, iff player has Emperor Thaurissan in hand.
    '''
    def has_emperor(self, player):
        return has_specific_card(player,"Emperor Thaurissan")
    
    ''' 
    Returns potential damage of all Frostbolts and Ice Lances in players hand.
    '''
    def get_available_combo_power(self, player):
        result = 0
        if (has_specific_card(player,"Malygos") and has_specific_card(player,"Frostbolt")):
            for card in player.hand:
                if (card.name == "Frostbolt"):
                    result = result + 8
                elif (card.name == "Ice Lance"):
                    result = result + 9
        return result