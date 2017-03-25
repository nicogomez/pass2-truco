from django.test import TestCase
from truco.models.card import Card

class CardTests(TestCase):

    def setUp(self):
        Card.objects.create(anchor=1)
        Card.objects.create(number=1, palo='e', position = 1, anchor=2)

    def test_creating_correct(self):
        card_1 = Card.objects.get(anchor=1)
        self.assertEqual(card_1.number, 0)
        self.assertEqual(card_1.palo, 'r')
        self.assertEqual(card_1.position, 0)

    def test_set_from_tuple(self):
        card_1 = Card.objects.get(anchor=1)
        card_1.set_from_tuple((3, 'o'))
        self.assertEqual(card_1.number, 3)
        self.assertEqual(card_1.palo, 'o')

    def test_en_mano(self):
        card_1 = Card.objects.get(anchor=1)
        self.assertEqual(card_1.en_mano(), True)

    def test_to_string(self):
        card_2 = Card.objects.get(anchor=2)
        self.assertEqual(card_2.to_string(), '1e')

    def test_get_score(self):
        card_2 = Card.objects.get(anchor=2)
        self.assertEqual(card_2.get_score(), 14)

    def test_get_css_class(self):
        card_2 = Card.objects.get(anchor=2)
        self.assertEqual(card_2.get_css_class(), 'firstCard')
        card_2.position = 2
        self.assertEqual(card_2.get_css_class(), 'secondCard')
        card_2.position = 3
        self.assertEqual(card_2.get_css_class(), 'thirdCard')
