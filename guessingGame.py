#!/usr/bin/env -S PYTHONPATH=../common python3

import numpy as np
import random

class GuessingGame:

    # Game constructor
    def __init__(self, max_guess = 100):
        # Keep a list/mapping of all the players
        self.players = {}

        # This is an INCLUSIVE maxGuess value
        # (i.e: if maxGuess = 100, guesses are in [1,100])
        self.max_guess = max_guess
        self.win_guess = np.random.randint(1, self.max_guess+1)
        print('Winning number is: ', self.win_guess)
    

    def get_num_players(self):
        return len(self.players.keys())
    

    # Re-generate player guesses whenever a player is added
    def __gen_player_guesses(self):

        # empty each player's list
        for player in self.players:
            self.players[player] = []

        # generate a list of maxGuess integers in random order
        #randIntList = np.random.choice(self.maxGuess, self.maxGuess)
        rand_int_list = np.array(random.sample(range(self.max_guess), self.max_guess))

        # Bump up all the values so min(randIntList) == 1
        rand_int_list = rand_int_list + 1

        # Convert us back to a python list
        rand_int_list = list(rand_int_list)

        curr_player = 0

        players_list = list(self.players.keys())
        # While there are still integers to hand out,
        # give the next integer to the next player
        # RoundRobin style makes sure no other players have too many guesses
        while rand_int_list:
            next_num = rand_int_list.pop()
            player = players_list[curr_player]
            self.players[player].append(next_num)
            curr_player = (curr_player+1) % self.get_num_players()

        for player in self.players:
            print(player, ': ', self.players[player], sep='')
        

    # Add new player
    def add_new_player(self, alias):
        # ReGen the guesses for all the players
        self.players[alias] = []
        self.__gen_player_guesses()
        print('Added player:', alias)


    # Drop player
    def drop_player(self, alias):
        del self.players[alias]


    # Get the guesses associated with an alias 
    def get_guesses_for_alias(self, alias):
        return self.players[alias]


    def get_win_guess(self):
        return self.win_guess


    # Restart the game
    def restart_game(self):
        self.win_guess = np.random.randint(1, self.max_guess+1)
        self.__gen_player_guesses()
        print("The winning number is now: " + str(self.win_guess))