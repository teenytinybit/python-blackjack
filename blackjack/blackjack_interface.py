# Module for Blackjack inteface class and methods

from cards import Card, BlackjackCardSet

class TextInterface(object):
    def __init__(self):
        self.name = "Text Interface"

    def displayCards(self, cards):
        card_display = ''
        for c in cards:
            if not c.isHidden():
                card_display += (c.getRank() + " of " + c.getSuit()).title() + '\n'
            else:
                card_display += '**Card Hidden**\n'
        card_display = card_display[:-1]
        print(card_display)
        print("- - - - - - - -")

    def displayScore(self, card_set):
        low_score = card_set.getTotals()[0]
        high_score = card_set.getTotals()[1]
        score_display = 'Total value: ' + str(low_score)
        score_display += ' or ' + str(high_score) if high_score > 0 else ''
        print(score_display)
        print("===============")

    def updateCardView(self, hand: BlackjackCardSet):
        self.displayCards(hand.getCards())
        self.displayScore(hand)