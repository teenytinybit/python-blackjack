import sys
from env import dev_path
sys.path.append(dev_path)

import unittest
from copy import deepcopy
from unittest.mock import Mock, call, patch
from unittest.case import skip
import test_cards, test_interface
from blackjack_misc import Outcome, Actions
from blackjack_game import BlackjackApp as BlackjackAppClass
from blackjack_interface import GraphicInterface, TextInterface
from cards import Card as CardClass, BlackjackCardSet as CardSetClass, RANKS, SUITS


class TestBlackjackBaseClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.inter = glob_interface()
        cls.app = BlackjackAppClass(cls.inter)
        cls.cards = {
            'ace': CardClass(SUITS[3], RANKS[0][0]),
            'two': CardClass(SUITS[0], RANKS[1][0]),
            'three': CardClass(SUITS[1], RANKS[2][0]),
            'four': CardClass(SUITS[2], RANKS[3][0]),
            'five': CardClass(SUITS[3], RANKS[4][0]),
            'six': CardClass(SUITS[0], RANKS[5][0]),
            'seven': CardClass(SUITS[1], RANKS[6][0]),
            'eight': CardClass(SUITS[2], RANKS[7][0]),
            'nine': CardClass(SUITS[3], RANKS[8][0]),
            'ten': CardClass(SUITS[0], RANKS[9][0]),
            'jack': CardClass(SUITS[1], RANKS[10][0]),
            'queen': CardClass(SUITS[2], RANKS[11][0]),
            'king': CardClass(SUITS[3], RANKS[12][0])
        }
        cls.tie_msg = "It's a tie!\n"
        cls.win_msg = "You won!\n"
        cls.loss_msg = "You lost!\n"
        cls.bust_msg = "Bust!\n"
        cls.blackjack_msg = "Blackjack! " + cls.win_msg


class TestBlackjackAppBets(TestBlackjackBaseClass):

    def setUp(self):
        self.app = BlackjackAppClass(self.inter)

    def test_adjust_bet_win(self):
        """
        Test that balance is adjusted accordingly when user wins
        """
        self.app.adjustBalance(Outcome.WIN, 0)
        self.assertEqual(self.app.balance, 120)

    def test_adjust_bet_loss(self):
        """
        Test that balance is adjusted accordingly when user loses
        """
        self.app.adjustBalance(Outcome.LOSS, 0)
        self.assertEqual(self.app.balance, 100)

    def test_adjust_bet_tie(self):
        """
        Test that balance does not change when it's a tie
        """
        self.app.adjustBalance(Outcome.TIE, 0)
        self.assertEqual(self.app.balance, 110)

    def test_adjust_bet_blackjack(self):
        """
        Test that balance is adjusted accordingly when user wins with a Blackjack
        """
        self.app.adjustBalance(Outcome.BLACKJACK, 0)
        self.assertEqual(self.app.balance, 130)

    def test_adjust_bet_multiple_outcomes(self):
        """
        Test that balance is adjusted accordingly when user wins and loses different hands
        """
        self.app.adjustBalance(Outcome.BLACKJACK, 0)
        self.app.adjustBalance(Outcome.TIE, 0)
        self.app.adjustBalance(Outcome.LOSS, 0)
        self.assertEqual(self.app.balance, 140)

    def test_set_bet(self):
        """
        Test that a bet, bets and balance parameters are set correctly
        """
        self.app.setBet(20)
        self.assertEqual(self.app.bet, 20)
        self.assertListEqual(self.app.bets, [20])

    def test_place_bet(self):
        """
        Test that a when a bet is placed, the balance is adjusted correctly
        """
        self.app.setBet(30)
        self.app.placeBet(0)
        self.assertEqual(self.app.balance, 70)


class TestBlackjackAppGetCard(TestBlackjackBaseClass):

    def test_get_card(self):
        """
        Test that a function produces a card object
        """
        card = self.app.drawCard()
        self.assertIsInstance(card, CardClass, msg="Incorrect object type")
        self.assertIsInstance(card.getRank(), str, msg="Rank is not a string")
        self.assertIsInstance(card.getSuit(), str, msg="Suit is not a string")

    def test_get_cards_different_suits(self):
        """
        Test that a function produces different card suits out of 1000 generated
        """
        times = 10000
        offset = times // 66  # 1.5% deviation allowance
        target = times // 4 - offset
        suits = []
        for i in range(times):
            card = self.app.drawCard()
            suits.append(card.getSuit())
        for y in range(len(SUITS)):
            s_lst = [s for s in suits if s == SUITS[y]]
            self.assertGreaterEqual(len(s_lst), target,
                                    msg=f"{SUITS[y]} appears less than {target} times out of {times}")

    def test_get_cards_different_ranks(self):
        """
        Test that a function produces different card ranks out of 2600 generated
        """
        times = 26000
        offset = times // 66  # 1.5% deviation allowance
        target = times // 13 - offset
        ranks = []
        for i in range(times):
            card = self.app.drawCard()
            ranks.append(card.getRank())

        for y in range(len(RANKS)):
            r_lst = [r for r in ranks if r == RANKS[y][0]]
            self.assertGreaterEqual(len(r_lst), target,
                                    msg=f"{RANKS[y][0]} appears less than {target} times out of {times}")


