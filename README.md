# Chopsticks

This repository contains a reinforcement-learning (RL) artificial intelligence (AI) algorithm that learns to play the [Chopsticks Game](https://en.wikipedia.org/wiki/Chopsticks_(hand_game)).

## Purpose

The purpose of this code is to practice object-oriented programming and implementing an AI algorithm.

# Usage

## Training

To train the RL agent, run `python simple_train.py`. This script has various arguments to configure how it runs, run `python simple_train.py -h` to see the list of arguments and their descriptions.

## Interactive Mode

To play, simply run `python interactive.py` and follow the command line prompts to submit your moves.

# Agent

The RL agent faces two decisions each turn and learns context-specific values for each action if can take. It acts probabilistically to manage the explore-exploit tradeoff, using a simple ['matchbox' strategy](https://en.wikipedia.org/wiki/Donald_Michie#Career_and_research).

The first decision is which hand to choose for attacking and which opponent hand to attack.

The second decision is whether or not the agent should redistribute the fingers on one hand, which is only possible if one hand has 0 fingers and the other has 2 or 4 fingers.

The state dictionary used as a key for each decision is a tuple, containing the player's hand and opponents hands. Four fields that each can take values 0 through 5 makes for roughly 1,200 states to learn.


# TODO

- [ ] Clean up printing/debug mode
