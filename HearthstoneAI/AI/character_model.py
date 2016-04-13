from fireplace.card import Hero
class Character_model:
    
    character = None
    health = -1
    atk = -1
    has_divine_shield = False
    has_taunt = False
    can_attack = True
    
    def __init__(self, character):
        self.character = character
        self.health = character.health
        self.atk = character.atk
        if (character.__class__ is Hero):
            self.has_divine_shield = False
            self.has_taunt = False
        else:
            self.has_divine_shield = character.divine_shield
            self.has_taunt = character.taunt
        self.can_attack = character.can_attack()
    
    def is_dead(self):
        return self.health < 1
    
    def get_copy(self):
        result = Character_model(self.character)
        result.atk = self.atk
        result.health = self.health
        result.has_divine_shield = self.has_divine_shield
        result.has_taunt = self.has_taunt
        result.can_attack = self.can_attack
        return result
    
    def deal_damage(self, amount):
        if (self.has_divine_shield and amount > 0):
            self.has_divine_shield = False
        else:
            self.health = self.health - amount
        
    def set_attacked(self):
        self.can_attack = False
        
    def __str__(self):
        result = 'HP:' + str(self.health) + ',ATK:' + str(self.atk)
        if (self.has_taunt):
            result = result + '(T)'
        if (self.has_divine_shield):
            result = result + '(D)'
        if (not(self.can_attack)):
            result = result + '(ZZZ)'    
        return result
    
    def __repr__(self):
        result = '[HP:' + str(self.health) + ',ATK:' + str(self.atk)
        if (self.has_taunt):
            result = result + '(T)'
        if (self.has_divine_shield):
            result = result + '(D)'
        if (not(self.can_attack)):
            result = result + '(ZZZ)' 
        result = result + ']'   
        return result
    