class TestBlackjackAppCanPlayValidation(TestBlackjackBaseClass):

    def test_user_can_play_valid_cards_score2(self):
        """
        Test that a user can add more cards with a total card score of 2 (< 21)
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['ace']))
        cards.addCard(deepcopy(self.cards['ace']))
        can_play = self.app.canPlay(cards)
        self.assertTrue(can_play)

    def test_user_can_play_valid_cards_score20(self):
        """
        Test that a user can add more cards with a total card score of 20 (< 21)
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['ten']))  # ten
        cards.addCard(deepcopy(self.cards['jack']))  # jack
        can_play = self.app.canPlay(cards)
        self.assertTrue(can_play)

    def test_user_cannot_play_invalid_cards(self):
        """
        Test that a user cannot add more cards with a total card score > 21
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['king']))  # king
        cards.addCard(deepcopy(self.cards['queen']))  # queen
        cards.addCard(deepcopy(self.cards['six']))  # six
        can_play = self.app.canPlay(cards)
        self.assertFalse(can_play)

    def test_user_cannot_play_at_limit21(self):
        """
        Test that a user cannot add more cards with a total card score = 21
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['king']))  # king
        cards.addCard(deepcopy(self.cards['ace']))  # ace
        can_play = self.app.canPlay(cards)
        self.assertFalse(can_play)

    def test_dealer_can_play_valid_cards_score2(self):
        """
        Test that dealer can add more cards with a total card score < 17
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['ace']))  # ace
        cards.addCard(deepcopy(self.cards['ace']))  # ace
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertTrue(can_play)

    def test_dealer_can_play_valid_cards_score16(self):
        """
        Test that dealer can add more cards with a total card score < 17
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['seven']))
        cards.addCard(deepcopy(self.cards['nine']))
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertTrue(can_play)

    def test_dealer_cannot_play_invalid_cards(self):
        """
        Test that dealer cannot add more cards with a total card score > 17
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['jack']))
        cards.addCard(deepcopy(self.cards['eight']))
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)

    def test_dealer_cannot_play_when_score21(self):
        """
        Test that dealer cannot add more cards with a total card score > 17
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['jack']))
        cards.addCard(deepcopy(self.cards['eight']))
        cards.addCard(deepcopy(self.cards['three']))
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)

    def test_dealer_cannot_play_at_limit(self):
        """
        Test that dealer cannot add more cards when score is = 17
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['queen']))
        cards.addCard(deepcopy(self.cards['seven']))
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)

    def test_dealer_cannot_play_at_limit_with_ace(self):
        """
        Test that a dealer stops playing when the card set has an ace, 
        and counting it as 11 brings the score to = 17
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['ace']))
        cards.addCard(deepcopy(self.cards['two']))
        cards.addCard(deepcopy(self.cards['four']))
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)

    def test_dealer_cannot_play_over_limit_with_ace(self):
        """
        Test that a dealer cannot play when the card set has an ace, 
        and counting it as 11 brings the score to > 17
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['ace']))
        cards.addCard(deepcopy(self.cards['nine']))
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)


class TestBlackjackAppScoreValidation(TestBlackjackBaseClass):

    def test_valid_cards_not_bust(self):
        """
        Test that a card set with a total score < 21 is recognised as valid
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['seven']))
        cards.addCard(deepcopy(self.cards['nine']))
        success = self.app.isSuccessful(cards)
        self.assertTrue(success)

    def test_valid_cards_not_bust_21(self):
        """
        Test that a card set with a total score = 21 is recognised as valid
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['seven']))
        cards.addCard(deepcopy(self.cards['nine']))
        cards.addCard(deepcopy(self.cards['five']))
        success = self.app.isSuccessful(cards)
        self.assertTrue(success)

    def test_invalid_cards_bust(self):
        """
        Test that a card set with a total score > 21 is recognised as bust
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['ten']))
        cards.addCard(deepcopy(self.cards['nine']))
        cards.addCard(deepcopy(self.cards['queen']))
        success = self.app.isSuccessful(cards)
        self.assertFalse(success)


