from django.test import TestCase
from truco.models import *
from django.contrib.auth.models import User

class EnvidoManagerTests(TestCase):

    def setUp(self):
        game_1 = Game.objects.create(name='1', team_a_score=6, team_b_score=10)
        game_1.round= Round()
        game_1.round.save()
        game_1.round.init_canto_managers()
        game_1.round.save()
        user_1 = User.objects.create_user(username='nano', password='nano')
        user_2 = User.objects.create_user(username='nico', password='nico')
        card_1 = Card.objects.create(number=12, palo='e', position=0, anchor=1)
        card_2 = Card.objects.create(number=7, palo='o', position=0, anchor=2)
        card_3 = Card.objects.create(number=1, palo='e', position=0, anchor=3)
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
        emgr = EnvidoManager.objects.get(round=game_1.round)
        canto_1= emgr.canto_set.create()
        canto_1.set_canto(1)

    def test_get_ultimo_canto(self):
        round_1 = Round.objects.get(id=1)
        emgr = EnvidoManager.objects.get(round=round_1)
        self.assertEqual(emgr.get_ultimo_canto(), 1)

    def test_get_estado_del_ultimo_canto(self):
        round_1 = Round.objects.get(id=1)
        emgr = EnvidoManager.objects.get(round=round_1)
        self.assertEqual(emgr.get_estado_del_ultimo_canto(), 1)

    def test_hay_algun_canto_aceptado(self):
        round_1 = Round.objects.get(id=1)
        emgr = EnvidoManager.objects.get(round=round_1)
        self.assertFalse(emgr.hay_algun_canto_aceptado())

    def test_aceptar_ultimo_canto(self):
        round_1 = Round.objects.get(id=1)
        emgr = EnvidoManager.objects.get(round=round_1)
        emgr.aceptar_ultimo_canto()
        self.assertTrue(emgr.hay_algun_canto_aceptado())
        canto = emgr.canto_set.last()
        self.assertEqual(canto.estado, 2) #aceptado

    def test_rechazar_ultimo_canto(self):
        round_1 = Round.objects.get(id=1)
        emgr = EnvidoManager.objects.get(round=round_1)
        emgr.rechazar_ultimo_canto()
        canto = emgr.canto_set.last()
        self.assertEqual(canto.estado, 3) #rechazado
    

    def test_recantar(self):
        round_1 = Round.objects.get(id=1)
        emgr = EnvidoManager.objects.get(round=round_1)

        user_2 = User.objects.get(username='nico')
        player_2 = Player.objects.get(user=user_2)
        #El player 2 canta retruco
        emgr.recantar(2, player_2) 
        emgr = EnvidoManager.objects.get(round=round_1)
        self.assertEqual(emgr.get_ultimo_canto(), 2) 
        self.assertEqual(emgr.get_estado_del_ultimo_canto(), 1)
        self.assertEqual(emgr.quien_canto_ultimo, player_2)

    def test_se_puede_cantar(self):
        round_1 = Round.objects.get(id=1)
        emgr = EnvidoManager.objects.get(round=round_1)
        self.assertTrue(emgr.se_puede_cantar(2))
        self.assertTrue(emgr.se_puede_cantar(3))
        self.assertTrue(emgr.se_puede_cantar(4))
        self.assertFalse(emgr.se_puede_cantar(5))

    def test_get_falta_envido_points(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        user_2 = User.objects.get(username='nico')
        player_2 = Player.objects.get(user=user_2)
        round_1 = Round.objects.get(id=1)
        emgr = EnvidoManager.objects.get(round=round_1)

        emgr.recantar(4, player_1)
        emgr.aceptar_ultimo_canto()
        self.assertEqual(emgr.get_falta_envido_points(), 5)

    def test_get_envido_points_to_assign(self):
        round_1 = Round.objects.get(id=1)
        emgr = EnvidoManager.objects.get(round=round_1)
        self.assertEqual(emgr.get_envido_points_to_assign(), 0)
        emgr.aceptar_ultimo_canto()
        self.assertEqual(emgr.get_envido_points_to_assign(), 2)

    def test_determine_envido_winner(self):
        user_1 = User.objects.get(username='nano')
        player_1 = Player.objects.get(user=user_1)
        player_1.declared_envido_points = 30
        player_1.save()
        user_2 = User.objects.get(username='nico')
        player_2 = Player.objects.get(user=user_2)
        player_2.declared_envido_points = 25
        player_2.save()
        round_1 = Round.objects.get(id=1)
        # import ipdb; ipdb.set_trace()
        emgr = EnvidoManager.objects.get(round=round_1)
        emgr.determine_envido_winner()
        self.assertEqual(round_1.team_a_round_score, emgr.get_envido_points_to_assign())