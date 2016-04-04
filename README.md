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

### Running AI
  1. Go to HearthstoneAI/HearthstoneAI/tests
  2. python

## Changes
* 03. 04. 2016
  1. Evaluation framework improved 
    * replays in /HearthstoneAI/game_results
    * summary results in /HearthstoneAI/game_results/results_summary.csv
  2. general_game.py extended
    * runnable in command-line with arguments: ai_1_name, deck_1_id, ai_2_name, deck_2_id, num_games
  3. All AIs are now in /HearthstoneAI/AI/bots/
  4. All decks are now in /HearthstoneAI/AI/decks/ and their names begins with class name followed by "_"