class TestBlackjackAppScoreCalc(TestBlackjackBaseClass):

    def test_high_score_calculation(self):
        """
        Test that a score is calculated correctly
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['ten']))
        cards.addCard(deepcopy(self.cards['nine']))
        score = self.app.getHighScore(cards)
        self.assertEqual(score, 19)

    def test_high_score_calculation_ace(self):
        """
        Test that a score is calculated correctly with ace in a card set
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['five']))
        cards.addCard(deepcopy(self.cards['ace']))
        score = self.app.getHighScore(cards)
        self.assertEqual(score, 16)

    def test_high_score_calculation_ace_over_limit(self):
        """
        Test that a score is calculated correctly with ace in a card set, 
        and the higherst score > 21
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['five']))
        cards.addCard(deepcopy(self.cards['nine']))
        cards.addCard(deepcopy(self.cards['ace']))
        score = self.app.getHighScore(cards)
        self.assertEqual(score, 15)


class TestBlackjackAppPlaySingleHand(TestBlackjackBaseClass):

    def setUp(self):
        self.app.interface.updateCardView = Mock()  # to avoid excessive output to the console during tests

    def test_user_plays_turn_valid_hand_stand(self):
        """
        Test that when user plays a valid hand and stands, 
        the cards are not changed
        """
        cards_control = CardSetClass()
        cards_control.addCard(deepcopy(self.cards['five']))
        cards_control.addCard(deepcopy(self.cards['four']))
        cards_test = deepcopy(cards_control)

        with patch('builtins.input', return_value='stand') as input_mock:
            self.app.playHand(cards_test)
            input_mock.assert_called_once()
        self.assertEqual(cards_test, cards_control)

    def test_user_plays_turn_invalid_hand(self):
        """
        Test that when user plays an invalid hand, turn ends and the cards are not changed
        """
        cards_control = CardSetClass()
        cards_control.addCard(deepcopy(self.cards['ten']))
        cards_control.addCard(deepcopy(self.cards['ten']))
        cards_control.addCard(deepcopy(self.cards['six']))
        cards_test = deepcopy(cards_control)

        with patch('builtins.input') as input_mock:
            self.app.playHand(cards_test)
            input_mock.assert_not_called()
        self.assertEqual(cards_test, cards_control)

    def test_user_plays_turn_valid_hand_hit_once(self):
        """
        Test that when user plays a valid hand and hits only once, 
        the cards are changed accordingly
        """
        cards_control = CardSetClass()
        cards_control.addCard(deepcopy(self.cards['five']))
        cards_control.addCard(deepcopy(self.cards['four']))
        cards_test = deepcopy(cards_control)

        with patch('builtins.input', side_effect=['hit', 'stand']) as input_mock:
            self.app.playHand(cards_test)
            self.assertEqual(input_mock.call_count, 2, msg="Should make 2 action input prompts")
        self.assertEqual(len(cards_test.getCards()), 3)
        self.assertCountEqual(cards_test.getCards()[:2], cards_control.getCards())

    def test_user_plays_turn_valid_hand_hit_max(self):
        """
        Test that when user plays a valid hand and hits until possible,
        the turn stops upon reaching a valid score max and the cards are changed accordingly
        """
        cards_control = CardSetClass()
        cards_control.addCard(deepcopy(self.cards['ace']))
        cards_control.addCard(deepcopy(self.cards['ace']))
        cards_test = deepcopy(cards_control)

        suit, rank = self.cards['two'].getSuit(), self.cards['two'].getRank()

        def side_effect():
            return CardClass(suit, rank)

        with patch('builtins.input', return_value='hit') as input_mock:
            with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
                self.app.playHand(cards_test)
            self.assertEqual(input_mock.call_count, 10, msg="Should make 10 action input prompts")
        self.assertEqual(len(cards_test.getCards()), 12)
        self.assertCountEqual(cards_test.getCards()[:2], cards_control.getCards())

    def test_user_plays_turn_valid_hand_multiple_hit(self):
        """
        Test that when user plays a valid hand and hits multiple times then stands, 
        turn ends and the cards are changed accordingly
        """
        cards_control = CardSetClass()
        cards_control.addCard(deepcopy(self.cards['ace']))
        cards_control.addCard(deepcopy(self.cards['two']))
        cards_test = deepcopy(cards_control)

        suit, rank = self.cards['three'].getSuit(), self.cards['three'].getRank()

        def side_effect():
            return CardClass(suit, rank)

        with patch('builtins.input', side_effect=['hit'] * 4 + ['stand']) as input_mock:
            with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
                self.app.playHand(cards_test)
            self.assertEqual(input_mock.call_count, 5, msg="Should make 5 action input prompts")
        self.assertEqual(len(cards_test.getCards()), 6)
        self.assertCountEqual(cards_test.getCards()[:2], cards_control.getCards())

    def test_dealer_plays_turn_valid_hand(self):
        """
        Test that when dealer plays a valid hand and is required to stand, 
        automatically stands and the cards are not changed
        """
        cards_control = CardSetClass()
        cards_control.addCard(deepcopy(self.cards['eight']))
        cards_control.addCard(deepcopy(self.cards['nine']))
        cards_test = deepcopy(cards_control)
        self.app.playHand(cards_test, is_dealer=True)
        self.assertEqual(cards_test, cards_control)

    def test_dealer_plays_turn_invalid_hand(self):
        """
        Test that when dealer plays an invalid hand, turn ends and the cards are not changed
        """
        cards_control = CardSetClass()
        cards_control.addCard(deepcopy(self.cards['ten']))
        cards_control.addCard(deepcopy(self.cards['ten']))
        cards_control.addCard(deepcopy(self.cards['six']))
        cards_test = deepcopy(cards_control)
        self.app.playHand(cards_test, is_dealer=True)
        self.assertEqual(cards_test, cards_control)

    def test_dealer_plays_turn_valid_hand_hit_once(self):
        """
        Test that when dealer plays a valid hand and can hit only once, 
        turn ends and the cards are changed accordingly
        """
        cards_control = CardSetClass()
        cards_control.addCard(deepcopy(self.cards['three']))
        cards_control.addCard(deepcopy(self.cards['four']))
        cards_test = deepcopy(cards_control)

        suit, rank = self.cards['jack'].getSuit(), self.cards['jack'].getRank()

        def side_effect():
            return CardClass(suit, rank)

        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            self.app.playHand(cards_test, is_dealer=True)
        self.assertEqual(len(cards_test.getCards()), 3)
        self.assertCountEqual(cards_test.getCards()[:2], cards_control.getCards())

    def test_dealer_plays_turn_valid_hand_multiple_hit(self):
        """
        Test that when dealer plays a valid hand and hits multiple times 
        before required to stand, turn ends and the cards are changed accordingly
        """
        cards_control = CardSetClass()
        cards_control.addCard(deepcopy(self.cards['two']))
        cards_control.addCard(deepcopy(self.cards['two']))
        cards_test = deepcopy(cards_control)

        suit, rank = self.cards['three'].getSuit(), self.cards['three'].getRank()

        def side_effect():
            return CardClass(suit, rank)

        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            self.app.playHand(cards_test, is_dealer=True)
        self.assertEqual(len(cards_test.getCards()), 7)
        self.assertCountEqual(cards_test.getCards()[:2], cards_control.getCards())

    @skip
    def test_play_hand_updates_card_view_player(self):
        """
        """

        return

    @skip
    def test_play_hand_updates_card_view_dealer(self):
        """
        """

        return


class TestBlackjackAppPlayFullRound(TestBlackjackBaseClass):

    def get_patch(self, target, **kwargs):
        target_patch = patch(target, **kwargs)
        self.addCleanup(target_patch.stop)
        return target_patch.start()

    def setUp(self):
        self.app = BlackjackAppClass(self.inter)
        self.app.interface.updateCardView = Mock()  # to avoid excessive output to the console during tests
        self.app.resetCards()
        self.print_patch = self.get_patch('builtins.print', side_effect=Mock())

    def test_natural_blackjack_user(self):
        """
        Test that checks for a natural blackjack before playing the hand,
        when user has blackjack

        **Note** Also checks for the correct card distribution, qty, money balance
        """
        PREDEFINED_VALUES = [
            self.cards['ten'],  # user card
            self.cards['nine'],
            self.cards['ace'],  # user card
            self.cards['five']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
        
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                balance_displ.assert_called_once_with(90)
                outcome_mock.assert_called_once_with(self.blackjack_msg)
        
        self.assertTrue(len(self.app.player_hand) == 1)
        self.assertTrue(len(self.app.player_hand[0].getCards()) == 2)
        self.assertEqual(self.app.player_hand[0].getCard(0), DRAWN_CARDS[0])
        self.assertEqual(self.app.player_hand[0].getCard(1), DRAWN_CARDS[2])
        self.assertTrue(len(self.app.dealer_hand.getCards()) == 2)
        
        self.assertEqual(self.app.balance, 120)

    def test_natural_blackjack_user_and_dealer(self):
        """
        Test that checks for a natural blackjack before playing the hand,
        when user and dealer both have blackjack
        """
        PREDEFINED_VALUES = [
            self.cards['jack'],
            self.cards['jack'],  # dealer's card
            self.cards['ace'],
            self.cards['ace']  # dealer's card
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
        
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                balance_displ.assert_called_once_with(90)
                outcome_mock.assert_called_once_with(self.tie_msg)

        self.assertTrue(len(self.app.player_hand) == 1)
        self.assertTrue(len(self.app.player_hand[0].getCards()) == 2)
        self.assertEqual(self.app.player_hand[0].getCard(0), DRAWN_CARDS[0])
        self.assertEqual(self.app.player_hand[0].getCard(1), DRAWN_CARDS[2])

        self.assertTrue(len(self.app.dealer_hand.getCards()) == 2)
        self.assertEqual(self.app.dealer_hand.getCard(0), DRAWN_CARDS[1])
        self.assertEqual(self.app.dealer_hand.getCard(1), DRAWN_CARDS[3])

        self.assertEqual(self.app.balance, 100)

    def test_natural_blackjack_dealer_only(self):
        """
        Test that checks dealer has natural blackjack before playing the hand
        """
        PREDEFINED_VALUES = [
            self.cards['two'],
            self.cards['ten'],  # dealer's card
            self.cards['three'],
            self.cards['ace']  # dealer's card
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value

        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                balance_displ.assert_called_once_with(90)
                outcome_mock.assert_called_once_with("Dealer's got Blackjack! " + self.loss_msg)

        self.assertTrue(len(self.app.dealer_hand.getCards()) == 2)
        self.assertEqual(self.app.dealer_hand.getCard(0), DRAWN_CARDS[1])
        self.assertEqual(self.app.dealer_hand.getCard(1), DRAWN_CARDS[3])

        self.assertEqual(self.app.balance, 90)

    @patch('builtins.input')
    def test_game_flow_user_bust(self, input_mock):
        """
        Test that the game flow is correct when user goes bust
        - correct message(s) displayed when user goes bust
        - user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """

        PREDEFINED_VALUES = [
            self.cards['two'],  # user card
            self.cards['three'],
            self.cards['four'],  # user card
            self.cards['five']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['ten'].getSuit(), self.cards['ten'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.return_value = 'hit'
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                outcome_mock.assert_has_calls([call(self.bust_msg)], call(self.loss_msg))
                balance_displ.assert_called_once_with(90)
        
        player_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2] + [CardClass(suit, rank)] * 2: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])

        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)]: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 90)

    @patch('builtins.input')
    def test_game_flow_user_dealer_tie(self, input_mock):
        """
        Test that the game flow is correct when it's a tie
        - correct message(s) displayed when it's a tie
        - user and dealer final cards match the pre-defined cards (expected score)
        """

        # starting score of 6 for both
        PREDEFINED_VALUES = [
            self.cards['two'],  # user card
            self.cards['two'],
            self.cards['four'],  # user card
            self.cards['four']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)  # ensures both user + dealer reach score 18

        input_mock.side_effect = ['hit', 'hit', 'stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                balance_displ.assert_has_calls([call(90), call(100)])
                outcome_mock.assert_called_with(self.tie_msg)
        
        expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2] + [CardClass(suit, rank)] * 2: expected_cards.addCard(ec)
        self.assertEqual(expected_cards, self.app.dealer_hand)
        self.assertEqual(self.app.player_hand[0], self.app.dealer_hand)

        self.assertEqual(self.app.balance, 100)

    @patch('builtins.input')
    def test_game_flow_dealer_win_no_blackjack(self, input_mock):
        """
        Test that the game flow is correct when when dealer wins with score < 21
        - correct message(s) displayed when dealer wins with score < 21
        - user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """

        # starting score of 6 for user, 8 for dealer
        PREDEFINED_VALUES = [
            self.cards['two'],  # user card
            self.cards['two'],
            self.cards['four'],  # user card
            self.cards['six']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['hit', 'hit', 'stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                balance_displ.assert_called_once_with(90)
                outcome_mock.assert_called_with(self.loss_msg)

        player_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2] + [CardClass(suit, rank)] * 2: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])

        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)] * 2: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 90)

    @patch('builtins.input')
    def test_game_flow_user_win_no_blackjack(self, input_mock):
        """
        Test that the game flow is correct when when user wins with score < 21
        - correct message(s) displayed when user wins with score < 21
        - user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """

        # starting score of 6 for user, 6/16 for dealer, 
        # allowing for a single hit and total score of 12
        PREDEFINED_VALUES = [
            self.cards['two'],  # user card
            self.cards['ace'],
            self.cards['four'],  # user card
            self.cards['five']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['hit', 'hit', 'stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                balance_displ.assert_has_calls([call(90), call(110)])
                outcome_mock.assert_called_with(self.win_msg)

        player_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2] + [CardClass(suit, rank)] * 2: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])

        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)]: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 110)

    @patch('builtins.input')
    def test_game_flow_user_win_blackjack(self, input_mock):
        """
        Test that the game flow is correct when user user wins with a Blackjack
        - correct message(s) displayed when user wins with a Blackjack
        - user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """

        # starting score of 6 for user, 6/16 for dealer, 
        # allowing for a single hit and total score of 12
        PREDEFINED_VALUES = [
            self.cards['three'],  # user card
            self.cards['ace'],
            self.cards['six'],  # user card
            self.cards['five']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['hit', 'hit', 'stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                balance_displ.assert_has_calls([call(90), call(110)])
                outcome_mock.assert_called_with(self.win_msg)

        player_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2] + [CardClass(suit, rank)] * 2: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])

        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)]: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 110)

    @skip("Same value cards can be split in this version of the game")
    @patch('builtins.input')
    def test_split_flow_no_split_diff_rank_same_value(self, input_mock):
        """
        Test that same value different rank cards cannot be split (eg., jack and queen, value 10)
        - user has 1 card set
        - user final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['jack'],  # user card
            self.cards['three'],
            self.cards['queen'],  # user card
            self.cards['four']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['five'].getSuit(), self.cards['five'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            self.app.playRound()
            balance_displ.assert_has_calls([call(90), call(110)])
        self.assertEqual(len(self.app.player_hand), 1, msg="Player must have one card set")
        
        player_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2]: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])

        self.assertEqual(self.app.balance, 110)

    @patch('builtins.input')
    def test_split_flow_split_diff_rank_same_value(self, input_mock):
        """
        Test that same value different rank cards can be split (eg., jack and queen, value 10)
        - user has 2 card sets
        - user final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['jack'],  # user card
            self.cards['three'],
            self.cards['queen'],  # user card
            self.cards['four']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['nine'].getSuit(), self.cards['nine'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['stand'] * 2
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            self.app.playRound()
            balance_displ.assert_has_calls([call(90), call(80), call(100), call(120)])
        self.assertEqual(len(self.app.player_hand), 2, msg="Player must have two card sets")
        
        player_expected_cards = CardSetClass()
        player_expected_cards.addCard(DRAWN_CARDS[0])
        player_expected_cards.addCard(CardClass(suit, rank))
        self.assertEqual(player_expected_cards, self.app.player_hand[0])

        player_expected_cards2 = CardSetClass()
        player_expected_cards2.addCard(DRAWN_CARDS[2])
        player_expected_cards2.addCard(CardClass(suit, rank))
        self.assertEqual(player_expected_cards2, self.app.player_hand[1])

        self.assertEqual(self.app.balance, 120)

    @patch('builtins.input')
    def test_split_flow_no_split_low_balance(self, input_mock):
        """
        Test that same cards cannot be split if the balance is insufficient
        - user has 1 card set
        - user final cards match the pre-defined cards (expected score)
        - balance must reflect playing with a single card hand only
        """
        PREDEFINED_VALUES = [
            self.cards['jack'],  # user card
            self.cards['three'],
            self.cards['jack'],  # user card
            self.cards['four']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        self.app.setBet(100)
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            self.app.playRound()
            balance_displ.assert_has_calls([call(0), call(200)])

        self.assertEqual(self.app.balance, 200)
        self.assertEqual(len(self.app.player_hand), 1, msg="Player must have one card set")
        
        player_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2]: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])

    @patch('builtins.input')
    def test_game_flow_user_double_bet_2_cards(self, input_mock):
        """
        Test that the game flow is correct when a user doubles a bet
        - correct expected final balance
        - correct message(s) displayed
        - user cards match the pre-defined cards (expected score)
        """

        # starting score of 6 for both
        PREDEFINED_VALUES = [
            self.cards['two'],  # user card
            self.cards['two'],
            self.cards['four'],  # user card
            self.cards['three']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['double', 'hit', 'hit', 'stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                balance_displ.assert_has_calls([call(90), call(80)])
                outcome_mock.assert_called_with(self.loss_msg)
        
        expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2] + [CardClass(suit, rank)]: expected_cards.addCard(ec)
        self.assertEqual(expected_cards, self.app.player_hand[0])
        self.assertEqual(len(self.app.player_hand), 1)

        self.assertEqual(self.app.balance, 80)

    @patch('builtins.input')    
    def test_game_flow_user_double_bet_too_many_cards(self, input_mock):
        """
        Test that a bet cannot be doubled when more than 2 cards present
        - correct expected final balance
        - correct message(s) displayed
        - userfinal cards match the pre-defined cards (expected score)
        """

        PREDEFINED_VALUES = [
            self.cards['two'],  # user card
            self.cards['two'],
            self.cards['four'],  # user card
            self.cards['three']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)
        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['hit', 'double', 'hit', 'stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                balance_displ.assert_has_calls([call(90), call(110)])
                outcome_mock.assert_called_with(self.win_msg)
        
        expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2] + [CardClass(suit, rank)] * 2: expected_cards.addCard(ec)
        self.assertEqual(expected_cards, self.app.player_hand[0])
        self.assertEqual(len(self.app.player_hand), 1)
        
        self.assertEqual(self.app.balance, 110)

    @patch('builtins.input')    
    def test_split_flow_no_split_after_double_bet(self, input_mock):
        """
        Test that cards cannot be split when a user doubles a bet
        - correct expected final balance
        - correct message(s) displayed
        - user and dealer final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['five'],  # user card
            self.cards['seven'],
            self.cards['five'],  # user card
            self.cards['two']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['eight'].getSuit(), self.cards['eight'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['double', 'split']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                outcome_mock.assert_called_once_with(self.win_msg)       
                balance_displ.assert_has_calls([call(90), call(80), call(120)])
                self.assertEqual(balance_displ.call_count, 3)

        self.assertEqual(len(self.app.player_hand), 1, msg="Player must have only 1 card set if bet was doubled")
        
        player_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2] + [CardClass(suit, rank)]: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])
        
        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)]: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 120)

    @patch('builtins.input')    
    def test_split_flow_split_no_double_bet_after(self, input_mock):
        """
        Test that a bet cannot be doubled when cards have been split at least once
        - correct expected final balance
        - correct message(s) displayed
        - user and dealer final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['five'],  # user card
            self.cards['three'],
            self.cards['five'],  # user card
            self.cards['four']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['seven'].getSuit(), self.cards['seven'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['double', 'stand'] * 2
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                outcome_mock.assert_has_calls([call(self.loss_msg)] * 2)           
                balance_displ.assert_has_calls([call(90), call(80)])
                self.assertEqual(balance_displ.call_count, 2)

        self.assertEqual(len(self.app.player_hand), 2, msg="Player must have two card sets if split once")
        
        player_expected_cards = CardSetClass()
        for ec in [DRAWN_CARDS[0], CardClass(suit, rank)]: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])
        self.assertEqual(player_expected_cards, self.app.player_hand[1])
        
        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)] * 2: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 80)
        
    @patch('builtins.input')
    def test_split_flow_user_bust_all(self, input_mock):
        """
        Test that the game flow is correct when cards are split 1 time and user busts both rounds
        - correct message(s) displayed for each round played that the user goes bust
        - user has two card sets
        - user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['five'],  # user card
            self.cards['three'],
            self.cards['five'],  # user card
            self.cards['four']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['seven'].getSuit(), self.cards['seven'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['hit'] * 4
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                outcome_mock.assert_has_calls([call(self.bust_msg)] * 2, call(self.loss_msg))
                balance_displ.assert_has_calls([call(90), call(80)])
                self.assertEqual(balance_displ.call_count, 2)
        self.assertEqual(len(self.app.player_hand), 2, msg="Player must have two card sets if split once")
        
        player_expected_cards = CardSetClass()
        for ec in [DRAWN_CARDS[0]] + [CardClass(suit, rank)] * 3: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])
        self.assertEqual(player_expected_cards, self.app.player_hand[1])
        
        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)] * 2: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 80)

    @patch('builtins.input')
    def test_split_flow_user_stand_all(self, input_mock):
        """
        Test that the game flow is correct when cards are split 1 time and user stands on all rounds
        - correct message(s) displayed for the expected outcome
        - user has two card sets
        - user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['five'],  # user card
            self.cards['three'],
            self.cards['five'],  # user card
            self.cards['four']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['seven'].getSuit(), self.cards['seven'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['stand'] * 2
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                outcome_mock.assert_has_calls([call(self.loss_msg)] * 2)           
                balance_displ.assert_has_calls([call(90), call(80)])
                self.assertEqual(balance_displ.call_count, 2)

        self.assertEqual(len(self.app.player_hand), 2, msg="Player must have two card sets if split once")
        
        player_expected_cards = CardSetClass()
        for ec in [DRAWN_CARDS[0], CardClass(suit, rank)]: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])
        self.assertEqual(player_expected_cards, self.app.player_hand[1])
        
        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)] * 2: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 80)

    @patch('builtins.input')
    def test_split_flow_hit_instead_of_split(self, input_mock):
        """
        Test that the game flow is correct when cards can be split but user chooses not to
        - correct message(s) displayed for the expected outcome
        - user has 1 card set
        - user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['five'],  # user card
            self.cards['three'],
            self.cards['five'],  # user card
            self.cards['four']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['seven'].getSuit(), self.cards['seven'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['hit', 'stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                outcome_mock.assert_called_once_with(self.loss_msg)           
                balance_displ.assert_called_once_with(90)

        self.assertEqual(len(self.app.player_hand), 1, msg="Player must have one card set if did not split")
        
        player_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[::2] + [CardClass(suit, rank)]: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])
        
        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)] * 2: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 90)

    @patch('builtins.input')
    def test_split_flow_max_times_loss(self, input_mock):
        """
        Test that the game flow is correct when cards are split 4 times (max) and user loses all times
        - correct message(s) displayed for the expected outcome
        - user has 4 card sets
        - all user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['five'],  # user card
            self.cards['three'],
            self.cards['five'],  # user card
            self.cards['four']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit_split, rank_split = self.cards['five'].getSuit(), self.cards['five'].getRank()
        suit, rank = self.cards['four'].getSuit(), self.cards['four'].getRank()
        USER_HITS = [12]
        EVERY_THIRD_HIT = 3

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            USER_HITS[0] = USER_HITS[0] - 1
            if USER_HITS[0] > 0 and USER_HITS[0] % EVERY_THIRD_HIT == 0:
                return CardClass(suit_split, rank_split)
            else:
                return CardClass(suit, rank)

        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        input_mock.side_effect = ['split', 'hit', 'stand'] * 4      # attempt to split to more than max (4) hands
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                # dealer scores 19, user scores 13 on all card sets, loss message x4 times
                outcome_mock.assert_has_calls([call(self.loss_msg)] * 4)
                balance_displ.assert_has_calls([call(90), call(80), call(70), call(60)])
                self.assertEqual(balance_displ.call_count, 4)
        
        self.assertEqual(len(self.app.player_hand), 4)
        
        player_expected_cards = [CardSetClass() for i in range(4)]
        for i in range(4):
            player_expected_cards[i].addCard(CardClass(suit_split, rank_split))
            player_expected_cards[i].addCard(CardClass(suit_split, rank_split) if i == 3 \
                                        else CardClass(suit, rank))
            player_expected_cards[i].addCard(CardClass(suit, rank))
            self.assertEqual(player_expected_cards[i], self.app.player_hand[i])
        
        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)] * 3: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 60)

    @patch('builtins.input')
    def test_split_flow_max_times_win(self, input_mock):
        """
        Test that the game flow is correct when cards are split 4 times (max) and wins all times
        - correct message(s) displayed for the expected outcome
        - user has 4 card sets
        - all user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['five'],  # user card
            self.cards['five'],
            self.cards['five'],  # user card
            self.cards['ace']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit_split, rank_split = self.cards['five'].getSuit(), self.cards['five'].getRank()
        suit, rank = self.cards['seven'].getSuit(), self.cards['seven'].getRank()
        USER_HITS = [12]
        EVERY_THIRD_HIT = 3

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            USER_HITS[0] = USER_HITS[0] - 1
            if USER_HITS[0] > 0 and USER_HITS[0] % EVERY_THIRD_HIT == 0:
                return CardClass(suit_split, rank_split)
            else:
                return CardClass(suit, rank)

        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        input_mock.side_effect = ['split', 'hit', 'stand'] * 4      # attempt to split to more than max (4) hands
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                # dealer scores 13, user scores 19 (and 17) on all card sets, win message x4 times
                outcome_mock.assert_has_calls([call(self.win_msg)] * 4)
                balance_displ.assert_has_calls([
                    call(90), call(80), call(70), call(60), 
                    call(80), call(100), call(120), call(140)
                ])
                self.assertEqual(balance_displ.call_count, 8)
        
        self.assertEqual(len(self.app.player_hand), 4)
        
        player_expected_cards = [CardSetClass() for i in range(4)]
        for i in range(4):
            player_expected_cards[i].addCard(CardClass(suit_split, rank_split))
            player_expected_cards[i].addCard(CardClass(suit_split, rank_split) if i == 3 \
                                        else CardClass(suit, rank))
            player_expected_cards[i].addCard(CardClass(suit, rank))
            self.assertEqual(player_expected_cards[i], self.app.player_hand[i])
        
        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)]: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 140)

    @patch('builtins.input')
    def test_split_flow_user_bust_and_win(self, input_mock):
        """
        Test that the game flow is correct when cards are split 1 time and user busts one round and wins the other
        - correct message(s) displayed for for each round played
        - user has 2 card sets
        - all user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['five'],  # user card
            self.cards['two'],
            self.cards['five'],  # user card
            self.cards['eight']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['seven'].getSuit(), self.cards['seven'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['hit'] * 3 + ['stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                outcome_mock.assert_has_calls([call(self.bust_msg)], call(self.win_msg))
                balance_displ.assert_has_calls([call(90), call(80), call(100)])
                self.assertEqual(balance_displ.call_count, 3)
        self.assertEqual(len(self.app.player_hand), 2, msg="Player must have two card sets if split once")
        
        player_expected_cards = CardSetClass()
        for ec in [DRAWN_CARDS[0]] + [CardClass(suit, rank)] * 3: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])
        
        player_expected_cards2 = CardSetClass()
        for ec in [DRAWN_CARDS[0]] + [CardClass(suit, rank)] * 2: player_expected_cards2.addCard(ec)
        self.assertEqual(player_expected_cards2, self.app.player_hand[1])
        
        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)]: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 100)

    @patch('builtins.input')
    def test_split_flow_user_win_and_lose(self, input_mock):
        """
        Test that the game flow is correct when cards are split 1 time and user wins one round 
        with a blackjack and loses the other on points
        - correct message(s) displayed for for each round played
        - user has 2 card sets
        - all user final cards match the pre-defined cards (expected score)
        - dealer final cards match the pre-defined cards (expected score)
        """
        PREDEFINED_VALUES = [
            self.cards['five'],  # user card
            self.cards['two'],
            self.cards['five'],  # user card
            self.cards['eight']
        ]
        DRAWN_CARDS = deepcopy(PREDEFINED_VALUES)

        suit, rank = self.cards['eight'].getSuit(), self.cards['eight'].getRank()

        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split', 'hit', 'stand']
        balance_displ = self.get_patch('blackjack_interface.TextInterface.updateBalanceDisplay')
        with patch('blackjack_game.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('blackjack_interface.TextInterface.showOutcomeMessage') as outcome_mock:
                self.app.playRound()
                outcome_mock.assert_has_calls([call(self.win_msg)], call(self.loss_msg))
                balance_displ.assert_has_calls([call(90), call(80), call(100)])
                self.assertEqual(balance_displ.call_count, 3)
        self.assertEqual(len(self.app.player_hand), 2, msg="Player must have two card sets if split once")

        player_expected_cards = CardSetClass()
        for ec in [DRAWN_CARDS[0]] + [CardClass(suit, rank)] * 2: player_expected_cards.addCard(ec)
        self.assertEqual(player_expected_cards, self.app.player_hand[0])
        
        player_expected_cards2 = CardSetClass()
        for ec in [DRAWN_CARDS[0]] + [CardClass(suit, rank)]: player_expected_cards2.addCard(ec)
        self.assertEqual(player_expected_cards2, self.app.player_hand[1])
        
        dealer_expected_cards = CardSetClass()
        for ec in DRAWN_CARDS[1::2] + [CardClass(suit, rank)]: dealer_expected_cards.addCard(ec)
        self.assertEqual(dealer_expected_cards, self.app.dealer_hand)

        self.assertEqual(self.app.balance, 100)


class TestBlackjackAppRunGame(unittest.TestCase):

    def get_patch(self, target, **kwargs):
        target_patch = patch(target, **kwargs)
        self.addCleanup(target_patch.stop)
        return target_patch.start()

    def setUp(self):
        self.inter = glob_interface()
        self.app = BlackjackAppClass(self.inter)
        self.print_patch = self.get_patch('builtins.print', side_effect=Mock())

    def test_has_greeting(self):
        """
        Test that when game runs, the interface calls greeting method
        """
        self.app.interface.wantsToPlay = Mock(return_value=False)
        with patch('blackjack_interface.TextInterface.greet') as greeting:
            self.app.runGame()
            greeting.assert_called_once()

    def test_wants_to_play_one_round(self):
        """
        Test that can play one round then end game
        """
        with patch('builtins.input', side_effect=['start', 25, 'exit']):
            with patch('blackjack_game.BlackjackApp.playRound') as play_round:
                self.app.runGame()
                play_round.assert_called_once()

    def test_wants_to_play_multiple_rounds(self):
        """
        Test that can play multiple rounds
        """
        with patch('builtins.input', side_effect=['start', 25] * 3 + ['exit']):
            with patch('blackjack_game.BlackjackApp.playRound') as play_round:
                self.app.runGame()
                play_round.assert_called()
                self.assertEqual(play_round.call_count, 3)
        
    def test_does_not_want_to_play_round(self):
        """
        Test that can exit game without playing any round
        """
        with patch('builtins.input', return_value='exit'):
            with patch('blackjack_game.BlackjackApp.playRound') as play_round:
                self.app.runGame()
                play_round.assert_not_called()

    def test_custom_bet_one_round(self):
        """
        Test that a custom bet can be used to play a round
        """
        test_bet = 50
        play_round = self.get_patch('blackjack_game.BlackjackApp.playRound')
        input_patch = self.get_patch('builtins.input', side_effect=['start', 'exit'])
        with patch('blackjack_interface.TextInterface.getBet', return_value=test_bet) as get_bet:
            with patch('blackjack_game.BlackjackApp.setBet') as set_bet:
                self.app.runGame()
                get_bet.assert_called_once()
                set_bet.assert_called_once()

    def test_custom_bets_multiple_rounds(self):
        """
        Test that different custom bets can be set for each round
        """
        test_bets = [10, 25, 50, 100]
        play_round = self.get_patch('blackjack_game.BlackjackApp.playRound')
        input_patch = self.get_patch('builtins.input', side_effect=['start'] * 4 + ['exit'])
        with patch('blackjack_interface.TextInterface.getBet', side_effect=test_bets) as get_bet:
            with patch('blackjack_game.BlackjackApp.setBet') as set_bet:
                self.app.runGame()
                get_bet.assert_called()
                self.assertEqual(get_bet.call_count, 4)
                set_bet.assert_called()
                self.assertEqual(set_bet.call_count, 4)
                bet_args = [bet_arg[0][0] for bet_arg in set_bet.call_args_list]
                self.assertListEqual(test_bets, bet_args)

    def test_cards_reset_after_round(self):
        """
        Test that cards reset (empty) each round
        """
        play_round = self.get_patch('blackjack_game.BlackjackApp.playRound')
        input_patch = self.get_patch('builtins.input', side_effect=['start', 10, 'start', 25, 'exit'])
        with patch('blackjack_game.BlackjackApp.resetCards') as reset_cards:
            self.app.runGame()
            reset_cards.assert_called()
            self.assertEqual(reset_cards.call_count, 2)
        
    def test_balance_valid_can_play(self):
        """
        Test that a game can be played with a sufficient balance
        """
        get_bet = self.get_patch('blackjack_interface.TextInterface.getBet', return_value=25)
        input_patch = self.get_patch('builtins.input', side_effect=['start', 'exit'])
        with patch('blackjack_game.BlackjackApp.playRound') as play_round:
            self.app.runGame()
            play_round.assert_called_once()

    def test_balance_insufficient_cannot_play(self):
        """
        Test that a game cannot be played with an insufficient balance
        """
        self.app.balance = 50
        input_patch = self.get_patch('builtins.input', side_effect=['start', 100, 25, 'exit'])
        with patch('blackjack_game.BlackjackApp.playRound') as play_round:
            self.app.runGame()
            play_round.assert_called_once()
            self.assertEqual(self.app.bet, 25)
    
    def test_balance_low_can_play_limited_rounds(self):
        """
        Test that a game can be played only as many times as the balance allow
        """
        def lose_bet():
            self.app.balance = self.app.balance - 10
        input_patch = self.get_patch('builtins.input', side_effect=['start'] * 11 + ['exit'])
        get_bet = self.get_patch('blackjack_interface.TextInterface.getBet', return_value=10)
        with patch('blackjack_game.BlackjackApp.playRound', side_effect=lose_bet) as play_round:
            self.app.runGame()
            play_round.assert_called()
            self.assertEqual(play_round.call_count, 10)

if __name__ == '__main__':

    def create_suite(test_cls):
        test_suite = []
        for tc in test_cls:
            loaded_tests = unittest.TestLoader().loadTestsFromTestCase(tc)
            test_suite.append(loaded_tests)
        return test_suite

    card_class_tests = [test_cards.TestCardClassMethods, test_cards.TestCardSetClassMethods]
    test_suite_cards = create_suite(card_class_tests)
    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(test_suite_cards))

    interface_tests = [test_interface.TestTextInterface, test_interface.TestGraphicInterface]
    test_suite_inter = create_suite(interface_tests)
    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(test_suite_inter))

    app_class_tests = [
        TestBlackjackAppBets, TestBlackjackAppGetCard, TestBlackjackAppCanPlayValidation,
        TestBlackjackAppScoreValidation, TestBlackjackAppScoreCalc,
        TestBlackjackAppPlaySingleHand, TestBlackjackAppPlayFullRound,
        TestBlackjackAppRunGame
    ]

    # test with text interface
    test_suite_text_game = create_suite(app_class_tests)
    glob_interface = TextInterface
    unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(test_suite_text_game))

