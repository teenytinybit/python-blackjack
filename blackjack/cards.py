# Module for cards class and methods

SUITS = ('hearts','spades','diamonds','clubs')
RANKS = (
        ('ace', [1, 11]), ('two', [2]), ('three', [3]), ('four', [4]), ('five', [5]), 
        ('six', [6]), ('seven', [7]), ('eight', [8]), ('nine', [9]), ('ten', [10]), 
        ('jack', [10]), ('queen', [10]), ('king', [10])
    )

class Card(object):
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.setValue(rank)
        self.hidden = False

    def setValue(self, rank):
        self.value = []
        for rec in RANKS:
            if rank == rec[0]:
                self.value = rec[1]
                break

    def toggleVisibility(self):
        self.hidden = not self.hidden

    def isHidden(self):
        return self.hidden

    def getSuit(self):
        return self.suit

    def getRank(self):
        return self.rank

    def getValue(self):
        return self.value

class BlackjackCardSet(object):
    def __init__(self, split=False):
        self.cards = []
        self.totals = [0] * 2
        self.has_ace = False
        self.split = split

    def addCard(self, card: Card):
        self.cards.append(card)
        if card.getRank() == RANKS[0][0]:
            self.has_ace = True
        self.__updateTotal()

    def getCard(self, idx):
        return self.cards[idx]

    def __updateTotal(self):
        low, high = 0, 1
        ace_n = 0
        totals = [0] * 2
        for c in self.cards:
            if not c.isHidden():
                totals[low] = totals[low] + c.getValue()[low]
                if c.getRank() == RANKS[0][0]:  # count an ace
                    ace_n += 1
        # use alt value for 1 ACE only, if the set has many
        if ace_n > 0:
            totals[high] = totals[low] + 10
        self.totals = totals

    def hideCard(self, idx):
        if not self.cards[idx].isHidden():
            self.cards[idx].toggleVisibility()
        self.__updateTotal()

    def revealCard(self, idx):
        if self.cards[idx].isHidden():
            self.cards[idx].toggleVisibility()
        self.__updateTotal()

    def doSplit(self):
        split_set = BlackjackCardSet(split=True)
        split_set.addCard(self.cards.pop())
        self.__updateTotal()
        self.split = True
        return split_set
    
    def hasAce(self):
        return self.has_ace
    
    def isSplit(self):
        return self.split

    def canSplit(self):
        return self.cards[0].getValue() == self.cards[1].getValue()

    def getTotals(self):
        return self.totals

    def getCards(self):
        return self.cards