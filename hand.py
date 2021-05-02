class Hand:

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
            raise ValueError(
                "Tried to add to hand with zero fingers: self.num - %s, hand - %s"
                % (self.num, hand)
            )

        self.player.reorder_hands()
