# HearthstoneAI 

## Goal

To implement AI for Hearthstone using open source Hearthstone simulator FirePlace: https://github.com/jleclanche/fireplace.

## Implemented

### Replays
* general_game.py that outputs following files:
  1. __.hdtreplay file__ viewable with Hearthstone Deck Tracker (https://github.com/Epix37/Hearthstone-Deck-Tracker/releases)
  2. __.csv file__ with game history for statistical processing
  3. __2 .hsdeck.txt file__ that list used decks

### Random player
* Plays cards and attacks randomly.
### Face hunter
* Plays cards to use maximum mana. Attacks opponent hero if possible (If not, destroys taunts). 
