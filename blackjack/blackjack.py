# Game of Blackjack
import argparse
import blackjack_interface
from blackjack_misc import Actions
from random import randint
from cards import Card, BlackjackCardSet, SUITS, RANKS

BLACKJACK = 21
MAX_HANDS = 4

def drawCard():
    # generate a random suit out of 4 possible
    suit = SUITS[randint(0, 3)]
    # generate a random card out of 13 possible
    rank = RANKS[randint(0, 12)][0]
    return Card(suit, rank)

def canPlay(hand: BlackjackCardSet, is_dealer=False):
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

def isSuccessful(hand: BlackjackCardSet):
    if hand.getTotals()[0] > 21:
        return False
    return True

def playHand(interface, hand: BlackjackCardSet, is_dealer=False, force_hit=False):
    action = Actions.HIT
    while canPlay(hand, is_dealer):
        if not is_dealer:
            action = interface.getAction(Actions.HIT, Actions.STAND)
        if action == Actions.HIT:
            hand.addCard(drawCard())
            interface.updateCardView(hand, is_dealer=is_dealer)
        elif action == Actions.STAND:
            break

def getScore(hand: BlackjackCardSet):
    score = hand.getTotals()[1] if (0 < hand.getTotals()[1] <= 21) \
                                else hand.getTotals()[0]
    return score

def playRound(interface):
    player_hand = [BlackjackCardSet()]
    dealer_hand = BlackjackCardSet()
    hidden_idx = 0
    tie_msg, win_msg, loss_msg = "It's a tie!\n", "You won!\n", "You lost!\n"
    # deal 2 initial cards for both
    for i in range(2):
        player_hand[0].addCard(drawCard())
        dealer_hand.addCard(drawCard())
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

    interface.updateCardView(player_hand[0])
    interface.updateCardView(dealer_hand, is_dealer=True)

    # analyse player's cards for a NATURAL Blackjack
    if BLACKJACK in player_hand[0].getTotals():
        # compare to dealer's cards if NATURAL Blackjack
        dealer_hand.revealCard(hidden_idx)
        interface.updateCardView(dealer_hand, is_dealer=True)
        if BLACKJACK in dealer_hand.getTotals():
            interface.showOutcomeMessage(tie_msg)
        else:
            interface.showOutcomeMessage("Blackjack! " + win_msg)
        return

    # analyse dealer's cards for a NATURAL Blackjack (if up card is 11 or 10)
    if any(x in dealer_hand.getTotals() for x in [10, 11]):
        dealer_hand.revealCard(hidden_idx)
        if BLACKJACK in dealer_hand.getTotals():
            interface.updateCardView(dealer_hand, is_dealer=True)
            interface.showOutcomeMessage("Dealer's got Blackjack! " + loss_msg)
            return
        else:
            dealer_hand.hideCard(hidden_idx)

    # allow splitting 2 same value cards, up to 4 hands allowed
    # player Hits or Stands 
    valid_hands = []
    for i in range(MAX_HANDS):
        if len(player_hand[i].getCards()) < 2:
            player_hand[i].addCard(drawCard())
            interface.updateCardView(player_hand[i])
        if i < MAX_HANDS - 1 and player_hand[i].canSplit():
            action = interface.getAction(Actions.HIT, Actions.STAND, Actions.SPLIT)
            if action == Actions.STAND:
                break
            if action == Actions.SPLIT:
                player_hand.append(player_hand[i].doSplit())
            player_hand[i].addCard(drawCard())
            interface.updateCardView(player_hand[i])
            playHand(interface, player_hand[i])
            valid_hands.append(isSuccessful(player_hand[i]))
            if valid_hands[-1] == False:
                interface.showOutcomeMessage("Bust!\n")
        else:
            playHand(interface, player_hand[i])
            valid_hands.append(isSuccessful(player_hand[i]))
            if valid_hands[-1] == False:
                interface.showOutcomeMessage("Bust!\n")
            break
    valid_indices = [i for i in range(len(valid_hands)) if valid_hands[i]]
    
    # dealer Hits until result >= 17
    dealer_hand.revealCard(hidden_idx)
    interface.updateCardView(dealer_hand, is_dealer=True)
    if len(valid_indices) == 0:
        interface.showOutcomeMessage(loss_msg)
        return

    playHand(interface, dealer_hand, is_dealer=True)
    if not isSuccessful(dealer_hand):
        interface.showOutcomeMessage("Dealer bust! " + win_msg)
        return

    # compare results to player
    dealer_high = getScore(dealer_hand)
    for v in valid_indices:                                     
        player_high = getScore(player_hand[v])
        if player_high == dealer_high:
            interface.showOutcomeMessage(tie_msg)
        elif player_high == BLACKJACK:
            interface.showOutcomeMessage("Blackjack! " + win_msg)
        elif player_high > dealer_high:
            interface.showOutcomeMessage(win_msg)
        else:
            interface.showOutcomeMessage(loss_msg)

def runGame(interface):
    # welcome message
    interface.greet()

    # start round or exit game    
    while interface.wantsToPlay():
        interface.initializeView()
        playRound(interface)
        interface.clear()

    print("Game closed. Thank you for playing!\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-interface', default='TextInterface', choices=['TextInterface', 'GraphicInterface'])
    args = parser.parse_args()
    interface_class = getattr(blackjack_interface, args.interface)
    interface = interface_class()
    runGame(interface)