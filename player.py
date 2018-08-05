from hand import Hand
from model import Model
from global_vars import *

class Player(object):

	num_hands = 2

	def __init__(self, name=None):
		if name is not None:
			self.name = name
		else:
			self.name = "No name"

		self.hands = []
		for i in range(Player.num_hands):
			self.hands.append(Hand(self))

	def __str__(self):
		return "Player with hands: " + ' '.join([hand.__str__() for hand in self.hands])

	def get_hands(self):
		return tuple(self.hands)

	def alive(self):
		return any([hand.num for hand in self.hands])

	def reorder_hands(self):
		self.hands.sort(key=lambda x: x.num)

class ComputerPlayer(Player):

	def __init__(self, model=None, name=None):
		super(ComputerPlayer, self).__init__(name=name)

		if model is None:
			model = Model()
		self.model = model

		self.attacks = []
		self.redistributions = []

	def __str__(self):
		return "Computer" + super(ComputerPlayer, self).__str__()

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

class InteractivePlayer(Player):

	def __init__(self, model=None, name=None):
		super(InteractivePlayer, self).__init__(name=name)

	def __str__(self):
		return "Interactive" + super(InteractivePlayer, self).__str__()

	def turn(self, opponent):
		# TD: get user input
		state = tuple(	[i.num for i in self.hands] + 
						[i.num for i in opponent.hands])
		self_state = state[0:2]
		opponent_state = state[2:4]

		# Ask if user wants to redistribute
		
		print 'Current state of the game is: '
		print self
		print opponent
		if 0 in self_state and all([i%2==0 for i in self_state]):
			redistribute = raw_input("Do you want to redistribute your fingers?(0 for no and 1 for yes) \n--->")
			if redistribute == '1':
				for i, h in enumerate(self.hands):
					if h.num == 0:
						i1 = i
					else:
						i2 = i
				val = self.hands[i2].num/2
				self.hands[i1].num = val
				self.hands[i2].num = val
				print 'Hands redistributed. New state of the game is: '
				print self
				print opponent
				state = tuple(	[i.num for i in self.hands] + 
						[i.num for i in opponent.hands])
				self_state = state[0:2]
				opponent_state = state[2:4]
			elif redistribute == '0':
				print 'Hands not redistributed'
			else:
				print 'Didn\'t get a 0 or 1 as expected for redistribution quesiton. Exiting'
				return False

		# Ask which hand user wants to use to attack
		if 0 in self_state or self_state[0] == self_state[1]:
			print 'You can only use one of your hands to attack.'
			self_choice = 1
		else:
			self_choice_str = raw_input('Which of your hands would you like to use to attack? (0-indexed) \n--->')
			try:
				self_choice = int(self_choice_str)
				if self_choice not in [0, 1]:
					raise ValueError
			except ValueError:
				print 'Didn\'t get a 0 or 1 as expected for self_choice quesiton. Exiting'
				return False

		# Ask which hand user wants to attack
		if 0 in opponent_state or opponent_state[0] == opponent_state[1]:
			print 'You can only attack one of your opponent\'s hands.'
			opponent_choice = 1
		else:
			opponent_choice_str = raw_input('Which of your opponent\'s hands would you like to attack? (0-indexed) \n--->')
			try:
				opponent_choice = int(opponent_choice_str)
				if opponent_choice not in [0, 1]:
					raise ValueError
			except ValueError:
				print 'Didn\'t get a 0 or 1 as expected for opponent_choice question. Exiting'
				return False

		opponent.hands[opponent_choice].add(self.hands[self_choice])
		return True

