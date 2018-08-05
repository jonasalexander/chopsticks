import pprint
import pickle
import os

from model import Model
from hand import Hand
from player import ComputerPlayer
from global_vars import *


def game(player1, player2):
	# Gameplay
	while True:

		player1.turn(player2)

		if not player2.alive():
			return True
			# 'Player B loses'

		player2.turn(player1)

		if not player1.alive():
			return False
			# 'Player A loses'


def main():

	# Initialization
	attack_dict = None
	if os.path.isfile("attack_dict.pickle") and LOAD and not FRESH_START:
		attack_dict = pickle.load(open("attack_dict.pickle", "rb"))

	attack_dict2 = None
	if os.path.isfile("attack_dict2.pickle") and LOAD and DIFF_MODELS and not FRESH_START:
		attack_dict2 = pickle.load(open("attack_dict2.pickle", "rb"))

	redistribution_dict = None
	if os.path.isfile("redistribution_dict.pickle") and LOAD and not FRESH_START:
		redistribution_dict = pickle.load(open("redistribution_dict.pickle", "rb"))

	redistribution_dict2 = None
	if os.path.isfile("redistribution_dict2.pickle") and LOAD and DIFF_MODELS and not FRESH_START:
		redistribution_dict2 = pickle.load(open("redistribution_dict2.pickle", "rb"))

	model = Model(attack_dict=attack_dict, redistribution_dict=redistribution_dict)
	model2 = Model(attack_dict=attack_dict2, redistribution_dict=redistribution_dict2)

	# Iterative gameplay
	num_a_wins = 0
	num_b_wins = 0
	num_iterations = 1000
	if DEBUG:
		num_iterations = 1
	for i in range(num_iterations):
		a = ComputerPlayer(model=model, name='A')
		if DIFF_MODELS:
			b = ComputerPlayer(model=model2, name='B')
		elif KEEP_B_STUPID:
			b = ComputerPlayer(model=Model(), name='B')
		else:
			b = ComputerPlayer(model=model, name='B')
		a_wins = game(a, b)
		if a_wins:
			if DEBUG:
				print 'Player B loses'
			a.model.update(a.attacks, a.redistributions, True)
			b.model.update(b.attacks, b.redistributions, False)
			num_a_wins += 1
		else:
			if DEBUG:
				print 'Player A loses'
			a.model.update(a.attacks, a.redistributions, False)
			b.model.update(b.attacks, b.redistributions, True)
			num_b_wins += 1

		if DEBUG:
			print 'A\'s attacks: %s' % a.attacks
			print 'B\'s attacks: %s' % b.attacks

	# Look at model(s) that evolved
	if DEBUG:
		pprint.pprint(a.model._attack_dict)
		if DIFF_MODELS:
			pprint.pprint(b.model._attack_dict)
		pprint.pprint(a.model._redistribution_dict)
		if DIFF_MODELS:
			pprint.pprint(b.model._redistribution_dict)

	if LOAD:
		pickle.dump(a.model._attack_dict, open("attack_dict.pickle", "wb"))
		pickle.dump(a.model._redistribution_dict, open("redistribution_dict.pickle", "wb"))
		if DIFF_MODELS:
			pickle.dump(b.model._attack_dict, open("attack_dict2.pickle", "wb"))
			pickle.dump(b.model._redistribution_dict, open("redistribution_dict2.pickle", "wb"))


	print num_a_wins
	print num_b_wins

if __name__ == '__main__':
	main()

