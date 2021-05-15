import sys
from env import dev_path
sys.path.append(dev_path)

import unittest
from copy import deepcopy
from unittest.mock import Mock, patch
from unittest.case import skip
from blackjack_interface import TextInterface, GraphicInterface
from cards import Card, BlackjackCardSet
from blackjack_misc import Outcome, Actions


class TestTextInterface(unittest.TestCase):

    def setUp(self):
        self.inter = TextInterface()
        self.PREDEFINED_CARDS = [
            Card('hearts', 'ten'),
            Card('spades', 'three'),
            Card('diamonds', 'two'),
            Card('clubs', 'four')
        ]

    def test_clear(self):
        """
        Test that clear() method does nothing
        """
        res = self.inter.clear()
        self.assertIsNone(res)
        
    def test_wants_to_play_yes(self):
        """
        Test that an appropriate response is returned when player wants to start the game
        """
        with patch('builtins.input', return_value='start'):
            res = self.inter.wantsToPlay()
            self.assertTrue(res)

    def test_wants_to_play_no(self):
        """
        Test that an appropriate response is returned when player wants to exit the game
        """
        with patch('builtins.input', return_value='exit'):
            res = self.inter.wantsToPlay()
            self.assertFalse(res)

    def test_close(self):
        """
        Test that the interface prints some exit message on close
        """
        with patch('builtins.print') as print_patch:
            self.inter.close()
            print_patch.assert_called_once()
            self.assertGreater(len(print_patch.call_args[0]), 0)
            msg = print_patch.call_args[0][0]
            self.assertIsInstance(msg, str)
            self.assertGreater(len(msg), 0, msg="Close message should not be empty")

    def test_greet(self):
        """
        Test that the interface prints some greeting message
        """
        with patch('builtins.print') as print_patch:
            self.inter.greet()
            print_patch.assert_called_once()
            self.assertGreater(len(print_patch.call_args[0]), 0)
            msg = print_patch.call_args[0][0]
            self.assertIsInstance(msg, str)
            self.assertGreater(len(msg), 0, msg="Greeting message should not be empty")

    def test_init_view(self):
        """
        Test that the game prints some text border before starting the round
        """
        with patch('builtins.print') as print_patch:
            self.inter.initializeView()
            print_patch.assert_called()

    def test_show_outcome_message(self):
        """
        Test that the method prints the defined message
        """
        defined_msg = "This is the expected message"
        with patch('builtins.print') as print_patch:
            res = self.inter.showOutcomeMessage(defined_msg)
            self.assertIsNone(res)
            print_patch.assert_called_once_with(defined_msg)

    def test_update_card_view_player(self):
        """
        Test that textual card view is displayed correctly for a player
        """
        card_hand = BlackjackCardSet()
        for card in self.PREDEFINED_CARDS:
            card_hand.addCard(deepcopy(card))

        ownership = "Your cards: "
        card_names = []
        for c in card_hand.getCards():
            card_names.append((c.getRank() + " of " + c.getSuit()).title())
        score = "Total value: 19"
        expected_el = [ownership] + card_names + [score]
        
        with patch('builtins.print') as print_patch:
            self.inter.updateCardView(card_hand)
            print_patch.assert_called()
            printed_args = [cl[0][0] for cl in print_patch.call_args_list]
            # check all expected text elements are there
            total_res = "".join(printed_args)
            found_els = []
            for el in expected_el:
                self.assertIn(el, total_res)
                found_els.append(total_res.index(el))
            
            last_element = -1
            for curr_element in found_els:
                self.assertGreater(curr_element, last_element)
                last_element = curr_element

        # check cards not changed
        cards = card_hand.getCards()
        self.assertEqual(len(cards), len(self.PREDEFINED_CARDS))
        for i in range(len(self.PREDEFINED_CARDS)):
            self.assertEqual(cards[i], self.PREDEFINED_CARDS[i])

    def test_update_card_view_hidden(self):
        """
        Test that textual card view is displayed correctly when some cards are hidden
        """
        card_hand = BlackjackCardSet()
        for i in range(len(self.PREDEFINED_CARDS)):
            card = self.PREDEFINED_CARDS[i]
            if i == 0:
                card.toggleVisibility()
            card_hand.addCard(deepcopy(card))

        ownership = "Your cards: "
        card_names = []
        for c in card_hand.getCards():
            card_names.append((c.getRank() + " of " + c.getSuit()).title())
        card_names[0] = "**Card Hidden**"
        score = "Total value: 9"
        expected_el = [ownership] + card_names + [score]
        
        with patch('builtins.print') as print_patch:
            self.inter.updateCardView(card_hand)
            print_patch.assert_called()
            printed_args = [cl[0][0] for cl in print_patch.call_args_list]
            # validate border length
            self.assertTrue(self.inter.BORDER_LENGTH + 1 >= len(printed_args[0]) >= self.inter.BORDER_LENGTH)
            # check all expected text elements are there
            total_res = "".join(printed_args)
            found_els = []
            for el in expected_el:
                self.assertIn(el, total_res)
                found_els.append(total_res.index(el))
            
            last_element = -1
            for curr_element in found_els:
                self.assertGreater(curr_element, last_element)
                last_element = curr_element

        # check cards not changed
        cards = card_hand.getCards()
        self.assertEqual(len(cards), len(self.PREDEFINED_CARDS))
        for i in range(len(self.PREDEFINED_CARDS)):
            self.assertEqual(cards[i], self.PREDEFINED_CARDS[i])

    def test_update_card_view_ace(self):
        """
        Test that textual card view is displayed correctly when ace is present
        """
        card_hand = BlackjackCardSet()
        for i in range(len(self.PREDEFINED_CARDS)):
            card = self.PREDEFINED_CARDS[i] if i > 0 else Card('spades', 'ace')
            card_hand.addCard(deepcopy(card))

        ownership = "Your cards: "
        card_names = []
        for c in card_hand.getCards():
            card_names.append((c.getRank() + " of " + c.getSuit()).title())
        score = "Total value: 10 or 20"
        expected_el = [ownership] + card_names + [score]
        
        with patch('builtins.print') as print_patch:
            self.inter.updateCardView(card_hand)
            print_patch.assert_called()
            printed_args = [cl[0][0] for cl in print_patch.call_args_list]
            # validate border length
            self.assertTrue(self.inter.BORDER_LENGTH + 1 >= len(printed_args[0]) >= self.inter.BORDER_LENGTH)
            # check all expected text elements are there
            total_res = "".join(printed_args)
            found_els = []
            for el in expected_el:
                self.assertIn(el, total_res)
                found_els.append(total_res.index(el))
            
            last_element = -1
            for curr_element in found_els:
                self.assertGreater(curr_element, last_element)
                last_element = curr_element

    def test_update_card_view_dealer(self):
        """
        Test that textual card view is displayed correctly for a dealer
        """
        card_hand = BlackjackCardSet()
        for card in self.PREDEFINED_CARDS:
            card_hand.addCard(deepcopy(card))

        ownership = "Dealer's cards: "
        card_names = []
        for c in card_hand.getCards():
            card_names.append((c.getRank() + " of " + c.getSuit()).title())
        score = "Total value: 19"
        expected_el = [ownership] + card_names + [score]
        
        with patch('builtins.print') as print_patch:
            self.inter.updateCardView(card_hand, is_dealer=True)
            print_patch.assert_called()
            printed_args = [cl[0][0] for cl in print_patch.call_args_list]
            # validate border length
            self.assertTrue(self.inter.BORDER_LENGTH + 1 >= len(printed_args[0]) >= self.inter.BORDER_LENGTH)
            # check all expected text elements are there
            total_res = "".join(printed_args)
            found_els = []
            for el in expected_el:
                self.assertIn(el, total_res)
                found_els.append(total_res.index(el))
            
            last_element = -1
            for curr_element in found_els:
                self.assertGreater(curr_element, last_element)
                last_element = curr_element

        # check cards not changed
        cards = card_hand.getCards()
        self.assertEqual(len(cards), len(self.PREDEFINED_CARDS))
        for i in range(len(self.PREDEFINED_CARDS)):
            self.assertEqual(cards[i], self.PREDEFINED_CARDS[i])

    def test_get_action_split(self):
        """
        Test that a method correctly asks for input and processes the response
        - Split option
        - correct message option is displayed
        - input is correctly processed
        """
        action = Actions.SPLIT
        other_actions = [a.value for a in Actions if a != action]
        with patch('builtins.input', side_effect=other_actions + [action.value]) as input_patch:
            self.inter.getAction(action)
            input_patch.assert_called()
            self.assertEqual(input_patch.call_count, 4)
            printed_args = [cl[0][0] for cl in input_patch.call_args_list if action.value in cl[0][0]]
            self.assertGreaterEqual(len(printed_args), 1)

    def test_get_action_regular(self):
        """
        Test that a method correctly asks for input and processes the response
        - Stand or Hit options
        - correct message options is displayed
        - input is correctly processed
        """
        return_vals = [Actions.DOUBLE.value, Actions.SPLIT.value, Actions.STAND.value]
        with patch('builtins.input', side_effect=return_vals) as input_patch:
            self.inter.getAction(Actions.STAND, Actions.HIT)
            input_patch.assert_called()
            self.assertEqual(input_patch.call_count, 3)
            printed_args = [cl[0][0] for cl in input_patch.call_args_list]
            opt = [(Actions.STAND.value in arg and Actions.HIT.value in arg) for arg in printed_args]
            self.assertTrue(any(opt))
            
    def test_get_action_all(self):
        """
        Test that a method correctly asks for input and processes the response
        - Split, Double, Stand and Hit option
        - correct message is displayed
        - input is correctly processed
        """
        with patch('builtins.input', side_effect=[Actions.HIT.value]) as input_patch:
            self.inter.getAction(Actions.STAND, Actions.HIT, Actions.SPLIT, Actions.DOUBLE)
            input_patch.assert_called()
            self.assertEqual(input_patch.call_count, 1)
            printed_args = [cl[0][0] for cl in input_patch.call_args_list]
            opt = [(
                Actions.STAND.value in arg \
                and Actions.HIT.value in arg \
                and Actions.DOUBLE.value in arg \
                and Actions.SPLIT.value in arg) for arg in printed_args]
            self.assertTrue(any(opt))

    def test_get_action_double(self):
        """
        Test that a method correctly asks for input and processes the response
        - Double option
        - correct message is displayed
        - input is correctly processed
        """
        action = Actions.DOUBLE
        other_actions = [a.value for a in Actions if a != action]
        with patch('builtins.input', side_effect=other_actions + [action.value]) as input_patch:
            self.inter.getAction(action)
            input_patch.assert_called()
            self.assertEqual(input_patch.call_count, 4)
            printed_args = [cl[0][0] for cl in input_patch.call_args_list if action.value in cl[0][0]]
            self.assertGreaterEqual(len(printed_args), 1)

    def test_get_bet(self):
        """
        Test that interface requests to input a custom bet amount
        - only defined bets of 10, 25, 50 and 100 are valid
        """
        test_bets = [10, 25, 50, 100]
        with patch('builtins.input', side_effect=test_bets):
            for bet in test_bets:
                actual_bet = self.inter.getBet(100)
                self.assertEqual(bet, actual_bet)

    def test_get_bet_negative(self):
        """
        Test that a negative bet is not allowed
        """
        test_bets = [-10, -25, -50, -100, 10]
        with patch('builtins.input', side_effect=test_bets):
            actual_bet = self.inter.getBet(100)
            self.assertEqual(10, actual_bet)

    def test_get_bet_non_standard(self):
        """
        Test that a positive non-defined bet is not allowed (e.g., 33) 
        """
        test_bets = [7, 33, 65, 70, 200, 25]
        with patch('builtins.input', side_effect=test_bets):
            actual_bet = self.inter.getBet(100)
            self.assertEqual(25, actual_bet)

    def test_get_bet_zero(self):
        """
        Test that a 0 bet is not allowed
        """
        test_bets = [0, 50]
        with patch('builtins.input', side_effect=test_bets):
            actual_bet = self.inter.getBet(100)
            self.assertEqual(50, actual_bet)

    def test_get_bet_non_int(self):
        """
        Test that non-integer bets are not allowed
        """
        test_bets = [0.5, 'abc', 10.3, 'hello', 50.99, 100.01, 25.0]
        with patch('builtins.input', side_effect=test_bets):
            actual_bet = self.inter.getBet(100)
            self.assertEqual(25, actual_bet)

    def test_get_bet_low_balance(self):
        """
        Test that bets available do not exceed total balance
        """
        test_bets = [50, 100, 25]
        with patch('builtins.input', side_effect=test_bets):
            actual_bet = self.inter.getBet(30)
            self.assertEqual(25, actual_bet)


class TestGraphicInterface(unittest.TestCase):

    def setUp(self):
        return

    @skip('Test not implemented yet')
    def test_greeting(self):
        return


