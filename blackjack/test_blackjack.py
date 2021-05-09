import unittest
from copy import deepcopy
from unittest.mock import DEFAULT, Mock, patch
from unittest.case import skip
from blackjack_interface import TextInterface
from blackjack import BlackjackApp as BlackjackAppClass
from cards import Card as CardClass, BlackjackCardSet as CardSetClass, RANKS, SUITS

class TestBlackjackAppGeneral(unittest.TestCase):

    def setUp(self):
        self.inter = TextInterface()
        self.app = BlackjackAppClass(self.inter)

        self.tie_msg = "It's a tie!\n"
        self.win_msg= "You won!\n"
        self.loss_msg = "You lost!\n"
        self.bust_msg = "Bust!\n"

        self.app.interface.updateCardView = Mock() # to avoid excessive output to the console during tests
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
            self.assertGreaterEqual(len(r_lst), target, msg=f"{RANKS[y][0]} appears less than {target} times out of {times}")

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
        cards.addCard(deepcopy(self.cards['ten']))   # ten
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
        cards.addCard(deepcopy(self.cards['six']))   # six
        can_play = self.app.canPlay(cards)
        self.assertFalse(can_play)

    def test_user_cannot_play_at_limit21(self):
        """
        Test that a user cannot add more cards with a total card score = 21
        """
        cards = CardSetClass()
        cards.addCard(deepcopy(self.cards['king']))  # king
        cards.addCard(deepcopy(self.cards['ace']))   # ace
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

        with patch('builtins.input', side_effect = ['hit', 'stand']) as input_mock:
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
            with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
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

        with patch('builtins.input', side_effect = ['hit'] * 4 + ['stand']) as input_mock:
            with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
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

        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
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

        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            self.app.playHand(cards_test, is_dealer=True)
        self.assertEqual(len(cards_test.getCards()), 7)
        self.assertCountEqual(cards_test.getCards()[:2], cards_control.getCards())

    def test_natural_blackjack_user(self):
        """
        Test that checks for a natural blackjack before playing the hand,
        when user has blackjack
        """
        PREDEFINED_VALUES = [
            self.cards['ten'],      # user card
            self.cards['nine'], 
            self.cards['ace'],      # user card
            self.cards['five']
        ]

        draw_card_wrapper = Mock(wraps=self.app.drawCard)
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return draw_card_wrapper()

        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_mock.assert_called_once_with("Blackjack! " + self.win_msg)

    def test_natural_blackjack_user_and_dealer(self):
        """
        Test that checks for a natural blackjack before playing the hand,
        when user and dealer both have blackjack
        """
        PREDEFINED_VALUES = [
            self.cards['jack'],
            self.cards['jack'],     # dealer's card
            self.cards['ace'], 
            self.cards['ace']       # dealer's card
        ]

        draw_card_wrapper = Mock(wraps=self.app.drawCard)
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return draw_card_wrapper()

        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_mock.assert_called_once_with(self.tie_msg)

    def test_natural_blackjack_dealer_only(self):
        """
        Test that checks dealer has natural blackjack before playing the hand
        **Note** Also tests for natural blackjack check when dealer's visible card is 10
        """
        PREDEFINED_VALUES = [
            self.cards['two'], 
            self.cards['ten'],      # dealer's card
            self.cards['three'], 
            self.cards['ace']       # dealer's card
        ]

        draw_card_wrapper = Mock(wraps=self.app.drawCard)
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return draw_card_wrapper()

        with patch('blackjack.BlackjackApp.drawCard', side_effect = side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_mock.assert_called_once_with("Dealer's got Blackjack! " + self.loss_msg)

    @skip("Will become redundant with new checkBlackjack func, visible cards no longer matter")
    def test_natural_blackjack_dealer_visible_card_11(self):
        """
        Test that checks whether dealer has natural blackjack when dealer's visible card is 11
        """
        return
    
    @patch('builtins.input')
    def test_game_flow_user_bust(self, input_mock):
        """
        Test that correct message is displayed when user goes bust
        """

        PREDEFINED_VALUES = [
            self.cards['two'],      # user card
            self.cards['three'], 
            self.cards['four'],     # user card
            self.cards['five']
        ]
        
        suit, rank = self.cards['ten'].getSuit(), self.cards['ten'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.return_value = 'hit'
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_call_args = [cl[0][0] for cl in print_mock.call_args_list]
                print_mock.assert_called_with(self.loss_msg)
                print_mock.assert_any_call(self.bust_msg)
                self.assertLess(print_call_args.index(self.bust_msg), print_call_args.index(self.loss_msg), 
                                msg="Should show bust message before the final game outcome is shown")

    @patch('builtins.input')
    def test_game_flow_user_dealer_tie(self, input_mock):
        """
        Test that correct message is displayed when it's a tie
        """

        # starting score of 6 for both
        PREDEFINED_VALUES = [
            self.cards['two'],      # user card
            self.cards['two'], 
            self.cards['four'],     # user card
            self.cards['four']
        ]

        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)    # ensures both user + dealer reach score 18

        input_mock.side_effect = ['hit', 'hit', 'stand']
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_mock.assert_called_with(self.tie_msg)

    @patch('builtins.input')
    def test_game_flow_dealer_win_no_blackjack(self, input_mock):
        """
        Test that correct message is displayed when dealer wins with score < 21
        """

        # starting score of 6 for user, 8 for dealer
        PREDEFINED_VALUES = [
            self.cards['two'],      # user card
            self.cards['two'], 
            self.cards['four'],     # user card
            self.cards['six']
        ]
        
        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['hit', 'hit', 'stand']
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_mock.assert_called_with(self.loss_msg)

    @patch('builtins.input')
    def test_game_flow_user_win_no_blackjack(self, input_mock):
        """
        Test that correct message is displayed when user wins with score < 21
        """

        # starting score of 6 for user, 6/16 for dealer, 
        # allowing for a single hit and total score of 12
        PREDEFINED_VALUES = [
            self.cards['two'],      # user card
            self.cards['ace'], 
            self.cards['four'],     # user card
            self.cards['five']
        ]
        
        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['hit', 'hit', 'stand']
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_mock.assert_called_with(self.win_msg)

    @patch('builtins.input')
    def test_game_flow_user_win_blackjack(self, input_mock):
        """
        Test that correct message is displayed when user wins with a Blackjack
        """

        # starting score of 6 for user, 6/16 for dealer, 
        # allowing for a single hit and total score of 12
        PREDEFINED_VALUES = [
            self.cards['three'],        # user card
            self.cards['ace'], 
            self.cards['six'],          # user card
            self.cards['five']
        ]
        
        suit, rank = self.cards['six'].getSuit(), self.cards['six'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['hit', 'hit', 'stand']
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_mock.assert_called_with("Blackjack! " + self.win_msg)

    # 4. analyse split hands flow outcome
    #     4.1. dealer has non-blackjack cards
    #         4.1.1. user's got two same cards and hits until bust on all ocassions
    #         4.1.2. user's got two same cards and stands on all ocassions
    #         4.2.3. user hits and gets same splittable hands every time
    #         4.2.4. user hits and busts one hand, not the other

    @patch('builtins.input')
    def test_split_flow_user_bust_all(self, input_mock):
        """
        Test that when cards are split correct outcomes are displayed for each round played, 
        when user busts all rounds
        """
        PREDEFINED_VALUES = [
            self.cards['five'],        # user card
            self.cards['three'], 
            self.cards['five'],          # user card
            self.cards['four']
        ]
        
        suit, rank = self.cards['seven'].getSuit(), self.cards['seven'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['hit'] * 4
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_call_args = [cl[0][0] for cl in print_mock.call_args_list]
                bust_idx = [arg.index(self.bust_msg) for arg in print_call_args if arg == self.bust_msg]
                self.assertEqual(len(bust_idx), 2)
                print_mock.assert_called_with(self.loss_msg)
                loss_idx = print_call_args.index(self.loss_msg)
                self.assertTrue(all(b_id < loss_idx for b_id in bust_idx), 
                                msg="Should show bust messages before the final game outcome is shown")

    @patch('builtins.input')
    def test_split_flow_user_stand_all(self, input_mock):
        """
        Test that when cards are split correct outcomes are displayed for each round played, 
        when user only stands on all rounds
        """
        PREDEFINED_VALUES = [
            self.cards['five'],        # user card
            self.cards['three'], 
            self.cards['five'],          # user card
            self.cards['four']
        ]
        
        suit, rank = self.cards['seven'].getSuit(), self.cards['seven'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['stand'] * 2
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_mock.assert_called_with(self.loss_msg)
                print_call_args = [cl[0][0] for cl in print_mock.call_args_list]
                self.assertEqual(print_call_args.count(self.loss_msg), 2)

    @skip("Cannot test without checking player's cards. Requires function re-writing.")
    @patch('builtins.input')
    def test_split_flow_max_times(self, input_mock):
        """
        Test that user can split cards up to 4 times and play each round
        """
        PREDEFINED_VALUES = [
            self.cards['five'],          # user card
            self.cards['three'], 
            self.cards['five'],          # user card
            self.cards['four']
        ]

        # draw_card_wrapper = Mock(wraps=self.app.drawCard)
        suit_split, rank_split = self.cards['five'].getSuit(), self.cards['five'].getRank()
        suit, rank = self.cards['four'].getSuit(), self.cards['four'].getRank()
        USER_HITS = [12]
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            USER_HITS[0] = USER_HITS[0] - 1
            if USER_HITS[0] > 0 and USER_HITS[0] % 3 == 0:
                return CardClass(suit_split, rank_split)
            else:
                return CardClass(suit, rank)

        input_mock.side_effect = ['split', 'hit', 'stand'] * 3 + ['hit', 'stand']
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                #TODO: check was split 4 times
                    # check player hands are 4, and each of them played
                    # check dealer's cards, then check the oucome matches expected
                    # depending on outcome check, final message
                # print_mock.assert_called_with(self.loss_msg)
                print_call_args = [cl[0][0] for cl in print_mock.call_args_list]

    @patch('builtins.input')
    def test_split_flow_user_bust_and_win(self, input_mock):
        """
        Test that when cards are split correct outcomes are displayed for each round played, 
        when user busts one round and wins the other
        """
        PREDEFINED_VALUES = [
            self.cards['five'],        # user card
            self.cards['two'], 
            self.cards['five'],        # user card
            self.cards['eight']
        ]
        
        suit, rank = self.cards['seven'].getSuit(), self.cards['seven'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split'] + ['hit'] * 3 + ['stand']
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_call_args = [cl[0][0] for cl in print_mock.call_args_list]
                print_mock.assert_called_with(self.win_msg)
                print_mock.assert_any_call(self.bust_msg)
                self.assertLess(print_call_args.index(self.bust_msg), print_call_args.index(self.win_msg), 
                                msg="Should show bust message before the final game outcome is shown")

    @patch('builtins.input')
    def test_split_flow_user_win_and_lose(self, input_mock):
        """
        Test that when cards are split correct outcomes are displayed for each round played, 
        when user wins one round with a blackjack and loses the other by without bust
        """
        PREDEFINED_VALUES = [
            self.cards['five'],        # user card
            self.cards['two'], 
            self.cards['five'],        # user card
            self.cards['eight']
        ]
        
        suit, rank = self.cards['eight'].getSuit(), self.cards['eight'].getRank()
        def side_effect():
            if len(PREDEFINED_VALUES) > 0:
                card_ref = PREDEFINED_VALUES.pop(0)
                value = deepcopy(card_ref)
                return value
            return CardClass(suit, rank)

        input_mock.side_effect = ['split', 'hit', 'stand']
        with patch('blackjack.BlackjackApp.drawCard', side_effect=side_effect):
            with patch('builtins.print') as print_mock:
                self.app.playRound()
                print_call_args = [cl[0][0] for cl in print_mock.call_args_list]
                print_mock.assert_called_with(self.loss_msg)
                print_mock.assert_any_call("Blackjack! " + self.win_msg)
                self.assertLess(print_call_args.index("Blackjack! " + self.win_msg), print_call_args.index(self.loss_msg), 
                                msg="Should show win message before the loss message is shown in this case")
        
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