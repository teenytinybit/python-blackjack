from datetime import time
from copy import deepcopy
import unittest
from unittest.mock import Mock, patch
from unittest.case import skip
from blackjack_interface import TextInterface
from blackjack import BlackjackApp as BlackjackAppClass
from cards import Card as CardClass, BlackjackCardSet as CardSetClass, RANKS, SUITS

class TestBlackjackAppGeneral(unittest.TestCase):

    def setUp(self):
        self.inter = TextInterface()
        self.app = BlackjackAppClass(self.inter)
        self.cards = {
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
        offset = times // 100 # 1% allowance
        target = times // 4 - offset
        suits = []
        for i in range(times):
            card = self.app.drawCard()
            suits.append(card.getSuit())
        for y in range(len(SUITS)):
            s_lst = [s for s in suits if s == SUITS[y]]
            # print(f"{SUITS[y]} appears {len(s_lst)} times out of {times}")
            self.assertGreaterEqual(len(s_lst), target, msg=f"{SUITS[y]} appears less than {target} times out of {times}")

    def test_get_cards_different_ranks(self):
        """
        Test that a function produces different card ranks out of 2600 generated
        """
        times = 26000
        offset = times // 100 # 1% allowance
        target = times // 13 - offset
        ranks = []
        for i in range(times):
            card = self.app.drawCard()
            ranks.append(card.getRank())

        for y in range(len(RANKS)):
            r_lst = [r for r in ranks if r == RANKS[y][0]]
            # print(f"{RANKS[y][0]} appears {len(r_lst)} times out of {times}")
            self.assertGreaterEqual(len(r_lst), target, msg=f"{RANKS[y][0]} appears less than {target} times out of {times}")

    def test_user_can_play_valid_cards_score2(self):
        """
        Test that a user can add more cards with a total card score of 2 (< 21)
        """
        cards = CardSetClass()
        cards.addCard(self.cards['ace'])
        cards.addCard(self.cards['ace'])
        can_play = self.app.canPlay(cards)
        self.assertTrue(can_play)

    def test_user_can_play_valid_cards_score20(self):
        """
        Test that a user can add more cards with a total card score of 20 (< 21)
        """
        cards = CardSetClass()
        cards.addCard(self.cards['ten'])   # ten
        cards.addCard(self.cards['jack'])  # jack
        can_play = self.app.canPlay(cards)
        self.assertTrue(can_play)

    def test_user_cannot_play_invalid_cards(self):
        """
        Test that a user cannot add more cards with a total card score > 21
        """
        cards = CardSetClass()
        cards.addCard(self.cards['king'])  # king
        cards.addCard(self.cards['queen'])  # queen
        cards.addCard(self.cards['six'])   # six
        can_play = self.app.canPlay(cards)
        self.assertFalse(can_play)

    def test_user_cannot_play_at_limit21(self):
        """
        Test that a user cannot add more cards with a total card score = 21
        """
        cards = CardSetClass()
        cards.addCard(self.cards['king'])  # king
        cards.addCard(self.cards['ace'])   # ace
        can_play = self.app.canPlay(cards)
        self.assertFalse(can_play)

    def test_dealer_can_play_valid_cards_score2(self):
        """
        Test that dealer can add more cards with a total card score < 17
        """
        cards = CardSetClass()
        cards.addCard(self.cards['ace'])  # ace
        cards.addCard(self.cards['ace'])  # ace
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertTrue(can_play)

    def test_dealer_can_play_valid_cards_score16(self):
        """
        Test that dealer can add more cards with a total card score < 17
        """
        cards = CardSetClass()
        cards.addCard(self.cards['seven'])
        cards.addCard(self.cards['nine'])
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertTrue(can_play)

    def test_dealer_cannot_play_invalid_cards(self):
        """
        Test that dealer cannot add more cards with a total card score > 17
        """
        cards = CardSetClass()
        cards.addCard(self.cards['jack'])
        cards.addCard(self.cards['eight'])
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)

    def test_dealer_cannot_play_when_score21(self):
        """
        Test that dealer cannot add more cards with a total card score > 17
        """
        cards = CardSetClass()
        cards.addCard(self.cards['jack'])
        cards.addCard(self.cards['eight'])
        cards.addCard(self.cards['three'])
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)

    def test_dealer_cannot_play_at_limit(self):
        """
        Test that dealer cannot add more cards when score is = 17
        """
        cards = CardSetClass()
        cards.addCard(self.cards['queen'])
        cards.addCard(self.cards['seven'])
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)

    def test_dealer_cannot_play_at_limit_with_ace(self):
        """
        Test that a dealer stops playing when the card set has an ace, 
        and counting it as 11 brings the score to = 17
        """
        cards = CardSetClass()
        cards.addCard(self.cards['ace'])
        cards.addCard(self.cards['two'])
        cards.addCard(self.cards['four'])
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)

    def test_dealer_cannot_play_over_limit_with_ace(self):
        """
        Test that a dealer cannot play when the card set has an ace, 
        and counting it as 11 brings the score to > 17
        """
        cards = CardSetClass()
        cards.addCard(self.cards['ace'])
        cards.addCard(self.cards['nine'])
        can_play = self.app.canPlay(cards, is_dealer=True)
        self.assertFalse(can_play)

    def test_valid_cards_not_bust(self):
        """
        Test that a card set with a total score < 21 is recognised as valid
        """
        cards = CardSetClass()
        cards.addCard(self.cards['seven'])
        cards.addCard(self.cards['nine'])
        success = self.app.isSuccessful(cards)
        self.assertTrue(success)

    def test_valid_cards_not_bust_21(self):
        """
        Test that a card set with a total score = 21 is recognised as valid
        """
        cards = CardSetClass()
        cards.addCard(self.cards['seven'])
        cards.addCard(self.cards['nine'])
        cards.addCard(self.cards['five'])
        success = self.app.isSuccessful(cards)
        self.assertTrue(success)

    def test_invalid_cards_bust(self):
        """
        Test that a card set with a total score > 21 is recognised as bust
        """
        cards = CardSetClass()
        cards.addCard(self.cards['ten'])
        cards.addCard(self.cards['nine'])
        cards.addCard(self.cards['queen'])
        success = self.app.isSuccessful(cards)
        self.assertFalse(success)

    def test_high_score_calculation(self):
        """
        Test that a score is calculated correctly
        """
        cards = CardSetClass()
        cards.addCard(self.cards['ten'])
        cards.addCard(self.cards['nine'])
        score = self.app.getHighScore(cards)
        self.assertEqual(score, 19)

    def test_high_score_calculation_ace(self):
        """
        Test that a score is calculated correctly with ace in a card set
        """
        cards = CardSetClass()
        cards.addCard(self.cards['five'])
        cards.addCard(self.cards['ace'])
        score = self.app.getHighScore(cards)
        self.assertEqual(score, 16)

    def test_high_score_calculation_ace_over_limit(self):
        """
        Test that a score is calculated correctly with ace in a card set, 
        and the higherst score > 21
        """
        cards = CardSetClass()
        cards.addCard(self.cards['five'])
        cards.addCard(self.cards['nine'])
        cards.addCard(self.cards['ace'])
        score = self.app.getHighScore(cards)
        self.assertEqual(score, 15)
    
    def test_user_plays_turn_valid_hand_stand(self):
        """
        Test that when user plays a valid hand and stands, 
        the cards are not changed
        """
        cards_control = CardSetClass()
        cards_control.addCard(self.cards['five'])
        cards_control.addCard(self.cards['four'])
        cards_test = deepcopy(cards_control)
        
        self.app.interface.updateCardView = Mock()      # to avoid excessive output to console during tests
        
        with patch('builtins.input', return_value='stand') as input_mock:
            self.app.playHand(cards_test)
            input_mock.assert_called_once()
        self.assertEqual(cards_test, cards_control)

    def test_user_plays_turn_invalid_hand(self):
        """
        Test that when user plays an invalid hand, turn ends and the cards are not changed
        """
        cards_control = CardSetClass()
        cards_control.addCard(self.cards['ten'])
        cards_control.addCard(self.cards['ten'])
        cards_control.addCard(self.cards['six'])
        cards_test = deepcopy(cards_control)
        
        self.app.interface.updateCardView = Mock()      # to avoid excessive output to console during tests
        
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
        cards_control.addCard(self.cards['five'])
        cards_control.addCard(self.cards['four'])
        cards_test = deepcopy(cards_control)

        self.app.interface.updateCardView = Mock()      # to avoid excessive output to console during tests
        
        with patch('builtins.input') as input_mock:
            input_mock.side_effect = ['hit', 'stand']
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
        cards_control.addCard(self.cards['ace'])
        cards_control.addCard(self.cards['ace'])
        cards_test = deepcopy(cards_control)

        mock_card = self.cards['two']
        
        self.app.interface.updateCardView = Mock()      # to avoid excessive output to console during tests
        
        with patch('builtins.input', return_value='hit') as input_mock:
            with patch('blackjack.BlackjackApp.drawCard', return_value=mock_card):
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
        cards_control.addCard(self.cards['ace'])
        cards_control.addCard(self.cards['two'])
        cards_test = deepcopy(cards_control)

        mock_card = self.cards['three']
        
        self.app.interface.updateCardView = Mock()      # to avoid excessive output to console during tests
        
        with patch('builtins.input') as input_mock:
            input_mock.side_effect = ['hit'] * 4 + ['stand']
            with patch('blackjack.BlackjackApp.drawCard', return_value=mock_card):
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
        cards_control.addCard(self.cards['eight'])
        cards_control.addCard(self.cards['nine'])
        cards_test = deepcopy(cards_control)
        self.app.interface.updateCardView = Mock()
        self.app.playHand(cards_test, is_dealer=True)
        self.assertEqual(cards_test, cards_control)

    def test_dealer_plays_turn_invalid_hand(self):
        """
        Test that when dealer plays an invalid hand, turn ends and the cards are not changed
        """
        cards_control = CardSetClass()
        cards_control.addCard(self.cards['ten'])
        cards_control.addCard(self.cards['ten'])
        cards_control.addCard(self.cards['six'])
        cards_test = deepcopy(cards_control)
        self.app.interface.updateCardView = Mock()
        self.app.playHand(cards_test, is_dealer=True)
        self.assertEqual(cards_test, cards_control)

    def test_dealer_plays_turn_valid_hand_hit_once(self):
        """
        Test that when dealer plays a valid hand and can hit only once, 
        turn ends and the cards are changed accordingly
        """
        cards_control = CardSetClass()
        cards_control.addCard(self.cards['three'])
        cards_control.addCard(self.cards['four'])
        cards_test = deepcopy(cards_control)

        mock_card = self.cards['jack']
        
        self.app.interface.updateCardView = Mock()      # to avoid excessive output to console during tests
        
        with patch('blackjack.BlackjackApp.drawCard', return_value=mock_card):
            self.app.playHand(cards_test, is_dealer=True)
        self.assertEqual(len(cards_test.getCards()), 3)
        self.assertCountEqual(cards_test.getCards()[:2], cards_control.getCards())

    def test_dealer_plays_turn_valid_hand_multiple_hit(self):
        """
        Test that when dealer plays a valid hand and hits multiple times 
        before required to stand, turn ends and the cards are changed accordingly
        """
        cards_control = CardSetClass()
        cards_control.addCard(self.cards['two'])
        cards_control.addCard(self.cards['two'])
        cards_test = deepcopy(cards_control)

        mock_card = self.cards['three']
        
        self.app.interface.updateCardView = Mock()      # to avoid excessive output to console during tests
        
        with patch('blackjack.BlackjackApp.drawCard', return_value=mock_card):
            self.app.playHand(cards_test, is_dealer=True)
        self.assertEqual(len(cards_test.getCards()), 7)
        self.assertCountEqual(cards_test.getCards()[:2], cards_control.getCards())

    def test_play_hand_updates_card_view_player(self):
        return

    def test_play_hand_updates_card_view_dealer(self):
        return

    def test_play_round(self):
        return

    def test_(self):
        return

if __name__ == '__main__':
    unittest.main()