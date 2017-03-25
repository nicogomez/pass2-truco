from django.test import TestCase
from truco.models import *
from django.contrib.auth.models import User

class PlayerTests(TestCase):

    def setUp(self):
        user_1 = User.objects.create_user(username='nano', password='nano')
        user_2 = User.objects.create_user(username='nico', password='nico')
        card_1 = Card.objects.create(number=12, palo='e', position=0, anchor=1)
        card_2 = Card.objects.create(number=7, palo='o', position=0, anchor=2)
        card_3 = Card.objects.create(number=1, palo='e', position=0, anchor=3)
        game_1 = Game.objects.create(name='1', team_a_score=6, team_b_score=10)
        game_1.round = Round(current_turn=1, confront_number=1, team_a_round_score=4, team_b_round_score=1)
        game_1.round.save()
        Player.objects.create(
            user=user_1,
            game=game_1,
            card_1=card_1,
            card_2=card_2,
            card_3=card_3,
            team=-1
        )
        Player.objects.create(
            user=user_2,
            game=game_1,
            card_1=card_1,
            card_2=card_2,
            card_3=card_3,
            team=1
        )

    def test_creating_correct(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        self.assertIsInstance(player_1.game, Game)
        self.assertEqual(player_1.team, -1)
        self.assertEqual(player_1.owner, False)
        self.assertIsInstance(player_1.card_1, Card)
        self.assertIsInstance(player_1.card_2, Card)
        self.assertIsInstance(player_1.card_3, Card)
        self.assertEqual(player_1.declared_envido_points, 0)
        self.assertEqual(player_1.place_on_table, 0)
        self.assertEqual(player_1.gone_to_mazo, False)

    def test_put_card(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        player_1.put_card('2')
        Card.objects.get(anchor=2)
        self.assertEqual(player_1.card_2.position, player_1.game.round.confront_number)

    def test_get_envido_points(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        self.assertEqual(player_1.get_envido_points(), 21)
        Card.objects.create(number=12, palo='o', anchor=4)
        player_1.card_1 = Card.objects.get(anchor=4)
        self.assertEqual(player_1.get_envido_points(), 27)
        Card.objects.create(number=12, palo='b', anchor=5)
        player_1.card_1 = Card.objects.get(anchor=5)
        self.assertEqual(player_1.get_envido_points(), 12)

    def test_get_current_cards(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        self.assertNotEqual(player_1.get_current_cards(), [])
        self.assertEqual(len(player_1.get_current_cards()), 3)

    def test_is_my_turn(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        self.assertFalse(player_1.is_my_turn())
        player_1.place_on_table = 1
        self.assertTrue(player_1.is_my_turn())

    def test_next_turn_is_mine(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        player_1.place_on_table = 1
        user_2 = User.objects.get(username='nico')
        player_2 = Player.objects.get(user=user_2)
        player_2.place_on_table = 0
        self.assertFalse(player_1.next_turn_is_mine())
        self.assertTrue(player_2.next_turn_is_mine())
        

    def test_get_my_team_score(self):
    # Tambien hace test de get_opponent_team_score
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        user_2 = User.objects.get(username='nico')
        player_2 = Player.objects.get(user=user_2)
        self.assertEqual(player_1.get_my_team_score(), 6)
        self.assertEqual(player_2.get_my_team_score(), 10)
        self.assertEqual(player_1.get_opponent_team_score(), 10)

    def test_get_my_team_round_score(self):
    # Tambien hace test de get_opponent_team_round_score
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        self.assertEqual(player_1.get_my_team_round_score(), 4)
        self.assertEqual(player_1.get_opponent_team_round_score(), 1)

    def test_declare_envido(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        user_2 = User.objects.get(username='nico')
        player_2 = Player.objects.get(user=user_2)
        player_1.game.round.init_canto_managers()
        player_1.declare_canto(1)
        self.assertEqual(player_1.declared_envido_points, 0)
        self.assertEqual(player_2.game.round.get_envido_manager().quien_canto_ultimo, player_1)

    def test_declare_vale_cuatro(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        user_2 = User.objects.get(username='nico')
        player_2 = Player.objects.get(user=user_2)
        player_1.game.round.init_canto_managers()
        player_1.declare_canto(5) #TRuco
        player_2.declare_canto(6) #Retruco
        player_1 = Player.objects.get(user=user_1)
        player_1.declare_canto(7)  #ValeCuatro
        player_2 = Player.objects.get(user=user_2)
        self.assertEqual(player_1.gone_to_mazo, False)
        self.assertEqual(player_1.game.round.get_truco_manager().quien_canto_ultimo, player_1)

    def test_leave_game(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        player_1.leave_game()
        self.assertEqual(len(Player.objects.all()), 1)

    def test_get_opponent_team(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        self.assertEqual(player_1.get_opponent_team(), 1)

    def test_get_card_by_number(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        self.assertEqual(player_1.get_card_by_number('1'), player_1.card_1)
        self.assertEqual(player_1.get_card_by_number('2'), player_1.card_2)
        self.assertEqual(player_1.get_card_by_number('3'), player_1.card_3)
        self.assertEqual(player_1.get_card_by_number('50'), None)

    def test_get_card_by_position(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        self.assertEqual(player_1.get_card_by_position(1), None)
        player_1.card_1.position = 1
        self.assertEqual(player_1.get_card_by_position(1), player_1.card_1)
        user_2 = User.objects.get(username='nico')
        player_2 = Player.objects.get(user=user_2)
        player_2.card_3.position = 1
        self.assertEqual(player_2.get_card_by_position(1), player_2.card_3)

    def test_delete_cards(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        self.assertEqual(len(Card.objects.all()), 3)
        player_1.delete_cards()
        player_1 = Player.objects.get(user=user_1)
        self.assertEqual(len(Card.objects.all()), 0)




