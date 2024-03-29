#!/usr/bin/env -S PYTHONPATH=../common python3

import numpy as np

class guessingGame:

    # Game constructor
    def __init__(self, maxGuess = 100):
        # Keep a list/mapping of all the players
        self.players = {}

        # This is an INCLUSIVE maxGuess value
        # (i.e: if maxGuess = 100, guesses are in [1,100])
        self.maxGuess = maxGuess
        return

    def getNumPlayers(self):
        return len(self.players.keys())
    
    # Re-generate player guesses whenever a player is added
    def __genPlayerGuesses(self):
        numPlayers = self.getNumPlayers()

        # empty each player's list
        for player in self.players:
            self.players[player] = []

        # generate a list of maxGuess integers in random order
        randIntList = np.random.choice(self.maxGuess, self.maxGuess)

        # Bump up all the values so min(randIntList) == 1
        randIntList = randIntList + 1

        # Convert us back to a python list
        randIntList = list(randIntList)

        currPlayer = 0

        # While there are still integers to hand out,
        # give the next integer to the next player
        while randIntList:
            nextNum = randIntList.pop()
            player = self.players.keys()[currPlayer]
            self.players[player].append(nextNum)
            currPlayer = (currPlayer+1) % getNumPlayers()


        for player in self.players:
            print(player, ': ', self.players[player], sep='')
        
        return

    # Add new player
    def addNewPlayer(self, alias):
        # Gen the guesses for the player
        self.players[alias] = []
        self.__genPlayerGuesses()
        return

    # Drop player
    def dropPlayer(self, alias):
        del self.players[alias]
        return

    # Get the guesses associated with an alias 
    def getGuesses(self, alias):
        return self.players

    # Start game
    def startGame(self):
        return

    # Pause game
    def pauseGame(self):
        return

    # Stop game
    def stopGame(self):
        return

    # Restart the game
    def restartGame(self):
        return



