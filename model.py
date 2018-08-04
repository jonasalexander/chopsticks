import random

from global_vars import *

class Model():

	def __init__(self, attack_dict=None, redistribution_dict=None):
		if attack_dict is None:
			attack_dict = {}
		self._attack_dict = attack_dict

		if redistribution_dict is None:
			redistribution_dict = {}
		self._redistribution_dict = redistribution_dict

	def __str__(self):
		return 'Attack dict: {0} \nRedistribute dict: {1}'.format(self._attack_dict, self._redistribution_dict)

	def attack(self, state):
		# state is a tuple of 
		# (attacker hand1, attacker hand2, opponent hand1, opponent hand2)
		# where hands are ordered by number of fingers to avoid duplicates

		num_hands = len([i for i in state if i>0])
		if not state in self._attack_dict:
			if num_hands == 4:
				self._attack_dict[state] = {0: 1, 1: 1, 2: 1, 3: 1}
			if num_hands == 3:
				self._attack_dict[state] = {0: 1, 1: 1}
			if num_hands == 2:
				self._attack_dict[state] = {0: 1}

		r = random.randint(1, sum(self._attack_dict[state].values()))
		rorig = r
		# figure out which hands this chioce corresponds to
		for option in self._attack_dict[state]:
			if r <= self._attack_dict[state][option]:
				# this is the option we want, now we just have to figure out
				# what indices this option corresponds to
				possible_indices = [i for i, e in enumerate(state) if e != 0]
				if len(possible_indices) == 2:
					indices = (possible_indices[0], possible_indices[1]-2)
				elif len(possible_indices) == 3:
					if possible_indices[1] > 1:
						# the second player has two hands left
						if option == 0:
							indices = (possible_indices[0], possible_indices[1]-2)
						elif option == 1:
							indices = (possible_indices[0], possible_indices[2]-2)
						else:
							raise ValueError("Receive unexpected state-options matchup in Model.attack(): state - %s, options - %s" % (state, self._attack_dict[state]))
					else:
						# the first player has two hands left
						if option == 0:
							indices = (possible_indices[0], possible_indices[2]-2)
						elif option == 1:
							indices = (possible_indices[1], possible_indices[2]-2)
						else:
							raise ValueError("Receive unexpected state-options matchup in Model.attack(): state - %s, options - %s" % (state, self._attack_dict[state]))
				elif len(possible_indices) == 4:
					if option == 0:
						indices = (possible_indices[0], possible_indices[2]-2)
					elif option == 1:
						indices = (possible_indices[0], possible_indices[3]-2)
					elif option == 2:
						indices = (possible_indices[1], possible_indices[2]-2)
					elif option == 3:
						indices = (possible_indices[1], possible_indices[3]-2)
					else:
						raise ValueError("Receive unexpected state-options matchup in Model.attack(): state - %s, options - %s" % (state, self._attack_dict[state]))
				else:
					raise ValueError("Received unexpected length of possible_indices: %s" % possible_indices)
				return (option, indices)
			else:
				r -= self._attack_dict[state][option]

		raise ValueError("Got a random choice %s outside the limit of options in self._attack_dict[state] %s with state %s." % (rorig, self._attack_dict[state], state))

	def redistribute(self, state):
		# can only do it if one hand has 0 fingers
		self_state = state[0:2]
		if not 0 in self_state:
			return (False, False)

		# and other hand has even fingers
		if not all([i%2==0 for i in self_state]):
			return (False, False)

		if state not in self._redistribution_dict:
			self._redistribution_dict[state] = {False: 1, True: 1}

		r = random.randint(1, sum(self._redistribution_dict[state].values()))

		# return True or False depending on the state the choice corresponds to
		return (True, r <= self._redistribution_dict[state][True])

	def update(self, moves, redistributions, was_good):
		if DEBUG:
			
			print 'In update...'
			print 'moves: ' + str(moves)
			print 'redistributions: ' + str(redistributions)
			print 'was_good: ' + str(was_good)
		for move in moves:
			state = move[0]
			decision = move[1]
			if DEBUG:
				print 'state: ' + str(state)
				print 'decision: ' + str(decision)
				print 'Before: ' + str(self._attack_dict[state])
			if was_good:
				self._attack_dict[state][decision] += 1
			else:
				if self._attack_dict[state][decision] > 1:
					self._attack_dict[state][decision] -= 1
				else:
					for i in self._attack_dict[state]:
						self._attack_dict[state][i] += 1
					self._attack_dict[state][decision] -= 1
			if DEBUG:
				print 'After: ' + str(self._attack_dict[state])

		for r in redistributions:
			state = r[0]
			decision = r[1]
			if DEBUG:
				print 'state: ' + str(state)
				print 'decision: ' + str(decision)
				print 'Before: ' + str(self._redistribution_dict[state])
			if was_good:
				self._redistribution_dict[state][decision] += 1
			else:
				self._redistribution_dict[state][not decision] += 1
			if DEBUG:
				print 'After: ' + str(self._redistribution_dict[state])
