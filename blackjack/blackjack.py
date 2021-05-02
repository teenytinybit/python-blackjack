# Game of Blackjack
import argparse
import blackjack_interface
from blackjack_misc import Actions
from random import randint
from cards import Card, BlackjackCardSet, SUITS, RANKS

BLACKJACK = 21
MAX_HANDS = 4

class BlackjackApp(object):
    def __init__(self, interface):
        self.name = "Blackjack Game"
        self.interface = interface
        self.win = None

    def drawCard(self):
        # generate a random suit out of 4 possible
        suit = SUITS[randint(0, 3)]
        # generate a random card out of 13 possible
        rank = RANKS[randint(0, 12)][0]
        return Card(suit, rank)

    def canPlay(self, hand: BlackjackCardSet, is_dealer=False):
        can_play = True

        if is_dealer and hand.hasAce():
            can_play = hand.getTotals()[1] < 17
        elif is_dealer:
            can_play = hand.getTotals()[0] < 17
        else:
            can_play = hand.getTotals()[0] < 21 and hand.getTotals()[1] != 21
            if hand.isSplit():
                first_card = hand.getCard(0)
                can_play = can_play and first_card.getRank() != RANKS[0][0]    # if was not split from ace

        return can_play

    def isSuccessful(self, hand: BlackjackCardSet):
        if hand.getTotals()[0] > 21:
            return False
        return True

    def playHand(self, hand: BlackjackCardSet, is_dealer=False):
        action = Actions.HIT
        while self.canPlay(hand, is_dealer):
            if not is_dealer:
                action = self.interface.getAction(Actions.HIT, Actions.STAND)
            if action == Actions.HIT:
                hand.addCard(self.drawCard())
                self.interface.updateCardView(hand, is_dealer=is_dealer)
            elif action == Actions.STAND:
                break

    def getScore(self, hand: BlackjackCardSet):
        score = hand.getTotals()[1] if (0 < hand.getTotals()[1] <= 21) \
                                    else hand.getTotals()[0]
        return score

    def playRound(self):
        player_hand = [BlackjackCardSet()]
        dealer_hand = BlackjackCardSet()
        hidden_idx = 0
        tie_msg, win_msg, loss_msg = "It's a tie!\n", "You won!\n", "You lost!\n"
        # deal 2 initial cards for both
        for i in range(2):
            player_hand[0].addCard(self.drawCard())
            dealer_hand.addCard(self.drawCard())
        # hide the 1st card
        dealer_hand.hideCard(hidden_idx)

        """
        TEST CODE =========================
        """
        # player_hand = [BlackjackCardSet()]
        # player_hand[0].addCard(Card('hearts', 'nine'))
        # player_hand[0].addCard(Card('spades', 'nine'))
        """
        TEST CODE =========================
        """

        self.interface.updateCardView(player_hand[0])
        self.interface.updateCardView(dealer_hand, is_dealer=True)

        # analyse player's cards for a NATURAL Blackjack
        if BLACKJACK in player_hand[0].getTotals():
            # compare to dealer's cards if NATURAL Blackjack
            dealer_hand.revealCard(hidden_idx)
            self.interface.updateCardView(dealer_hand, is_dealer=True)
            if BLACKJACK in dealer_hand.getTotals():
                self.interface.showOutcomeMessage(tie_msg)
            else:
                self.interface.showOutcomeMessage("Blackjack! " + win_msg)
            return

        # analyse dealer's cards for a NATURAL Blackjack (if up card is 11 or 10)
        if any(x in dealer_hand.getTotals() for x in [10, 11]):
            dealer_hand.revealCard(hidden_idx)
            if BLACKJACK in dealer_hand.getTotals():
                self.interface.updateCardView(dealer_hand, is_dealer=True)
                self.interface.showOutcomeMessage("Dealer's got Blackjack! " + loss_msg)
                return
            else:
                dealer_hand.hideCard(hidden_idx)

        # allow splitting 2 same value cards, up to 4 hands allowed
        # player Hits or Stands 
        valid_hands = []
        for i in range(MAX_HANDS):
            if len(player_hand[i].getCards()) < 2:
                player_hand[i].addCard(self.drawCard())
                self.interface.updateCardView(player_hand[i])
            if i < MAX_HANDS - 1 and player_hand[i].canSplit():
                action = self.interface.getAction(Actions.HIT, Actions.STAND, Actions.SPLIT)
                if action == Actions.STAND:
                    break
                if action == Actions.SPLIT:
                    player_hand.append(player_hand[i].doSplit())
                player_hand[i].addCard(self.drawCard())
                self.interface.updateCardView(player_hand[i])
                self.playHand(player_hand[i])
                valid_hands.append(self.isSuccessful(player_hand[i]))
                if valid_hands[-1] == False:
                    self.interface.showOutcomeMessage("Bust!\n")
            else:
                self.playHand(player_hand[i])
                valid_hands.append(self.isSuccessful(player_hand[i]))
                if valid_hands[-1] == False:
                    self.interface.showOutcomeMessage("Bust!\n")
                break
        valid_indices = [i for i in range(len(valid_hands)) if valid_hands[i]]
        
        # dealer Hits until result >= 17
        dealer_hand.revealCard(hidden_idx)
        self.interface.updateCardView(dealer_hand, is_dealer=True)
        if len(valid_indices) == 0:
            self.interface.showOutcomeMessage(loss_msg)
            return

        self.playHand(dealer_hand, is_dealer=True)
        if not self.isSuccessful(dealer_hand):
            self.interface.showOutcomeMessage("Dealer bust! " + win_msg)
            return

        # compare results to player
        dealer_high = self.getScore(dealer_hand)
        for v in valid_indices:                                     
            player_high = self.getScore(player_hand[v])
            if player_high == dealer_high:
                self.interface.showOutcomeMessage(tie_msg)
            elif player_high == BLACKJACK:
                self.interface.showOutcomeMessage("Blackjack! " + win_msg)
            elif player_high > dealer_high:
                self.interface.showOutcomeMessage(win_msg)
            else:
                self.interface.showOutcomeMessage(loss_msg)

    def runGame(self):
        # welcome message
        self.interface.greet()

        # start round or exit game    
        while self.interface.wantsToPlay():
            self.interface.initializeView()
            self.playRound()
            self.interface.clear()
        
        self.interface.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-interface', default='TextInterface', choices=['TextInterface', 'GraphicInterface'])
    args = parser.parse_args()
    interface_class = getattr(blackjack_interface, args.interface)
    interface = interface_class()
    app = BlackjackApp(interface)
    app.runGame()
