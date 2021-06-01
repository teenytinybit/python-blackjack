# Game of Blackjack
import argparse
from random import randint
import blackjack_interface
from blackjack_misc import Actions, Outcome
from cards import Card, BlackjackCardSet, SUITS, RANKS

BLACKJACK = 21
MAX_HANDS = 4
STD_BET = 10

class BlackjackApp(object):
    def __init__(self, interface):
        self.name = "Blackjack Game"
        self.interface = interface
        self.balance = 100
        self.bet = STD_BET
        self.bets = [STD_BET]
        self.player_hand = [BlackjackCardSet()]
        self.dealer_hand = BlackjackCardSet()
    
    def adjustBalance(self, outcome, hand: int):
        if outcome == Outcome.BLACKJACK:
            self.balance = self.balance + self.bets[hand] * 3
        elif outcome == Outcome.WIN:
            self.balance = self.balance + self.bets[hand] * 2
        elif outcome == Outcome.TIE:
            self.balance = self.balance + self.bets[hand]

    def drawCard(self):
        # generate a random suit out of 4 possible
        suit = SUITS[randint(0, 3)]
        # generate a random card out of 13 possible
        rank = RANKS[randint(0, 12)][0]
        return Card(suit, rank)

    def canPlay(self, hand: BlackjackCardSet, is_dealer=False):
        can_play = True

        if is_dealer and hand.hasAce():
            can_play = hand.getScore()[1] < 17
        elif is_dealer:
            can_play = hand.getScore()[0] < 17
        else:
            can_play = not hand.isSplitFromAce() and hand.getScore()[0] < 21 and hand.getScore()[1] != 21

        return can_play

    def isSuccessful(self, hand: BlackjackCardSet):
        if hand.getScore()[0] > 21:
            return False
        return True

    def playHand(self, hand_idx, is_dealer=False, actions=[]):
        hand = self.dealer_hand if is_dealer else self.player_hand[hand_idx]
        action = Actions.HIT
        while self.canPlay(hand, is_dealer):
            if not is_dealer:
                action = self.interface.getAction(actions)
            
            if action == Actions.STAND:
                break
            elif action == Actions.DOUBLE:
                self.placeBet(hand_idx)
                self.bets[hand_idx] = self.bet * 2
                self.interface.updateBalanceDisplay(self.balance)
                hand.addCard(self.drawCard())
                self.interface.updateCardView(hand, is_dealer=is_dealer)
                break
            elif action == Actions.SPLIT:
                self.player_hand.append(self.player_hand[hand_idx].doSplit())
                self.bets.append(self.bet)
                self.placeBet(hand_idx)
                self.interface.moveSplitCard(action='hold')
                self.interface.updateBalanceDisplay(self.balance)
                action = Actions.HIT
            
            if action == Actions.HIT:
                hand.addCard(self.drawCard())
                self.interface.updateCardView(hand, is_dealer=is_dealer)
            actions = [Actions.HIT, Actions.STAND]  # limit available actions after the first hit

    def getHighScore(self, hand: BlackjackCardSet):
        score = hand.getScore()[1] if (0 < hand.getScore()[1] <= 21) \
                                    else hand.getScore()[0]
        return score

    def placeBet(self, hand: int):
        self.balance = self.balance - self.bets[hand]

    def startRound(self):
        hidden_idx = 0
        tie_msg, win_msg, loss_msg = "It's a tie!\n", "You won!\n", "You lost!\n"
        messages = {
            'win': win_msg,
            'blackjack' : "Blackjack! " + win_msg,
            'loss': loss_msg,
            'tie':tie_msg
        }
        self.placeBet(0)
        self.interface.updateBalanceDisplay(self.balance)
        # deal 2 initial cards for both
        for i in range(2):
            self.player_hand[0].addCard(self.drawCard())
            self.dealer_hand.addCard(self.drawCard())
        # hide the 1st card
        self.dealer_hand.hideCard(hidden_idx)

        self.interface.updateCardView(self.player_hand[0])
        self.interface.updateCardView(self.dealer_hand, is_dealer=True)

        # analyse player's cards for a NATURAL Blackjack
        if self.player_hand[0].hasBlackjack():
            # compare to dealer's cards if NATURAL Blackjack
            self.dealer_hand.revealCard(hidden_idx)
            self.interface.updateCardView(self.dealer_hand, is_dealer=True)
            if self.dealer_hand.hasBlackjack():
                self.interface.showOutcomeMessage(messages[Outcome.TIE.value])
                self.adjustBalance(Outcome.TIE, 0)
            else:
                self.interface.showOutcomeMessage(messages[Outcome.BLACKJACK.value])
                self.adjustBalance(Outcome.BLACKJACK, 0)
            return

        # analyse dealer's cards for a NATURAL Blackjack (if up card is 11 or 10)
        if self.dealer_hand.hasBlackjack():
            self.dealer_hand.revealCard(hidden_idx)
            self.interface.updateCardView(self.dealer_hand, is_dealer=True)
            self.interface.showOutcomeMessage("Dealer's got Blackjack! " + messages[Outcome.LOSS.value])
            return

        # allow splitting 2 same value cards, up to 4 hands allowed
        # doubling allowed on initial 2 cards, cannot combine with splitting
        # player Hits or Stands
        valid_hands = []
        for i in range(MAX_HANDS):
            if len(self.player_hand[i].getCards()) < 2:
                self.player_hand[i].addCard(self.drawCard())
                self.interface.moveSplitCard(action='release')
                self.interface.updateCardView(self.player_hand[i])
            actions_opt = [Actions.HIT, Actions.STAND]
            if i == 0 and self.balance >= self.bet:
                actions_opt.append(Actions.DOUBLE)
            if i < MAX_HANDS - 1 and self.player_hand[i].canSplit() and self.balance >= self.bet:
                actions_opt.append(Actions.SPLIT)

            self.playHand(i, actions=actions_opt)
            if not self.interface.isAlive():
                return
            success = self.isSuccessful(self.player_hand[i])
            valid_hands.append(success)
            if not success:
                if len(self.player_hand) > i + 1 or valid_hands.count(True) == 0:
                    self.interface.showOutcomeMessage("Bust!\n", no_button=True)
                else:
                    self.interface.showOutcomeMessage("Bust!\n", button_text='continue')
            elif len(self.player_hand) > i + 1:
                self.interface.setAsideCardSet(i)
            
            if len(self.player_hand) == i + 1:
                break

        not_bust_indices = [i for i in range(len(valid_hands)) if valid_hands[i]]
        not_bust_indices.reverse()

        # dealer Hits until result >= 17
        self.dealer_hand.revealCard(hidden_idx)
        self.interface.updateCardView(self.dealer_hand, is_dealer=True)
        self.playHand(None, is_dealer=True)
        if len(not_bust_indices) == 0:
            self.interface.showOutcomeMessage(messages[Outcome.LOSS.value])
            return

        # compare results to player
        dealer_high = self.getHighScore(self.dealer_hand)
        extra_msg = "" if dealer_high < 22 else "Dealer bust! "
        for v in not_bust_indices:
            player_high = self.getHighScore(self.player_hand[v])
            outcome = None
            if player_high == dealer_high:
                outcome = Outcome.TIE
            elif dealer_high > 21 or player_high > dealer_high:
                outcome = Outcome.WIN
            else:
                outcome = Outcome.LOSS
            self.interface.showSettledCardView(self.player_hand[v], v)
            msg_btn_text = 'back' if v == not_bust_indices[-1] else 'next result'
            self.interface.showOutcomeMessage(extra_msg + messages[outcome.value], button_text=msg_btn_text)
            self.adjustBalance(outcome, v)
            if not outcome == Outcome.LOSS:
                self.interface.updateBalanceDisplay(self.balance)

    def resetCards(self):
        self.player_hand = [BlackjackCardSet()]
        self.dealer_hand = BlackjackCardSet()

    def runGame(self):
        # welcome message
        self.interface.greet()
        self.interface.updateBalanceDisplay(self.balance)
        # start round or exit game
        while self.interface.isAlive() and self.balance >= 10 and self.interface.wantsToPlay():
            self.setBet(self.interface.getBet(self.balance))
            if not self.interface.isAlive():
                break
            self.interface.initializeView()
            self.startRound()
            self.resetCards()
            self.interface.clear()
            self.interface.updateBalanceDisplay(self.balance)

        if self.balance < 10:
            self.interface.close()
        
    def setBet(self, bet):
        self.bet = bet
        self.bets = [bet]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('-interface', default='TextInterface', choices=['TextInterface', 'GraphicInterface'])
    parser.add_argument('-interface', default='GraphicInterface', choices=['TextInterface', 'GraphicInterface'])
    args = parser.parse_args()
    interface_class = getattr(blackjack_interface, args.interface)
    interface = interface_class()
    app = BlackjackApp(interface)
    app.runGame()
