# HearthstoneAI 

## Description
  * Using FirePlace Hearthstone simulator https://github.com/jleclanche/fireplace.
  * Replays
  * Results statistically processable
  * Random bot
  * Face hunter

## Requirements
  * Python 3.5+

## Installation
  * pip install -r requirements.txt

## Examples

### Running game N times
 * Let say we want to run Face_hunter (hunter_face deck) VS Random_bot (hunter_face deck) 5 times.
  1. Open CMD
  2. Navigate to ...\HearthstoneAI\tests
  3. "python general_game.py Face_hunter hunter_face Random_bot hunter_face 5"

### Creating a new AI
 * Each AI must be located in \HearthstoneAI\AI\bots\
 * Before starting, let you inspire by bot_template.py - There is everything you need to implement + some advices

### Adding a new deck
 * Deck is a .txt file located in \HearthstoneAI\AI\decks\
 * Its name must begin with the class name it is designated for. This has to be followed by "_"
  * Hunter deck file must be named hunter_WHATEVER.txt
  * Mage deck file must be named mage_WHATEVER.txt
 * Deck file must consist of 30 card names (1 card on 1 line)

### Running AI
  1. Go to HearthstoneAI/HearthstoneAI/tests
  2. python

## Changes
* 03. 04. 2016
  1. Evaluation framework improved 
    * replays in \HearthstoneAI\game_results
    * summary results in \HearthstoneAI\game_results\results_summary.csv
  2. general_game.py extended
    * runnable in command-line with arguments: ai_1_name, deck_1_id, ai_2_name, deck_2_id, num_games
  3. All AIs are now in \HearthstoneAI\AI\bots\
  4. All decks are now in \HearthstoneAI\AI\decks\ and their names begins with class name followed by "_"
