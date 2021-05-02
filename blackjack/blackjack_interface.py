# Module for Blackjack inteface class and methods
from blackjack_misc import Actions
from cards import Card, BlackjackCardSet

class TextInterface(object):
    def __init__(self):
        self.name = "Text Interface"
        self.MARGIN = 21
        self.BORDER_LENGTH = self.MARGIN + 4

    def _addCardsBorder(self):
        print("- " * (self.BORDER_LENGTH // 2))

    def _addBorder(self):
        print("=" * self.BORDER_LENGTH)

    def _addGameBorder(self):
        print("=" * 54 + "\n")

    def clear(self):
        return

    def close(self):
        print("Game closed. Thank you for playing!\n")

    def displayCards(self, cards):
        card_display = ""
        for c in cards:
            if not c.isHidden():
                card_name = (c.getRank() + " of " + c.getSuit()).title()
                card_display += "| " + card_name.center(self.MARGIN) + " |\n"
            else:
                card_display += "| " + "**Card Hidden**".center(self.MARGIN) + " |\n"
        card_display = card_display[:-1]
        print(card_display)
        self._addCardsBorder()

    def displayScore(self, hand):
        low_score = hand.getTotals()[0]
        high_score = hand.getTotals()[1]
        score_display = "Total value: " + str(low_score)
        score_display += " or " + str(high_score) if high_score > 0 else ""
        print("| " + score_display.center(self.MARGIN) + " |")
        self._addBorder()
        print("")

    def getAction(self, *actions):
        btn_options = [f"'{a.value}'" for a in actions]
        action_msg = ""
        if Actions.SPLIT in actions:
            btn_options.remove(f"'{Actions.SPLIT.value}'")
            action_msg += "\nType 'split' if you'd like to split cards. "
        if Actions.DOUBLE in actions:
            btn_options.remove(f"'{Actions.DOUBLE.value}'")
            action_msg += "\nType 'double' to double the bet. "
        action_msg += f"\nType {' or '.join(btn_options)} to proceed. "

        action = input(action_msg)
        while action not in [a.value for a in actions]:
            action = input(action_msg)
        return Actions(action)

    def greet(self):
        print("Welcome to the game of Blackjack!\n")

    def initializeView(self):
        self._addGameBorder()

    def showOutcomeMessage(self, outcome):
        print(outcome)

    def updateCardView(self, hand: BlackjackCardSet, is_dealer=False):
        whose = "Dealer's" if is_dealer else "Your"
        title = (whose + " cards:").center(self.MARGIN)
        self._addBorder()
        print("| " + title + " |\n| " + " " * self.MARGIN + " |")
        self.displayCards(hand.getCards())
        self.displayScore(hand)

    def wantsToPlay(self):
        btn = ""
        while btn not in ['start', 'exit']:
            btn = input("Please type 'start' to begin or 'exit' to leave: ")
        return btn == 'start'
