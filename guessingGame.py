#!/usr/bin/env -S PYTHONPATH=../common python3

import numpy as np
import random
from threading import Lock


MAX_GUESS = 100

class GuessingGame:

    # Game constructor
    def __init__(self, max_guess = MAX_GUESS):
        # Keep a list/mapping of all the players
        self.players = {}
        self.lock = Lock()

        # This is an INCLUSIVE maxGuess value
        # (i.e: if maxGuess = 100, guesses are in [1,100])
        self.max_guess = max_guess
        self.win_guess = np.random.randint(1, self.max_guess+1) # generate a random winning number
        # print('Winning number is: ', self.win_guess)
    

    # get the number of players in the game
    def get_num_players(self):
        return len(self.players.keys())
    

    # Re-generate guesses for all players
    def __gen_player_guesses(self):

        # empty each player's list
        self.lock.acquire()
        for player in self.players.items():
            # self.lock.acquire()
            self.players[player] = []
            # self.lock.release()
        self.lock.release()

        # generate a list of maxGuess integers in random order
        # randIntList = np.random.choice(self.maxGuess, self.maxGuess)
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

            self.lock.acquire()
            player = players_list[curr_player]
            self.players[player].append(next_num)
            self.lock.release()

            curr_player = (curr_player+1) % self.get_num_players()

        for player in self.players:
            self.lock.acquire()
            print(player, ': ', self.players[player], sep='')
            self.lock.release()
        

    # Add new player
    def add_new_player(self, alias):
        # ReGen the guesses for all the players
        self.lock.acquire()
        self.players[alias] = []
        self.lock.release()

       # self.__gen_player_guesses()
        print('Added player:', alias)


    # Drop a player
    def drop_player(self, alias):
        self.lock.acquire()
        del self.players[alias]
        self.lock.release()


    # Get the guesses associated with an alias 
    def get_guesses_for_alias(self, alias):
        self.lock.acquire()
        res = self.players[alias]
        self.lock.release()
        return res


    # Get the winning number 
    def get_win_guess(self):
        return self.win_guess


    # Restart the game
    def restart_game(self):
        self.lock.acquire()
        self.win_guess = np.random.randint(1, self.max_guess+1)
        self.lock.release()
        self.__gen_player_guesses()
        print("The winning number is now: " + str(self.win_guess))