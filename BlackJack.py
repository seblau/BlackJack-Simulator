import sys
from random import shuffle

import numpy as np
import scipy.stats as stats
import pylab as pl
import matplotlib.pyplot as plt

from importer.StrategyImporter import StrategyImporter


GAMES = 100
ROUNDS_PER_GAME = 20
SHOE_SIZE = 8
SHOE_PENETRATION = 0.05
BET_SPREAD = 20.0

DECK_SIZE = 52.0
CARDS = {"Ace": 11, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 10, "Queen": 10, "King": 10}
BASIC_OMEGA_II = {"Ace": 0, "Two": 1, "Three": 1, "Four": 2, "Five": 2, "Six": 2, "Seven": 1, "Eight": 0, "Nine": -1, "Ten": -2, "Jack": -2, "Queen": -2, "King": -2}

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
        self.count = 0
        self.count_history = []
        self.decks = decks
        self.cards = self.init_cards()

    def __str__(self):
        s = ""
        for c in self.cards:
            s += "%s\n" % c
        return s

    def init_cards(self):
        """
        Initialize the shoe with shuffled playing cards and set count to zero.
        """
        self.count = 0
        self.count_history.append(self.count)

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
        if self.shoe_penetration() < SHOE_PENETRATION:
            self.reshuffle = True
        card = self.cards.pop()
        self.do_count(card)
        return card

    def do_count(self, card):
        """
        Add the dealt card to current count.
        """
        self.count += BASIC_OMEGA_II[card.name]
        self.count_history.append(self.truecount())

    def truecount(self):
        """
        Returns: The current true count.
        """
        return self.count / (self.decks * self.shoe_penetration())

    def shoe_penetration(self):
        """
        Returns: Ratio of cards that are still in the shoe to all initial cards.
        """
        return len(self.cards) / (DECK_SIZE * self.decks)

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
    def __init__(self, hand=None, dealer_hand=None):
        self.hands = [hand]
        self.dealer_hand = dealer_hand

    def set_hands(self, new_hand, new_dealer_hand):
        self.hands = [new_hand]
        self.dealer_hand = new_dealer_hand

    def play(self, shoe):
        for hand in self.hands:
            # print "Playing Hand: %s" % hand
            self.play_hand(hand, shoe)

    def play_hand(self, hand, shoe):
        if hand.length() < 2:
            if hand.cards[0].name == "Ace":
                hand.cards[0].value = 11
            self.hit(hand, shoe)

        while not hand.busted() and not hand.blackjack():
            if hand.soft():
                flag = SOFT_STRATEGY[hand.value][self.dealer_hand.cards[0].name]
            elif hand.splitable():
                flag = PAIR_STRATEGY[hand.value][self.dealer_hand.cards[0].name]
            else:
                flag = HARD_STRATEGY[hand.value][self.dealer_hand.cards[0].name]

            if flag == 'D':
                if hand.length() == 2:
                    # print "Double Down"
                    hand.doubled = True
                    self.hit(hand, shoe)
                    break
                else:
                    flag = 'H'

            if flag == 'Sr':
                if hand.length() == 2:
                    # print "Surrender"
                    hand.surrender = True
                    break
                else:
                    flag = 'H'

            if flag == 'H':
                self.hit(hand, shoe)
                
            if flag == 'P':
                self.split(hand, shoe)
                
            if flag == 'S': 
                break                   

    def hit(self, hand, shoe):
        c = shoe.deal()
        hand.add_card(c)
        # print "Hitted: %s" % c

    def split(self, hand, shoe):
        self.hands.append(hand.split())
        # print "Splitted %s" % hand
        self.play_hand(hand, shoe)


class Dealer(object):
    """
    Represent the dealer
    """
    def __init__(self, hand=None):
        self.hand = hand

    def set_hand(self, new_hand):
        self.hand = new_hand

    def play(self, shoe):
        while self.hand.value < 17:
            self.hit(shoe)

    def hit(self, shoe):
        c = shoe.deal()
        self.hand.add_card(c)
        # print "Dealer hitted: %s" %c


class Game(object):
    """
    """
    def __init__(self):
        self.shoe = Shoe(SHOE_SIZE)
        self.money = 0.0
        self.stake = 1.0
        self.player = Player()
        self.dealer = Dealer()

    def start(self):
        if self.shoe.truecount() > 6:
            self.stake = BET_SPREAD
        else:
            self.stake = 1.0

        player_hand = Hand([self.shoe.deal(), self.shoe.deal()])
        dealer_hand = Hand([self.shoe.deal()])
        self.player.set_hands(player_hand, dealer_hand)
        self.dealer.set_hand(dealer_hand)
        # print "Dealer Hand: %s" % self.dealer.hand
        # print "Player Hand: %s\n" % self.player.hands[0]

        self.player.play(self.shoe)
        self.dealer.play(self.shoe)

        # print ""
        
        for hand in self.player.hands:
            win = 0.0

            if not hand.surrender:
                if hand.busted():
                    status = "LOST"
                else:
                    if hand.blackjack():
                        if self.dealer.hand.blackjack():
                            status = "PUSH"
                        else:
                            status = "WON 3:2"
                    elif self.dealer.hand.busted():
                        status = "WON"
                    elif self.dealer.hand.value < hand.value:
                        status = "WON"
                    elif self.dealer.hand.value > hand.value:
                        status = "LOST"
                    elif self.dealer.hand.value == hand.value:
                        if self.dealer.hand.blackjack():
                            status = "LOST"  # player's 21 vs dealers blackjack
                        else:
                            status = "PUSH"
            else:
                status = "SURRENDER"

            if status == "LOST":
                win += -1
            elif status == "WON":
                win += 1
            elif status == "WON 3:2":
                win += 1.5
            elif status == "SURRENDER":
                win += -0.5
            if hand.doubled: win *= 2

            win *= self.stake

            self.money += win

            # print "Player Hand: %s %s (Value: %d, Busted: %r, BlackJack: %r, Splithand: %r, Soft: %r, Surrender: %r, Doubled: %r)" % (hand, status, hand.value, hand.busted(), hand.blackjack(), hand.splithand, hand.soft(), hand.surrender, hand.doubled)
        
        # print "Dealer Hand: %s (%d)" % (self.dealer.hand, self.dealer.hand.value)

        if self.shoe.reshuffle:
            self.shoe.reshuffle = False
            self.shoe.cards = self.shoe.init_cards()

    def get_money(self):
        return self.money    


if __name__ == "__main__":
    importer = StrategyImporter(sys.argv[1])
    HARD_STRATEGY, SOFT_STRATEGY, PAIR_STRATEGY = importer.import_player_strategy()

    h = []
    countings = []

    for g in range(GAMES):
        game = Game()

        for i in range(ROUNDS_PER_GAME):
            # print '%s GAME no. %d %s' % (20 * '#', i + 1, 20 * '#')
            game.start()

        h.append(game.get_money())
        countings += game.shoe.count_history

        print "WIN for Game no. %d: %f" % (g + 1, game.get_money())

    sume = 0.0
    for value in h:
        sume += value
    print "Overall: %f" % sume

    h = sorted(h)
    fit = stats.norm.pdf(h, np.mean(h), np.std(h))  #this is a fitting indeed
    pl.plot(h,fit,'-o')
    pl.hist(h,normed=True)      #use this to draw histogram of your data
    pl.show()                   #use may also need add this 

    plt.ylabel('count')
    plt.plot(countings, label='x')
    plt.legend()
    plt.show()
