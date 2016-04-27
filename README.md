# HearthstoneAI 

## Description
  * Using FirePlace Hearthstone simulator https://github.com/jleclanche/fireplace.
  * Replays
  * Results statistically processable
  * Random bot
  * Face hunter
  * Malygos freeze mage
  * Secret paladin
  * Q learner with neural network

## Requirements
  * Python 3.5+

## Installation
 * Navigate to \HearthstoneAI\
 * "pip install -r requirements.txt"
 * And finally run bootstrap.bat

## Usage examples

#### Running game N times
 * Let say we want to run Face_hunter (hunter_face deck) VS Random_bot (hunter_face deck) 5 times.
  1. Navigate to ...\HearthstoneAI\tests
  2. "python general_game.py Face_hunter hunter_face Random_bot hunter_face 5"
  3. If we want also to clear results_summary.csv file, instead of 2.: 
     "python general_game.py Face_hunter hunter_face Random_bot hunter_face 5 T"

#### Results
 * Each simulation creates its own folder in \HearthstoneAI\game_results\
 * Result folder is named AI_1_id-deck_1_id-AI_2_id-deck_2_id-date-num_game_today
 * Same naming convention is applied to the files that folder contains. That are:
  * .hdtreplay file viewable by Hearthstone Deck Tracker - https://github.com/Epix37/Hearthstone-Deck-Tracker
  * .csv file containing snapshot of game state before each turn on each line
 * Summary game result is located in HearthstoneAI\game_results\results_summary.csv

#### Creating a new AI
 * Each AI must be located in \HearthstoneAI\AI\bots\
 * Before starting, let you inspire by bot_template.py - There is everything you need to implement + some advices

#### Adding a new deck
 * Deck is a .txt file located in \HearthstoneAI\AI\decks\
 * Its name must begin with the class name it is designated for. This has to be followed by "_"
  * Hunter deck file must be named hunter_WHATEVER.txt
  * Mage deck file must be named mage_WHATEVER.txt
 * Deck file must consist of 30 card names (1 card on 1 line)

## Changes
* 03. 04. 2016
  1. Evaluation framework improved 
    * replays in \HearthstoneAI\game_results
    * summary results in \HearthstoneAI\game_results\results_summary.csv
  2. general_game.py extended
    * runnable in command-line with arguments: ai_1_name, deck_1_id, ai_2_name, deck_2_id, num_games
  3. All AIs are now in \HearthstoneAI\AI\bots\
  4. All decks are now in \HearthstoneAI\AI\decks\ and their names begins with class name followed by "_"
* 10. 04. 2016
  1. Malygos freeze mage
    * Tries to survive until combo is playable (freeze + def. secrets)
    * Combo: 
      a. TURN   N: Emperor Thaurissan
      b. TURN N+1: Malygos + 2x Frost Bolt + 2x Ice Lance
  2. Mulligan phase
    * From now, AIs implements get_mulligans(self, choice_cards), that shoud return unwanted cards. This is called before 1st turn of a game. 
  3. Spell targets in Replays
    * Replays show also the target of Spell, if there exists one.
  4. Results summary
    * You can add "T" as a 6th argument, if you want to clear results_summary.csv file before the next simulation
    * Column "Winner" added to results_summary.csv file
* 13. 04. 2016
  1. Secret paladin implemented
    * tries to have predominance on the field == primary destroys minions
  2. Taunt an Divine shield are now visible in replays
* 27. 04. 2016
  1. Q_learning with neural networks
    * working but in phase of win_rate optimization
