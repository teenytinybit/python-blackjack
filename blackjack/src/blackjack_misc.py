from enum import Enum

class Actions(Enum):
    HIT = 'hit'
    STAND ='stand'
    SPLIT ='split'
    DOUBLE ='double'

class Outcome(Enum):
    WIN = 'win'
    BLACKJACK = 'blackjack'
    LOSS = 'loss'
    TIE = 'tie'

ACCEPTED_BETS = [10, 25, 50, 100]
