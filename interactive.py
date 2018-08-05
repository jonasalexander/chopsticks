import pickle
import os

from player import ComputerPlayer, InteractivePlayer
from model import Model

def main():
	if (not os.path.isfile("attack_dict.pickle") or 
		not os.path.isfile("redistribution_dict.pickle")):
		print 'Create strategy pickles first.'
		return

	attack_dict = pickle.load(open("attack_dict.pickle", "rb"))
	redistribution_dict = pickle.load(open("redistribution_dict.pickle", "rb"))

	model = Model(attack_dict=attack_dict, redistribution_dict=redistribution_dict)

	a = ComputerPlayer(model=model, name='Computer')
	name = raw_input('Enter your name:\n')
	b = InteractivePlayer(name=name)

	start_str = raw_input('Should the computer start? (0 for no and 1 for yes)')
	try:
		start = int(start_str)
		if start not in [0, 1]:
			raise ValueError
	except ValueError:
		print 'Didn\'t get a 0 or 1 as expected for start_str question. Exiting'
		return

	while True:
		if start == 1:
			a.turn(b)

			if not b.alive():
				print b.name + ' loses'
				break

			turn_success = b.turn(a)

			if not turn_success:
				return

			if not a.alive():
				print 'Computer loses'
				break
		elif start == 0:
			turn_success = b.turn(a)

			if not turn_success:
				return

			if not a.alive():
				print 'Computer loses'
				break

			a.turn(b)

			if not b.alive():
				print b.name + ' loses'
				break

	print 'Even if you just won, the computer got smarter soo...'
	pickle.dump(a.model._attack_dict, open("attack_dict.pickle", "wb"))
	pickle.dump(a.model._redistribution_dict, open("redistribution_dict.pickle", "wb"))

if __name__ == '__main__':
	main()