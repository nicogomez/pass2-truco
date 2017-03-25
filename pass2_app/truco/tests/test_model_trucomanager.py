from django.test import TestCase
from truco.models import *
from django.contrib.auth.models import User

class TrucoManagerTests(TestCase):

    def setUp(self):
        game_1 = Game.objects.create(name='1')
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
        
        tmgr = TrucoManager.objects.get(round=game_1.round)
        tmgr.quien_canto_ultimo = Player.objects.get(user=user_1)
        canto_1= tmgr.canto_set.create()
        canto_1.set_canto(5)

    def test_get_ultimo_canto(self):
        round_1 = Round.objects.get(id=1)
        tmgr = TrucoManager.objects.get(round=round_1)
        self.assertEqual(tmgr.get_ultimo_canto(), 5)

    def test_get_estado_del_ultimo_canto(self):
        round_1 = Round.objects.get(id=1)
        tmgr = TrucoManager.objects.get(round=round_1)
        self.assertEqual(tmgr.get_estado_del_ultimo_canto(), 1)

    def test_hay_algun_canto_aceptado(self):
        round_1 = Round.objects.get(id=1)
        tmgr = TrucoManager.objects.get(round=round_1)
        self.assertFalse(tmgr.hay_algun_canto_aceptado())

    def test_aceptar_ultimo_canto(self):
        round_1 = Round.objects.get(id=1)
        tmgr = TrucoManager.objects.get(round=round_1)
        tmgr.aceptar_ultimo_canto()
        self.assertTrue(tmgr.hay_algun_canto_aceptado())
        canto = tmgr.canto_set.last()
        self.assertEqual(canto.estado, 2) #aceptado

    def test_rechazar_ultimo_canto(self):
        round_1 = Round.objects.get(id=1)
        tmgr = TrucoManager.objects.get(round=round_1)
        tmgr.rechazar_ultimo_canto()
        canto = tmgr.canto_set.last()
        self.assertEqual(canto.estado, 3) #rechazado

    def test_recantar(self):
        round_1 = Round.objects.get(id=1)
        tmgr = TrucoManager.objects.get(round=round_1)
        user_2 = User.objects.get(username='nico')
        player_2 = Player.objects.get(user=user_2)
        # El player 2 canta retruco
        tmgr.recantar(6, player_2) 
        tmgr = TrucoManager.objects.get(round=round_1)
        self.assertEqual(tmgr.get_ultimo_canto(), 6) 
        self.assertEqual(tmgr.get_estado_del_ultimo_canto(), 1)
        self.assertEqual(tmgr.quien_canto_ultimo, player_2)

    def test_se_puede_cantar(self):
        round_1 = Round.objects.get(id=1)
        tmgr = TrucoManager.objects.get(round=round_1)
        self.assertTrue(tmgr.se_puede_cantar(6))
        self.assertFalse(tmgr.se_puede_cantar(7))

    def test_get_truco_points_to_assign(self):
        round_1 = Round.objects.get(id=1)
        tmgr = TrucoManager.objects.get(round=round_1)
        self.assertEqual(tmgr.get_truco_points_to_assign(), 1)
        tmgr.aceptar_ultimo_canto()
        self.assertEqual(tmgr.get_truco_points_to_assign(), 2)



