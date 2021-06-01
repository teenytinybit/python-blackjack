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
        self._setValue(rank)
        self.hidden = False

    def getSuit(self):
        return self.suit

    def getRank(self):
        return self.rank

    def getValue(self):
        return self.value

    def isHidden(self):
        return self.hidden

    def _setValue(self, rank):
        self.value = []
        for rec in RANKS:
            if rank == rec[0]:
                self.value = rec[1]
                break

    def toggleVisibility(self):
        self.hidden = not self.hidden

    def __str__(self):
        return self.rank + " of " + self.suit

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return (self.rank == other.rank and self.suit == other.suit)

class BlackjackCardSet(object):
    def __init__(self, no_split=False):
        self.cards = []
        self.score = [0] * 2
        self.has_ace = False
        self.no_split = no_split
        self.blackjack = False

    def addCard(self, card: Card):
        self.cards.append(card)
        if card.getRank() == RANKS[0][0]:
            self.has_ace = True
        self._updateTotal()

    def canSplit(self):
        if len(self.cards) == 2 and not self.no_split:
            return self.cards[0].getValue() == self.cards[1].getValue()
        return False

    def doSplit(self):
        split_set = BlackjackCardSet(no_split=self.cards[0].getRank() == RANKS[0][0])
        split_set.addCard(self.cards.pop())
        self._updateTotal()
        self.no_split = True
        return split_set
    
    def getCard(self, idx):
        return self.cards[idx]

    def getCards(self):
        return self.cards

    def getScore(self):
        return self.score

    def hasAce(self):
        return self.has_ace

    def hasBlackjack(self):
        return self.blackjack

    def hideCard(self, idx):
        if not self.cards[idx].isHidden():
            self.cards[idx].toggleVisibility()
        self._updateTotal()

    def isSplitDisabled(self):
        return self.no_split

    def isSplitFromAce(self):
        if self.no_split and len(self.cards) > 0:
            return self.cards[0].getRank() == RANKS[0][0]
        return False

    def revealCard(self, idx):
        if self.cards[idx].isHidden():
            self.cards[idx].toggleVisibility()
        self._updateTotal()

    def _updateTotal(self):
        low, high = 0, 1
        visible_ace = 0
        full_score = [0] * 2
        visible_score = [0] * 2
        for c in self.cards:
            if not c.isHidden():
                visible_score[low] = visible_score[low] + c.getValue()[low]
                if c.getRank() == RANKS[0][0]:  # count an ace
                    visible_ace += 1
            full_score[low] = full_score[low] + c.getValue()[low]
        # use alt value for 1 ACE only, if the set has many
        if visible_ace > 0:
            visible_score[high] = visible_score[low] + 10
        if self.has_ace:
            full_score[high] = full_score[low] + 10
        self.score = visible_score
        self.blackjack = 21 in full_score and len(self.cards) == 2

    def __str__(self):
        cards_str = ""
        for c in self.cards:
            cards_str += str(c) + "\n"
        cards_str = cards_str[:-1]
        return cards_str

    def __eq__(self, other):
        if not isinstance(other, BlackjackCardSet):
            return NotImplemented
        if len(self.cards) != len(other.cards):
            return False
        
        used_idx = []
        for c in self.cards:
            for i in range(len(other.cards)):
                if (c == other.cards[i]) and (i not in used_idx):
                    used_idx.append(i)
                    break
        return len(used_idx) == len(self.cards)