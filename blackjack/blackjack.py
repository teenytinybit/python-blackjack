# Game of Blackjack
from random import randint
from enum import Enum
from blackjack_interface import TextInterface
from cards import Card, BlackjackCardSet, SUITS, RANKS

BLACKJACK = 21
MAX_HANDS = 4

class Actions(Enum):
    HIT = 'hit'
    STAND ='stand'
    SPLIT ='split'
    DOUBLE ='double'

def drawCard():
    # generate a random suit out of 4 possible
    suit = SUITS[randint(0, 3)]
    # generate a random card out of 13 possible
    rank = RANKS[randint(0, 12)][0]
    return Card(suit, rank)

def displayCards(cards):
    card_display = ''
    for c in cards:
        if not c.isHidden():
            card_display += (c.getRank() + " of " + c.getSuit()).title() + '\n'
        else:
            card_display += '**Card Hidden**\n'
    card_display = card_display[:-1]
    print(card_display)
    print("- - - - - - - -")

def displayScore(hand: BlackjackCardSet):
    low_score = hand.getTotals()[0]
    high_score = hand.getTotals()[1]
    score_display = 'Total value: ' + str(low_score)
    score_display += ' or ' + str(high_score) if high_score > 0 else ''
    print(score_display)
    print("===============")

def updateCardView(hand: BlackjackCardSet):
    displayCards(hand.getCards())
    displayScore(hand)

def doHit(hand: BlackjackCardSet):
    hand.addCard(drawCard())
    updateCardView(hand)

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
        print("Bust!")
        return False
    return True

def playHand(hand: BlackjackCardSet, is_dealer=False, force_hit=False):
    whose = "Dealer's" if is_dealer else "Your"
    if force_hit:
        print(f"==============\n{whose} cards:\n")
        doHit(hand)
    
    action = Actions.HIT
    while canPlay(hand, is_dealer):
        if not is_dealer:
            action = getAction(Actions.HIT, Actions.STAND)
        if action == Actions.HIT:
            print(f"==============\n{whose} cards:\n")
            doHit(hand)
        elif action == Actions.STAND:
            break

def showOutcomeMessage(outcome):
    print(outcome)

def getAction(*actions):
    options = [a.value for a in actions]
    action_msg = ""
    if Actions.SPLIT in actions:
        options.remove(Actions.SPLIT.value)
        action_msg += "\nType 'split' if you'd like to split cards. "
    if Actions.DOUBLE in actions:
        options.remove(Actions.DOUBLE.value)
        action_msg += "\nType 'double' to double the bet. "
    action_msg += f"\nType {' or '.join(options)} to proceed." 
    action = input(action_msg)
    return Actions(action)

def wantsToSplit():
    split = input("Type 'split' to split your cards.  ") == 'split'
    return split

def getScore(hand: BlackjackCardSet):
    score = hand.getTotals()[1] if (0 < hand.getTotals()[1] <= 21) \
                                else hand.getTotals()[0]
    return score

def playRound():
    player_hand = [BlackjackCardSet()]
    dealer_hand = BlackjackCardSet()
    hidden_idx = 0
    tie_msg, win_msg, loss_msg = "It's a tie!", "You won!", "You lost!"
    # deal 2 initial cards for both
    for i in range(2):
        player_hand[0].addCard(drawCard())
        dealer_hand.addCard(drawCard())
    # hide the 1st card
    dealer_hand.hideCard(hidden_idx)


    # """
    # TEST CODE =========================
    # """
    # player_hand = [BlackjackCardSet()]
    # player_hand[0].addCard(Card('hearts', 'ace'))
    # player_hand[0].addCard(Card('spades', 'ace'))
    # """
    # TEST CODE =========================
    # """


    print("Your cards:\n")
    updateCardView(player_hand[0])

    print("\nDealer's cards:\n")
    updateCardView(dealer_hand)

    # analyse player's cards for a NATURAL Blackjack
    if BLACKJACK in player_hand[0].getTotals():
        # compare to dealer's cards if NATURAL Blackjack
        dealer_hand.revealCard(hidden_idx)
        updateCardView(dealer_hand)
        if BLACKJACK in dealer_hand.getTotals():
            showOutcomeMessage(tie_msg)
        else:
            showOutcomeMessage("Blackjack! " + win_msg)
        return

    # analyse dealer's cards for a NATURAL Blackjack (if up card is 11 or 10)
    if any(x in dealer_hand.getTotals() for x in [10, 11]):
        dealer_hand.revealCard(hidden_idx)
        if BLACKJACK in dealer_hand.getTotals():
            updateCardView(dealer_hand)
            showOutcomeMessage(loss_msg)
            return
        else:
            dealer_hand.hideCard(hidden_idx)

    # allow splitting 2 same value cards, up to 4 hands allowed
    # player Hits or Stands 
    valid_hands = []
    for i in range(MAX_HANDS):
        if len(player_hand[i].getCards()) < 2:
            doHit(player_hand[i])
        if i < MAX_HANDS - 1 and player_hand[i].canSplit():
            action = getAction(Actions.HIT, Actions.STAND, Actions.SPLIT)
            if action == Actions.STAND:
                break
            if action == Actions.SPLIT:
                player_hand.append(player_hand[i].doSplit())
            playHand(player_hand[i], force_hit=True)
            valid_hands.append(isSuccessful(player_hand[i]))
        else:
            playHand(player_hand[i])
            valid_hands.append(isSuccessful(player_hand[i]))
            break
    valid_indices = [i for i in range(len(valid_hands)) if valid_hands[i]]
    
    # dealer Hits until result >= 17
    print("===============\nDealer's cards:\n")
    dealer_hand.revealCard(hidden_idx)
    updateCardView(dealer_hand)
    if len(valid_indices) == 0:
        showOutcomeMessage(loss_msg)
        return

    playHand(dealer_hand, is_dealer=True)
    if not isSuccessful(dealer_hand):
        showOutcomeMessage(win_msg)
        return

    # compare results to player
    dealer_high = getScore(dealer_hand)
    for v in valid_indices:                                     
        player_high = getScore(player_hand[v])
        if player_high == dealer_high:
            showOutcomeMessage(tie_msg)
        elif player_high == BLACKJACK:
            showOutcomeMessage("Blackjack! " + win_msg)
        elif player_high > dealer_high:
            showOutcomeMessage(win_msg)
        else:
            showOutcomeMessage(loss_msg)

    return

def runGame():
    border = "========================================================\n"
    nextGame = True
    while nextGame:
        print(border)
        playRound()
        # ask to play next game round
        btn = input("\nType 'start' to play another round.  ")
        nextGame = (btn == 'start')
        print(border)

def main():
    # interface = TextInterface()
    # welcome message
    print("Welcome to the game of Blackjack!\
        \nType 'start' to begin.\
        \nIf you would like to exit type 'exit'.\n")

    # start or exit game
    btn = input("")
    while btn not in ['start', 'exit']:
        print("Please type 'start' to begin or 'exit' to leave.")
        btn = input("")

    if btn == 'exit':
        print("Game closed.")
        return
    elif btn == 'start':
        # start game
        runGame()
    
    print("Game ended. Thank you for playing!\n")

main()