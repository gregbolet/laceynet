#!/usr/bin/env python3

class WorkerData:

    # 0 = waiting to start
    # 1 = running
    # 2 = paused
    # 3 = stopped -- waiting for restart
    status = 0

    # The list of numbers this node will be "guessing"
    numbersToGuess = []

    # Current index of the number being guessed
    currGuess = 0

    # Netowrk identifiers for the worker assigned this data
    ipAddr = ''
    networkAlias = ''
