import sys
from random import shuffle

from importer.StrategyImporter import StrategyImporter


ROUNDS = 100000
SHOE_SIZE = 8
SHOE_PENETRATION = 0.2
DECK_SIZE = 52.0
CARDS = {"Ace": 11, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 10, "Queen": 10, "King": 10}

HARD_STRATEGY = {}
SOFT_STRATEGY = {}
PAIR_STRATEGY = {}


class Card(object):
    """
    Represents a playing card with name and value.
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return "%s" % self.name


class Shoe(object):
    """
    Represents the shoe, which consists of a number of card decks.
    """
    reshuffle = False

    def __init__(self, decks):
        self.decks = decks
        self.cards = self.init_cards()

    def __str__(self):
        s = ""
        for c in self.cards:
            s += "%s\n" % c
        return s

    def init_cards(self):
        """
        Initialize the shoe with shuffled playing cards.
        """
        cards = []
        for d in range(self.decks):
            for c in CARDS:
                for i in range(0, 4):
                    cards.append(Card(c, CARDS[c]))
        shuffle(cards)
        return cards

    def deal(self):
        """
        Returns:    The next card off the shoe. If the shoe penetration is reached,
                    the shoe gets reshuffled.
        """
        if (len(self.cards) / (DECK_SIZE * self.decks)) < SHOE_PENETRATION:
            self.reshuffle = True
        return self.cards.pop()


class Hand(object):
    """
    Represents a hand, either from the dealer or from the player
    """
    _value = 0
    _aces = []
    _aces_soft = 0
    splithand = False
    surrender = False
    doubled = False

    def __init__(self, cards):
        self.cards = cards

    def __str__(self):
        h = ""
        for c in self.cards:
            h += "%s " % c
        return h

    @property
    def value(self):
        """
        Returns: The current value of the hand (aces are either counted as 1 or 11).
        """
        self._value = 0
        for c in self.cards:
            self._value += c.value

        if self._value > 21 and self.aces_soft > 0:
            for ace in self.aces:
                if ace.value == 11:
                    self._value -= 10
                    ace.value = 1
                    if self._value <= 21:
                        break

        return self._value

    @property
    def aces(self):
        """
        Returns: The all aces in the current hand.
        """
        self._aces = []
        for c in self.cards:
            if c.name == "Ace":
                self._aces.append(c)
        return self._aces

    @property
    def aces_soft(self):
        """
        Returns: The number of aces valued as 11
        """
        self._aces_soft = 0
        for ace in self.aces:
            if ace.value == 11:
                self._aces_soft += 1
        return self._aces_soft

    def soft(self):
        """
        Determines whether the current hand is soft (soft means that it consists of aces valued at 11).
        """
        if self.aces_soft > 0:
            return True
        else:
            return False

    def splitable(self):
        """
        Determines if the current hand can be splitted.
        """
        if self.length() == 2 and self.cards[0].name == self.cards[1].name:
            return True
        else:
            return False

    def blackjack(self):
        """
        Check a hand for a blackjack. Note: 3x7 is also counted as a blackjack.
        """
        if not self.splithand and self.value == 21:
            if all(c.value == 7 for c in self.cards):
                return True
            elif self.length() == 2:
                return True
            else:
                return False
        else:
            return False

    def busted(self):
        """
        Checks if the hand is busted.
        """
        if self.value > 21:
            return True
        else:
            return False

    def add_card(self, card):
        """
        Add a card to the current hand.
        """
        self.cards.append(card)

    def split(self):
        """
        Split the current hand.
        Returns: The new hand created from the split.
        """
        self.splithand = True
        c = self.cards.pop()
        new_hand = Hand([c])
        new_hand.splithand = True
        return new_hand

    def length(self):
        """
        Returns: The number of cards in the current hand.
        """
        return len(self.cards)


class Player(object):
    """
    Represent a player
    """
    def __init__(self, hand, dealer_hand, shoe):
        self.hands = [hand]
        self.dealer_hand = dealer_hand
        self.shoe = shoe

    def play(self):
        for hand in self.hands:
            print "Playing Hand: %s" % hand
            self.play_hand(hand)

    def play_hand(self, hand):
        if hand.length() < 2:
            if hand.cards[0].name == "Ace":
                hand.cards[0].value = 11
            self.hit(hand)

        while not hand.busted() and not hand.blackjack():
            if hand.soft():
                flag = SOFT_STRATEGY[hand.value][dealer_hand.cards[0].name]
            elif hand.splitable():
                flag = PAIR_STRATEGY[hand.value][dealer_hand.cards[0].name]
            else:
                flag = HARD_STRATEGY[hand.value][dealer_hand.cards[0].name]

            if flag == 'D':
                if hand.length() == 2:
                    print "Double Down"
                    hand.doubled = True
                    self.hit(hand)
                    break
                else:
                    flag = 'H'

            if flag == 'Sr':
                if hand.length() == 2:
                    print "Surrender"
                    hand.surrender = True
                    break
                else:
                    flag = 'H'

            if flag == 'H':
                self.hit(hand)
                
            if flag == 'P':
                self.split(hand)
                
            if flag == 'S': 
                break                   

    def hit(self, hand):
        c = self.shoe.deal()
        hand.add_card(c)
        print "Hitted: %s" % c

    def split(self, hand):
        self.hands.append(hand.split())
        print "Splitted %s" % hand
        self.play_hand(hand)


class Dealer(object):
    """
    Represent the dealer
    """
    def __init__(self, hand, shoe):
        self.hand = hand
        self.shoe = shoe

    def play(self):
        while self.hand.value < 17:
            self.hit()

    def hit(self):
        c = self.shoe.deal()
        self.hand.add_card(c)
        print "Dealer hitted: %s" %c


if __name__ == "__main__":
    importer = StrategyImporter(sys.argv[1])
    HARD_STRATEGY, SOFT_STRATEGY, PAIR_STRATEGY = importer.import_player_strategy()

    shoe = Shoe(SHOE_SIZE)

    money = 0.0

    for i in range(ROUNDS):
        print "############################################################ GAME no. %d ############################################################" % (i + 1)

        player_hand = Hand([shoe.deal(), shoe.deal()])
        dealer_hand = Hand([shoe.deal()])
        player = Player(player_hand, dealer_hand, shoe)
        dealer = Dealer(dealer_hand, shoe)
        print "Dealer Hand: %s" % dealer.hand
        print "Player Hand: %s\n" % player.hands[0]
    
        player.play()
        dealer.play()
    
        print ""
        for hand in player.hands:
            if not hand.surrender:
                if hand.busted():
                    status = "LOST"
                else:
                    if dealer.hand.busted():
                        status = "WON"
                    elif dealer.hand.value < hand.value:
                        status = "WON"
                    elif dealer.hand.value > hand.value:
                        status = "LOST"
                    elif dealer.hand.value == hand.value:
                        status = "PUSH"
                    if hand.blackjack():
                        if dealer.hand.blackjack():
                            status = "PUSH"
                        else:
                            status = "WON 3:2"
            else:
                status = "SURRENDER"
    
            print "Player Hand: %s %s (Value: %d, Busted: %r, BlackJack: %r, Splithand: %r, Soft: %r, Surrender: %r, Doubled: %r)" % (hand, status, hand.value, hand.busted(), hand.blackjack(), hand.splithand, hand.soft(), hand.surrender, hand.doubled)
        print "Dealer Hand: %s (%d)" % (dealer.hand, dealer.hand.value)

        win = 0.0
        if status == "LOST":
            win = -1
        elif status == "WON":
            win = 1
        elif status == "WON 3:2":
            win = 1.5
        elif status == "SURRENDER":
            win = -0.5
        if hand.doubled: win *= 2

        money += win

        if shoe.reshuffle:
            print "\nReshuffle Shoe"
            shoe.reshuffle = False
            shoe.cards = shoe.init_cards()
    print "WIN %f" % money
