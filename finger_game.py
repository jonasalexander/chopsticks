import random
import pprint
import pickle
import os

DEBUG = True
LOAD = True
DIFF_MODELS = False
KEEP_B_STUPID = False
FRESH_START = False

class Hand():

	max_num = 5
	
	def __init__(self, player):
		self.num = 1
		self.player = player

	def __str__(self):
		return "Hand with %s fingers" % self.num

	def add(self, hand):
		if self.num + hand.num > Hand.max_num:
			self.num = 0
		elif not self.num == 0:
			self.num += hand.num
		else:
			raise ValueError("Tried to add to hand with zero fingers: self.num - %s, hand - %s" % (self.num, hand))

		self.player.reorder_hands()

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

class Player():

	num_hands = 2

	def __init__(self, model=None, name=None):
		if name is not None:
			self.name = name
		else:
			self.name = "No name"

		self.hands = []
		for i in range(Player.num_hands):
			self.hands.append(Hand(self))

		if model is None:
			model = Model()
		self.model = model

		self.attacks = []
		self.redistributions = []

	def __str__(self):
		return "Player with hands: " + ' '.join([hand.__str__() for hand in self.hands])

	def get_hands(self):
		return tuple(self.hands)

	def alive(self):
		return any([hand.num for hand in self.hands])

	def reorder_hands(self):
		self.hands.sort(key=lambda x: x.num)

	def turn(self, opponent):
		state = tuple(	[i.num for i in self.hands] + 
						[i.num for i in opponent.hands])

		# redistribute based on probability
		(had_option, redistribute) = self.model.redistribute(state)
		if had_option:
			self.redistributions.append((state, redistribute))

		if redistribute:
			for i, h in enumerate(self.hands):
				if h.num == 0:
					i1 = i
				else:
					i2 = i
			val = self.hands[i2].num/2
			self.hands[i1].num = val
			self.hands[i2].num = val
			if DEBUG:
				print 'Player ' + self.name + ' decided to split fingers'

		# attack based on probability
		(num, indices) = self.model.attack(state)

		if DEBUG:
			print 'Player '+ self.name + '\' s turn'
			print 'state: ' + str(state)
			print 'Move was to add hand %s to hand %s' % \
				(self.hands[indices[0]], opponent.hands[indices[1]])

		opponent.hands[indices[1]].add(self.hands[indices[0]])

		self.attacks.append((state, num))


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
		a = Player(model=model, name='A')
		if DIFF_MODELS:
			b = Player(model=model2, name='B')
		elif KEEP_B_STUPID:
			b = Player(model=Model(), name='B')
		else:
			b = Player(model=model, name='B')
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

