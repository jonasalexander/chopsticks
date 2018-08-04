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

	while True:
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

if __name__ == '__main__':
	main()