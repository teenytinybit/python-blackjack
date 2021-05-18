import sys
from unittest.case import skip
from env import dev_path
sys.path.append(dev_path)

import unittest
from cards import Card, BlackjackCardSet, RANKS, SUITS

class TestCardClassMethods(unittest.TestCase):

    def test_correct_values_set_on_init(self):
        """
        Test that a card objects initialises correctly
        """
        for rank in range(len(RANKS)):
            card = Card(SUITS[0], RANKS[rank][0])
            self.assertCountEqual(card.getValue(), RANKS[rank][1])

    def test_not_hidden_on_init(self):
        """
        Test that a card objects initialises as visible
        """
        suit, rank = SUITS[0], RANKS[2][0]
        card = Card(suit, rank)
        self.assertFalse(card.isHidden())

    def test_toggle_visibility(self):
        """
        Test that a card object switches visibility
        """
        suit, rank = SUITS[0], RANKS[2][0]
        card = Card(suit, rank)
        card.toggleVisibility()
        self.assertTrue(card.isHidden())
        card.toggleVisibility()
        self.assertFalse(card.isHidden())


class TestCardSetClassMethods(unittest.TestCase):

    def setUp(self):
        self.ranks = {
            'ace': RANKS[0],
            'two': RANKS[1],
            'three': RANKS[2],
            'four': RANKS[3],
            'five': RANKS[4],
            'six': RANKS[5],
            'seven': RANKS[6],
            'eight': RANKS[7],
            'nine': RANKS[8],
            'ten': RANKS[9],
            'jack': RANKS[10],
            'queen': RANKS[11],
            'king': RANKS[12]
        }

    def test_correct_init(self):
        """
        Test that a cardset object initialises correctly
        """
        cardset = BlackjackCardSet()
        self.assertFalse(any([cardset.isSplitFromAce(), cardset.hasAce(), cardset.hasBlackjack()]))
        self.assertEqual(cardset.getScore(), [0, 0])
        self.assertEqual(cardset.getCards(), [])
        
    def test_correct_init_split_set(self):
        """
        Test that a cardset object initialises correctly when split is disabled
        """
        cardset = BlackjackCardSet(no_split=True)
        self.assertFalse(any([
            cardset.canSplit() ,cardset.isSplitFromAce(),
            cardset.hasAce(), cardset.hasBlackjack()
        ]))
        self.assertEqual(cardset.getScore(), [0, 0])
        self.assertEqual(cardset.getCards(), [])
        
    def test_add_cards(self):
        """
        Test that cards are added to a cardset object and object updated
        """
        test_cards = [
            Card(SUITS[1], 'four'),
            Card(SUITS[2], 'five'),
            Card(SUITS[3], 'six')
        ]
        expected_score = 15
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        
        self.assertEqual(len(cardset.getCards()), len(test_cards))
        for i in range(len(test_cards)):
            self.assertEqual(cardset.getCard(i), test_cards[i])
        self.assertEqual(cardset.getScore()[0], expected_score)
        self.assertFalse(any([
            cardset.canSplit(), cardset.isSplitFromAce(), 
            cardset.hasAce(), cardset.hasBlackjack()
        ]))
        
    def test_add_cards_ace(self):
        """
        Test that cards incuding a single ace are added to a cardset object and object updated
        """
        test_cards = [
            Card(SUITS[1], 'ace'),
            Card(SUITS[2], 'five'),
            Card(SUITS[3], 'six')
        ]
        expected_score = [12, 22]
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        
        self.assertTrue(cardset.hasAce())
        self.assertListEqual(cardset.getScore(), expected_score)
        self.assertEqual(len(cardset.getCards()), len(test_cards))
        for i in range(len(test_cards)):
            self.assertEqual(cardset.getCard(i), test_cards[i])
        self.assertFalse(any([cardset.canSplit(), cardset.isSplitFromAce(), cardset.hasBlackjack()]))

    def test_add_cards_multiple_ace(self):
        """
        Test that cards incuding multiple aces are added to a cardset object and object updated
        """
        test_cards = [
            Card(SUITS[1], 'ace'),
            Card(SUITS[2], 'ace'),
            Card(SUITS[3], 'six'),
            Card(SUITS[3], 'two')
        ]
        expected_score = [10, 20]
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        
        self.assertTrue(cardset.hasAce())
        self.assertListEqual(cardset.getScore(), expected_score)
        self.assertEqual(len(cardset.getCards()), len(test_cards))
        for i in range(len(test_cards)):
            self.assertEqual(cardset.getCard(i), test_cards[i])
        self.assertFalse(any([cardset.canSplit(), cardset.isSplitFromAce(), cardset.hasBlackjack()]))

    def test_add_cards_21_not_blackjack(self):
        """
        Test that when added cards with a total score of 21 are NOT recognised as a blackjack
        """
        test_cards = [
            Card(SUITS[1], 'ten'),
            Card(SUITS[2], 'eight'),
            Card(SUITS[3], 'three')
        ]
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        
        self.assertFalse(cardset.hasBlackjack())
        self.assertEqual(len(cardset.getCards()), len(test_cards))
        for i in range(len(test_cards)):
            self.assertEqual(cardset.getCard(i), test_cards[i])
        self.assertFalse(any([cardset.canSplit(), cardset.isSplitFromAce(), cardset.hasAce()]))

    def test_add_cards_21_blackjack(self):
        """
        Test that when two cards with a total score of 21 are recognised as a blackjack
        """
        test_cards = [
            Card(SUITS[1], 'ten'),
            Card(SUITS[2], 'ace')
        ]
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        
        self.assertTrue(cardset.hasBlackjack())
        self.assertTrue( cardset.hasAce())
        self.assertEqual(len(cardset.getCards()), len(test_cards))
        for i in range(len(test_cards)):
            self.assertEqual(cardset.getCard(i), test_cards[i])
        self.assertFalse(any([cardset.canSplit(), cardset.isSplitFromAce()]))

    def test_can_split(self):
        """
        Test that cards can be split when same ranked cards present
        """
        test_cards = [
            Card(SUITS[1], 'three'),
            Card(SUITS[2], 'three')
        ]
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        self.assertTrue(cardset.canSplit())

    def test_can_split_diff_rank_same_val(self):
        """
        Test that cards can be split when same value different ranked cards present
        """
        test_cards = [
            Card(SUITS[1], 'ten'),  #value = 10
            Card(SUITS[2], 'jack')  #value = 10
        ]
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        self.assertTrue(cardset.canSplit())

    @skip("Same value cards can be split in this version of the game")
    def test_cannot_split_diff_rank_same_val(self):
        """
        Test that cards cannot be split when same value different ranked cards present
        """
        test_cards = [
            Card(SUITS[1], 'ten'),  #value = 10
            Card(SUITS[2], 'jack')  #value = 10
        ]
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        self.assertFalse(cardset.canSplit())

    def test_cannot_split_single_card(self):
        """
        Test that cards cannot be split when a hand LESS than 2 cards
        """
        cardset = BlackjackCardSet()
        cardset.addCard(Card(SUITS[1], 'ace'))
        self.assertFalse(cardset.canSplit())

    def test_cannot_split_has_more_than_two_cards(self):
        """
        Test that cards cannot be split when a hand has MORE than 2 cards, 
        even is same ranked cards are present
        """
        test_cards = [
            Card(SUITS[1], 'three'),
            Card(SUITS[2], 'three'),
            Card(SUITS[3], 'six')
        ]
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        self.assertFalse(cardset.canSplit())

    def test_cannot_split_when_split_disabled(self):
        """
        Test that cards cannot be split when the hand has splitting disabled
        """
        test_cards = [
            Card(SUITS[1], 'nine'),
            Card(SUITS[2], 'nine')
        ]
        cardset = BlackjackCardSet(no_split=True)
        for tc in test_cards: cardset.addCard(tc)
        self.assertFalse(cardset.canSplit())

    def test_hide_card_score_updates(self):
        """
        Test that when a card is hidden, score reflects only visible cards
        """
        test_cards = [
            Card(SUITS[1], 'two'),      # will be hidden
            Card(SUITS[2], 'four'),
            Card(SUITS[3], 'six'),      # will be hidden
            Card(SUITS[0], 'eight')
        ]
        expected_score = 12
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        cardset.hideCard(0)
        cardset.hideCard(2)
        cards = cardset.getCards()
        self.assertTrue(all([cards[0].isHidden(), cards[2].isHidden()]))
        self.assertEqual(cardset.getScore()[0], expected_score)

    def test_reveal_card_score_updates(self):
        """
        Test that when a card is revealed, score reflects visible cards
        """
        test_cards = [
            Card(SUITS[1], 'five'),      # will be revealed
            Card(SUITS[2], 'four'),
            Card(SUITS[3], 'three'),      # will be revealed
            Card(SUITS[0], 'eight')
        ]
        test_cards[0].toggleVisibility()
        test_cards[2].toggleVisibility()
        
        expected_score = 20
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        cardset.revealCard(0)
        cardset.revealCard(2)
        cards = cardset.getCards()
        self.assertFalse(any([cards[0].isHidden(), cards[2].isHidden()]))
        self.assertEqual(cardset.getScore()[0], expected_score)

    def test_do_split_ace(self):
        """
        Test original cards are split (from Ace) correctly and a new split hand is returned 
        with split disabled
        """
        test_cards = [
            Card(SUITS[1], 'ace'),
            Card(SUITS[2], 'ace')
        ]
        expected_score = [1, 11]
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        cardset2 = cardset.doSplit()
        self.assertIsInstance(cardset2, BlackjackCardSet)
        card_sets = (cardset, cardset2)
        for i in range(2):
            self.assertTrue(card_sets[i].isSplitFromAce())
            self.assertEqual(len(card_sets[i].getCards()), 1)
            self.assertListEqual(card_sets[i].getScore(), expected_score)
            self.assertFalse(card_sets[i].canSplit())
            card = card_sets[i].getCard(0)
            self.assertEqual(card, test_cards[i])
            self.assertFalse(card.isHidden())

    def test_do_split_regular(self):
        """
        Test original cards are split correctly and a new split hand is returned
        """
        test_cards = [
            Card(SUITS[1], 'jack'),
            Card(SUITS[2], 'jack')
        ]
        expected_score = 10
        cardset = BlackjackCardSet()
        for tc in test_cards: cardset.addCard(tc)
        cardset2 = cardset.doSplit()
        self.assertIsInstance(cardset2, BlackjackCardSet)
        card_sets = (cardset, cardset2)
        for i in range(2):
            self.assertFalse(card_sets[i].isSplitFromAce())
            self.assertFalse(card_sets[i].canSplit())
            self.assertEqual(len(card_sets[i].getCards()), 1)
            self.assertEqual(card_sets[i].getScore()[0], expected_score)
            card = card_sets[i].getCard(0)
            self.assertEqual(card, test_cards[i])
            self.assertFalse(card.isHidden())
        
